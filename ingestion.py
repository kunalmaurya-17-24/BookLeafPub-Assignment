import os
import re
import pathlib
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import SupabaseVectorStore
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
    task_type="retrieval_document",
    output_dimensionality=768
    )

class KnowledgeBaseIngestor:
    def __init__(self, data_dir: str | pathlib.Path):
        self.data_dir = pathlib.Path(data_dir)
        
        self.link_scanner = re.compile(
            r'(https?://[^\s<>"{}|\\^`\[\]]+)|'    
            r'(www\d{0,3}\.[^\s<>"{}|\\^`\[\]]+)',
            re.IGNORECASE
        )
 
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", " ", ""]
        )

    def extract_native_links(self, pdf_path: pathlib.Path) -> List[str]:
        
        links = []
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                for link in page.get_links():
                    uri = link.get("uri")
                    if uri:
                        links.append(uri)
            doc.close()
        except Exception as e:
            print(f"⚠️ Error extracting links from {pdf_path.name}: {e}")
        return list(set(links))

    def process_pdf(self, pdf_path: pathlib.Path) -> List[Any]:
        
        print(f"🔗 Processing: {pdf_path.name}")
        
        native_links = self.extract_native_links(pdf_path)
        loader = PyMuPDFLoader(str(pdf_path))
        documents = loader.load()
        
       
        for doc in documents:
            text_links = self.link_scanner.findall(doc.page_content)
            extracted_text_links = [l[0] or l[1] for l in text_links]
            
            doc.metadata["all_links"] = list(set(native_links + extracted_text_links))
            doc.metadata["source_file"] = pdf_path.name

       
        return self.text_splitter.split_documents(documents)

    def run_ingestion(self):
        
        all_chunks = []
        pdf_files = list(self.data_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"❌ No PDFs found in {self.data_dir}")
            return

        print(f"🚀 Found {len(pdf_files)} PDFs. Starting ingestion...")
        
        for p in pdf_files:
            chunks = self.process_pdf(p)
            all_chunks.extend(chunks)

        print(f" Total chunks created: {len(all_chunks)}")
        
        if not all_chunks:
            print(" No content extracted. Check your PDF files.")
            return

        #Upload to Supabase Vector Store
        print("Uploading to Supabase (knowledge_base table)...")
        try:
            SupabaseVectorStore.from_documents(
                all_chunks,
                embeddings,
                client=supabase,
                table_name="knowledge_base",
                query_name="match_documents"
            )
            print(" Ingestion successfully completed.")
        except Exception as e:
            print(f" Failed to upload to Supabase: {e}")

if __name__ == "__main__":
    
    KNOWLEDGE_BASE_DIR = r"E:\BOOKLEAF\knowledge_base"
    
    ingestor = KnowledgeBaseIngestor(data_dir=KNOWLEDGE_BASE_DIR)
    ingestor.run_ingestion()
