from django.db import models

class CVUpload(models.Model):
    cv_file = models.FileField(upload_to='uploads/')
    job_description = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

