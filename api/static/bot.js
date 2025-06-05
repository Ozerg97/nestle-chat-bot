const toggleBtn   = document.getElementById("chat-toggle");
const chatBox     = document.getElementById("chat-wrapper");
const sendBtn     = document.getElementById("chat-send");
const inputField  = document.getElementById("chat-input");
const chatScroll  = document.getElementById("chat-scroll");


let firstOpen = true;  

toggleBtn.onclick = () => {
  const isHidden = chatBox.classList.toggle("hidden");
  chatBox.dataset.open = isHidden ? "false" : "true";

  if (!isHidden && firstOpen){
    appendMessage("bot", "Hello, I'm the madewithnestle.ca AI chatbot, how can I help?");
    firstOpen = false;
  }
};
sendBtn.onclick = sendMessage;
inputField.addEventListener("keypress", e => {
  if (e.key === "Enter") sendMessage();
});

function sendMessage(){
  const text = inputField.value.trim();
  if (!text) return;

  appendMessage("user", text);
  inputField.value = "";
  showTyping();

  fetch("/ask", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ question: text })
  })
  .then(r => r.json())
  .then(d => {
    hideTyping();
    appendMessage("bot", d.answer);
  })
  .catch(err => {
    hideTyping();
    appendMessage("bot", "Oups ! Une erreur est survenue.");
    console.error(err);
  });
}


function appendMessage(sender, text) {
  const row = document.createElement('div');
  row.className = `msg-row ${sender}`;

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.innerHTML =
      `<i class="fa-${sender === 'user' ? 'regular fa-user' : 'solid fa-robot'}"></i>`;

  const bubble = document.createElement('div');
  bubble.className = `msg ${sender} markdown-body`;

  if (sender === 'bot') {
    bubble.innerHTML = DOMPurify.sanitize(marked.parse(text));
  } else {
    bubble.textContent = text;
  }

  if (sender === 'user') {

    row.appendChild(avatar);
    row.appendChild(bubble);
  } 
  else {
    row.appendChild(avatar);
    row.appendChild(bubble);
  }

  chatScroll.appendChild(row);
  chatScroll.scrollTop = chatScroll.scrollHeight;
}




let typingNode = null;
function showTyping(){
  typingNode = document.createElement("div");
  typingNode.className = "msg bot";
  typingNode.innerHTML = `<span class="avatar"><i class="fa-solid fa-robot"></i></span>
                          <span class="typing"><span></span><span></span><span></span></span>`;
  chatScroll.appendChild(typingNode);
  chatScroll.scrollTop = chatScroll.scrollHeight;
}
function hideTyping(){
  if (typingNode){
    typingNode.remove();
    typingNode = null;
  }
}
