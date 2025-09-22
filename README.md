



# 🚀 Boutique Co-Pilot: A Proactive AI Shopping Assistant for GKE



**Live Demo:** `http://YOUR_INGRESS_IP_ADDRESS`
**Video Demo:** `https://your-youtube-or-vimeo-link`

---

## 💡 Inspiration & Goal

Built for the **GKE Turns 10 Hackathon**, the "Boutique Co-Pilot" project reimagines the e-commerce experience. The goal was to seamlessly integrate a powerful, proactive, and context-aware AI assistant into the existing "Online Boutique" microservices application, showcasing the power and flexibility of Google Kubernetes Engine and Vertex AI.

Instead of a reactive, stateless chatbot, we aimed to create a true co-pilot that understands the user's journey—what they see, what they click, and what they have in their cart—to provide truly intelligent and helpful assistance. The entire project was built and deployed on **GKE Autopilot** to maximize efficiency and scalability while minimizing operational overhead.

---

## ✨ Key Features

Our Co-Pilot is more than just a chat window; it's a deeply integrated assistant with "eyes" and "memory."

* **👁️ Multimodal Vision:** The assistant can "see" product images on product detail pages. You can ask it about visual attributes like color and style, and it will answer based on the image content.
* **📄 Full Page Awareness:** The Co-Pilot scrapes the content of the page the user is currently on.
    * On a **product page**, it knows the product's name, price, and detailed description.
    * On the **homepage**, it knows the list of featured products and their prices.
* **🛒 Cart Awareness:** The assistant can read the contents of the shopping cart on any page. It knows the number of items and, when on the cart page, can see a detailed list of products, quantities, prices, shipping costs, and the final total.
* **🧠 Conversational Memory:** Using `sessionStorage`, the Co-Pilot remembers the conversation history across page navigations within a single browser session, allowing for natural, multi-turn dialogue.
* **💡 Intelligent Recommendations:** The AI prompt is engineered to combine all available contexts (page content, cart, conversation history) to provide creative and relevant product recommendations, acting as a helpful salesperson.
* **🏗️ Scalable Microservice Architecture:** The Co-Pilot was implemented as a new, independent microservice (`co-pilot-agent`) without modifying the source code of the original 10 backend services, demonstrating a clean, non-intrusive integration pattern.

---

## 🏛️ Architecture

The system is deployed on a single GKE Autopilot cluster. A **GKE Ingress** acts as the central router, directing traffic to the appropriate service based on the URL path. User requests are funneled either to the modified **Frontend** service or our new **Co-Pilot Agent** service.

The agent itself is a stateless Python FastAPI application that securely communicates with the **Vertex AI Gemini API** using **Workload Identity** for authentication.



## 💻 Tech Stack

  * **Orchestration:** Google Kubernetes Engine (GKE) Autopilot
  * **Artificial Intelligence:** Google Cloud Vertex AI (Gemini 2.0 Flash Lite Model)
  * **Container Registry:** Google Artifact Registry
  * **CI/CD:** Google Cloud Build
  * **Backend:** Python 3.11 with FastAPI
  * **Frontend Integration:** Vanilla JavaScript, jQuery, HTML5, CSS3
  * **Networking:** GKE Ingress, Google Cloud Load Balancer
  * **Authentication:** GKE Workload Identity

-----

## 🔧 Running the Project (From Scratch)

This project requires a Google Cloud project with billing enabled.

1.  **Prepare Local Environment:**

      * Clone this repository.
      * Clone the `microservices-demo` repository into a directory named `frontend-source` and `git checkout v0.10.0`.
      * Apply all code modifications as developed (`chat.js`, `main.py`, `footer.html`, `Dockerfile`s, etc.).

2.  **Setup Cloud Infrastructure:**

      * Set the `$PROJECT_ID` environment variable.
      * Enable the GKE, Artifact Registry, Vertex AI, and Cloud Build APIs.
      * Create a GKE Autopilot cluster.
      * Create a firewall rule to allow health checks from the Google Cloud Load Balancer.
      * Create a repository in Artifact Registry.

3.  **Build Container Images:**

      * Navigate to the `co-pilot-agent` directory and run `gcloud builds submit` to build the agent image.
      * Navigate to the `frontend-source` directory and run `gcloud builds submit` to build the custom frontend image.

4.  **Deploy to GKE:**

      * Apply the original `kubernetes-manifests.yaml` to deploy the base Online Boutique application.
      * Apply the `deployment.yaml` and `service.yaml` for the `co-pilot-agent`.
      * Patch the `frontend-external` service to be of type `NodePort`.
      * Apply the `ingress.yaml` manifest.
      * Use `kubectl set image` to point the `frontend` and `co-pilot-agent` deployments to the newly built container images in Artifact Registry.

5.  **Configure Permissions:**

      * Create a Google Service Account (GSA) and a Kubernetes Service Account (KSA).
      * Grant the GSA the `Vertex AI User` IAM role.
      * Configure Workload Identity by creating an IAM policy binding between the GSA and KSA and annotating the KSA.
      * Patch the `co-pilot-agent` deployment to use the configured KSA.

-----

## 🚧 Challenges & Lessons Learned

  * **JavaScript Conflicts:** The biggest challenge was integrating modern vanilla JavaScript into the legacy frontend, which uses older versions of jQuery and Bootstrap. This caused numerous subtle bugs (race conditions, event propagation issues) that required deep debugging and a final, robust solution using jQuery for event delegation.
  * **Cloud-Native State Management:** Our initial implementation used an in-memory dictionary in the agent to store user history. We quickly discovered this is not a viable solution in a scalable, ephemeral environment like Kubernetes, where pods can be restarted at any time. This highlighted the importance of using external, persistent state stores like Redis (Memorystore) for session data in a production application.
  * **Permissions are Key:** Correctly configuring permissions (Workload Identity and Firewall rules) was critical and a major source of errors. A single misconfigured IAM binding or a missing firewall rule can cause the entire application to fail in non-obvious ways (e.g., `502` or `422` errors).

-----

## ⏭️ Future Improvements

  * **Persistent State:** Migrate the click history and session data to a managed **Memorystore for Redis** instance to make it robust and scalable.
  * **Proactive Engagement:** Implement logic for the Co-Pilot to initiate a conversation based on user behavior (e.g., "I see you've been looking at sunglasses for a while, can I help you find the perfect pair?").
  * **Model Tuning:** Experiment with more powerful Gemini models (like `gemini-2.0-flash`) and fine-tuning for a more specialized brand personality.

-----

Created by **rufiix** for the GKE Turns 10 Hackathon.



