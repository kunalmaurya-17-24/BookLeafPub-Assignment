import operator
from typing import Annotated, List, TypedDict, Optional
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from tools import search_knowledge_base, check_author_status, log_interaction_to_supabase
from identity import resolve_author_identity


load_dotenv()


llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    author_email: Optional[str]
    platform: str # 'whatsapp', 'instagram', 'email', 'web'
    sender_id: str # The handle or ID from the platform
    confidence: float
    handover_required: bool


def call_model(state: AgentState):
    """
    The 'Oracle' node. Decides if tools are needed or if it can answer.
    """
    messages = state["messages"]
    author_email = state.get("author_email")
    

    system_prompt = (
        "You are the BookLeaf Publishing AI Automation Specialist. "
        "Your goal is to assist authors with their publishing queries and status updates.\n\n"
        "GUIDELINES:\n"
        "1. For GENERAL policy questions (royalties, timelines, challenge rules, submission guidelines, "
        "login help, bestseller info, limitations), ALWAYS use the 'search_knowledge_base' tool to find the answer. "
        "These questions do NOT require an email — answer them directly from the knowledge base.\n"
        "   1a. If a question covers multiple topics (e.g. 'royalties for the 21-day challenge'), "
        "call 'search_knowledge_base' TWICE with two focused queries: one for 'royalties' and one for '21-day challenge rules'. "
        "Then combine both results in your answer.\n"
        "2. For AUTHOR-SPECIFIC queries (book status, ISBN lookup, payment status, go-live date, manuscript status), "
        "you MUST have the author's email. If the user has ALREADY provided their email earlier in the conversation, "
        "reuse it — do NOT ask for it again. Only ask if no email has been shared yet. "
        "Then use the 'check_author_status' tool with their email.\n"
        "3. If a query involves legal matters (copyright, lawsuits, infringement) or is unusual/out of scope, "
        "do NOT attempt to give legal advice. Instead, tell the user you are flagging this for a human BookLeaf representative "
        "who will follow up with them, and offer to connect them now.\n"
        "4. ALWAYS be polite and professional."
    )
    
    
    if author_email:
        system_prompt += (
            f"\n\nIMPORTANT: This user has been identified via our Identity Unification system. "
            f"Their verified email is: {author_email}. "
            f"Use this email directly with the Author Status tool — do NOT ask them for it again."
        )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    # Bind tools
    tools = [search_knowledge_base, check_author_status]
    llm_with_tools = llm.bind_tools(tools)
    
    chain = prompt | llm_with_tools
    response = chain.invoke({"messages": messages})
    
    return {"messages": [response]}


def evaluate_response(state: AgentState):
    """
    Node to evaluate if the response meets the 80% confidence threshold.
    """
    last_message = state["messages"][-1]
    
  
    if isinstance(last_message, ToolMessage):
        return "continue"
    
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    
    
    
    content = last_message.content if isinstance(last_message.content, str) else str(last_message.content)
    content = content.lower()
    uncertain_terms = ["i'm not sure", "i don't know", "please contact", "unusual request"]
    
    confidence = 0.95
    if any(term in content for term in uncertain_terms):
        confidence = 0.60
        
    
    query_text = str(state["messages"][0].content)
    response_text = str(last_message.content)
    
   
    log_interaction_to_supabase.invoke({
        "query": query_text,
        "response": response_text,
        "confidence": confidence,
        "email": state["author_email"],
        "platform": state["platform"]
    })
    
    if confidence < 0.80:
        return "handover"
    
    return "end"


workflow = StateGraph(AgentState)


workflow.add_node("agent", call_model)
workflow.add_node("action", ToolNode([search_knowledge_base, check_author_status]))


workflow.set_entry_point("agent")


workflow.add_edge("action", "agent")

workflow.add_conditional_edges(
    "agent",
    evaluate_response,
    {
        "continue": "action",
        "handover": END, # In a real app, this would go to a HandoverNode
        "end": END
    }
)


memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


def run_customer_bot(user_input: str, platform: str, sender_id: str, thread_id: str = "default"):
    """
    Entry point that incorporates Identity Unification.
    """

    email = resolve_author_identity(platform, sender_id)
    

    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "author_email": email,
        "platform": platform,
        "sender_id": sender_id,
        "confidence": 1.0,
        "handover_required": False
    }
    
    config = {"configurable": {"thread_id": thread_id}}
    final_output = app.invoke(initial_state, config=config)
    

    last_msg = final_output["messages"][-1]
    content = last_msg.content
    if isinstance(content, list):

        text_parts = [part['text'] for part in content if isinstance(part, dict) and 'text' in part]
        return " ".join(text_parts)
    
    return str(content)