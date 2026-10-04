// Initialize markdown configuration
marked.setOptions({
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-'
});

if(document.getElementById('generateForm')) {
    document.getElementById('generateForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('generateBtn');
        const loading = document.getElementById('loadingState');
        
        btn.disabled = true;
        loading.classList.remove('d-none');
        
        const payload = {
            idea: document.getElementById('ideaInput').value,
            options: {
                type: document.getElementById('optType').value,
                stack: document.getElementById('optStack').value,
                team: document.getElementById('optTeam').value,
            }
        };

        try {
            const res = await fetch('/api/project', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if(data.id) {
                window.location.href = `/project/${data.id}`;
            }
        } catch(err) {
            alert('Failed to initialize project.');
            btn.disabled = false;
            loading.classList.add('d-none');
        }
    });
}