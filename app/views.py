import os
import json
import uuid
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.conf import settings
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.models import User, File, Session
from app.serializers import UserSerializer, FileSerializer


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


# функция проверяет, верно ли, что запрос пришёл от пользователя с открытой сессией
def check_user_session(request):
    user_session = get_user_session(request)
    if user_session is not None:
        return True

    return False


# функция проверяет, верно ли, что запрос пришёл от админа
def check_admin_session(request):
    user_session = get_user_session(request)
    user_login = user_session.login
    try:
        user = User.objects.get(login=user_login)
        return user.admin
    except ObjectDoesNotExist:
        return False


# функция открывает сессию и возвращает response
def set_session_id(status_code, user_login, user_password, user_data):
    cookie_key = "user_session_id"
    new_id = str(uuid.uuid4())
    add_session = Session(session_id=new_id, login=user_login, password=user_password,
                          user_id=user_data[0]["id"])
    add_session.save()
    json_user_data = json.dumps(user_data[0])
    response = HttpResponse(
        json_user_data,
        content_type="application/json",
        charset="utf-8",
        status=status_code
    )
    response.set_cookie(
        cookie_key,
        value=new_id,
        max_age=14 *24 * 3600,
        secure=False,
        httponly=True,
        samesite="lax"
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


# ModelViewSet объектов Users
class UsersViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):

        if check_user_session(request) and check_admin_session(request):
            queryset = self.queryset
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)

        return Response({"Error_message": "Ошибка авторизации"}, status=401)

    def create(self, request, *args, **kwargs):
        try:
            name, login, password, email = (
                request.data["name"],
                request.data["login"],
                request.data["password"],
                request.data["email"]
            )
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
        except Http404:
            return Response({"detail": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):

        if check_user_session(request) and check_admin_session(request):
            instance = self.get_object()
            instance.admin = request.data.get('admin')
            instance.save()
            serializer = self.get_serializer(instance)
            return Response({
                "status_code": 200,
                "user": serializer.data
            })
        return Response({"Error_message": "Ошибка авторизации"}, status=401)

    def destroy(self, request, *args, **kwargs):

        if check_user_session(request) and check_admin_session(request):
            try:
                instance = self.get_object()
                self.perform_destroy(instance)
            except Http404:
                return Response({"detail": "User is not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"Error_message": "Ошибка авторизации"}, status=401)


# ModelViewSet объектов Files
class FilesViewSet(ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def create(self, request, *args, **kwargs):

        if check_user_session(request):
            file_name, user_id, comment, file_content, file_size = (
                request.data["file_name"],
                request.data["user_id"],
                request.data["comment"],
                request.data["new_file"],
                request.data["file_size"]
            )

            files_with_this_name = File.objects.filter(file_name=file_name) & File.objects.filter(user_id=user_id)
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
            file_owner.update(files_storage_size=final_storage_size)

            file_data = FileSerializer(file).data
            content = {
                "status_code": 200,
                "status": "OK",
                "create_object": file_data
            }
            return Response(content)

        return Response({"Error_message": "Ошибка авторизации"}, status=401)

    def update(self, request, *args, **kwargs):

        if check_user_session(request):
            instance = self.get_object()
            file_name = request.data.get('file_name')
            if file_name is not None:
                instance.file_name = file_name
                instance.save()
                serializer = self.get_serializer(instance)
                return Response({
                    "status_code": 200,
                    "file": serializer.data
                })

            return Response({"detail": "file_name is required."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"Error_message": "Ошибка авторизации"}, status=401)

    def destroy(self, request, *args, **kwargs):

        if check_user_session(request):

            try:
                instance = self.get_object()
                self.perform_destroy(instance)
            except Http404:
                return Response({"detail": "File is not found"}, status=status.HTTP_404_NOT_FOUND)

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"Error_message": "Ошибка авторизации"}, status=401)

    def retrieve_by_link(self, request):

        if check_user_session(request):

            try:
                file_link = request.GET.get("link")
                file_instance = File.objects.get(file_link=file_link)
                serializer = self.get_serializer(file_instance)
                return Response(serializer.data)
            except ObjectDoesNotExist:
                return Response({'error': 'File is not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({"Error_message": "Ошибка авторизации"}, status=401)


# Декоратор @api_view принимает список методов HTTP, на которые должно отвечать представление.
@api_view(['GET'])
def get_link_for_file(request, file_id):
    if check_user_session(request):
        print(request.COOKIES.get("user_session_id", "None"))
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

    return Response({"Error_message": "Ошибка авторизации"}, status=401)


@api_view(["POST"])
def login_view(request):
    try:
        user_login, user_password = request.data["login"], request.data["password"]
        search_user = User.objects.filter(login=user_login, password=user_password)
        user_data = UserSerializer(search_user, many=True).data

        if user_data:
            if Session.objects.filter(login=user_login):
                return Response({
                    "status": 401,
                    "error_message": "Пользователь уже вошел в систему"
                }, status=401)

            status_code = 200

            return set_session_id(status_code, user_login, user_password, user_data)

        return Response({"error_msg": "user not found"})
    except Exception as e:
        return Response({"error": f'{e}'}, status=500)


@api_view(["DELETE"])
def logout_view(request):
    try:
        user_login = request.data["login"]
        response = delete_session_id(Response({
            "status": "deleted"
        }, status=204), user_login)

        if response:
            return response

        return Response({"error_msg": "user not found"}, status=401)

    except Exception as e:
        return Response({"error": f'{e}'}, status=500)


@api_view(["POST"])
def check_session(request):
    try:
        user_login, user_password = request.data["login"], request.data["password"]
        search_session = Session.objects.filter(login=user_login, password=user_password)
        if search_session:
            search_user_data = UserSerializer(User.objects.filter(login=user_login), many=True).data
            return Response({
                "status_code": 200,
                "status": True,
                "user": search_user_data
            })

        return Response({"error_message": "user not found"}, status=401)
    except Exception as e:
        return Response({'error': f'{e}'}, status=500)


@api_view(["GET"])
def get_user_files(request, user_id):
    # print(request.COOKIES.get("user_session_id", "None"))
    if check_user_session(request):
        # print(request.COOKIES.get("user_session_id", "None"))
        user_files = File.objects.filter(user_id=user_id)
        user_files_data = FileSerializer(user_files, many=True).data
        return Response(user_files_data)

    return Response({"Error_message": "Ошибка авторизации"}, status=401)


@api_view(['GET'])
def download_file(request, file_id):
    if check_user_session(request):
        try:
            file_obj = File.objects.get(id=file_id)
            file_name_in_media = str(FileSerializer(file_obj).data["id"])
            file_path = os.path.join(settings.MEDIA_ROOT, file_name_in_media)
            print(file_path)
            if not os.path.exists(file_path):
                raise Http404("File does not exist")

            current_datetime = datetime.datetime.utcnow()
            file_obj.update(last_upload_date=current_datetime)

            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{file_obj.file_name}"'
                return response

        except ObjectDoesNotExist:
            raise Http404("File is not found")

    return Response({"Error_message": "Ошибка авторизации"}, status=401)
