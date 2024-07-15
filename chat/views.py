from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib.auth.forms import UserCreationForm
from .forms import SimpleUserCreationForm, SimpleLoginForm
from .models import SimpleUser
from django.contrib.auth import login
from django.contrib.auth.models import User
import os

def chatPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login-user")
    context = {}
    return render(request, "chat/chatPage.html", context)

def register(request):
    if request.method == 'POST':
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            simple_user = form.save(commit=False)
            simple_user.save()
            # Django의 인증 시스템을 위한 User 객체도 생성
            user = User.objects.create_user(username=simple_user.username, password=simple_user.password)
            login(request, user)
            return redirect('chat-page')
    else:
        form = SimpleUserCreationForm()
    return render(request, 'chat/RegisterPage.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = SimpleLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                simple_user = SimpleUser.objects.get(username=username, password=password)
                user = User.objects.get(username=username)
                login(request, user)
                return redirect('chat-page')
            except SimpleUser.DoesNotExist:
                form.add_error(None, "잘못된 아이디 또는 비밀번호입니다.")
    else:
        form = SimpleLoginForm()
    return render(request, 'chat/LoginPage.html', {'form': form})

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_name = default_storage.save(file.name, file)
        file_url = default_storage.url(file_name)
        return JsonResponse({
            'status': 'success',
            'file_name': file_name,
            'file_url': file_url
        })
    return JsonResponse({'status': 'error'}, status=400)