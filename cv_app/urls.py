"""
URL configuration for cv_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from cv_app.views import home
from .views import home,UserProfileView, MyTokenObtainPairView, view_company_applications, create_job, get_user_profile, register,generate_cv_feedback, user_login, user_logout, profile,post_job, job_list, apply_job, view_applications,job_applications,submit_application,register_user
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('feedback/', include('feedback.urls')),
    path('', home, name='home'),  # Add the home page route
    path('register/<str:user_type>/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),  # Add this line for profile page
    path('post-job/', post_job, name='post_job'),
    path('jobs/', job_list, name='job_list'),
    path('apply-job/<int:job_id>/', apply_job, name='apply_job'),
    path('view-applications/', view_applications, name='view_applications'),
    path('job-applications/<int:job_id>/', job_applications, name='job_applications'),
    path('api/jobs/list/', job_list, name='job_list'),
    path('api/apply/', submit_application, name='submit_application'),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', register_user, name='register_user'),
    path('api/cv-feedback/', generate_cv_feedback, name='cv_feedback'),
    path('api/jobs/', create_job, name='create_job'),
    path('api/company/applications/', view_company_applications, name='view_company_applications'),
    path('api/profile/', UserProfileView.as_view(), name='user_profile'),   
    path('api/rank-applicants/<int:job_id>/', views.rank_applicants, name='rank_applicants'),
]

# Serve media files during development
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
