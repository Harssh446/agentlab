DOC_PROMPTS = {
    "prd": "Write a professional Product Requirements Document (PRD) for this project. Include Overview, Problem Statement, Target Audience, Core Features, and Non-functional requirements. Use Markdown. Do not include conversational filler.",
    "trd": "Write a Technical Requirements Document (TRD). Include Tech Stack recommendations, System Requirements, Security considerations, and Performance metrics. Use Markdown.",
    "architecture": "Write an Architecture Overview. Describe the high-level system components, data flow, and deployment strategy. Use Markdown.",
    "database": "Design a Database Schema. List tables/collections, fields, data types, and relationships. Format as clean Markdown tables.",
    "api": "Design RESTful API endpoints. For each, include: Method, Path, Purpose, and an example JSON request/response payload. Use Markdown.",
    "ui": "Write a UI/UX Brief. List necessary pages, key UI components, and user flow paths. Use Markdown.",
    "steps": "Write a sequential implementation checklist. Format as a Markdown checklist (- [ ] Step 1...). Break it down from initial setup to deployment.",
    "diagram": "Create a Mermaid.js flowchart (graph TD) that maps the user journey and application flow based on the project idea. RETURN ONLY valid Mermaid syntax. Do NOT use markdown code blocks (```). Start immediately with 'graph TD'."
}

def get_doc_system_prompt(doc_type):
    base = "You are an expert Principal Software Engineer and Product Manager generating technical documentation. Output ONLY raw Markdown content without any conversational greeting or explanations."
    if doc_type == "diagram":
        base = "You are an expert system architect. Output ONLY valid Mermaid.js graph syntax. Do not wrap in markdown tags."
    return base