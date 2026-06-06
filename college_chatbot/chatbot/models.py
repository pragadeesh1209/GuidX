from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField(max_length=100)
    fee = models.IntegerField()
    duration = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
    name = models.CharField(max_length=100, blank=True, null=True)
    education_level = models.CharField(max_length=50, blank=True, null=True)
    ug_degree = models.CharField(max_length=100, blank=True, null=True)
    stream = models.CharField(max_length=100, blank=True, null=True)
    marks = models.FloatField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    preferences = models.TextField(blank=True, null=True)
    current_subcategory = models.CharField(max_length=100, blank=True, null=True)
    current_course_index = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Profile: {self.session_id}"

class SearchHistory(models.Model):
    profile = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='history')
    conversation_id = models.CharField(max_length=255, null=True, blank=True)
    query = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"History: {self.profile.session_id} - Conv: {self.conversation_id} at {self.timestamp}"
