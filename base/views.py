import django.contrib.auth.models
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import RoomForm, MessageForm
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
    context = {'rooms': rooms, 'topics': topics, 'rooms_count': rooms_count}

    return render(request, 'base/home.html', context)


def room(request, pk):
    value = Room.objects.get(id=pk)
    room_message = value.message_set.all().order_by('-created')
    participants = value.message_set.all().values('user__username').distinct()
    # print(testtt)
    # participants = value.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=value,
            body=request.POST.get('body')
        )
        value.participants.add(request.user)
    context = {'room': value, 'room_message': room_message, 'participants': participants}
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
    return render(request, 'base/delete_rom.html', {'obj': message_comment})


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
    user_name = Room(host=request.user)

    form_full = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=user_name)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form_full}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    room_name = Room.objects.get(id=pk)
    form = RoomForm(instance=room_name)

    if request.user != room_name.host:
        messages.error(request, 'Access Denied')
        return redirect('home')
    context = {'form': form}
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room_name)
        if form.is_valid():
            form.save()
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
    return render(request, 'base/delete_rom.html', {'obj': room_name})
