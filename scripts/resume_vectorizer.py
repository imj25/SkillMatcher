import pdfplumber
import os
import glob
from pydantic import BaseModel
from typing import List, Dict, Any
from langchain_community.llms import Ollama
from sentence_transformers import SentenceTransformer
import chromadb
import json
import hashlib
from chromadb.utils.embedding_functions import EmbeddingFunction

# 1. Define custom embedding function for mxbai
class MXBAIEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1")
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.model.encode(input).tolist()

# 2. Define structured CV format
class CVExperience(BaseModel):
    role: str
    company: str
    years: int

class CVData(BaseModel):
    name: str
    email: str
    technical_skills: List[str]  # Hard/technical skills
    soft_skills: List[str]  # Soft skills
    experience: List[CVExperience]
    education: str

# 3. Initialize components
llm = Ollama(model="deepseek-r1:14b", temperature=0)
chroma_client = chromadb.PersistentClient(path="cv_db")

# Global ChromaDB collection
cv_collection = None

def initialize_chroma_collection():
    """Initialize the ChromaDB collection with custom embeddings"""
    global cv_collection
    
    # Create embedding function
    embedding_func = MXBAIEmbeddingFunction()
    
    # Try to get or create collection
    try:
        # First try to get existing collection
        cv_collection = chroma_client.get_collection(
            name="cv_collection",
            embedding_function=embedding_func
        )
        print("Found existing CV collection in database.")
    except Exception as e:
        # If that fails for any reason, create a new collection
        print(f"Creating new CV collection: {str(e)}")
        cv_collection = chroma_client.create_collection(
            name="cv_collection",
            embedding_function=embedding_func
        )
        print("Created new CV collection in database.")
    
    return cv_collection

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw text from PDF resume"""
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)

def parse_cv(pdf_text: str) -> Dict:
    """Convert raw CV text to structured data using LLM with both hard and soft skills extraction"""
    
    prompt = f"""
    Extract from this CV and return ONLY JSON:
    {pdf_text}
    
    Required Format:
    ```json
    {{
      "name": "Full Name",
      "email": "email@example.com",
      "technical_skills": ["skill1", "skill2"],
      "soft_skills": ["communication", "leadership", "teamwork"],
      "experience": [
        {{"role": "Position", "company": "Company", "years": X}}
      ],
      "education": "Degree"
    }}
    ```
    
    For technical_skills, extract hard/technical/domain-specific skills relevant to any industry.
    For soft_skills, extract interpersonal abilities, traits and transferable skills.
    """
    response = llm.invoke(prompt)
    try:
        return json.loads(response.split("```json")[1].split("```")[0].strip())
    except:
        return {
            "name": "Unknown",
            "email": "unknown@example.com",
            "technical_skills": [],
            "soft_skills": [],
            "experience": [],
            "education": ""
        }

def prepare_metadata(cv_data: Dict) -> Dict:
    """Convert CV data to ChromaDB-compatible metadata"""
    return {
        "name": str(cv_data.get("name", "")),
        "email": str(cv_data.get("email", "")),
        "technical_skills": json.dumps(cv_data.get("technical_skills", [])),
        "soft_skills": json.dumps(cv_data.get("soft_skills", [])),
        "experience": json.dumps([exp if isinstance(exp, dict) else exp.__dict__ 
                                for exp in cv_data.get("experience", [])]),
        "education": str(cv_data.get("education", ""))
    }

def generate_document_id(file_path: str) -> str:
    """Generate a consistent document ID from file path"""
    return hashlib.md5(file_path.encode()).hexdigest()

def embed_and_store_cv(pdf_path: str, pdf_text: str, cv_data: Dict) -> str:
    """Embed CV text and store in ChromaDB with metadata"""
    global cv_collection
    
    # Ensure collection is initialized
    if cv_collection is None:
        cv_collection = initialize_chroma_collection()
    
    doc_id = generate_document_id(pdf_path)
    metadata = prepare_metadata(cv_data)
    
    # Simple add with upsert=True (will update if exists)
    try:
        cv_collection.upsert(
            ids=[doc_id],
            documents=[pdf_text],
            metadatas=[metadata]
        )
        print(f"Successfully stored document: {doc_id}")
    except Exception as e:
        print(f"Error storing document {doc_id}: {str(e)}")
        # Try a different approach if upsert fails
        try:
            # First delete if exists (ignore errors)
            try:
                cv_collection.delete(ids=[doc_id])
            except:
                pass
            
            # Then add fresh
            cv_collection.add(
                ids=[doc_id],
                documents=[pdf_text],
                metadatas=[metadata]
            )
            print(f"Added document with fallback method: {doc_id}")
        except Exception as add_error:
            print(f"Critical error storing document: {str(add_error)}")
    
    return doc_id

def get_similar_cvs(query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """Find similar CVs based on text query using vector similarity"""
    global cv_collection
    
    # Ensure collection is initialized
    if cv_collection is None:
        cv_collection = initialize_chroma_collection()
    
    # Query the collection
    try:
        results = cv_collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
    except Exception as e:
        print(f"Error querying CV collection: {str(e)}")
        return []
    
    formatted_results = []
    if results and results.get('ids') and results.get('metadatas'):
        for i, doc_id in enumerate(results['ids'][0]):
            metadata = results['metadatas'][0][i]
            try:
                # Parse JSON strings back to lists
                technical_skills = json.loads(metadata.get('technical_skills', '[]'))
                soft_skills = json.loads(metadata.get('soft_skills', '[]'))
                experience = json.loads(metadata.get('experience', '[]'))
                
                formatted_results.append({
                    'id': doc_id,
                    'name': metadata.get('name', 'Unknown'),
                    'email': metadata.get('email', 'unknown@example.com'),
                    'technical_skills': technical_skills,
                    'soft_skills': soft_skills,
                    'experience': experience,
                    'education': metadata.get('education', ''),
                    'similarity': 1 - results['distances'][0][i] if 'distances' in results else None 
                })
            except Exception as e:
                print(f"Error parsing metadata for document {doc_id}: {str(e)}")
                continue
    
    return formatted_results

def score_cv(cv_data: Dict, job_desc: str, tech_weight: float = 0.7, soft_weight: float = 0.3) -> Dict:
    """
    Generate weighted score and analysis for candidates across multiple industries
    
    Parameters:
        cv_data: Dictionary containing CV information
        job_desc: String describing the job requirements
        tech_weight: Weight for technical/hard skills (default 0.7 or 70%)
        soft_weight: Weight for soft skills (default 0.3 or 30%)
    """
    prompt = f"""
    You are an expert CV-to-Job matching system. Analyze the following CV against the job description and:

    1. Assign a relevance score (0-100), broken down as follows:
       - Hard skills match (50% weight):
         - Required skills: 70% of this category
         - Bonus/nice-to-have skills: 30% of this category
         - Full match = 1.0, partial/related = 0.5, missing = 0.0
       - Experience duration vs requirement (20% weight):
         - Matches or exceeds: 100%
         - Undershoots by <1 year: 75%
         - Undershoots by 1-2 years: 50%
         - Undershoots by 2+ years: 20%
         - Not stated: 0%
       - Education/certifications (15% weight):
         - Direct match: 100%
         - Related field: 50%
         - Irrelevant/missing: 0%
       - Domain or industry fit (10% weight):
         - Has relevant experience in target domain: 100%
         - Adjacent/related domain: 50%
         - Irrelevant or no domain context: 0%
       - Soft skills / role fit indicators (5% weight)

    2. List:
       - Matched skills (required and bonus)
       - Missing or weak requirements
       - Any relevant soft skills or domain experience

    3. Output ONLY in valid JSON format:

    Job Description: {job_desc}

    CV Data:
    - Name: {cv_data.get('name', 'Unknown')}
    - Technical Skills: {', '.join(cv_data.get('technical_skills', []))}
    - Soft Skills: {', '.join(cv_data.get('soft_skills', []))}
    - Experience: {json.dumps(cv_data.get('experience', []), indent=2)}
    - Education: {cv_data.get('education', '')}

    Output format:
    ```json
    {{
      "relevance_score": [calculated_score_0_to_100],  // >> Force single number
      "justification": "[concise_reason]",
      "key_matches": ["skill1", "skill2"],
      "missing_requirements": ["requirement1", "requirement2"],
      "soft_skills": ["skillA", "skillB"],
      "domain_fit": "[industry or domain match, or 'None']"
    }}
    ```
    
    Important rules:
    - For key_matches, list EXACT qualifications that match the job requirements
    - If there are no matches at all, set key_matches to ["None"]
    - In justification, DO NOT use the candidate's name - refer to them as "the candidate"
    - Domain fit should be a short phrase describing industry relevance
    """
    
    response = llm.invoke(prompt)
    
    try:
        json_str = response.split("```json")[1].split("```")[0].strip()
        result = json.loads(json_str)
        
        # Get matches, ensuring we handle empty lists
        matches = result.get("key_matches", [])
        if not matches or (len(matches) == 1 and matches[0].lower() == "none"):
            matches = ["None"]
            
        return {
            "relevance_score": result.get("relevance_score", 0),
            "justification": result.get("justification", "Analysis incomplete"),
            "key_matches": matches[:5],
            "missing_requirements": result.get("missing_requirements", [])[:5],
            "soft_skills": result.get("soft_skills", [])[:3],
            "domain_fit": result.get("domain_fit", "None")
        }
    except Exception as e:
        print(f"Scoring error: {str(e)}")
        return {
            "relevance_score": 0,
            "justification": "Analysis failed",
            "key_matches": ["None"],
            "missing_requirements": [],
            "soft_skills": [],
            "domain_fit": "None"
        }

def semantic_match_job_to_candidates(job_desc: str, top_n: int = 5) -> List[Dict]:
    """
    Find best candidates based on semantic similarity between job description and CVs
    
    Parameters:
        job_desc: String containing job description
        top_n: Number of top candidates to return
    """
    # First find candidates based on semantic similarity (Embedding-based similarity search)
    similar_candidates = get_similar_cvs(job_desc, n_results=top_n)
    
    # Score and rank each candidate (LLM-powered scoring)
    results = []
    for candidate in similar_candidates:
        scored = score_cv(candidate, job_desc)
        results.append({
            "cv_id": candidate["id"],
            "applicant": candidate["name"],
            "similarity_score": candidate.get("similarity", 0),
            **scored
        })
    
    return sorted(results, key=lambda x: x["relevance_score"], reverse=True)

def process_job_applications(job_desc: str, cv_paths: List[str], 
                            tech_weight: float = 0.7, soft_weight: float = 0.3) -> List[Dict]:
    """
    Main pipeline with industry-agnostic weighted scoring and embedding
    
    Parameters:
        job_desc: String containing job description
        cv_paths: List of paths to CV PDF files
        tech_weight: Weight for technical/hard skills (default 0.7)
        soft_weight: Weight for soft skills (default 0.3)
    """
    results = []
    
    # First process and store all CVs with embeddings
    for path in cv_paths:
        try:
            print(f"Processing {path}...")
            text = extract_text_from_pdf(path)
            cv_data = parse_cv(text)
            
            # Store with embeddings
            doc_id = embed_and_store_cv(path, text, cv_data)
            
            # Score against job description
            scored = score_cv(cv_data, job_desc, tech_weight, soft_weight)
            results.append({
                "cv_file": path,
                "cv_id": doc_id,
                "applicant": cv_data.get("name", "Unknown"),
                **scored
            })
        except Exception as e:
            print(f"Skipped {path} due to error: {str(e)}")
    
    return sorted(results, key=lambda x: x["relevance_score"], reverse=True)

def search_cv_by_query(query_text: str, top_n: int = 5) -> List[Dict]:
    """
    Search for CVs based on a free-text query using embeddings
    
    Parameters:
        query_text: Free text query to search for
        top_n: Number of top results to return
    """
    similar_candidates = get_similar_cvs(query_text, n_results=top_n)
    
    # Format results
    return [{
        "id": candidate["id"],
        "name": candidate["name"],
        "email": candidate["email"],
        "technical_skills": candidate["technical_skills"],
        "soft_skills": candidate["soft_skills"],
        "experience": candidate["experience"],
        "education": candidate["education"],
        "similarity_score": candidate.get("similarity", 0)
    } for candidate in similar_candidates]

def get_cv_files_from_folder(folder_path: str = "test_resumes") -> List[str]:
    """Get all PDF files from the specified folder"""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder '{folder_path}' not found")
    
    return glob.glob(os.path.join(folder_path, "*.pdf"))

def hybrid_job_matching(job_desc: str, top_n: int = 5, 
                       semantic_weight: float = 0.4, 
                       scoring_weight: float = 0.6) -> List[Dict]:
    """
    Combined ranking using both semantic similarity and LLM scoring
    
    Parameters:
        job_desc: Job description text
        top_n: Number of candidates to return
        semantic_weight: Weight for embedding similarity (0-1)
        scoring_weight: Weight for LLM scoring (0-1)
    """
    # Get semantically similar candidates
    similar_candidates = get_similar_cvs(job_desc, n_results=top_n*2)
    
    # Score and combine metrics
    scored_candidates = []
    for candidate in similar_candidates:
        # Get LLM analysis
        scored = score_cv(candidate, job_desc)
        
        # Normalize scores to 0-1 range
        similarity_norm = candidate.get("similarity", 0)  # Already 0-1 after fix
        relevance_norm = scored["relevance_score"] / 100  # Convert 0-100 to 0-1
        
        # Calculate combined score
        combined = ((similarity_norm * semantic_weight) + (relevance_norm * scoring_weight)) * 100
        
        scored_candidates.append({
            **candidate,
            **scored,
            "combined_score": combined,
            "similarity_score": similarity_norm,
            "relevance_score_normalized": relevance_norm
        })
    
    # Return top candidates sorted by combined score
    return sorted(scored_candidates, key=lambda x: x["combined_score"], reverse=True)[:top_n]

def setup_script():
    """Initialize all required components"""
    print("Initializing mxbai embedding model...")
    global cv_collection
    cv_collection = initialize_chroma_collection()
    print("ChromaDB collection initialized.")

# Example execution
if __name__ == "__main__":
    # Initialize components first
    setup_script()
    
    job_description = """
    Full Stack ASP.NET Developer (3+ years experience)

    We are seeking an experienced Full Stack Developer with expertise in ASP.NET technologies. The ideal candidate will have:

    Technical Requirements:
    - Minimum 3 years of hands-on experience in full stack development using ASP.NET
    - Strong front-end skills: HTML5, CSS3, Bootstrap, JavaScript
    - Back-end expertise: C#, Entity Framework (both Database First and Code First approaches)
    - Database experience: MySQL and SQL Server
    - API development and integration experience

    Preferred Qualifications:
    - Experience with modern JavaScript frameworks (Angular, React, or Vue.js)
    - Knowledge of .NET Core
    - Understanding of RESTful services and microservices architecture
    - Familiarity with cloud platforms (Azure, AWS)
    - Experience with version control systems (Git)

    Responsibilities:
    - Develop and maintain web applications using ASP.NET stack
    - Design and implement both front-end and back-end components
    - Create and optimize database structures
    - Build and consume APIs
    - Collaborate with cross-functional teams to deliver high-quality software solutions
    """
    
    try:
        # Get all PDF files from test_resumes folder
        cv_files = get_cv_files_from_folder()
        
        if not cv_files:
            print("No PDF files found in test_resumes folder")
            exit()
            
        print(f"Found {len(cv_files)} CVs to process")
        
        # Process all CVs
        print("\n===== PROCESSING ALL CVS WITH EMBEDDINGS =====")
        ranked_results = process_job_applications(job_description, cv_files, tech_weight=0.7, soft_weight=0.3)
        
        print("\nRanked Applicants:")
        for i, result in enumerate(ranked_results, 1):
            print(f"\n{i}. {result['cv_file']} (Score: {result['relevance_score']}/100)")
            print(f"Applicant: {result['applicant']}")
            print(f"Summary: {result['justification']}")
            print(f"Domain Fit: {result['domain_fit']}")
            print(f"Matches: {', '.join(result['key_matches'])}")
            print(f"Soft Skills: {', '.join(result['soft_skills'])}")
            print(f"Missing: {', '.join(result['missing_requirements'])}")
        

        

        
        # Demonstrate semantic job matching
        print("\n===== SEMANTIC JOB MATCHING EXAMPLE =====")
        print("Finding best candidates based on semantic similarity to job description...")
        semantic_job_results = semantic_match_job_to_candidates(job_description, top_n=5)
        
        print(f"\nFound {len(semantic_job_results)} semantically relevant candidates:")
        for i, result in enumerate(semantic_job_results, 1):
            print(f"\n{i}. {result['applicant']} (Score: {result['relevance_score']}/100)")
            print(f"Summary: {result['justification']}")
            print(f"Domain Fit: {result['domain_fit']}")
            print(f"Matches: {', '.join(result['key_matches'])}")
            print(f"Missing: {', '.join(result['missing_requirements'])}")

    except Exception as e:
        print(f"Error processing CVs: {str(e)}")