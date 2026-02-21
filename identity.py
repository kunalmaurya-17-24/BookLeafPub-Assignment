import os
import re
from typing import List, Dict, Any, Optional
from rapidfuzz import fuzz, process
from dotenv import load_dotenv
from supabase.client import Client, create_client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)


llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)

class IdentityUnifier:
    def __init__(self):
        self.confidence_threshold = 85.0 

    def get_all_authors(self) -> List[Dict[str, Any]]:
        """Retrieve all primary authors from the database for matching pool"""
        response = supabase.table("author_status").select("email, book_title").execute()
        return response.data

    def fuzzy_match_author(self, input_identifier: str, pool: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        emails = [a['email'] for a in pool]
        titles = [a['book_title'] for a in pool]
        

        email_matches = process.extract(input_identifier, emails, scorer=fuzz.partial_ratio, limit=2)

        title_matches = process.extract(input_identifier, titles, scorer=fuzz.WRatio, limit=2)
        
        candidates = []

        for match, score, idx in email_matches:
            candidates.append({"email": pool[idx]['email'], "score": score, "reason": "Email Match"})
        for match, score, idx in title_matches:
            candidates.append({"email": pool[idx]['email'], "score": score, "reason": "Title Match"})
            
        return candidates

    def llm_disambiguate(self, input_identifier: str, platform: str, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:

        if not candidates:
            return {"email": None, "confidence": 0, "reason": "No candidates found"}

        prompt = ChatPromptTemplate.from_template("""
        You are an Identity Unification Specialist at BookLeaf Publishing.
        Task: Link a user handle from {platform} to an existing author profile.
        
        Input Handle/ID: {identifier}
        Platform: {platform}
        
        Potential Database Candidates:
        {candidates_list}
        
        Analyze the handle and the candidates. Is there a high probability (above 85%) that this handle belongs to one of the authors?
        A handle like '@sarapoetry23' likely belongs to 'sara.johnson@xyz.com'.
        
        Return your response in JSON format:
        {{
            "matched_email": "email or null",
            "confidence_score": 0-100,
            "justification": "Short reason why"
        }}
        """)
        
        candidates_str = "\n".join([f"- {c['email']} (Fuzzy Score: {c['score']}, Match Logic: {c['reason']})" for c in candidates])
        chain = prompt | llm
        
        try:
            response = chain.invoke({
                "platform": platform,
                "identifier": input_identifier,
                "candidates_list": candidates_str
            })
            import json, re

            content = response.content
            if not isinstance(content, str):

                if isinstance(content, list):
                    content = " ".join(p.get('text', '') for p in content if isinstance(p, dict))
                else:
                    content = str(content)
                
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            

            try:
                result = json.loads(content.strip())
            except json.JSONDecodeError:

                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    result = json.loads(match.group())
                else:
                    raise
            return result
        except Exception as e:
            return {"email": None, "confidence": 0, "reason": f"LLM Error: {str(e)}"}

    def link_identity(self, email: str, platform: str, handle_or_id: str):
       
        try:
            supabase.table("author_identities").insert({
                "primary_email": email,
                "platform": platform,
                "handle_or_id": handle_or_id
            }).execute()
            return True
        except Exception as e:
            print(f"Error linking identity: {e}")
            return False


unifier = IdentityUnifier()

def resolve_author_identity(platform: str, identifier: str) -> Optional[str]:

    existing = supabase.table("author_identities").select("primary_email").eq("platform", platform).eq("handle_or_id", identifier).execute()
    if existing.data:
        return existing.data[0]['primary_email']
    

    pool = unifier.get_all_authors()
    fuzzy_candidates = unifier.fuzzy_match_author(identifier, pool)
    

    resolution = unifier.llm_disambiguate(identifier, platform, fuzzy_candidates)
    
    if resolution.get("confidence_score", 0) >= 85:
        email = resolution["matched_email"]
        unifier.link_identity(email, platform, identifier)
        return email
    
    return None
