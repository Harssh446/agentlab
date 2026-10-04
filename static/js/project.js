document.addEventListener('DOMContentLoaded', () => {
    mermaid.initialize({ startOnLoad: false, theme: 'dark' });
    renderAllMarkdown();

    // Check if we need to run the generation pipeline
    if (window.STATUS === 'Draft') {
        runGenerationPipeline();
    }

    // Bind Chat
    document.getElementById('chatForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('chatInput');
        const msg = input.value;
        if (!msg) return;
        
        appendChat(msg, 'user');
        input.value = '';
        
        const typingId = appendChat('...', 'ai');
        
        try {
            const res = await fetch(`/api/project/${window.PROJECT_ID}/chat`, {
                method: 'POST',
                headers:{'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            const data = await res.json();
            updateChat(typingId, data.reply);
        } catch(e) {
            updateChat(typingId, 'Error connecting to AI.');
        }
    });

    // Bind Document Actions (Edit, Copy, Regen, Save)
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', (e) => toggleEdit(e.target.closest('button').dataset.doc, true));
    });
    document.querySelectorAll('.cancel-edit-btn').forEach(btn => {
        btn.addEventListener('click', (e) => toggleEdit(e.target.dataset.doc, false));
    });
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const doc = e.target.closest('button').dataset.doc;
            const text = document.getElementById(`textarea-${doc}`).value;
            navigator.clipboard.writeText(text);
            const orig = e.target.closest('button').innerHTML;
            e.target.closest('button').innerHTML = '<i class="fa-solid fa-check"></i> Copied';
            setTimeout(() => e.target.closest('button').innerHTML = orig, 2000);
        });
    });
    document.querySelectorAll('.save-edit-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const doc = e.target.dataset.doc;
            const content = document.getElementById(`textarea-${doc}`).value;
            await saveDocument(doc, content);
            toggleEdit(doc, false);
            updateView(doc, content);
            addHistory(`Manually edited ${doc}`);
        });
    });
    document.querySelectorAll('.regen-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const doc = e.target.closest('button').dataset.doc;
            if(confirm(`Regenerate ${doc.toUpperCase()}? This will overwrite it.`)){
                await generateDocument(doc);
            }
        });
    });
});

async function runGenerationPipeline() {
    for (const doc of window.DOC_ORDER) {
        // If empty or has a spinner status
        const statusIcon = document.getElementById(`status-${doc}`);
        if(statusIcon.innerHTML.includes('fa-clock') || statusIcon.innerHTML.includes('fa-spin')) {
            statusIcon.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin text-warning"></i>';
            await generateDocument(doc);
        }
    }
    window.STATUS = 'Finished';
    addHistory("Pipeline completed");
}

async function generateDocument(doc) {
    const statusIcon = document.getElementById(`status-${doc}`);
    statusIcon.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin text-warning"></i>';
    
    try {
        const res = await fetch(`/api/generate_doc/${window.PROJECT_ID}/${doc}`, {method: 'POST'});
        const data = await res.json();
        
        if(data.status === 'success') {
            updateView(doc, data.content);
            document.getElementById(`textarea-${doc}`).value = data.content;
            statusIcon.innerHTML = '<i class="fa-solid fa-check text-success"></i>';
            addHistory(`Generated ${doc}`);
        } else {
            statusIcon.innerHTML = '<i class="fa-solid fa-xmark text-danger" title="Failed"></i>';
        }
    } catch (e) {
        statusIcon.innerHTML = '<i class="fa-solid fa-xmark text-danger" title="Error"></i>';
    }
}

async function saveDocument(doc, content) {
    await fetch(`/api/project/${window.PROJECT_ID}/save_doc`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({doc_type: doc, content: content})
    });
}

function updateView(doc, content) {
    const display = document.getElementById(`display-${doc}`);
    display.innerHTML = '';
    
    if (doc === 'diagram') {
        const d = document.createElement('div');
        d.className = 'mermaid';
        d.textContent = content;
        display.appendChild(d);
        mermaid.init(undefined, d);
    } else {
        const d = document.createElement('div');
        d.className = 'rendered-md';
        d.innerHTML = marked.parse(content);
        display.appendChild(d);
    }
}

function renderAllMarkdown() {
    window.DOC_ORDER.forEach(doc => {
        const display = document.getElementById(`display-${doc}`);
        const rawEl = display.querySelector('.raw-md');
        if (rawEl) {
            const raw = rawEl.textContent;
            display.querySelector('.rendered-md').innerHTML = marked.parse(raw);
        }
        const m = display.querySelector('.mermaid');
        if(m) mermaid.init(undefined, m);
    });
}

function toggleEdit(doc, showEdit) {
    const display = document.getElementById(`display-${doc}`);
    const editArea = document.getElementById(`edit-area-${doc}`);
    if(showEdit) {
        display.classList.add('d-none');
        editArea.classList.remove('d-none');
        editArea.classList.add('d-flex');
    } else {
        display.classList.remove('d-none');
        editArea.classList.add('d-none');
        editArea.classList.remove('d-flex');
    }
}

function appendChat(msg, sender) {
    const id = 'msg-' + Date.now();
    const box = document.getElementById('chatHistory');
    const div = document.createElement('div');
    div.id = id;
    div.className = `chat-msg ${sender === 'user' ? 'chat-user' : 'chat-ai'}`;
    div.innerHTML = marked.parse(msg);
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
    return id;
}

function updateChat(id, msg) {
    const el = document.getElementById(id);
    if(el) {
        el.innerHTML = marked.parse(msg);
        const box = document.getElementById('chatHistory');
        box.scrollTop = box.scrollHeight;
    }
}

function addHistory(text) {
    const log = document.getElementById('historyLog');
    const li = document.createElement('li');
    li.className = "list-group-item bg-transparent text-light border-secondary p-2";
    const time = new Date().toTimeString().split(' ')[0];
    li.innerHTML = `<span class="text-muted">[${time}]</span> <span class="text-accent">System</span>: ${text}`;
    log.insertBefore(li, log.firstChild);
}