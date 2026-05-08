import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph
from config import GROQ_API_KEY, LLM_MODEL

class ShoppingAgent:
    def __init__(self, rag_engine):
        self.rag = rag_engine
        self.llm = ChatGroq(
            model=LLM_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.2
        )

    def retrieve_products(self, state):
        query = state["query"]
        results = self.rag.search(query)
        return {"products": results, "query": query}

    def generate_recommendation(self, state):
        query = state["query"]
        products = state["products"]
        
        products_context = json.dumps(products, indent=2, ensure_ascii=False)

        prompt = f"""
User query: {query}

Available Products:
{products_context}

Task:
1. Recommend the best laptops from the list.
2. Explain why they fit the user's request.
3. Provide the link for each recommendation.
"""
        response = self.llm.invoke([
            SystemMessage(content="You are a helpful Egyptian shopping assistant."),
            HumanMessage(content=prompt)
        ])
        return {"answer": response.content}

    def build_graph(self):
        workflow = StateGraph(dict)
        workflow.add_node("retrieve", self.retrieve_products)
        workflow.add_node("generate", self.generate_recommendation)
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        return workflow.compile()