from django.urls import path
from .views import upload_cv

urlpatterns = [
    path('', upload_cv, name='upload_cv'),  # Route for uploading a CV
]
