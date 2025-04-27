from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            next_url = request.GET.get('next', '/dashboard/')  # 处理next参数
            return redirect(next_url)
        else:
            return render(request,'login.html',{'error':'Invalid creder'})
    return render(request,'login.html')

@login_required
def dashboard(request):
    return render(request,'dashboard.html',{'user':request.user})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')