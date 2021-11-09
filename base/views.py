from django.shortcuts import render, redirect
from .models import Room, Topic
from .forms import RoomForm
from django.db.models import Q


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


def create_room(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


def update_room(request, pk):
    room_name = Room.objects.get(id=pk)
    form = RoomForm(instance=room_name)
    context = {'form': form}
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room_name)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'base/room_form.html', context)


def delete_room(request, pk):
    room_name = Room.objects.get(id=pk)
    if request.method == 'POST':
        room_name.delete()
        return redirect('home')
    return render(request, 'base/delete_rom.html', {'obj': room_name})
