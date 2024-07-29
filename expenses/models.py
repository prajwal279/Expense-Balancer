from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name=models.CharField(max_length=60)
    members=models.ManyToManyField(User, related_name="group_members")

def __str__(self):
    return self.name


class Expense(models.Model):
    SPLIT_METHOD =[
        ('E','Equal'),
        ('P','Percentage'),
        ('C','Custom')
    ]
    amount_spent=models.DecimalField(max_digits=10,decimal_places=2)
    description=models.CharField(max_length=100, null=True, blank=True)
    date_incurred=models.DateField()
    paid_by=models.ForeignKey(User,on_delete=models.CASCADE)
    group=models.ForeignKey(Group,on_delete=models.CASCADE)
    split_method=models.CharField(max_length=1,choices=SPLIT_METHOD,default='E')

class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)



class Friendship(models.Model):
    user1 = models.ForeignKey(User, related_name='friends1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friends2', on_delete=models.CASCADE)
    
