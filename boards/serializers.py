from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Board


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'participants']



class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'name', 'background_photo']
