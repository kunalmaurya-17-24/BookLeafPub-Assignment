import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from supabase.client import Client, create_client


load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env file")

supabase: Client = create_client(supabase_url, supabase_key)


embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    task_type="retrieval_query",
    output_dimensionality=768
    )



@tool
def search_knowledge_base(query: str) -> str:
    """
    Searches the BookLeaf Publishing FAQ Knowledge Base for answers to general publishing questions, 
    writing challenge rules, royalties, publishing timelines, and other policies.
    """
    try:
        # Generate query embedding using the same model as ingestion
        query_embedding = embeddings.embed_query(query)
        
       
        result = supabase.rpc("match_documents", {
            "query_embedding": query_embedding,
            "match_count": 3
        }).execute()
        
        if not result.data:
            return "No specific information found in the Knowledge Base for this query."
        
        formatted_results = []
        for doc in result.data:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            source = metadata.get("source_file", "Unknown")
            links = metadata.get("all_links", [])
            link_str = f"\nRelevant Links: {', '.join(links)}" if links else ""
            formatted_results.append(f"[Source: {source}]\n{content}{link_str}")
            
        return "\n\n---\n\n".join(formatted_results)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error searching Knowledge Base: {str(e)}"

@tool
def check_author_status(email: str) -> str:
    """
    Queries the internal database for specific author status, book titles, ISBNs, 
    royalty status, and key dates using their email address.
    """
    try:
        # Standard SQL lookup in author_status table
        response = supabase.table("author_status").select("*").eq("email", email.strip().lower()).execute()
        
        if not response.data:
            return f"No author record found for email: {email}. Please verify the email or ask for a different one."
        
        data = response.data[0]
        status_report = (
            f"Author Status Report for {email}:\n"
            f"- Book Title: {data.get('book_title')}\n"
            f"- ISBN: {data.get('isbn') or 'Pending'}\n"
            f"- Publishing Status: {data.get('publishing_status')}\n"
            f"- Royalty Status: {data.get('royalty_status')}\n"
            f"- Submission Date: {data.get('final_submission_date')}\n"
            f"- Go-Live Date: {data.get('book_live_date') or 'TBD'}"
        )
        return status_report
    except Exception as e:
        return f"Error querying author status: {str(e)}"

@tool
def log_interaction_to_supabase(query: str, response: str, confidence: float, email: Optional[str] = None, platform: str = "web"):
    """
    Logs the user query, bot response, confidence score, and platform to the database for audit and human escalation tracking.
    Required by the assignment to monitor the 80% confidence threshold.
    """
    try:
        log_entry = {
            "query": query,
            "response": response,
            "confidence_score": confidence,
            "author_email": email,
            "platform_used": platform
        }
        supabase.table("bot_logs").insert(log_entry).execute()
        return "Interaction logged successfully to Supabase."
    except Exception as e:
        return f"Error logging interaction: {str(e)}"