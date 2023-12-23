from django.contrib import admin
from .models import Project, Board, List, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',)
    search_fields = ('name', 'author__username',)
    filter_horizontal = ('participants',)

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'project',)
    search_fields = ('name', 'project__name',)

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('name', 'board', 'project',)
    search_fields = ('name', 'board__name', 'project__name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'assignee', 'priority', 'due_date', 'completed',)
    search_fields = ('title', 'author__username', 'assignee__username',)
    list_filter = ('priority', 'due_date', 'completed',)
