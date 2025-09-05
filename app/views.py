import os
import json
import uuid
import re
from datetime import datetime, timezone

import rest_framework.exceptions
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, Http404
from django.conf import settings
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.models import User, File, Session
from app.serializers import UserSerializer, FileSerializer


# функция проверяет корректность данных пользователя или выбрасывает ошибку
def user_data_is_valid(pattern, value, error_message):
    is_valid = pattern.match(value)
    if is_valid is None:
        raise rest_framework.exceptions.ValidationError(error_message)
    return True


# функция возвращает данные о пользователе, если логин и пароль корректны, или возвращает None
def get_user_data(user_login, user_password):
    try:
        search_user = User.objects.get(login=user_login)
        is_password_valid = check_password(user_password, search_user.password)
        if is_password_valid:
            user_data = UserSerializer(search_user).data
            return user_data
        return None

    except ObjectDoesNotExist:
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
    try:
        search_session = Session.objects.get(login=user_login)
        search_session.delete()
        cookie_key = "user_session_id"
        response.delete_cookie(cookie_key)
        return response

    except ObjectDoesNotExist:
        return False


# функция возвращает имя файла и добавляет в имя файла номер копии и расширение
def get_file_name_or_name_with_postfix(user_id, filename):
    files_with_this_name = File.objects.filter(user_id=user_id, file_name=filename)
    final_file_name = filename

    if files_with_this_name:
        now = datetime.now(timezone.utc)
        formatted_date = now.strftime("%Y-%m-%d_%H_%M_%S")

        dot_index = filename.rfind('.')

        if dot_index < 0:
            final_file_name = f"{filename}_{formatted_date}"

        else:
            name = filename[:dot_index]
            extension = filename[dot_index:]
            final_file_name = f"{name}_{formatted_date}{extension}"

    return final_file_name


def change_file_field_value(instance, changing_field, new_value):
    if new_value:
        if changing_field == 'file_name':
            final_field_value = get_file_name_or_name_with_postfix(instance.user_id, new_value)
        else:
            final_field_value = new_value

        setattr(instance, changing_field, final_field_value)
        serializer = FileSerializer(instance)
        instance.save()

        content = {
            "status_code": 200,
            "status": "OK",
            "file": serializer.data
        }

    else:
        if changing_field == 'file_name':
            error_msg = "File_name is required"
        else:
            error_msg = "Comment is required"

        content = {
            "status_code": 400,
            "status": "ERROR",
            "error_message": error_msg
        }

    return Response(content)


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

            password_pattern = re.compile(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{6,}$")
            password_error_msg = ('В пароле должно быть не менее 6 символов, в том числе, не менее одной заглавной '
                                  'буквы, цифры и специального символа')

            email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
            email_error_msg = 'Введите правильный адрес электронной почты'

            login_pattern = re.compile(r"^[a-zA-Z][a-zA-Z0-9]{3,20}$")
            login_error_msg = ('Корректный логин должен состоять только из латинских букв и цифр, первый символ - '
                               'буква, длина от 4 до 20 символов')

            if (user_data_is_valid(password_pattern, password, password_error_msg)
                    and user_data_is_valid(login_pattern, login, login_error_msg)
                    and user_data_is_valid(email_pattern, email, email_error_msg)):

                user = User(
                    name=name,
                    login=login,
                    password=make_password(password),
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

        except Exception as e:
            return Response({
                "status_code": 500,
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
            file_name, user_id, comment, file_content, file_size, extension = (
                request.data["file_name"],
                request.data["user_id"],
                request.data["comment"],
                request.data["new_file"],
                request.data["file_size"],
                request.data["extension"]
            )

            final_file_name = get_file_name_or_name_with_postfix(user_id, file_name)

            now = datetime.now(timezone.utc)
            formatted_date = now.strftime("%Y-%m-%d_%H_%M_%S")
            file_path_in_user_dir = f'{formatted_date}{extension}'

            file = File(
                file_name=final_file_name,
                comment=comment,
                file_content=file_content,
                file_link="",
                file_size=file_size,
                date=now,
                file_path_in_user_dir=file_path_in_user_dir,
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
            changing_field = request.data.get('changing_field')
            new_value = request.data.get('new_value')

            return change_file_field_value(instance, changing_field, new_value)

        except Http404:
            return Response({"detail": "File is not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            file_owner = User.objects.get(id=instance.user_id)
            storage_size_of_owner = file_owner.files_storage_size
            final_storage_size = storage_size_of_owner - int(instance.file_size)
            file_owner.files_storage_size = final_storage_size
            file_owner.save()

            self.perform_destroy(instance)

        except Http404:
            return Response({"detail": "File is not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"status": "deleted"}, status=204)


# Декоратор @api_view принимает список методов HTTP, на которые должно отвечать представление.
@api_view(['PATCH'])
def get_link_for_file(request):
    try:
        file_id = request.data["file_id"]
        file_id_str = str(file_id)
        file_link = str(uuid.uuid5(uuid.NAMESPACE_URL, file_id_str))
        file_for_update = File.objects.filter(id=file_id).update(file_link=file_link)

        if file_for_update:
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
                "error_message": "Не удалось получить ссылку"
            }

        return Response(content)

    except Exception as e:
        return Response({"Error": f"{e}"}, status=500)


@api_view(['GET'])
def retrieve_by_link(request):
    try:
        file_link = request.GET.get("link")
        file_instance = File.objects.get(file_link=file_link)
        serializer = FileSerializer(file_instance)
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

        return Response({"Error_msg": "user not found"}, status=404)

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

        return Response({"Error_msg": "user not found"}, status=404)

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

        return Response({"Error_message": "user not found"}, status=404)

    except Exception as e:
        return Response({"Error": f"{e}"}, status=500)


@api_view(["POST"])
def get_user_files(request):
    try:
        user_id = request.data["user_id"]
        User.objects.get(id=user_id)
        user_files = File.objects.filter(user_id=user_id)
        user_files_data = FileSerializer(user_files, many=True).data
        return Response(user_files_data)

    except ObjectDoesNotExist:
        return Response({'error': f'User is not found'}, status=404)

    except Exception as e:
        return Response({'error': f'{e}'}, status=500)


@api_view(["POST"])
def get_users(request):
    try:
        request_from_admin = request.data["request_from_admin"]
        if request_from_admin:
            users_queryset = User.objects.all()
            users_data = UserSerializer(users_queryset, many=True).data
            return Response(users_data)

        return Response({"Error_message": "Права администратора не подтверждены"}, status=401)

    except Exception as e:
        return Response({'error': f'{e}'}, status=500)


@api_view(['PATCH'])
def download_file(request):
    try:
        user_id, file_id, is_user_files_for_admin = (
            request.data["user_id"],
            request.data["file_id"],
            request.data["is_user_files_for_admin"]
        )

        file_obj = File.objects.get(id=file_id)
        if is_user_files_for_admin or file_obj.user_id == user_id:
            file_path_in_user_dir = str(FileSerializer(file_obj).data["file_path_in_user_dir"])
            dir_name_in_media = f'user_{user_id}'
            file_path = os.path.join(settings.MEDIA_ROOT, dir_name_in_media, file_path_in_user_dir)
            print(file_path)
            if not os.path.exists(file_path):
                raise Http404("File does not exist")

            current_datetime = datetime.now(timezone.utc)
            file_obj.last_upload_date = current_datetime
            file_obj.save()

            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{file_obj.file_name}"'
                return response

        return Response({"Error_message": "Недостаточно прав"}, status=401)

    except ObjectDoesNotExist:
        raise Http404("File is not found")
