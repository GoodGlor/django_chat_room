from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import Room, Message, User


class MyUserCreationFrom(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'password1', 'password2', 'email', 'bio', 'avatar', ]


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']
