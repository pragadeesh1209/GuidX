with open('chatbot/templates/chatbot/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the entire speakText function
idx_start = content.find('function speakText(text, btn)')
if idx_start == -1:
    idx_start = content.find('function speakText(text)')

# Find the end of the function by counting braces
depth = 0
idx = idx_start
for i, ch in enumerate(content[idx_start:]):
    if ch == '{': depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            idx_end = idx_start + i + 1
            break

old_func = content[idx_start:idx_end]

new_func = '''function speakText(text, btn) {
            if (!synth) return;
            synth.cancel();
            isSpeaking = false;

            // Clean text but KEEP unicode characters for multilingual support
            let clean = text
                .replace(/[#*_`>~]/g, '')
                .replace(/\n+/g, ' ')
                .replace(/\s+/g, ' ')
                .trim();

            if (!clean) return;

            if (btn) btn.innerHTML = '&#128266; Speaking...';

            // Split into small chunks by sentence or word count
            const chunkSize = 160;
            const sentences = clean.match(/[^.!?\\u0964]+[.!?\\u0964]*/g) || [clean];
            const chunks = [];

            for (const sentence of sentences) {
                if (sentence.trim().length === 0) continue;
                if (sentence.length <= chunkSize) {
                    chunks.push(sentence.trim());
                } else {
                    // Split long sentences by words
                    const words = sentence.split(' ');
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
                }
            }

            if (chunks.length === 0) return;

            let chunkIndex = 0;
            isSpeaking = true;

            function speakNext() {
                if (chunkIndex >= chunks.length) {
                    isSpeaking = false;
                    if (btn) btn.innerHTML = '&#128266; Speak';
                    return;
                }

                const utt = new SpeechSynthesisUtterance(chunks[chunkIndex]);
                utt.lang = selectedLang;
                utt.rate = 0.88;
                utt.pitch = 1.0;
                utt.volume = 1.0;

                // Pick best voice for selected language
                const voices = synth.getVoices();
                const langCode = selectedLang.split('-')[0];
                const exactMatch = voices.find(v => v.lang === selectedLang);
                const partialMatch = voices.find(v => v.lang.startsWith(langCode));
                if (exactMatch) utt.voice = exactMatch;
                else if (partialMatch) utt.voice = partialMatch;

                utt.onend = () => {
                    chunkIndex++;
                    // Small delay between chunks for reliability
                    setTimeout(speakNext, 80);
                };

                utt.onerror = (e) => {
                    console.warn('Speech error on chunk', chunkIndex, e.error);
                    chunkIndex++;
                    setTimeout(speakNext, 100);
                };

                try {
                    synth.speak(utt);
                } catch(e) {
                    console.error('Speak failed:', e);
                    chunkIndex++;
                    setTimeout(speakNext, 100);
                }
            }

            // Chrome requires a tiny delay after cancel() before speaking
            setTimeout(speakNext, 100);
        }'''

content = content.replace(old_func, new_func)

with open('chatbot/templates/chatbot/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("speakText fixed!")
print("Old length:", len(old_func))
print("New length:", len(new_func))