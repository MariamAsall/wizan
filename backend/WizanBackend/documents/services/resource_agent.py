from langchain_core.prompts import ChatPromptTemplate
from ai.llm import get_llm

STUDY_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful study assistant. Answer based ONLY on the provided context. "
     "If the answer is not in the context, say 'I don't have information about that in your documents.'"),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])

def run_resource_agent(question: str, context: str) -> str:
    chain = STUDY_PROMPT | get_llm()
    response = chain.invoke({"context": context, "question": question})
    return response.content