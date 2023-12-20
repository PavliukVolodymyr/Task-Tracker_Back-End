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