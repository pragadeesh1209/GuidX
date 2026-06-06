with open('chatbot/templates/chatbot/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Get everything before <script> and after </script>
script_start = content.rfind('<script>')
script_end = content.rfind('</script>') + 9
before = content[:script_start]
after = content[script_end:]

new_script = '''<script>
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("userInput");
    const typingEl = document.getElementById("typing-indicator");
    const suggestionsEl = document.getElementById("suggestions");
    const heroBanner = document.getElementById("heroBanner");
    const waveform = document.getElementById("waveform");
    let isTyping = false, msgCount = 0;
    let selectedLang = 'en-IN';
    let recognition = null;
    let synth = window.speechSynthesis;
    let isRecording = false, isSpeaking = false;
    let currentGroup = '';

    const langNames = {'en-IN':'English','ta-IN':'Tamil','hi-IN':'Hindi','ml-IN':'Malayalam','te-IN':'Telugu'};

    function setLang(lang, btn) {
        selectedLang = lang;
        document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
        if (btn) btn.classList.add('active');
        const lbl = document.getElementById('langLabel');
        if (lbl) lbl.textContent = langNames[lang];
    }

    function openSidebar() {
        document.getElementById("sidebar").classList.add("open");
        document.getElementById("overlay").classList.add("open");
    }

    function closeSidebar() {
        document.getElementById("sidebar").classList.remove("open");
        document.getElementById("overlay").classList.remove("open");
    }

    function quickAsk(text) {
        userInput.value = text;
        closeSidebar();
        sendMessage();
    }

    async function typeWriter(element, text) {
        const normalized = text.replace(/\n/g, "\n");
        const temp = document.createElement("div");
        temp.innerHTML = marked.parse(normalized);
        const fullText = temp.innerText;
        let i = 0;
        element.textContent = "";
        return new Promise(resolve => {
            function type() {
                if (i < fullText.length) {
                    element.textContent = fullText.substring(0, i + 1);
                    i++;
                    chatBox.scrollTop = chatBox.scrollHeight;
                    setTimeout(type, 8);
                } else {
                    element.innerHTML = marked.parse(normalized);
                    chatBox.scrollTop = chatBox.scrollHeight;
                    resolve();
                }
            }
            type();
        });
    }

    function speakText(text) {
        if (!synth) return;
        synth.cancel();
        isSpeaking = false;
        const clean = text.replace(/[#*_`>~]/g, '').replace(/\n+/g, ' ').replace(/\s+/g, ' ').trim();
        if (!clean) return;
        const chunkSize = 160;
        const words = clean.split(' ');
        const chunks = [];
        let current = '';
        for (const word of words) {
            if ((current + ' ' + word).trim().length > chunkSize) {
                if (current) chunks.push(current.trim());
                current = word;
            } else {
                current = (current + ' ' + word).trim();
            }
        }
        if (current) chunks.push(current.trim());
        if (!chunks.length) return;
        let idx = 0;
        isSpeaking = true;
        function speakNext() {
            if (idx >= chunks.length) { isSpeaking = false; return; }
            const utt = new SpeechSynthesisUtterance(chunks[idx]);
            utt.lang = selectedLang;
            utt.rate = 0.88;
            utt.volume = 1.0;
            const voices = synth.getVoices();
            const langCode = selectedLang.split('-')[0];
            const match = voices.find(v => v.lang === selectedLang) || voices.find(v => v.lang.startsWith(langCode));
            if (match) utt.voice = match;
            utt.onend = () => { idx++; setTimeout(speakNext, 80); };
            utt.onerror = () => { idx++; setTimeout(speakNext, 100); };
            synth.speak(utt);
        }
        setTimeout(speakNext, 150);
    }

    async function appendMessage(text, isUser) {
        if (msgCount === 0 && !isUser && heroBanner) heroBanner.style.display = "none";
        msgCount++;
        const wrapper = document.createElement("div");
        wrapper.className = "msg-wrapper " + (isUser ? "user-wrapper" : "bot-wrapper");
        if (!isUser) {
            const av = document.createElement("div");
            av.className = "bot-avatar";
            av.textContent = "GX";
            wrapper.appendChild(av);
        }
        const col = document.createElement("div");
        col.className = "msg-col";
        const msg = document.createElement("div");
        msg.className = "msg " + (isUser ? "user-msg" : "bot-msg");
        col.appendChild(msg);
        wrapper.appendChild(col);
        chatBox.appendChild(wrapper);
        if (isUser) {
            msg.textContent = text;
            chatBox.scrollTop = chatBox.scrollHeight;
        } else {
            await typeWriter(msg, text);
            const actions = document.createElement("div");
            actions.className = "msg-actions";
            const speakBtn = document.createElement("button");
            speakBtn.className = "speak-btn";
            speakBtn.innerHTML = "&#128266; Speak";
            speakBtn.onclick = () => speakText(text);
            actions.appendChild(speakBtn);
            col.appendChild(actions);
            speakText(text);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    function updateSuggestions(suggestions) {
        suggestionsEl.innerHTML = "";
        if (!suggestions || !suggestions.length) return;
        suggestions.forEach(s => {
            const chip = document.createElement("div");
            chip.className = "chip";
            chip.textContent = s;
            chip.onclick = () => { userInput.value = s; sendMessage(); };
            suggestionsEl.appendChild(chip);
        });
    }

    async function sendMessage() {
        if (isTyping) return;
        const message = userInput.value.trim();
        if (!message) return;
        await appendMessage(message, true);
        userInput.value = "";
        isTyping = true;
        typingEl.style.display = "block";
        chatBox.scrollTop = chatBox.scrollHeight;
        try {
            const res = await fetch("/chatbot/chat/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": "{{ csrf_token }}"
                },
                body: JSON.stringify({ message })
            });
            const data = await res.json();
            typingEl.style.display = "none";
            isTyping = false;
            updateSuggestions(data.suggestions);
            await appendMessage(data.reply, false);
        } catch (err) {
            console.error("Chat error:", err);
            typingEl.style.display = "none";
            isTyping = false;
            await appendMessage("Connection error. Please try again.", false);
        }
    }

    function clearChat() {
        chatBox.innerHTML = "";
        suggestionsEl.innerHTML = "";
        msgCount = 0;
        if (heroBanner) heroBanner.style.display = "flex";
        appendMessage("Session reset. How can GuidX help you today?", false);
    }

    function toggleMic() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Voice input works in Google Chrome.');
            return;
        }
        if (isRecording) { recognition.stop(); return; }
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SR();
        recognition.lang = selectedLang;
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.onstart = () => {
            isRecording = true;
            const mb = document.getElementById("micBtn");
            if (mb) mb.classList.add("recording");
            if (waveform) waveform.classList.add("active");
        };
        recognition.onresult = (e) => {
            userInput.value = e.results[0][0].transcript;
            sendMessage();
        };
        recognition.onerror = (e) => console.log('Voice error:', e.error);
        recognition.onend = () => {
            isRecording = false;
            const mb = document.getElementById("micBtn");
            if (mb) mb.classList.remove("recording");
            if (waveform) waveform.classList.remove("active");
        };
        recognition.start();
    }

    async function loadGroup(group) {
        currentGroup = group;
        const titleEl = document.getElementById('histGroupTitle');
        if (titleEl) titleEl.textContent = group;
        document.querySelectorAll('[id^="grp-"]').forEach(el => {
            el.style.background = 'transparent';
            el.style.borderLeft = '2px solid transparent';
        });
        const slug = group.toLowerCase().replace(/\s+/g, '-');
        const grpEl = document.getElementById('grp-' + slug);
        if (grpEl) {
            grpEl.style.background = 'rgba(17,100,102,0.2)';
            grpEl.style.borderLeft = '2px solid var(--teal-lt)';
        }
        const listEl = document.getElementById('histMsgList');
        if (!listEl) return;
        listEl.innerHTML = '<div style="font-size:0.78rem;color:var(--text3);padding:10px;text-align:center;">Loading...</div>';
        try {
            const res = await fetch('/chatbot/conversation/?group=' + encodeURIComponent(group));
            const data = await res.json();
            if (!data.messages || !data.messages.length) {
                listEl.innerHTML = '<div style="font-size:0.78rem;color:var(--text3);padding:10px;text-align:center;">No chats found</div>';
                return;
            }
            listEl.innerHTML = '';
            data.messages.forEach(msg => {
                const item = document.createElement('div');
                item.style.cssText = 'background:var(--surface2);border:1px solid var(--border);border-radius:7px;padding:7px 12px;cursor:pointer;margin-bottom:4px;';
                item.innerHTML = '<div style="font-size:0.8rem;color:var(--mint);font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + msg.query + '</div><div style="font-size:0.65rem;color:var(--text3);margin-top:4px;">' + msg.time + '</div>';
                item.onmouseenter = () => { item.style.borderColor = 'var(--teal-lt)'; };
                item.onmouseleave = () => { item.style.borderColor = 'var(--border)'; };
                item.onclick = () => loadConversation(msg.query, msg.response);
                listEl.appendChild(item);
            });
        } catch(e) {
            if (listEl) listEl.innerHTML = '<div style="font-size:0.78rem;color:var(--text3);padding:10px;">Error loading chats</div>';
        }
    }

    function loadConversation(query, response) {
        chatBox.innerHTML = '';
        suggestionsEl.innerHTML = '';
        msgCount = 1;
        if (heroBanner) heroBanner.style.display = 'none';
        const hp = document.getElementById('historyPanel');
        if (hp) hp.style.display = 'none';
        appendMessage(query, true);
        setTimeout(() => appendMessage(response, false), 100);
    }

    userInput.addEventListener("keypress", e => {
        if (e.key === "Enter") { e.preventDefault(); sendMessage(); }
    });

    window.addEventListener("DOMContentLoaded", () => {
        if (synth && synth.onvoiceschanged !== undefined) {
            synth.onvoiceschanged = () => synth.getVoices();
        }
        if (synth) synth.getVoices();
        setTimeout(() => {
            appendMessage("Hello! I am GuidX — your AI career guide for all of India. Ask me about courses, colleges, eligibility or careers after 12th grade. I speak Tamil, Hindi, Malayalam, Telugu and English!", false);
            updateSuggestions(["Engineering courses after 12th", "Medical courses after 12th", "Top IIT NIT colleges India", "I scored 85% which college?"]);
        }, 500);
    });
</script>'''

content = before + new_script + after

with open('chatbot/templates/chatbot/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
with open('chatbot/templates/chatbot/chat.html', 'r', encoding='utf-8') as f:
    check = f.read()
idx = check.rfind('<script>')
script = check[idx:]
print("duplicate const col:", script.count('const col = document.createElement'))
print("async sendMessage:", 'async function sendMessage' in script)
print("keypress:", 'keypress' in script)
print("Done!")