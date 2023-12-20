from django.urls import path
from .views import ProjectListView, AddParticipantByEmailView
from .views import CreateProjectView, ProjectEditNameView
from .views import ProjectListViewId, DeleteParticipantByEmailView
from .views import CreateBoardView, BoardListView, BoardByIdView
from .views import UserProjectsView, UpdateBoard, DeleteBoardView
from .views import CreateListView, EditListNameView


urlpatterns = [
    # Дії над проєктами
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
    path('projects/user', UserProjectsView.as_view(), name='user-projects'),

    # Дії над дошками
    path('projects/<int:project_id>/boards/create/', CreateBoardView.as_view(), name='create-board'),
    path('projects/<int:project_id>/boards/', BoardListView.as_view(), name='board-list'),
    path('projects/<int:project_id>/boards/<int:board_id>/', BoardByIdView.as_view(), name='board-id'),
    path('projects/<int:project_id>/boards/<int:board_id>/update/', UpdateBoard.as_view(), name='board-update'),
    # path('projects/<int:project_id>/boards/<int:board_id>/delete/', DeleteBoardView.as_view(), name='delete-board'),

    # Дії над списками
    path('projects/boards/<int:board_id>/lists/create/', CreateListView.as_view(), name='create-list'),
    path('projects/boards/lists/<int:list_id>/edit/', EditListNameView.as_view(), name='edit-list-name'),


]