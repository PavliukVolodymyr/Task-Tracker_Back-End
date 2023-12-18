from django.urls import path
from .views import ProjectListView, AddParticipantByEmailView
from .views import CreateProjectView, ProjectEditNameView
from .views import ProjectListViewId, DeleteParticipantByEmailView


urlpatterns = [
    path('projects/create/', CreateProjectView.as_view(), name='create-project'),
    path('projects/<int:pk>', ProjectListViewId.as_view(), name='project-list-id'),
    path('projects/userProjects/', ProjectListView.as_view(), name='project-list'),
    path('projects/edit/<int:project_id>/name/', ProjectEditNameView.as_view(), 
                                                    name='project-detail'),
    path('projects/participant/add/<int:project_id>', AddParticipantByEmailView.as_view(), 
                                                    name='add-participant-to-project'),
    path('projects/<int:project_id>/participants/<int:participant_id>/', 
                                                    DeleteParticipantByEmailView.as_view(),
                                                    name='delete-participant'),
]