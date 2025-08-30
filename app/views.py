import os
import json
import uuid
from datetime import datetime, timezone

from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, Http404
from django.conf import settings
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.models import User, File, Session
from app.serializers import UserSerializer, FileSerializer


# функция возвращает данные о пользователе, если логин и пароль корректны, или возвращает None
def get_user_data(user_login, user_password):
    search_user = User.objects.filter(login=user_login)
    user_data = UserSerializer(search_user, many=True).data
    if user_data:
        hashed_password = user_data[0]["password"]
        is_password_valid = check_password(user_password, hashed_password)
        if is_password_valid:
            return user_data[0]
        return None
    return None


# функция получает экземпляр существующей сессии или возвращает None
def get_user_session(request):
    cookie_key = "user_session_id"
    session_id = request.COOKIES.get(cookie_key, None)
    print(session_id)
    if session_id is not None:
        try:
            user_session = Session.objects.get(session_id=session_id)
            return user_session
        except ObjectDoesNotExist:
            return None
    return None


# функция возвращает данные о пользователе с открытой сессией или возвращает None
def get_user_data_with_exist_session(request):
    user_session = get_user_session(request)
    if user_session is not None:
        user = User.objects.filter(login=user_session.login)
        user_data = UserSerializer(user, many=True).data
        if user_data:
            return user_data[0]

    return None


# функция открывает сессию и возвращает объект HttpResponse
def set_session_id(status_code, user_login, user_data):
    cookie_key = "user_session_id"
    new_id = str(uuid.uuid4())
    new_session = Session(session_id=new_id, login=user_login, user_id=user_data["id"])
    new_session.save()

    json_user_data = json.dumps(user_data)
    response = HttpResponse(
        json_user_data,
        content_type="application/json",
        charset="utf-8",
        status=status_code
    )
    response.set_cookie(
        cookie_key,
        value=new_id,
        max_age=14 * 24 * 3600,
        secure=settings.SESSION_COOKIE_SECURE,
        httponly=True,
        samesite=settings.SESSION_COOKIE_SAMESITE
    )
    return response


# функция удаляет сессию
def delete_session_id(response, user_login):
    search_session = Session.objects.filter(login=user_login)
    if search_session:
        del search_session
        cookie_key = "user_session_id"
        response.delete_cookie(cookie_key)
        return response
    return False


# функция возвращает имя файла и добавляет в имя файла номер копии и расширение
def add_postfix(filename):
    dot_index = filename.rfind('.')

    if dot_index < 0:
        return f"{filename} (1)"

    name = filename[:dot_index]
    extension = filename[dot_index:]

    return f"{name} (1){extension}"


