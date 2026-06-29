from langchain_core.prompts import ChatPromptTemplate
from ai.llm import safe_llm_call

STUDY_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful study assistant. Answer based ONLY on the provided context. "
     "If the answer is not in the context, say 'I don't have information about that in your documents.'"),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])

def run_resource_agent(question: str, context: str) -> str:
    """
    CHANGED: previously built a LangChain chain directly with
    get_llm() (always Gemini, no fallback parameter ever passed) and
    invoked it — meaning this agent had ZERO fallback to Groq and
    ZERO circuit breaker coverage, unlike every other agent in this
    app, which all go through safe_llm_call(). Confirmed by reading
    the original code, not assumed: if Gemini failed here, this whole
    agent crashed with no recovery path at all.

    Fix: format the prompt template into a plain string ourselves,
    then call safe_llm_call() like every other agent does. This gets
    this agent the same circuit-breaker + Groq-fallback coverage as
    cognitive_agent, task_regulator_agent, planning_agent, and
    task_decompose_agent — for free, no new logic needed here.
    """
    formatted_prompt = STUDY_PROMPT.format(context=context, question=question)
    return safe_llm_call(formatted_prompt)