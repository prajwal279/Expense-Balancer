from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth.models import User
from .models import Group,Expense,ExpenseSplit
from .forms import ExpenseForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import Friendship

@login_required(login_url='login')
def HomePage(request):
    groups = request.user.group_members.all()
    context = {}
    context['groups'] = groups
    view_group_id = request.GET.get("group_id")
    context['view_group_id'] = view_group_id
    return render (request,'home.html',context)

def SignupPage(request):
    if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')

        if pass1!=pass2:
            return HttpResponse("Password mismatch!!!")
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

def LogoutPage(request):
    logout(request)
    return redirect('login')

@login_required
def add_friend(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        friend = User.objects.get(username=username)
        if request.user != friend:
            friendship_exists = Friendship.objects.filter(user1=request.user, user2=friend).exists()
            # if friendship_exists:
            #     return HttpResponse("No such friend exists!")                                                                            
            if not friendship_exists:
                Friendship.objects.create(user1=request.user, user2=friend)
                Friendship.objects.create(user1=friend, user2=request.user)
        return redirect('friend_list')
    
    friends = request.user.friends1.all()  
   
    return render(request, 'add_friends.html', {'friends': friends})
     
@login_required
def friend_list(request):
    friends = Friendship.objects.filter(user2=request.user)
    friend_users = set()
    for friend in friends:
        if friend.user1 != request.user:
            friend_users.add(friend.user1)
    return render(request, 'friend_list.html', {'friends': friend_users})

@login_required
def create_group(request):
    groups = request.user.group_members.all()
    friends = request.user.friends2.all()
    if request.method == 'POST':
        group_name = request.POST.get('name')
        friends = request.POST.getlist('friends')
        existing_group = Group.objects.filter(name=group_name).exists()
        if existing_group:
            return HttpResponse("Group with this name already exists!")
        group = Group.objects.create(name=group_name)
        group.members.add(*friends)
        group.members.add(request.user)
        return redirect('home')
    view_group_id = request.GET.get("view_group_id")
    return render(request, 'create_group.html', {'friends': friends, 'groups':groups,'view_group_id':view_group_id})

@login_required
def view_group(request):
    groups = request.user.group_members.all()
    friends = request.user.friends2.all()
    if request.method == 'POST':
        group_name = request.POST.get('name')
        friends = request.POST.getlist('friends')
        existing_group = Group.objects.filter(name=group_name).exists()
        if existing_group:
            return HttpResponse("Group name already exists!")
        group = Group.objects.create(name=group_name)
        group.members.add(*friends)
        group.members.add(request.user)
        return redirect('home')
    view_group_id = request.GET.get("view_group_id")
    return render(request, 'view_group.html', {'friends': friends, 'groups':groups,'view_group_id':view_group_id})

@login_required
def delete_friend(request,friend_id):
    friend = User.objects.get(id=friend_id)
    friendshipobject=get_object_or_404(Friendship,user1=request.user,user2=friend)
    friendshipobject2=get_object_or_404(Friendship,user2=request.user,user1=friend)
    if request.method =='POST':
        friendshipobject.delete()
        friendshipobject2.delete()
        return redirect('friend_list')
    return render(request,'delete_friend.html',{'friend':friend})

@login_required 
def delete_group(request,group_id):
    group = get_object_or_404(Group, pk=group_id)
    if request.method == 'POST':
        group.delete()
        return redirect('create_group')
    return render(request, 'delete_group.html', {'group': group})

@login_required
def edit_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    friends = request.user.friends2.all()  
    group_members = group.members.all()    
    if request.method == 'POST':
        group_name = request.POST.get('name')
        if group_name != group.name:
            existing_group = Group.objects.filter(name=group_name).exists()
            if existing_group:
                return HttpResponse("Group with this name already exists!")
            group.name = group_name
            group.save()
        new_members = request.POST.getlist('friends')
        new_members.append(request.user)
        group.members.set(new_members)
        return redirect('create_group')
    return render(request, 'edit_group.html', {'group': group, 'friends': friends, 'group_members': group_members})

@login_required
def create_expense(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    context = {}
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.paid_by = request.user
            expense.save()
            context = {'group':group,'expense':expense}
            users = group.members.all()
            if expense.split_method == 'E':
                context['equals'] = True
                T_amount = expense.amount_spent / users.count()
                context['amount']=T_amount
                context['next']=True
                context['form']=form
                for user in users:
                    ExpenseSplit.objects.create(expense=expense, user=user, amount=T_amount)
            elif expense.split_method == 'P':
                context['percentage'] = True
                context['next']=True
                context['expense'] = expense
                context['form']=form
            elif expense.split_method == 'C':
                context['custom'] = True
                context['next']=True
                context['form']=form
            return render(request, 'create_expense.html', context)
        if request.POST.get('expense_id') and request.POST.get('p_flag'):
            expense = Expense.objects.get(id=request.POST.get('expense_id'))
            form = ExpenseForm()
            context['form']=form
            for key, value in request.POST.items():
                split = ExpenseSplit()
                if "percentage" in key:
                    user_id = int(key[11:])
                    user = User.objects.get(id=user_id)
                    split.user = user
                    split.amount = (float(value)/100) * float(expense.amount_spent)
                    split.expense = expense
                    split.save()
        if request.POST.get('expense_id') and request.POST.get('c_flag'):
            expense = Expense.objects.get(id=request.POST.get('expense_id'))
            form = ExpenseForm()
            context['form']=form
            for key, value in request.POST.items():
                split = ExpenseSplit()
                if "percentage" in key:
                    user_id = int(key[11:])
                    user = User.objects.get(id=user_id)
                    split.user = user
                    split.amount = float(value)
                    split.expense = expense
                    split.save()
    else:
        form = ExpenseForm()
    return render(request, 'create_expense.html', {'form': form, 'group': group})

@login_required
def split_expense(request):
    groups = request.user.group_members.all()
    friends = request.user.friends2.all()
    return render(request, 'split_expense.html', {'friends': friends, 'groups':groups})



def show_expense(request):
    splits = ExpenseSplit.objects.filter(user=request.user)
    return render(request, 'equal_expense.html', {'splits':splits})

