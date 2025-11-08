# main/views.py
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import JobSeekerRegistrationForm, CompanyRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, Application
from .forms import JobPostForm, JobApplicationForm

def home(request):
    return render(request, "cv_app/home.html")

def job_seeker_register(request):
    if request.method == 'POST':
        form = JobSeekerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Change to a job seeker dashboard if needed
    else:
        form = JobSeekerRegistrationForm()
    return render(request, 'cv_app/register.html', {'form': form, 'user_type': 'Job Seeker'})

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import JobSeekerRegistrationForm, CompanyRegistrationForm

def register(request, user_type):
    if user_type == 'job_seeker':
        form_class = JobSeekerRegistrationForm
    elif user_type == 'company':
        form_class = CompanyRegistrationForm
    else:
        return redirect('home')  # Redirect to home if user_type is invalid

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to dashboard/home after registration
    else:
        form = form_class()

    return render(request, 'cv_app/register.html', {'form': form, 'user_type': user_type.capitalize()})



def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(f"Attempting to authenticate user: {username}")  # Debug print
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                print(f"User {username} authenticated successfully.")  # Debug print
                login(request, user)
                return redirect('home')  # Redirect after successful login
            else:
                print(f"Authentication failed for user: {username}")  # Debug print
                messages.error(request, "Invalid username or password.")
        else:
            print("Form errors:", form.errors)  # Debug print
    else:
        form = LoginForm()
    
    return render(request, "cv_app/login.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    context = {
        'username': request.user.username
    }
    return render(request, 'cv_app/profile.html', context)  # Make sure you have a profile.html

@login_required
def post_job(request):
    if request.user.user_type != 'company':
        return redirect('home')  # Only companies can post jobs

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            return redirect('job_list')
    else:
        form = JobPostForm()
    return render(request, 'cv_app/post_job.html', {'form': form})

def job_list(request):
    # Fetch jobs ordered by creation date (newest first)
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'cv_app/job_list.html', {'jobs': jobs})

@login_required
def apply_job(request, job_id):
    if request.user.user_type != 'job_seeker':
        return redirect('home')  # Only job seekers can apply

    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            return redirect('job_list')
    else:
        form = JobApplicationForm()
    return render(request, 'cv_app/apply_job.html', {'form': form, 'job': job})

@login_required
def view_applications(request):
    if request.user.user_type != 'company':
        return redirect('home')  # Only companies can view applications

    # Get all jobs posted by the company
    jobs = Job.objects.filter(posted_by=request.user)
    return render(request, 'cv_app/view_applications.html', {'jobs': jobs})

@login_required
def job_applications(request, job_id):
    if request.user.user_type != 'company':
        return redirect('home')  # Only companies can view applications

    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications = job.applications.all()
    return render(request, 'cv_app/job_applications.html', {'job': job, 'applications': applications})

@login_required
def apply_job(request, job_id):
    if request.user.user_type != 'job_seeker':
        return redirect('home')  # Only job seekers can apply

    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            return redirect('job_list')
    else:
        form = JobApplicationForm()
    return render(request, 'cv_app/apply_job.html', {'form': form, 'job': job})
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Job
from .serializers import JobSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from .models import Application
from .serializers import ApplicationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

@api_view(['GET'])
def job_list(request):
    jobs = Job.objects.all()
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def submit_application(request):
    serializer = ApplicationSerializer(data=request.data)

    if serializer.is_valid():
        # ✅ Pass the applicant as a keyword argument
        application = serializer.save(applicant=request.user)
        return Response(ApplicationSerializer(application).data, status=201)

    return Response(serializer.errors, status=400)



from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer

