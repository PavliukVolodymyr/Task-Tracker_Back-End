from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Board, List, Task
from django.utils import timezone



class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'participants']



class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'name', 'description', 'background_photo']



class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ['id', 'name', 'board', 'project']



class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'author', 'assignee', 'priority', 'due_date', 'completed', 'list']
          

