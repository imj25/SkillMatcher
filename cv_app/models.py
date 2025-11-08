from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('company', 'Company'),
    )
    is_job_seeker = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='job_seeker')

    company_name = models.CharField(max_length=255, blank=True, null=True)  # Only for companies
    job_title = models.CharField(max_length=255, blank=True, null=True)  # Only for job seekers

    def __str__(self):
        return self.username
    
class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='job_applications')
    cv_file = models.FileField(upload_to='cvs/', blank=True, null=True)  # Add this line
    applied_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='pending')

    def __str__(self):
        return f"{self.applicant.username} applied for {self.job.title}"
