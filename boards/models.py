from django.db import models
from django.contrib.auth.models import User



class Project(models.Model):
    name = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_projects')
    participants = models.ManyToManyField(User, related_name='projects_participated', blank=True)

    def __str__(self):
        return f"Project: {self.name}, Author: {self.author.username}"



class Board(models.Model):
    name = models.CharField(max_length=255)
    background_photo = models.ImageField(upload_to='board_backgrounds/', null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='boards')

    def __str__(self):
        return f"Board: {self.name}, Project: {self.project.name}"
