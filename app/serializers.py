import re
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.models import User, File, Session


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'login', 'password', 'email', 'admin', 'files_storage_size']

    def validate_password(self, value):
        pattern = re.compile(r"^(?=.*\\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\\W).{6,}$")

        is_valid = pattern.match(value)
        if is_valid is None:
            raise ValidationError('В пароле должно быть не менее 6 символов, в том числе, не менее'
                                  'одной заглавной буквы, цифры и специального символа')
        return make_password(value)

    def validate_email(self, value):
        pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]\.[a-zA-Z]{2,}$")

        is_valid = pattern.match(value)
        if is_valid is None:
            raise ValidationError('Введите правильный адрес электронной почты')
        return value

    def validate_login(self, value):
        pattern = re.compile(r"^[a-zA-Z]{1}[a-zA-Z0-9]{3,20}}$")

        is_valid = pattern.match(value)
        if is_valid is None:
            raise ValidationError('Корректный логин должен состоять только из латинских букв и цифр, '
                                  'первый символ - буква, длина от 4 до 20 символов')
        return value


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            'id',
            'file_content',
            'file_name',
            'comment',
            'file_link',
            'file_size',
            'date',
            'last_upload_date',
            'user_id'
        ]


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['login']