# ModelViewSet объектов User
class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            name, login, password, email = (
                request.data["name"],
                request.data["login"],
                request.data["password"],
                request.data["email"]
            )

            # В UserSerializer организована проверка email, логина и пароля. Перед сохранением
            # пароль хэшируется с помощью make_password
            user = User(
                name=name,
                login=login,
                password=password,
                email=email
            )
            user.save()

            user_data = UserSerializer(user).data
            content = {
                "status_code": 200,
                "status": "OK",
                "create_object": user_data
            }
            return Response(content)

        except ValidationError as e:
            return Response({
                "status_code": 400,
                "status": "ERROR",
                "error_message": f'{e}'}
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            request_from_admin = request.data.get('request_from_admin')
            if request_from_admin:
                instance.admin = request.data.get('new_admin_rights')
                instance.save()
                serializer = self.get_serializer(instance)
                content = {
                    "status_code": 200,
                    "status": "OK",
                    "user": serializer.data
                }
            else:
                content = {
                    "status_code": 401,
                    "status": "ERROR",
                    "error_message": "Права администратора не подтверждены"
                }

            return Response(content)

        except Http404:
            return Response({"detail": "User is not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Http404:
            return Response({"detail": "User is not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"status": "deleted"}, status=204)


# ModelViewSet объектов Files
class FilesViewSet(ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def create(self, request, *args, **kwargs):
        try:
            file_name, user_id, comment, file_content, file_size = (
                request.data["file_name"],
                request.data["user_id"],
                request.data["comment"],
                request.data["new_file"],
                request.data["file_size"]
            )

            files_with_this_name = File.objects.filter(user_id=user_id, file_name=file_name)
            final_file_name = file_name
            if files_with_this_name:
                final_file_name = add_postfix(file_name)

            file = File(
                file_name=final_file_name,
                comment=comment,
                file_content=file_content,
                file_link="",
                file_size=file_size,
                user_id=user_id
            )
            file.save()

            file_owner = User.objects.get(id=user_id)
            storage_size_of_owner = file_owner.files_storage_size
            final_storage_size = storage_size_of_owner + int(file_size)
            file_owner.files_storage_size = final_storage_size
            file_owner.save()

            file_data = FileSerializer(file).data
            content = {
                "status_code": 200,
                "status": "OK",
                "create_object": file_data
            }
            return Response(content)

        except Exception as e:
            return Response({"Error": f"{e}"}, status=500)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            file_name = request.data.get('file_name')
            if file_name is not None:
                instance.file_name = file_name
                instance.save()
                serializer = self.get_serializer(instance)
                content = {
                    "status_code": 200,
                    "status": "OK",
                    "file": serializer.data
                }
            else:
                content = {
                    "status_code": 400,
                    "status": "ERROR",
                    "error_message": "File_name is required"
                }

            return Response(content)

        except Http404:
            return Response({"detail": "File is not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)

        except Http404:
            return Response({"detail": "File is not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"status": "deleted"}, status=204)


# Декоратор @api_view принимает список методов HTTP, на которые должно отвечать представление.
@api_view(['PATCH'])
def get_link_for_file(request):
    try:
        file_id = request.data["file_id"]
        file_link = str(uuid.uuid5(uuid.NAMESPACE_URL, file_id))
        counts_update = File.objects.get(id=file_id).update(file_link=file_link)
        if counts_update:
            content = {
                "status_code": 200,
                "status": "OK",
                "file_id": file_id,
                "file_link": file_link
            }
        else:
            content = {
                "status_code": 400,
                "status": "ERROR",
                "error_message": "При обновлении возникла ошибка"
            }

        return Response(content)

    except Exception as e:
        return Response({"Error": f"{e}"}, status=500)


@api_view(['GET'])
def retrieve_by_link(self, request):
    try:
        file_link = request.GET.get("link")
        file_instance = File.objects.get(file_link=file_link)
        serializer = self.get_serializer(file_instance)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response({"Error": "File is not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"Error": f"{e}"}, status=500)


@api_view(["POST"])
def login_view(request):
    try:
        user_login, user_password = request.data["login"], request.data["password"]
        user_data = get_user_data(user_login, user_password)

        if user_data is not None:
            if Session.objects.filter(login=user_login):
                return Response({
                    "status": 401,
                    "error_message": "Пользователь уже вошел в систему"
                }, status=401)

            status_code = 200
            return set_session_id(status_code, user_login, user_data)

        return Response({"Error_msg": "user not found"})
    except Exception as e:
        return Response({"Error": f"{e}"}, status=500)


@api_view(["DELETE"])
def logout_view(request):
    try:
        user_login = request.data["login"]
        response = delete_session_id(Response({
            "status": "deleted"
        }, status=204), user_login)

        if response:
            return response

        return Response({"Error_msg": "user not found"}, status=401)

    except Exception as e:
        return Response({"Error": f"{e}"}, status=500)


@api_view(["GET"])
def get_mycloud_user(request):
    try:
        exist_session_user = get_user_data_with_exist_session(request)
        if exist_session_user is not None:
            return Response({
                "status_code": 200,
                "status": True,
                "user": exist_session_user
            })

        return Response({"Error_message": "Ошибка авторизации"}, status=401)

    except Exception as e:
        return Response({"Error": f"{e}"}, status=500)


@api_view(["POST"])
def check_session(request):
    try:
        user_login, user_password = request.data["login"], request.data["password"]
        search_session = Session.objects.filter(login=user_login)

        if search_session:
            user_data = get_user_data(user_login, user_password)
            if user_data is not None:
                return Response({
                    "status_code": 200,
                    "status": True,
                    "user": user_data
                })
            return Response({"Error_message": "Неверный логин или пароль"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"Error_message": "user not found"}, status=401)

    except Exception as e:
        return Response({"Error": f"{e}"}, status=500)


@api_view(["POST"])
def get_user_files(request):
    try:
        user_id = request.data["user_id"],
        user_files = File.objects.filter(user_id=user_id)
        user_files_data = FileSerializer(user_files, many=True).data
        return Response(user_files_data)

    except Exception as e:
        return Response({'error': f'{e}'}, status=500)


@api_view(["POST"])
def get_users(request):
    try:
        request_from_admin = request.data["request_from_admin"]
        if request_from_admin:
            user_queryset = User.objects.all()
            users_data = UserSerializer(user_queryset, many=True)
            return Response(users_data)

        return Response({"Error_message": "Права администратора не подтверждены"}, status=401)

    except Exception as e:
        return Response({'error': f'{e}'}, status=500)


@api_view(['PATCH'])
def download_file(request):
    try:
        user_id, file_id, share_file, is_user_files_for_admin = (
            request.data["user_id"],
            request.data["file_id"],
            request.data["share_file"],
            request.data["is_user_files_for_admin"]
        )
        file_obj = File.objects.get(id=file_id)
        if share_file or is_user_files_for_admin or file_obj.user_id == user_id:
            file_name_in_media = str(FileSerializer(file_obj).data["id"])
            file_path = os.path.join(settings.MEDIA_ROOT, file_name_in_media)
            print(file_path)
            if not os.path.exists(file_path):
                raise Http404("File does not exist")

            current_datetime = datetime.now(timezone.utc)
            file_obj.update(last_upload_date=current_datetime)

            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{file_obj.file_name}"'
                return response

        return Response({"Error_message": "Недостаточно прав"}, status=status.HTTP_400_BAD_REQUEST)

    except ObjectDoesNotExist:
        raise Http404("File is not found")
