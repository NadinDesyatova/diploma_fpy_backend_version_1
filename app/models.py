from django.db import models


def user_directory_path(instance):
    return 'user_{0}/{1}'.format(instance.user.id, instance.file_name)


class User(models.Model):
    name = models.CharField(max_length=100)
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=1000)
    email = models.CharField(max_length=100)
    admin = models.BooleanField(default=False, blank=True)
    files_storage_size = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.login


class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_content = models.FileField(upload_to=user_directory_path)
    file_name = models.CharField(max_length=255)
    file_link = models.CharField(max_length=200)
    file_size = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    last_upload_date = models.DateTimeField(blank=True)
    comment = models.CharField(max_length=300)

    def __str__(self):
        return self.file_name


class Session(models.Model):
    session_id = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login = models.CharField(max_length=100, unique=True)
