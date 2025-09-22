// chat.js

document.addEventListener("DOMContentLoaded", () => {
  // --- Zmienne globalne ---
  // Prosty unikalny ID dla sesji użytkownika
  const userId = `web-user-${Date.now()}`;
  const agentServiceUrl = `${window.location.protocol}//${window.location.hostname}`; // Bez portu

  // --- Tworzenie UI czatu ---
  function createChatUI() {
    const chatIcon = document.createElement("div");
    chatIcon.id = "copilot-icon";
    chatIcon.innerText = "🤖";
    document.body.appendChild(chatIcon);

    const chatWindow = document.createElement("div");
    chatWindow.id = "copilot-window";
    chatWindow.innerHTML = `
      <div id="copilot-header">Boutique Co-Pilot</div>
      <div id="copilot-messages"></div>
      <div id="copilot-input-container">
        <input type="text" id="copilot-input" placeholder="Ask me anything...">
        <button id="copilot-send">Send</button>
      </div>
    `;
    document.body.appendChild(chatWindow);

    // --- Logika UI ---
    chatIcon.addEventListener("click", () => {
      chatWindow.style.display = chatWindow.style.display === "flex" ? "none" : "flex";
    });

    document.getElementById("copilot-send").addEventListener("click", sendMessage);
    document.getElementById("copilot-input").addEventListener("keypress", (e) => {
      if (e.key === "Enter") sendMessage();
    });

    addMessage("assistant", "Hi! I'm your shopping co-pilot. How can I help you today?");
  }

  function addMessage(sender, text) {
    const messagesContainer = document.getElementById("copilot-messages");
    const messageElement = document.createElement("div");
    messageElement.classList.add("copilot-message", `${sender}-message`);
    messageElement.innerText = text;
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  async function sendMessage() {
    const input = document.getElementById("copilot-input");
    const messageText = input.value.trim();
    if (!messageText) return;

    addMessage("user", messageText);
    input.value = "";
    input.disabled = true;

    try {
      const response = await fetch(`${agentServiceUrl}/copilot-api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, message: messageText }),
      });
      const data = await response.json();
      addMessage("assistant", data.response);
    } catch (error) {
      console.error("Error communicating with Co-Pilot:", error);
      addMessage("assistant", "Sorry, I'm having trouble connecting right now.");
    } finally {
      input.disabled = false;
      input.focus();
    }
  }

  // --- Logika śledzenia zdarzeń ---
  async function trackProductView(productId) {
    console.log(`User ${userId} viewed product: ${productId}`);
    try {
      await fetch(`${agentServiceUrl}/copilot-api/event`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          event_type: "view_product",
          product_id: productId,
        }),
      });
    } catch (error) {
      console.error("Error tracking event:", error);
    }
  }

  function addTrackingListeners() {
    document.querySelectorAll('a[href*="/product/"]').forEach(link => {
      link.addEventListener("click", (e) => {
        const productId = e.currentTarget.href.split("/product/")[1];
        trackProductView(productId);
      });
    });
  }

  // --- CSS i inicjalizacja ---
  function injectCSS() {
    const style = document.createElement('style');
    style.innerHTML = `
      #copilot-icon { position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; background-color: #4285F4; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; cursor: pointer; z-index: 999; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
      #copilot-window { display: none; flex-direction: column; position: fixed; bottom: 90px; right: 20px; width: 350px; height: 500px; background-color: white; border-radius: 10px; box-shadow: 0 4px 16px rgba(0,0,0,0.2); z-index: 1000; }
      #copilot-header { background-color: #4285F4; color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-weight: bold; }
      #copilot-messages { flex-grow: 1; padding: 10px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
      .copilot-message { padding: 8px 12px; border-radius: 15px; max-width: 80%; }
      .user-message { background-color: #e0e0e0; align-self: flex-end; }
      .assistant-message { background-color: #d1e3ff; align-self: flex-start; }
      #copilot-input-container { display: flex; padding: 10px; border-top: 1px solid #ccc; }
      #copilot-input { flex-grow: 1; border: 1px solid #ccc; border-radius: 5px; padding: 8px; }
      #copilot-send { margin-left: 10px; padding: 8px 12px; background-color: #4285F4; color: white; border: none; border-radius: 5px; cursor: pointer; }
    `;
    document.head.appendChild(style);
  }

  createChatUI();
  injectCSS();
  // Nasłuchujemy na kliknięcia po lekkim opóźnieniu, aby dać stronie czas na załadowanie
  setTimeout(addTrackingListeners, 1000);
});