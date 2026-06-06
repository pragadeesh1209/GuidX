with open('chatbot/templates/chatbot/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the entire broken appendMessage function
idx_start = content.find('async function appendMessage')
depth = 0
idx_end = idx_start
for i, ch in enumerate(content[idx_start:]):
    if ch == '{': depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            idx_end = idx_start + i + 1
            break

old_func = content[idx_start:idx_end]

new_func = '''async function appendMessage(text, isUser) {
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
        if (isUser) {
            msg.textContent = text;
            col.appendChild(msg);
            wrapper.appendChild(col);
            chatBox.appendChild(wrapper);
            chatBox.scrollTop = chatBox.scrollHeight;
        } else {
            col.appendChild(msg);
            wrapper.appendChild(col);
            chatBox.appendChild(wrapper);
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
    }'''

if old_func:
    content = content.replace(old_func, new_func, 1)
    print("appendMessage fixed!")
    print("Old had duplicate col:", content.count('const col = document.createElement') )
else:
    print("Function not found!")

with open('chatbot/templates/chatbot/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done!")