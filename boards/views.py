from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project
from .serializers import ProjectSerializer
from .utils import valid_user



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

        # Перевірити, чи користувач має право редагувати цей проект
        if user != project.author:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        # Отримати дані для оновлення з запиту та частково оновити проект
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
