from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount_spent', 'description', 'date_incurred', 'split_method'] 

