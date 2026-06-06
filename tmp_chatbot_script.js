
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
    let availableVoices = [];
    if (synth) {
        availableVoices = synth.getVoices();
        if ('onvoiceschanged' in synth) {
            synth.onvoiceschanged = () => {
                availableVoices = synth.getVoices();
                console.log('SpeechSynthesis voices updated', availableVoices.length);
            };
        } else if (window.speechSynthesis && window.speechSynthesis.addEventListener) {
            window.speechSynthesis.addEventListener('voiceschanged', () => {
                availableVoices = synth.getVoices();
                console.log('SpeechSynthesis voices updated', availableVoices.length);
            });
        }
    }
    let isRecording = false, isSpeaking = false;
    let currentSpeakBtn = null;
    let currentUtterance = null;
    let currentSpeechResolve = null;
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

    function getPreferredVoice(voices) {
        if (!voices || !voices.length) return null;
        const langCode = selectedLang.split('-')[0];
        return voices.find(v => v.lang === selectedLang) || voices.find(v => v.lang.startsWith(langCode)) || voices[0];
    }

    function cancelCurrentSpeech() {
        if (synth && (synth.speaking || synth.pending)) {
            synth.cancel();
        }
        if (currentUtterance) {
            currentUtterance = null;
        }
        if (currentSpeechResolve) {
            currentSpeechResolve();
            currentSpeechResolve = null;
        }
        if (currentSpeakBtn) {
            currentSpeakBtn.classList.remove('active');
            currentSpeakBtn = null;
        }
        isSpeaking = false;
    }

    function speakText(text) {
        if (!('speechSynthesis' in window)) return Promise.resolve();
        if (!synth) synth = window.speechSynthesis;
        const clean = text.replace(/[#*_`>~]/g, '').replace(/\n+/g, ' ').replace(/\s+/g, ' ').trim();
        if (!clean) return Promise.resolve();
        if (!availableVoices.length && synth) {
            availableVoices = synth.getVoices();
        }
        const voiceList = availableVoices.length ? availableVoices : synth.getVoices();
        const preferred = getPreferredVoice(voiceList);
        console.log('TTS voice list', voiceList.map(v => `${v.lang}:${v.name}`));
        return new Promise(resolve => {
            currentSpeechResolve = resolve;
            const utterance = new SpeechSynthesisUtterance(clean);
            utterance.lang = selectedLang;
            utterance.rate = 0.88;
            utterance.volume = 1.0;
            if (preferred) {
                utterance.voice = preferred;
                console.log('TTS selected voice', preferred.name, preferred.lang);
            }
            currentUtterance = utterance;
            isSpeaking = true;
            console.log('TTS started', { text: clean, lang: selectedLang, voice: preferred ? preferred.name : null });
            utterance.onend = () => {
                console.log('TTS ended');
                isSpeaking = false;
                currentUtterance = null;
                if (currentSpeakBtn) {
                    currentSpeakBtn.classList.remove('active');
                    currentSpeakBtn = null;
                }
                if (currentSpeechResolve) {
                    currentSpeechResolve();
                    currentSpeechResolve = null;
                }
            };
            utterance.onerror = (e) => {
                console.error('TTS utterance error', e);
                isSpeaking = false;
                currentUtterance = null;
                if (currentSpeakBtn) {
                    currentSpeakBtn.classList.remove('active');
                    currentSpeakBtn = null;
                }
                if (currentSpeechResolve) {
                    currentSpeechResolve();
                    currentSpeechResolve = null;
                }
            };
            if (synth && synth.paused) synth.resume();
            synth.speak(utterance);
        });
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
            speakBtn.type = 'button';
            speakBtn.innerHTML = "&#128266; Speak";
            speakBtn.addEventListener('click', async () => {
                try {
                    if (currentSpeakBtn === speakBtn && isSpeaking) {
                        cancelCurrentSpeech();
                        return;
                    }
                    if (isSpeaking) {
                        cancelCurrentSpeech();
                    }
                    currentSpeakBtn = speakBtn;
                    speakBtn.classList.add('active');
                    isSpeaking = true;
                    await speakText(text);
                } catch (e) {
                    console.error('Speak button error', e);
                } finally {
                    if (currentSpeakBtn === speakBtn) {
                        speakBtn.classList.remove('active');
                        currentSpeakBtn = null;
                    }
                    isSpeaking = false;
                }
            });
            actions.appendChild(speakBtn);
            col.appendChild(actions);
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
        if (isRecording && recognition) { recognition.stop(); return; }
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SR();
        recognition.lang = selectedLang;
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.onstart = () => {
            isRecording = true;
            console.log('Voice recognition started', selectedLang);
            const mb = document.getElementById("micBtn");
            if (mb) mb.classList.add("recording");
            if (waveform) waveform.classList.add("active");
        };
        recognition.onresult = (e) => {
            console.log('Voice recognition result', e.results);
            if (e.results && e.results[0] && e.results[0][0]) {
                userInput.value = e.results[0][0].transcript;
                sendMessage();
            }
        };
        recognition.onerror = (e) => {
            console.error('Voice recognition error', e.error || e.message || e);
        };
        recognition.onend = () => {
            console.log('Voice recognition ended');
            isRecording = false;
            recognition = null;
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

