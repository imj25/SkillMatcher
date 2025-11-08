import requests

# Upload CVs
##### this end-point for job seeker form
##### this end-point need to job_id and cv_file
files = [("files", open(r"C:\Users\PC\Desktop\CV_Analysis2\test_resumes\marwan.pdf", "rb")),("files", open(r"C:\Users\PC\Desktop\CV_Analysis2\test_resumes\cv1.pdf", "rb")),("files", open(r"C:\Users\PC\Desktop\CV_Analysis2\test_resumes\abd.pdf", "rb"))]
data = {"job_id": "backend_dev_2023"}
upload_response = requests.post("http://localhost:8000/upload-cvs", files=files , data=data)
print(upload_response.json())

#### this end-point for company form
#### this end-point need to take job_title , job_description , cv_paths
# Match candidates

    
job_data = {
    "job_title": "Full Stack ASP.NET Developer (3+ years experience)",
    "job_description": """We are seeking an experienced Full Stack Developer with expertise in ASP.NET technologies. The ideal candidate will have:

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
    - Collaborate with cross-functional teams to deliver high-quality software solutions""",
    "cv_paths":  upload_response.json()['cv_paths'],

}
match_response = requests.post("http://localhost:8000/match-candidates", json=job_data)

print(match_response.text)