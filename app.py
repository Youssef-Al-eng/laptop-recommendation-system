import streamlit as st
import json
import os
from groq import Groq
from rag_engine import RAGEngine
import config

# Initialize Groq client
client = Groq(api_key=config.GROQ_API_KEY)

@st.cache_resource
def load_system():
    """Load RAG engine and product data from config"""
    rag = RAGEngine()
    if config.ALL_PRODUCTS:
        rag.build_index(config.ALL_PRODUCTS)
        return rag, config.ALL_PRODUCTS
    return None, []

rag, products_list = load_system()

if "messages" not in st.session_state:
    st.session_state.messages = []

# UI Layout
st.title("Smart Recommendation system for Laptop Store")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Logic
if prompt := st.chat_input("Ask me about our inventory..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if rag:
        # Check if user wants broad info vs. specific search
        broad_keywords = ["all", "everything", "list", "sort", "rest", "بقية", "كل", "قائمة", "رتب", "عرض"]
        is_broad_query = any(word in prompt.lower() for word in broad_keywords) or "how many" in prompt.lower()

        if is_broad_query:
            # Provide full list for counting or sorting tasks
            context = "FULL INVENTORY LIST:\n"
            for p in config.ALL_PRODUCTS:
                context += f"- {p.get('Full Name')} | Price: {p.get('Price')}\n"
        else:
            # Use RAG to find the most relevant matches
            search_results = rag.search(prompt)
            context = "SPECIFIC TOP MATCHES:\n"
            for p in search_results:
                context += f"- {p.get('Full Name')} | Price: {p.get('Price')} | CPU: {p.get('CPU')} | GPU: {p.get('GPU')} | RAM: {p.get('RAM')}\n"
        
        # System instructions for the AI
        system_prompt = f"""
        You are a smart AI Sales Assistant for a laptop store.
        
        STORE STATUS:
        - Total laptops available: {config.TOTAL_LAPTOPS}
        
        CURRENT DATA CONTEXT:
        {context}
        
        GUIDELINES:
        1. Answer the correct total count ({config.TOTAL_LAPTOPS}) if asked.
        2. Use the FULL INVENTORY list if the user wants to see everything or the 'rest'.
        3. Perform sorting (price/alphabetical) based on the context provided.
        4. Be professional and explain why specific laptops fit user needs.
        5. Be polite; don't list products for simple greetings.
        """

        with st.chat_message("assistant"):
            try:
                # Get response from Groq LLM
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model=config.LLM_MODEL,
                )
                
                ai_response = chat_completion.choices[0].message.content
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Database is empty. Please run the scraper first.")