@api_view(['POST'])
def register_user(request):
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import fitz  # PyMuPDF
import openai  # Make sure this is openai==0.28 if using the classic API call syntax

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_cv_feedback(request):
    # Ensure file is present and is a PDF
    file = request.FILES.get('cv_file')  # Grab the file from the request
    if not file or not file.name.lower().endswith('.pdf'):
        return Response({'error': 'Only PDF files are supported.'}, status=400)

    # Extract text from PDF
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
    except Exception as e:
        return Response({'error': f'Error reading PDF: {str(e)}'}, status=500)

    # Check if text was extracted
    if not text.strip():
        return Response({'error': 'CV appears to be empty or unreadable.'}, status=400)

    # Prepare prompt for OpenAI
    prompt = (
        "You're an expert career advisor. Provide constructive feedback on the following CV in 150 words maximum. no lists:\n\n"
        f"{text[:3000]}"  # Trim large CVs if needed
    )

    # Generate feedback using OpenAI API
    try:
        openai.api_key = settings.OPENAI_API_KEY  # Set the API key
        response = openai.ChatCompletion.create(  # API call using the chat completion endpoint
            model="gpt-4",  # Specify the model
            messages=[{"role": "user", "content": prompt}],  # Pass the prompt in the required format
            max_tokens=800  # Limit feedback tokens
        )
        feedback = response['choices'][0]['message']['content']  # Extract the feedback text
        return Response({'feedback': feedback})
    except Exception as e:
        print("OpenAI error:", str(e))
        return Response({'error': f'OpenAI API error: {str(e)}'}, status=500)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email,
        'user_type': user.user_type
    })
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Job
from .serializers import JobSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job(request):
    user = request.user
    if not user.is_authenticated or not user.user_type == 'company':
        return Response({'error': 'Only companies can post jobs'}, status=403)

    data = request.data.copy()
    job = Job(
        title=data.get('title'),
        description=data.get('description'),
        location=data.get('location'),
        posted_by=user
    )
    job.save()
    serializer = JobSerializer(job)
    return Response(serializer.data, status=201)
# views.py
from .serializers import JobWithApplicationsSerializer  # import the new serializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_company_applications(request):
    user = request.user
    if user.user_type != 'company':
        return Response({'error': 'Only companies can view applications'}, status=403)

    jobs = Job.objects.filter(posted_by=user)
    serializer = JobWithApplicationsSerializer(jobs, many=True)
    return Response(serializer.data)


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_type'] = self.user.user_type  # 👈 Add user_type from the model
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CustomUser, Job, Application

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # For job seekers
        if user.user_type == 'job_seeker':
            # Get jobs applied by the job seeker
            applications = Application.objects.filter(applicant=user)
            applied_jobs = [
                {
                    "id": app.job.id,
                    "title": app.job.title,
                    "company": app.job.posted_by.username  # Or .email or .company_name
                }
                for app in applications
            ]


            data = {
                'name': user.username,
                'email': user.email,
                'applied_jobs': applied_jobs
            }

        # For companies
        elif user.user_type == 'company':
            # Get jobs posted by the company
            jobs = Job.objects.filter(posted_by=user)
            posted_jobs = [{"id": job.id, "title": job.title} for job in jobs]

            data = {
                'name': user.username,
                'email': user.email,
                'posted_jobs': posted_jobs
            }

        else:
            return Response({'error': 'Invalid user type'}, status=400)

        return Response(data)

import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Job, Application
from .serializers import ApplicationSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])

def rank_applicants(request, job_id):
    job = Job.objects.get(id=job_id)

    # First, upload all CVs
    upload_url = "http://127.0.0.1:8001/upload-cvs"
    upload_files = []
    for app in Application.objects.filter(job=job):
        upload_files.append(('files', open(app.cv_file.path, 'rb')))

    upload_response = requests.post(upload_url, data={'job_id': str(job_id)}, files=upload_files)

    if upload_response.status_code != 200:
        return Response({'error': 'Failed to upload CVs'}, status=500)

    cv_paths = upload_response.json()['cv_paths']

    # Now, match candidates
    match_url = "http://127.0.0.1:8001/match-candidates"
    match_payload = {
        "job_description": job.description,
        "cv_paths": cv_paths
    }

    match_response = requests.post(match_url, json=match_payload)

    if match_response.status_code == 200:
        ranked = match_response.json()['results']
        return Response({'ranked': ranked})
    else:
        return Response({'error': 'Failed to rank applicants'}, status=500)


