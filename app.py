import os
import io
import zipfile
from datetime import datetime
import uuid
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from dotenv import load_dotenv

import data_manager as dm
from ai_helper import ask_ai
from prompts import DOC_PROMPTS, get_doc_system_prompt

load_dotenv()
app = Flask(__name__)

DOC_ORDER = ["prd", "trd", "architecture", "database", "api", "ui", "steps", "diagram"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects')
def projects():
    projs = dm.load_projects()
    return render_template('projects.html', projects=projs)

@app.route('/api/project', methods=['POST'])
def create_project():
    data = request.json
    idea = data.get('idea', 'Unnamed Project')
    options = data.get('options', {})
    project = dm.create_project(idea, options)
    return jsonify({"id": project['id']})

@app.route('/project/<project_id>')
def project_workspace(project_id):
    project = dm.get_project(project_id)
    if not project:
        return "Project not found", 404
    return render_template('project.html', project=project, doc_order=DOC_ORDER)

@app.route('/api/generate_doc/<project_id>/<doc_type>', methods=['POST'])
def generate_doc(project_id, doc_type):
    project = dm.get_project(project_id)
    if not project or doc_type not in DOC_PROMPTS:
        return jsonify({"error": "Invalid request"}), 400

    idea = project['idea']
    options = project.get('options', {})
    
    # Build context from previously generated docs to maintain consistency
    context = ""
    for dt in DOC_ORDER:
        if dt == doc_type: break
        if dt in project['documents']:
            context += f"\n\n--- Previous Document ({dt}) ---\n{project['documents'][dt]}"
            
    system_prompt = get_doc_system_prompt(doc_type)
    user_prompt = f"Project Idea: {idea}\nConstraints: {options}\n{DOC_PROMPTS[doc_type]}\n\nContext:{context}"
    
    content = ask_ai(system_prompt, user_prompt, doc_type, idea)
    
    project['documents'][doc_type] = content
    project['history'].append({
        "timestamp": datetime.now().isoformat(),
        "action": "Generated",
        "details": f"Generated {doc_type}"
    })
    
    if len(project['documents']) == len(DOC_ORDER):
        project['status'] = "Finished"
    else:
        project['status'] = "Generating"
        
    dm.update_project(project_id, project)
    
    return jsonify({"status": "success", "content": content})

@app.route('/api/project/<project_id>/save_doc', methods=['POST'])
def save_doc(project_id):
    data = request.json
    doc_type = data.get('doc_type')
    content = data.get('content')
    project = dm.get_project(project_id)
    if project and doc_type:
        project['documents'][doc_type] = content
        project['history'].append({
            "timestamp": datetime.now().isoformat(),
            "action": "Edited",
            "details": f"Manually edited {doc_type}"
        })
        dm.update_project(project_id, project)
        return jsonify({"status": "success"})
    return jsonify({"error": "Failed"}), 400

@app.route('/api/project/<project_id>/chat', methods=['POST'])
def chat(project_id):
    data = request.json
    message = data.get('message')
    project = dm.get_project(project_id)
    
    system_prompt = "You are a helpful coding assistant for this project. Keep answers concise."
    context_str = f"Project Idea: {project['idea']}\n"
    if 'prd' in project['documents']: context_str += f"PRD Summary:\n{project['documents']['prd'][:500]}\n"
    
    user_prompt = f"Context:\n{context_str}\n\nUser Question: {message}"
    
    reply = ask_ai(system_prompt, user_prompt, "chat", project['idea'])
    return jsonify({"reply": reply})

@app.route('/download/<project_id>/<doc_type>')
def download_md(project_id, doc_type):
    project = dm.get_project(project_id)
    if not project or doc_type not in project['documents']:
        return "Not found", 404
        
    content = project['documents'][doc_type]
    mem = io.BytesIO()
    mem.write(content.encode('utf-8'))
    mem.seek(0)
    return send_file(mem, as_attachment=True, download_name=f"{doc_type}.md", mimetype='text/markdown')

@app.route('/download_zip/<project_id>')
def download_zip(project_id):
    project = dm.get_project(project_id)
    if not project:
        return "Not found", 404
        
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w') as zf:
        for doc_name, content in project['documents'].items():
            ext = 'mmd' if doc_name == 'diagram' else 'md'
            zf.writestr(f"{doc_name}.{ext}", content)
    mem_zip.seek(0)
    return send_file(mem_zip, as_attachment=True, download_name=f"Project_{project_id[:8]}.zip", mimetype='application/zip')

@app.route('/delete/<project_id>', methods=['POST'])
def delete_proj(project_id):
    dm.delete_project(project_id)
    return redirect(url_for('projects'))

@app.route('/duplicate/<project_id>', methods=['POST'])
def duplicate_proj(project_id):
    original = dm.get_project(project_id)
    if original:
        new_proj = dm.create_project(f"Copy of {original['idea']}", original.get('options', {}))
        new_proj['documents'] = original['documents'].copy()
        new_proj['status'] = "Finished"
        new_proj['history'].append({"timestamp": datetime.now().isoformat(), "action": "Duplicated", "details": f"Copied from {project_id}"})
        dm.update_project(new_proj['id'], new_proj)
    return redirect(url_for('projects'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)