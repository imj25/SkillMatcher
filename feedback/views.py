import os
from django.shortcuts import render
from django.conf import settings
from .forms import CVUploadForm
from .models import CVUpload
from .utils import extract_text_from_pdf, get_cv_feedback
from PyPDF2 import PdfReader


def upload_cv(request):
    feedback = None

    if request.method == "POST":
        # Initialize the form with POST data and files
        form = CVUploadForm(request.POST, request.FILES)

        if form.is_valid():
            # Save the form to get the uploaded file
            cv_upload = form.save()
            cv_file = cv_upload.cv_file  # Get the uploaded file
            job_description = form.cleaned_data['job_description']

            try:
                # Read the PDF file content
                pdf_reader = PdfReader(cv_file)
                cv_text = " ".join(page.extract_text() for page in pdf_reader.pages)
            except Exception as e:
                cv_text = "Unable to extract text from the uploaded CV. Please upload a valid PDF."

            # Generate feedback if the CV text was extracted
            if cv_text.strip():
                feedback = get_cv_feedback(cv_text, job_description)
            else:
                feedback = "No text found in the uploaded CV. Please check the file content."
    else:
        # If not a POST request, show an empty form
        form = CVUploadForm()

    # Render the template with the form and feedback (if any)
    return render(request, "feedback/upload.html", {"form": form, "feedback": feedback})
