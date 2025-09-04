from rest_framework import serializers

from app.models import User, File, Session


class UserSerializer(serializers.ModelSerializer):
    files = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'login', 'password', 'email', 'admin', 'files_storage_size', 'files']


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
            'user_id',
            'file_path_in_user_dir'
        ]


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['login']
