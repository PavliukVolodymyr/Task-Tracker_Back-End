from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Board, List, Task
from .serializers import ProjectSerializer, BoardSerializer
from .serializers import ListSerializer, TaskSerializer
from .utils import valid_user
from django.shortcuts import get_object_or_404
from accounts.models import EmailVerification
from django.contrib.auth.models import User
from django.http import Http404
from django.db.models import Q
from django.db import models
from django.utils import timezone
from datetime import datetime




class CreateProjectView(APIView):
    def post(self, request):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)
        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати дані для нового проекту з запиту
        project_data = request.data.get('project_data', {})

        # Додати користувача як автора проекту
        project_data['author'] = user.id
        project_data['participants'] = [user.id]

        # Створити серіалізатор для зберігання даних проекту
        serializer = ProjectSerializer(data=project_data)

        if serializer.is_valid():
            # Зберегти проект у базі даних
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProjectListView(APIView):
    def get(self, request):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)
        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати всі проекти та серіалізувати їх
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



class ProjectEditNameView(APIView):
    def patch(self, request, project_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)
        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати проект за ідентифікатором
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Перевірити чи користувач має право редагувати цей проект
        if user != project.author:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Отримати дані для оновлення з запиту та частково оновити проект
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AddParticipantByEmailView(APIView):

    def post(self, request, project_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = user.id

        # Перевірити чи користувач є автором проекту
        try:
            project = Project.objects.get(author_id=user_id, pk=project_id)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found for the author.'}, status=status.HTTP_404_NOT_FOUND)

        # Знайти запис про верифікацію по емейлу
        email = request.data.get('email', '')

        try:
            email_verification = EmailVerification.objects.get(email=email, is_verified=True)
            participant = email_verification.user
        except EmailVerification.DoesNotExist:
            return Response({'detail': 'Email not found or not verified.'}, status=status.HTTP_404_NOT_FOUND)

        project.participants.add(participant)
        return Response({'detail': 'Participant added successfully.'}, status=status.HTTP_200_OK)



class DeleteParticipantByEmailView(APIView):

    def delete(self, request, project_id, participant_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = user.id

        # Перевірити чи користувач є автором проекту
        try:
            project = Project.objects.get(author_id=user_id, pk=project_id)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found for the author.'}, status=status.HTTP_404_NOT_FOUND)

        # Знайти учасника за його ідентифікатором
        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            raise Http404

        # Перевірити чи учасник є членом проекту
        if participant not in project.participants.all():
            return Response({'detail': 'Participant not found in the project.'}, status=status.HTTP_404_NOT_FOUND)

        # Видалити учасника з проекту
        project.participants.remove(participant)
        return Response({'detail': 'Participant removed successfully.'}, status=status.HTTP_200_OK)



class ProjectListViewId(APIView):

    def get(self, request, pk):

        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UserProjectsView(APIView):

    def get(self, request):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати всі проекти, де користувач є членом чи автором
        projects = Project.objects.filter(models.Q(author=user) | models.Q(participants=user)).distinct()

        # Здійснити серіалізацію та повернути дані проектів
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class CreateBoardView(APIView):

    def post(self, request, project_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = user.id

        # Перевірити, чи користувач є автором проекту
        try:
            project = Project.objects.get(author_id=user_id, pk=project_id)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found for the author.'}, status=status.HTTP_404_NOT_FOUND)

        # Створити дошку
        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project_id=project_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BoardListView(APIView):

    def get(self, request, project_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Ваша функція/код перевірки та отримання користувача за токеном
        user = valid_user(access_token_str)

        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати проект за ідентифікатором
        project = get_object_or_404(Project, pk=project_id)

        # Перевірити, чи користувач має доступ до цього проекту (автор чи член проекту)
        if user.id != project.author.id and user not in project.participants.all():
                return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Отримати список дошок для цього проекту
        boards = Board.objects.filter(project=project)

        # Серіалізувати та повернути дані
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class BoardByIdView(APIView):

    def get(self, request, project_id, board_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати проект за ідентифікатором
        project = get_object_or_404(Project, pk=project_id)

        # Перевірити, чи користувач має доступ до цього проекту (автор чи член проекту)
        if user.id != project.author.id and user not in project.participants.all():
                return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Знайти дошку за ідентифікатором у межах проекту
        try:
            board = Board.objects.get(project_id=project_id, id=board_id)
        except Board.DoesNotExist:
            return Response({'detail': 'Board not found for the project.'}, status=status.HTTP_404_NOT_FOUND)

        # Здійснити серіалізацію та повернути дані дошки
        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UpdateBoard(APIView):

    def patch(self, request, project_id, board_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Перевірити чи користувач має доступ до цього проекту (автор чи член проекту)
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user.id != project.author.id:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Отримати дошку
        board = get_object_or_404(Board, id=board_id, project=project)

        # Отримати дані для оновлення з запиту та частково оновити дошку
        serializer = BoardSerializer(board, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DeleteBoardView(APIView):

    def delete(self, request, project_id, board_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = user.id

        # Перевірити чи користувач є автором дошки
        board = get_object_or_404(Board, id=board_id, project_id=project_id)

        if user_id != board.project.author.id:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Видалити дошку
        board.delete()

        return Response({'detail': 'Board deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)



class CreateListView(APIView):

    def post(self, request, board_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати дошку за ідентифікатором
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            return Response({'detail': 'Board not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Отримати проєкт, до якого належить дошка
        project = board.project

        # Перевірити чи користувач є автором або членом проєкту
        if user.id != project.author.id and user not in project.participants.all():
                return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Отримати дані для створення списку з тіла запиту
        list_data = request.data
        list_data['board'] = board.id
        list_data['project'] = project.id

        # Створити новий список
        serializer = ListSerializer(data=list_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ListsViewBoard(APIView):

    def get(self, request, board_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Ваша функція/код перевірки та отримання користувача за токеном
        user = valid_user(access_token_str)

        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати дошку за ідентифікатором
        board = get_object_or_404(Board, pk=board_id)

        # Отримати проєкт дошки
        project = board.project

        # Перевірити, чи користувач має доступ до цього проекту (автор чи член проекту)
        if user.id != project.author.id and user not in project.participants.all():
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Отримати всі списки дошки
        lists = List.objects.filter(board=board)

        # Серіалізувати та повернути дані
        serializer = ListSerializer(lists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ListViewId(APIView):

    def get(self, request, list_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Ваша функція/код перевірки та отримання користувача за токеном
        user = valid_user(access_token_str)

        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати список за ідентифікатором
        list_instance = get_object_or_404(List, pk=list_id)

        # Отримати дошку та проєкт для цього списку
        board = list_instance.board
        project = list_instance.project

        # Перевірити, чи користувач має доступ до цього проекту (автор чи член проекту)
        if user.id != project.author.id and user not in project.participants.all():
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Серіалізувати та повернути дані
        serializer = ListSerializer(list_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)



class EditListNameView(APIView):

    def patch(self, request, list_id):
        # Отримати токен із запиту та перевірити валідність користувача
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]
        user = valid_user(access_token_str)
        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Знайти список за ідентифікатором
        list_instance = get_object_or_404(List, id=list_id)

        project = list_instance.project

        # Перевірити чи користувач є автором або членом проєкту
        if user.id != project.author.id and user not in project.participants.all():
                return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)


        # Отримати нову назву списку з тіла запиту
        new_name = request.data.get('name', '')

        # Змінити назву та зберегти список
        list_instance.name = new_name
        list_instance.save()

        # Серіалізувати та повернути відповідь
        serializer = ListSerializer(list_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)



class DeleteListView(APIView):

    def delete(self, request, list_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати список за ідентифікатором
        try:
            list_to_delete = List.objects.get(pk=list_id)
        except List.DoesNotExist:
            return Response({'detail': 'List not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Отримати проєкт, до якого належить список
        project = list_to_delete.project

        # Перевірити чи користувач є автором списку або автором проєкту
        if user.id != project.author.id:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Видалити список та пов'язані таски
        list_to_delete.delete()

        return Response({'detail': 'List deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)



class CreateTaskView(APIView):

    def post(self, request, list_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати список за ідентифікатором
        try:
            task_list = List.objects.get(pk=list_id)
        except List.DoesNotExist:
            return Response({'detail': 'List not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Отримати проєкт до якого належить список
        project = task_list.project

        # Перевірити чи користувач є автором або членом проєкту
        if user.id != project.author.id and user not in project.participants.all():
                return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)


        # Отримати дані для створення таски з тіла запиту
        task_data = request.data
        task_data['list'] = task_list.id
        task_data['author'] = user.id
        
        # Перевірити чи вказаний виконавець є членом проекту або списку
        assignee_id = task_data.get('assignee')
        if assignee_id:
            try:
                assignee = User.objects.get(pk=assignee_id)
                if assignee not in project.participants.all() and assignee not in project.participants.all():
                    return Response({'detail': 'Assignee must be a member of the project or list.'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'detail': 'Assignee not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Перевірити чи дата виконання є в майбутньому
        due_date_str = task_data.get('due_date')
        if due_date_str:
            due_date = datetime.fromisoformat(due_date_str)
            due_date = timezone.make_aware(due_date)  # Зробити offset-aware
            if due_date <= timezone.now():
                return Response({'detail': 'Due date must be in the future.'}, status=status.HTTP_400_BAD_REQUEST)  
        
        # Створити нову таску
        serializer = TaskSerializer(data=task_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ListTasksView(APIView):

    def get(self, request, list_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        user = valid_user(access_token_str)

        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати список за ідентифікатором
        task_list = get_object_or_404(List, pk=list_id)

        # Отримати проєкт до якого належить список
        project = task_list.project

        # Перевірити чи користувач має доступ до цього проекту 
        if user.id != project.author.id and user not in project.participants.all():
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Отримати всі таски для цього списку
        tasks = Task.objects.filter(list=task_list)

        # Серіалізувати та повернути дані
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class TaskDetailView(APIView):

    def get(self, request, task_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        user = valid_user(access_token_str)

        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати таску за ідентифікатором
        task_instance = get_object_or_404(Task, pk=task_id)

        # Отримати список та проєкт для цієї таски
        task_list = task_instance.list
        project = task_list.project

        # Перевірити чи користувач має доступ до цього проекту (автор чи член проекту)
        if user.id != project.author.id and user not in project.participants.all():
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Серіалізувати та повернути дані
        serializer = TaskSerializer(task_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UserTasksView(APIView):

    def get(self, request):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        user = valid_user(access_token_str)

        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати всі таски де користувач є виконавцем
        tasks = Task.objects.filter(assignee=user)

        # Серіалізувати та повернути дані
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UserAuthoredTasksView(APIView):

    def get(self, request):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        user = valid_user(access_token_str)

        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати всі таски, де користувач є автором
        tasks = Task.objects.filter(author=user)

        # Серіалізувати та повернути дані
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class CompleteTaskView(APIView):

    def put(self, request, task_id, is_completed):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати завдання за ідентифікатором
        task = get_object_or_404(Task, pk=task_id)

        # Перевірити чи користувач є автором або виконавцем завдання
        if user.id != task.author.id and user.id != task.assignee.id:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Оновити статус завдання
        task.completed = is_completed
        task.save()

        # Серіалізувати та повернути дані
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)



class EditTaskView(APIView):

    def put(self, request, task_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати таску за ідентифікатором
        task = get_object_or_404(Task, pk=task_id)

        # Перевірити чи користувач є автором таски
        if user.id != task.author.id:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Отримати дані для редагування таски з тіла запиту
        task_data = request.data

        # Серіалізувати та оновити таску
        serializer = TaskSerializer(task, data=task_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DeleteTaskView(APIView):

    def delete(self, request, task_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        # Перевірити валідність та отримати користувача
        user = valid_user(access_token_str)

        if user is None:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати таску за ідентифікатором
        task = get_object_or_404(Task, pk=task_id)

        # Перевірити чи користувач є автором таски
        if user.id != task.author.id:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Видалити таску
        task.delete()

        return Response({'detail': 'Task successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)



class ProjectDetailView(APIView):

    def get(self, request, project_id):
        # Отримати токен із запиту
        access_token_str = request.headers.get('Authorization', '').split(' ')[1]

        user = valid_user(access_token_str)

        if not user:
            return Response({'detail': 'Invalid access token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Отримати проєкт за ідентифікатором
        project = get_object_or_404(Project, pk=project_id)

        # Перевірити чи користувач є автором чи членом проєкту
        if user.id != project.author.id and user not in project.participants.all():
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Серіалізувати дані проєкту
        project_serializer = ProjectSerializer(project).data

        # Отримати дошки для цього проєкту
        boards = Board.objects.filter(project=project)
        board_serializer = BoardSerializer(boards, many=True).data

        # Отримати списки для цих дошок
        lists = List.objects.filter(board__in=boards)
        list_serializer = ListSerializer(lists, many=True).data

        # Отримати таски для цих списків
        tasks = Task.objects.filter(list__in=lists)
        task_serializer = TaskSerializer(tasks, many=True).data

        # Повернути дані у вигляді відповіді
        response_data = {
            'project': project_serializer,
            'boards': board_serializer,
            'lists': list_serializer,
            'tasks': task_serializer,
        }

        return Response(response_data, status=status.HTTP_200_OK)
