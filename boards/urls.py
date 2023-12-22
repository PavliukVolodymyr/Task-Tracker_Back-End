from django.urls import path
from .views import ProjectListView, AddParticipantByEmailView
from .views import CreateProjectView, ProjectEditNameView
from .views import ProjectListViewId, DeleteParticipantByEmailView
from .views import CreateBoardView, BoardListView, BoardByIdView
from .views import UserProjectsView, UpdateBoard, DeleteBoardView
from .views import CreateListView, EditListNameView, DeleteListView
from .views import CreateTaskView, ListsViewBoard, ListViewId
from .views import ListTasksView, TaskDetailView, UserTasksView
from .views import UserAuthoredTasksView, CompleteTaskView
from .views import EditTaskView, DeleteTaskView, ProjectDetailView



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
    path('projects/<int:project_id>/detail/', ProjectDetailView.as_view(), name='project-detail-view'),


    # Дії над дошками
    path('projects/<int:project_id>/boards/create/', CreateBoardView.as_view(), name='create-board'),
    path('projects/<int:project_id>/boards/', BoardListView.as_view(), name='board-list'),
    path('projects/<int:project_id>/boards/<int:board_id>/', BoardByIdView.as_view(), name='board-id'),
    path('projects/<int:project_id>/boards/<int:board_id>/update/', UpdateBoard.as_view(), name='board-update'),
    # path('projects/<int:project_id>/boards/<int:board_id>/delete/', DeleteBoardView.as_view(), name='delete-board'),


    # Дії над списками
    path('projects/boards/<int:board_id>/lists/create/', CreateListView.as_view(), name='create-list'),
    path('projects/boards/lists/<int:list_id>/edit/', EditListNameView.as_view(), name='edit-list-name'),
    path('projects/boards/lists/<int:list_id>/delete/', DeleteListView.as_view(), name='delete-list'),
    path('projects/boards/<int:board_id>/lists/', ListsViewBoard.as_view(), name='board-lists'),
    path('projects/boards/lists/<int:list_id>/', ListViewId.as_view(), name='list-detail'),

    
    # Дії над тасками
    path('projects/boards/lists/<int:list_id>/tasks/create/', CreateTaskView.as_view(), name='create-task'),
    path('projects/boards/lists/<int:list_id>/tasks/', ListTasksView.as_view(), name='list-tasks'),
    path('projects/boards/lists/tasks/<int:task_id>/', TaskDetailView.as_view(), name='task-detail'),
    path('projects/boards/lists/tasks/assigned/', UserTasksView.as_view(), name='user-assigned-tasks'),
    path('projects/boards/lists/tasks/authored/', UserAuthoredTasksView.as_view(), name='user-authored-tasks'),
    path('projects/boards/lists/tasks/<int:task_id>/complete/<str:is_completed>/', CompleteTaskView.as_view(), name='complete-task'),
    path('projects/boards/lists/tasks/<int:task_id>/edit/', EditTaskView.as_view(), name='edit-task'),
    path('projects/boards/lists/tasks/<int:task_id>/delete/', DeleteTaskView.as_view(), name='delete-task'),


]