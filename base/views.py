from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import RoomForm, MessageForm, UserForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Room, Topic, Message
from django.contrib import messages
import django.contrib.auth.models
from django.db.models import Q


def register_page(request):
    form = UserCreationForm()
    context = {'form': form}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Something is wrong')

    return render(request, 'login_page.html', context)


def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except django.contrib.auth.models.User.DoesNotExist:
            messages.error(request, 'User dose not exist')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password incorrect')
    context = {'page': page}
    return render(request, 'login_page.html', context)


def logout_page(request):
    logout(request)
    return redirect('home')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__username__icontains=q)

    )
    rooms_count = rooms.count()
    topics = Topic.objects.all()
    messages_room = Message.objects.filter(Q(room__topic__name__icontains=q))
    user = request.user
    context = {'rooms': rooms, 'topics': topics, 'rooms_count': rooms_count, 'all_messages': messages_room,
               'user': user}
    return render(request, 'base/home.html', context)


def room(request, pk):
    value = Room.objects.get(id=pk)
    room_message = value.message_set.all().order_by('-created')
    user = request.user
    participants = value.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=value,
            body=request.POST.get('body')
        )

        value.participants.add(request.user)
    context = {'room': value, 'all_messages': room_message, 'user': user, 'participants': participants}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def delete_message(request, pk):
    message_comment = Message.objects.get(id=pk)
    room_id = message_comment.room.id
    if request.user != message_comment.user:
        messages.error(request, 'Access Denied')
        return redirect('room', room_id)
    if request.method == 'POST':
        message_comment.delete()
        return redirect('room', room_id)
    return render(request, 'base/delete_room.html', {'obj': message_comment})


@login_required(login_url='login')
def update_message(request, pk):
    message_comment = Message.objects.get(id=pk)
    form = MessageForm(instance=message_comment)
    room_id = message_comment.room.id
    if request.user != message_comment.user:
        messages.error(request, 'Access Denied')
        return redirect('room', room_id)
    context = {'form': form}
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message_comment)
        if form.is_valid():
            form.save()
            return redirect('room', room_id)
    return render(request, 'base/message_form.html', context)


@login_required(login_url='login')
def create_room(request):
    form_full = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )

        return redirect('home')

    context = {'form': form_full, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    room_name = Room.objects.get(id=pk)
    form = RoomForm(instance=room_name)
    topics = Topic.objects.all()

    if request.user != room_name.host:
        messages.error(request, 'Access Denied')
        return redirect('home')
    context = {'form': form, 'topics': topics, 'room': room_name}

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room_name.name = request.POST.get('name')
        room_name.topic = topic
        room_name.description = request.POST.get('description')
        room_name.save()
        return redirect('home')
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def delete_room(request, pk):
    room_name = Room.objects.get(id=pk)
    if request.user != room_name.host:
        messages.error(request, 'Access Denied')
        return redirect('home')
    if request.method == 'POST':
        room_name.delete()
        return redirect('home')
    return render(request, 'base/delete_room.html', {'obj': room_name})


def profile_page(request, pk):
    user = User.objects.get(id=pk)
    user_rooms = user.room_set.all()
    user_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': user_rooms, 'all_messages': user_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def edit_user_page(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile_page', pk=user.id)

    context = {'form': form}
    return render(request, 'base/edit_user.html', context)
