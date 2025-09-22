// chat.js (Wersja OSTATECZNA - zsynchronizowana z backendem)

if (!window.coPilotHasRun) {
    window.coPilotHasRun = true;

    document.addEventListener("DOMContentLoaded", () => {
        const userId = `web-user-${Date.now()}`;
        const agentServiceUrl = `${window.location.protocol}//${window.location.hostname}`;
        const storedHistory = sessionStorage.getItem('chatHistory');
        let chatHistory = storedHistory ? JSON.parse(storedHistory) : [];

        function renderHistory() { /* ... ta funkcja pozostaje bez zmian ... */ }
        function createChatUI() { /* ... ta funkcja pozostaje bez zmian ... */ }

       // OSTATECZNA POPRAWKA FUNKCJI CZYTANIA STRONY
// OSTATECZNA WERSJA - czyta poprawnie opis produktu
// OSTATECZNA WERSJA - poprawny selektor opisu
// OSTATECZNA, POPRAWIONA WERSJA CZYTANIA OPISU
// OSTATECZNA WERSJA - najbardziej niezawodne szukanie opisu
// FINAL, DEFINITIVE VERSION
// OSTATECZNA WERSJA - najbardziej niezawodne szukanie opisu
// OSTATECZNA WERSJA - najbardziej niezawodne szukanie opisu
// OSTATECZNA WERSJA - czyta również URL obrazka
// OSTATECZNA WERSJA - spójna struktura danych
function scrapePageContext() {
    // Sprawdzamy, czy jesteśmy na stronie produktu
    const nameElement = document.querySelector('div.product-wrapper > h2');
    const priceElement = document.querySelector('p.product-price');
    
    if (nameElement && priceElement) {
        const descriptionElement = document.querySelector('p.product-price + p');
        const imageElement = document.querySelector('img.product-image');
        return {
            type: 'product_page',
            name: nameElement.textContent.trim(),
            price: priceElement.textContent.trim(),
            description: descriptionElement ? descriptionElement.textContent.trim() : "No description available.",
            image_url: imageElement ? imageElement.src : null,
            products_on_page: [] // Pusta lista, bo jesteśmy na stronie jednego produktu
        };
    }
    
    // Sprawdzamy, czy jesteśmy na stronie głównej
    const productCards = document.querySelectorAll('.hot-product-card');
    if (productCards.length > 0) {
        const products = [];
        productCards.forEach(card => {
            const nameElement = card.querySelector('.hot-product-card-name');
            const priceElement = card.querySelector('.hot-product-card-price');
            if (nameElement && priceElement) {
                products.push({ name: nameElement.textContent.trim(), price: priceElement.textContent.trim() });
            }
        });
        return { 
            type: 'homepage',
            name: null,
            price: null,
            description: null,
            image_url: null,
            products_on_page: products 
        };
    }

    return null; // Jesteśmy na innej stronie (np. w koszyku), gdzie nie ma kontekstu produktów
}
        

        // --- Pełne wersje funkcji, które się nie zmieniają ---
        function renderHistory() { const messagesContainer = document.getElementById("copilot-messages"); if (!messagesContainer) return; messagesContainer.innerHTML = ''; chatHistory.forEach(msg => { const [sender, ...textParts] = msg.split(': '); const text = textParts.join(': '); const messageElement = document.createElement("div"); messageElement.classList.add("copilot-message", `${sender.toLowerCase()}-message`); messageElement.innerText = text; messagesContainer.appendChild(messageElement); }); messagesContainer.scrollTop = messagesContainer.scrollHeight; }
        function createChatUI() {const chatIcon = document.createElement("div"); chatIcon.id = "copilot-icon"; chatIcon.innerText = "🤖"; const chatWindow = document.createElement("div"); chatWindow.id = "copilot-window"; const header = document.createElement("div"); header.id = "copilot-header"; header.innerText = "Boutique Co-Pilot"; const messagesContainer = document.createElement("div"); messagesContainer.id = "copilot-messages"; const inputContainer = document.createElement("div"); inputContainer.id = "copilot-input-container"; const inputField = document.createElement("input"); inputField.id = "copilot-input"; inputField.type = "text"; inputField.placeholder = "Ask me anything..."; const sendButton = document.createElement("button"); sendButton.id = "copilot-send"; sendButton.innerText = "Send"; inputContainer.appendChild(inputField); inputContainer.appendChild(sendButton); chatWindow.appendChild(header); chatWindow.appendChild(messagesContainer); chatWindow.appendChild(inputContainer); document.body.appendChild(chatIcon); document.body.appendChild(chatWindow); if (chatHistory.length === 0) { addMessage("assistant", "Hi! I'm your shopping co-pilot. How can I help you today?"); } else { renderHistory(); } }
        function scrapeCartContents() { const itemRows = document.querySelectorAll('.cart-summary-item-row'); const shippingCostElement = document.querySelector('.cart-summary-shipping-row > .text-right'); const totalCostElement = document.querySelector('.cart-summary-total-row > .text-right'); if (itemRows.length === 0) { const cartSizeElement = document.querySelector('.cart-size-circle'); if (cartSizeElement && cartSizeElement.textContent.trim() !== '0') { return { type: 'summary_view', item_count: parseInt(cartSizeElement.textContent.trim(), 10) }; } return null; } const items = []; itemRows.forEach(row => { const nameElement = row.querySelector('h4'); const priceElement = row.querySelector('strong'); let quantity = 1; const allDivs = row.querySelectorAll('.col'); allDivs.forEach(div => { const divText = div.textContent.trim(); if (divText.startsWith('Quantity:')) { quantity = parseInt(divText.replace('Quantity:', '').trim(), 10); } }); if (nameElement && priceElement) { items.push({ name: nameElement.textContent.trim(), quantity: quantity, price: priceElement.textContent.trim() }); } }); return { type: 'detailed_view', items: items, shipping_cost: shippingCostElement ? shippingCostElement.textContent.trim() : "N/A", total_cost: totalCostElement ? totalCostElement.textContent.trim() : "N/A" }; }
        function addMessage(sender, text) { const fullMessage = `${sender.charAt(0).toUpperCase() + sender.slice(1)}: ${text}`; chatHistory.push(fullMessage); if (chatHistory.length > 10) { chatHistory = chatHistory.slice(-10); } sessionStorage.setItem('chatHistory', JSON.stringify(chatHistory)); const messagesContainer = document.getElementById("copilot-messages"); if (!messagesContainer) return; const messageElement = document.createElement("div"); messageElement.classList.add("copilot-message", `${sender}-message`); messageElement.innerText = text; messagesContainer.appendChild(messageElement); messagesContainer.scrollTop = messagesContainer.scrollHeight; }
        async function sendMessage() { const input = document.getElementById("copilot-input"); if (!input) return; const messageText = input.value.trim(); if (!messageText) return; addMessage("user", messageText); input.value = ""; input.disabled = true; const pageContext = scrapePageContext(); const cartContents = scrapeCartContents(); try { const response = await fetch(`${agentServiceUrl}/copilot-api/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ user_id: userId, message: messageText, page_context: pageContext, cart_contents: cartContents, chat_history: chatHistory }), }); const data = await response.json(); addMessage("assistant", data.response); } catch (error) { console.error("Error communicating with Co-Pilot:", error); addMessage("assistant", "Sorry, I'm having trouble connecting right now."); } finally { input.disabled = false; input.focus(); } }
        // NOWA, ULEPSZONA WERSJA
function setupEventListeners() {
    // Używamy jQuery .on() do delegacji zdarzeń
    $(document.body).on('click', '#copilot-icon', function() {
        const chatWindow = document.getElementById('copilot-window');
        if (chatWindow) {
            const isOpening = chatWindow.style.display !== "flex";
            chatWindow.style.display = isOpening ? "flex" : "none";

            // Jeśli właśnie otworzyliśmy okno, przewiń na sam dół
            if (isOpening) {
                const messagesContainer = document.getElementById('copilot-messages');
                if (messagesContainer) {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            }
        }
    });

    $(document.body).on('click', '#copilot-send', function() {
        sendMessage();
    });

    $(document.body).on('keypress', '#copilot-input', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    $(document.body).on('click', 'a[href*="/product/"]', function() {
        const productId = this.href.split("/product/")[1];
        trackProductView(productId);
    });
}
        async function trackProductView(productId) { try { await fetch(`${agentServiceUrl}/copilot-api/event`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ user_id: userId, event_type: "view_product", product_id: productId, }), }); } catch (error) { console.error("Error tracking event:", error); } }
        function injectCSS() { const style = document.createElement('style'); style.innerHTML = ` #copilot-icon { position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; background-color: #4285F4; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; cursor: pointer; z-index: 99998; box-shadow: 0 4px 8px rgba(0,0,0,0.2); } #copilot-window { display: none; flex-direction: column; position: fixed; bottom: 90px; right: 20px; width: 350px; height: 500px; background-color: white; border-radius: 10px; box-shadow: 0 4px 16px rgba(0,0,0,0.2); z-index: 99999; } #copilot-header { background-color: #4285F4; color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-weight: bold; } #copilot-messages { flex-grow: 1; padding: 10px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; } .copilot-message { padding: 8px 12px; border-radius: 15px; max-width: 80%; word-wrap: break-word; } .user-message { background-color: #e0e0e0; align-self: flex-end; } .assistant-message { background-color: #d1e3ff; align-self: flex-start; } #copilot-input-container { display: flex; padding: 10px; border-top: 1px solid #ccc; } #copilot-input { flex-grow: 1; border: 1px solid #ccc; border-radius: 5px; padding: 8px; } #copilot-send { margin-left: 10px; padding: 8px 12px; background-color: #4285F4; color: white; border: none; border-radius: 5px; cursor: pointer; } `; document.head.appendChild(style); }

        // Finalne uruchomienie
        createChatUI();
        injectCSS();
        setupEventListeners();
    });
}