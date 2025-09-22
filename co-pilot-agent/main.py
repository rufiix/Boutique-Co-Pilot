# main.py (Wersja MULTIMODALNA)
import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image

# --- Konfiguracja ---
PROJECT_ID = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("GCP_REGION")
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel("gemini-2.0-flash-lite")
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Pamięć podręczna ---
user_context = {}

# --- Modele danych (Pydantic) ---
class PageContext(BaseModel):
    type: str
    name: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None # Nowe pole na URL obrazka
    products_on_page: Optional[List[dict]] = None

# ... (reszta modeli Pydantic bez zmian) ...
class CartItem(BaseModel): name: str; quantity: int; price: str
class Cart(BaseModel): type: str; items: Optional[List[CartItem]] = None; shipping_cost: Optional[str] = None; total_cost: Optional[str] = None; item_count: Optional[int] = None
class UserEvent(BaseModel): user_id: str; event_type: str; product_id: str
class ChatMessage(BaseModel): user_id: str; message: str; page_context: Optional[PageContext] = None; cart_contents: Optional[Cart] = None; chat_history: Optional[List[str]] = None

# --- Endpointy API ---
@app.get("/")
def read_root(): return {"Status": "Co-Pilot Agent is running"}

@app.post("/copilot-api/event")
def receive_event(event: UserEvent):
    # ... bez zmian ...
    if event.user_id not in user_context: user_context[event.user_id] = {"viewed_products": []}
    if event.product_id not in user_context[event.user_id]["viewed_products"]: user_context[event.user_id]["viewed_products"].append(event.product_id)
    return {"status": "event received"}

@app.post("/copilot-api/chat")
def chat_with_copilot(chat_message: ChatMessage):
    user_message = chat_message.message
    
    # --- Zbieranie kontekstu tekstowego (bez zmian) ---
    # ... (cała logika dla viewed_products, page_context_text, cart_text, history_text bez zmian) ...
    context = user_context.get(chat_message.user_id, {"viewed_products": []}); viewed_products = ", ".join(context["viewed_products"]) or "none"
    page_context_text = "User is not on a specific product page."; cart_text = "The user's shopping cart is empty."; history_text = "This is the beginning of the conversation."
    if chat_message.page_context:
        if chat_message.page_context.type == 'product_page': page_context_text = f"User is on a product page for:\n- Name: {chat_message.page_context.name}\n- Price: {chat_message.page_context.price}\n- Description: {chat_message.page_context.description}"
        elif chat_message.page_context.type == 'homepage' and chat_message.page_context.products_on_page: products_list = "\n".join([f"- {p['name']} ({p['price']})" for p in chat_message.page_context.products_on_page]); page_context_text = f"User is on the homepage, which displays these products:\n{products_list}"
    if chat_message.cart_contents:
        if chat_message.cart_contents.type == 'detailed_view' and chat_message.cart_contents.items: items_in_cart = "\n".join([f"- {item.name} (Quantity: {item.quantity}, Price: {item.price})" for item in chat_message.cart_contents.items]); cart_text = f"The user is on the cart page. The cart contains:\n{items_in_cart}\n- Shipping Cost: {chat_message.cart_contents.shipping_cost}\n- Total Cost: {chat_message.cart_contents.total_cost}"
        elif chat_message.cart_contents.type == 'summary_view' and chat_message.cart_contents.item_count > 0: cart_text = f"The user has {chat_message.cart_contents.item_count} item(s) in their cart."
    if chat_message.chat_history: history_text = "Here is the recent conversation history:\n" + "\n".join(chat_message.chat_history)

    # --- TWORZENIE PROMPTU MULTIMODALNEGO ---
    prompt_text = f"""
    You are an e-commerce assistant. Analyze the user's question and the provided image (if any).

Context:
- Conversation History: {history_text}
- Shopping Cart: {cart_text}
- Current Page: {page_context_text}
- Recently Viewed Products: {viewed_products}

User's Question: "{user_message}"

Instructions:
1. Analyze all provided context to understand the user's situation.  
2. If the user asks to **list products on the page** and the "Currently Viewed Page Context" indicates you are on the homepage, list the products from the `products_on_page` list.  
3. If the user asks about their cart, use the "Shopping Cart Context" to answer.  
4. If the user asks about the current product on a product page (e.g., "what's the price?", "what is it made of?"), use the "Currently Viewed Page Context".  
5. To provide detailed information (materials, sizing, specifications), the user must be on the product detail page. If they are not, politely suggest they open the product page first.  
6. If the question is about the **visual aspects of a product** (e.g., color, style, pattern, shape), use the IMAGE as the primary source of truth.  
7. When describing visual aspects, always state them confidently and directly. Do not use uncertain wording such as "it appears", "it looks like", or "seems".  
8. If the user asks for an opinion or recommendation, be a creative but helpful salesperson.  
9. Use the "Conversation History" to understand the flow of the conversation and answer "meta" questions (like "what did I ask before?").  
10. If the user is on a product page and asks about their cart, respond that cart information is available in the "Shopping Cart Context" (unless it was explicitly mentioned in the Conversation History).  
11. If a question doesn’t fit the above cases, prioritize data in this order: Current Page → Shopping Cart → Viewed Products → Conversation History.  
12. If context data is missing or unclear, politely say so and ask the user for clarification instead of guessing.  
13. Keep your answers short, warm, and conversational—like a boutique shopping assistant: friendly but precise.  


    """
    
    prompt_parts = [prompt_text]
    # Nowa, bezpieczna wersja
    image_url = None
    if chat_message.page_context and chat_message.page_context.image_url:
        image_url = chat_message.page_context.image_url

    if image_url:
        try:
            # Pobierz obrazek z URL
            image_response = requests.get(image_url)
            image_response.raise_for_status() # Sprawdź, czy nie ma błędu HTTP
            # Stwórz obiekt obrazu dla Gemini
            image = Image.from_bytes(image_response.content)
            prompt_parts.append(image)
        except Exception as e:
            print(f"Error downloading image: {e}")

    try:
        response = model.generate_content(prompt_parts) # Wysyłamy prompt multimodalny
        ai_response = response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        ai_response = "I'm having a little trouble thinking right now. Please try again in a moment."

    return {"response": ai_response}