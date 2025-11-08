import os
import PyPDF2
import openai  # Corrected the import for openai

# Set the API key
openai.api_key = os.environ.get("OPENAI_API_KEY")  # Use environment variable to get API key

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def get_cv_feedback(cv_text, job_description):
    try:
        # Create a prompt for ChatGPT
        prompt = (
            f"Provide a concise and actionable summary (75ish words maximum, no lists) of feedback on how to improve the following CV "
            f"to better fit the job description. Focus on missing skills, experiences, and formatting improvements. Make some remarks about the uploaded document, for example, 'I see you majored in x and have some experience in y'.\n\n"
            f"CV:\n{cv_text}\n\n"
            f"Job Description:\n{job_description}\n\n"
            f"Feedback:"
        )

        # Send the prompt to ChatGPT
        response = openai.ChatCompletion.create(  # Correct API method
            model="gpt-3.5-turbo",  # You can use "gpt-4" for better quality
            messages=[
                {"role": "system", "content": "You are a helpful career advisor."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the assistant's reply
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"An error occurred: {e}"
