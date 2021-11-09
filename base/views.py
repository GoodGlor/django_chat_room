import django.contrib.auth.models
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Topic
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import RoomForm
from django.db.models import Q


def register_page(request):
    form = UserCreationForm()
    context = {'form': form}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
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
        username = request.POST.get('username').lower()
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
    context = {'room': value}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
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
