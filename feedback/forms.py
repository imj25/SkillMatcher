from django import forms
from .models import CVUpload

class CVUploadForm(forms.ModelForm):
    class Meta:
        model = CVUpload
        fields = ['cv_file', 'job_description']
