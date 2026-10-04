import os
from groq import Groq

def get_fallback_content(doc_type, idea, context=""):
    fallbacks = {
        "prd": f"# Product Requirements Document\n\n## Overview\nProject based on: {idea}\n\n## Features\n- Core feature 1\n- Core feature 2\n\n## Target Audience\nUsers needing this solution.",
        "trd": f"# Technical Requirements Document\n\n## Stack\n- Frontend: HTML/CSS/JS\n- Backend: Python/Flask\n- Data: JSON\n\n## Constraints\nMust run offline or with minimal latency.",
        "architecture": f"# Architecture Overview\n\n## Client-Server Model\n- Client makes HTTP/REST requests.\n- Server processes AI generation and handles local JSON storage.",
        "database": f"# Database Schema\n\n## Data Storage\nJSON files.\n\n### `projects.json`\n- `id`: String (UUID)\n- `idea`: String\n- `created`: Timestamp\n- `status`: String",
        "api": f"# API Endpoints\n\n## GET /api/status\n- **Purpose**: Check system health.\n- **Response**: `{{\"status\": \"ok\"}}`",
        "ui": f"# UI/UX Brief\n\n## Pages\n1. **Home**: Input form for project idea.\n2. **Workspace**: Multi-tab interface for documents.\n\n## Theme\nDark mode, monospaced fonts.",
        "steps": f"# Implementation Steps\n\n- [ ] 1. Initialize Flask project.\n- [ ] 2. Setup JSON data manager.\n- [ ] 3. Build UI templates.\n- [ ] 4. Integrate AI generation.",
        "diagram": f"graph TD\n    A[User] -->|Inputs Idea| B(Web Interface)\n    B --> C{{Flask Server}}\n    C --> D[Groq API / AI]\n    C --> E[(JSON File)]\n    D --> C\n    E --> C",
        "chat": f"I am running in offline fallback mode. I understand your project: {idea}. How can I help you manually?"
    }
    return fallbacks.get(doc_type, f"# {doc_type.upper()}\nContent for {idea}")

def ask_ai(system_prompt, user_prompt, doc_type="chat", idea=""):
    api_key = "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"
    model = os.environ.get("GROQ_MODEL", "llama3-8b-8192")
    
    if not api_key or api_key == "your_groq_api_key_here":
        return get_fallback_content(doc_type, idea)
        
    try:
        client = Groq(api_key=api_key, timeout=20.0)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=model,
            temperature=0.3,
            max_tokens=2048
        )
        content = response.choices[0].message.content.strip()
        
        # Clean up Markdown blocks if Groq surrounds the diagram with them
        if doc_type == "diagram":
            if content.startswith("```mermaid"):
                content = content[10:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
                
        return content.strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return get_fallback_content(doc_type, idea)