from django.urls import path
from .views import ProjectListView 
from .views import CreateProjectView, ProjectEditNameView


urlpatterns = [
    path('projects/create/', CreateProjectView.as_view(), name='create-project'),
    path('projects/userProjects/', ProjectListView.as_view(), name='project-list'),
    path('projects/edit/<int:project_id>/name', ProjectEditNameView.as_view(), name='project-detail'),
]