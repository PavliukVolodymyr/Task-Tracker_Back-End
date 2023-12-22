from django.db import models
from django.contrib.auth.models import User



class Project(models.Model):
    name = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_projects')
    participants = models.ManyToManyField(User, related_name='projects_participated', blank=True)

    def __str__(self):
        return f"Project: {self.name}, Author: {self.author.username}"



class Board(models.Model):
    description = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255)
    background_photo = models.ImageField(upload_to='board_backgrounds/', null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='boards')

    def __str__(self):
        return f"Board: {self.name}, Project: {self.project.name}"



class List(models.Model):
    name = models.CharField(max_length=255)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='lists')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='lists')

    def save(self, *args, **kwargs):
        # Автоматично встановити проєкт дошки для списку при збереженні
        if not self.board:
            raise ValueError("List must be associated with a board.")
        if not self.project:
            self.project = self.board.project
        super().save(*args, **kwargs)

    def __str__(self):
        return f"List: {self.name}, Board: {self.board.name}, Project: {self.project.name}"



class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_tasks')
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title
