from rest_framework import serializers
from .models import Job, Application, CustomUser
from rest_framework import serializers
from django.contrib.auth import get_user_model


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'created_at']

class ApplicationSerializer(serializers.ModelSerializer):
    applicant_email = serializers.SerializerMethodField()
    applicant_username = serializers.SerializerMethodField()
    cv_url = serializers.FileField(source='cv_file', read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'applicant', 'job', 'cv_file', 'cv_url', 'applied_at', 'applicant_username', 'applicant_email']
        extra_kwargs = {
            'applicant': {'read_only': True}
        }

    def get_applicant_username(self, obj):
        return obj.applicant.username
    def get_applicant_email(self, obj):
        if obj.applicant and hasattr(obj.applicant, 'email'):
            return obj.applicant.email
        return None


User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'user_type']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            user_type=validated_data.get('user_type', 'job_seeker')
        )
        return user

from rest_framework import serializers
from .models import Job, Application
from .serializers import ApplicationSerializer   # already defined above

class JobWithApplicationsSerializer(serializers.ModelSerializer):
    applications = ApplicationSerializer(many=True, read_only=True)

    class Meta:
        model  = Job
        fields = ['id', 'title', 'description', 'location',
                  'created_at', 'applications']