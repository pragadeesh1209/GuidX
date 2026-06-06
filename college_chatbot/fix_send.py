with open('chatbot/templates/chatbot/chat.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Make sendMessage async
if 'async function sendMessage' not in content:
    content = content.replace('function sendMessage()', 'async function sendMessage()')
    print("sendMessage made async!")
else:
    print("sendMessage already async")

# Fix 2: Make sure keypress works
old_key = 'keypress", e => { if (e.key === "Enter") sendMessage(); });'
new_key = 'keypress", async (e) => { if (e.key === "Enter") { e.preventDefault(); await sendMessage(); } });'
if old_key in content:
    content = content.replace(old_key, new_key)
    print("keypress fixed!")
else:
    print("keypress pattern not found - checking...")
    idx = content.find('keypress')
    print(repr(content[idx:idx+100]))

with open('chatbot/templates/chatbot/chat.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done!")