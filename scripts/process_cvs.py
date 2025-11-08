import pdfplumber
import os
import glob
from pydantic import BaseModel
from typing import List, Dict, Any
from langchain_community.llms import Ollama
from sentence_transformers import SentenceTransformer
import json
import hashlib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
import concurrent.futures
from fastapi import UploadFile, File ,Form
import tempfile
import torch  # Add this import

# d_main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ───── CORS ────────────────────────────────────────
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ───────────────────────────────────────────────────

# … rest of your routes …

# ------ Configuration ------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")
# ------ Configuration ------
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "mistral:7b-instruct-q4_K_M"
MAX_WORKERS = 4  # For multithreading

# Initialize components with GPU support
embedder = SentenceTransformer(EMBEDDING_MODEL).to(DEVICE)  # Move model to GPU
llm = Ollama(model=LLM_MODEL, temperature=0)


# ------ Data Models ------
class CVExperience(BaseModel):
    role: str
    company: str
    years: int

class CVData(BaseModel):
    name: str
    email: str
    technical_skills: List[str]
    soft_skills: List[str]
    experience: List[CVExperience]
    education: str
    embedding: List[float]  # Added embedding storage

class JobRequest(BaseModel):
    job_title: str
    job_description: str
    cv_paths: List[str]

# ------ Core Functions ------
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ------ Modified GPU Functions ------
def process_single_cv(cv_path: str) -> Dict:
    """Process CV with GPU support"""
    try:
        print(f"Processing {cv_path} on {DEVICE}...")
        text = extract_text_from_pdf(cv_path)
        if not text.strip():
            return {"status": "error", "message": "Empty or image-only PDF", "path": cv_path}
        cv_data = parse_cv(text)
        
        # GPU-accelerated embedding
        with torch.no_grad():
            cv_data["embedding"] = embedder.encode(text, device=DEVICE, convert_to_tensor=True).cpu().numpy().tolist()
            
        return {"status": "success", "data": cv_data, "path": cv_path}
    except Exception as e:
        print(f"⚠️  CV failed: {cv_path} → {e}")
        return {"status": "error", "message": str(e), "path": cv_path}

def extract_text_from_pdf(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        texts = []
        for page in pdf.pages:
            t = page.extract_text() or ''   # <- fall back to empty string
            texts.append(t)
        return "\n".join(texts)

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
    
    try:
        response = llm.invoke(prompt)
        
        # Enhanced JSON extraction with multiple fallbacks
        json_str = None
        try:
            # First try standard extraction
            json_str = response.split("```json")[1].split("```")[0].strip()
        except IndexError:
            # Fallback: look for any JSON block
            json_blocks = [b for b in response.split("```") if b.strip().startswith('{')]
            if json_blocks:
                json_str = json_blocks[0].strip('json').strip()

        # Final fallback: try parsing entire response as JSON
        if not json_str:
            json_str = response.strip()

        result = json.loads(json_str)

        # Robust list handling with type checking
        def safe_get_list(data, key, max_items=None):
            items = data.get(key, [])
            if not isinstance(items, list):
                items = [items] if items else []
            return items[:max_items] if max_items else items

        return {
            "relevance_score": int(result.get("relevance_score", 0)),
            "justification": str(result.get("justification", "Analysis incomplete")),
            "key_matches": safe_get_list(result, "key_matches", 5) or ["None"],
            "missing_requirements": safe_get_list(result, "missing_requirements", 5),
            "soft_skills": safe_get_list(result, "soft_skills", 3),
            "domain_fit": str(result.get("domain_fit", "None"))
        }
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed. Raw LLM response:\n{response}")
        return error_fallback()
    except Exception as e:
        print(f"Scoring error: {str(e)}\nResponse: {response[:200]}...")
        return error_fallback()

def error_fallback():
    return {
        "relevance_score": 0,
        "justification": "Analysis failed",
        "key_matches": ["None"],
        "missing_requirements": [],
        "soft_skills": [],
        "domain_fit": "None"
    }

# ------ API Endpoints ------
@app.post("/match-candidates")
async def match_candidates(
    job_req: JobRequest,
    tech_weight: float = 0.7,
    soft_weight: float = 0.3,
    top_n: int = 5
):
    """Main API endpoint for candidate matching"""
    try:
        # Process CVs with multithreading
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(process_single_cv, path) for path in job_req.cv_paths]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Generate job embedding on GPU
        with torch.no_grad():
            job_embedding = embedder.encode(job_req.job_description, device=DEVICE, convert_to_tensor=True).cpu().numpy()

        
        # Calculate similarities and scores
        candidates = []
        for result in results:
            if result["status"] != "success":
                continue
                
            cv_data = result["data"]
            similarity = cosine_similarity(job_embedding, cv_data.get("embedding", []))
            scored = await run_in_threadpool(score_cv, cv_data, job_req.job_description)
            
            candidates.append({
                "applicant": cv_data.get("name", "Unknown"),
                "similarity": similarity,
                "relevance_score": scored["relevance_score"],
                "combined_score": (similarity * 0.4) + (scored["relevance_score"]/100 * 0.6),
                **scored,
                "cv_path": result["path"],  # << Add this line (bulletproof ID)
            })

        # Sort and return results
        sorted_candidates = sorted(candidates, key=lambda x: x["combined_score"], reverse=True)[:top_n]
        return {"results": sorted_candidates}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-cvs")
async def upload_cvs(
    job_id: str = Form(...),  # Get job_id from form data
    files: List[UploadFile] = File(...)
):
    """Upload CVs to a job-specific folder"""
    try:
        base_dir = "uploaded_cvs"
        job_dir = os.path.join(base_dir, job_id)
        
        # Create directory if not exists
        os.makedirs(job_dir, exist_ok=True)
        
        saved_paths = []
        
        for file in files:
            # Sanitize filename
            filename = file.filename.replace(" ", "_")
            file_path = os.path.join(job_dir, filename)
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(await file.read())
            
            saved_paths.append(file_path)
        
        return {
            "job_id": job_id,
            "cv_paths": saved_paths,
            "message": f"CVs uploaded successfully to {job_dir}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ------ Main Execution ------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)