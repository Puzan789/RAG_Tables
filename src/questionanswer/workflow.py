from src.questionanswer.qdrant_db import QdrantConfig
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from src.config import settings
from langgraph.graph import StateGraph, START, END
from src.questionanswer.schemas import GraphState

llm = ChatGroq(
    model=settings.GROQ_MODEL, api_key=settings.GROQ_API_KEY, temperature=0.5
)
config = QdrantConfig()


def retrieve(state):
    """Retrieve document best on the current state"""
    updated_state = state.copy()
    query = updated_state["question"]
    points = config.search_documents(query)
    updated_state["documents"] = points
    return updated_state


def generate(state):
    """Generate response based on the current state"""
    updated_state = state.copy()
    question = updated_state["question"]
    documents = updated_state["documents"]
    prompt = ChatPromptTemplate.from_template(
        """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context
to answer the question. If you don't know the answer, just say that you don't know.
Question: {question}
Context: {context}
Answer:
"""
    )

    rag_chain = prompt | llm | StrOutputParser()
    generation = rag_chain.invoke({"context": documents, "question": question})
    # Update the state with the generated response
    state["generation"] = generation
    return state


def create_workflow():
    """
    Create a workflow that retrieves documents and generates a response.
    """
    workflow = StateGraph(GraphState)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()

