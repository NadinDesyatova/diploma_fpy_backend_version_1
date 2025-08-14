from rest_framework import serializers
from app.models import User, File, Session


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'login', 'password', 'email', 'admin', 'files_storage_size']


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
        fields = ['login', 'password']
