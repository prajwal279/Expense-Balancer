from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth.models import User
from .models import Group
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import Friendship
# Create your views here.
@login_required(login_url='login')
def HomePage(request):
    return render (request,'home.html')

def SignupPage(request):
    if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')

        if pass1!=pass2:
            return HttpResponse("Your password and confrom password are not Same!!")
        else:

            my_user=User.objects.create_user(uname,email,pass1)
            my_user.save()
            return redirect('login')


    return render (request,'signup.html')

def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return HttpResponse ("Username or Password is incorrect!!!")

    return render (request,'login.html')

@login_required
def create_group(request):
    groups = request.user.group_members.all()
    friends = request.user.friends2.all()
    if request.method == 'POST':
        group_name = request.POST.get('name')
        friends = request.POST.getlist('friends')
        existing_group = Group.objects.filter(name=group_name).first()
        if existing_group:
            return HttpResponse("Group with this name already exists!")
        group = Group.objects.create(name=group_name)
        group.members.add(*friends)
        group.members.add(request.user)
        return redirect('home')
    return render(request, 'create_group.html', {'friends': friends, 'groups':groups})

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    if request.method == 'POST':
        group.delete()
        return redirect('home')

    return render(request, 'delete_group.html', {'group': group})


@login_required
def add_friend(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        friend = get_object_or_404(User, username=username)

        if request.user != friend:
            friendship_exists = Friendship.objects.filter(user1=request.user, user2=friend).exists()

            if not friendship_exists:
                Friendship.objects.create(user1=request.user, user2=friend)
                Friendship.objects.create(user1=friend, user2=request.user)

        return redirect('friend_list')
    
    friends = request.user.friends1.all()  
    print(friends)

    return render(request, 'add_friends.html', {'friends': friends})

@login_required
def friend_list(request):
    # Retrieve all friendships where the current user is involved
    friends = Friendship.objects.filter(user1=request.user) | Friendship.objects.filter(user2=request.user)
    
    # Collect all unique friend users
    friend_users = set()
    for friend in friends:
        if friend.user1 != request.user:
            friend_users.add(friend.user1)
        if friend.user2 != request.user:
            friend_users.add(friend.user2)

    return render(request, 'friend_list.html', {'friends': friend_users})


def LogoutPage(request):
    logout(request)
    return redirect('signup')