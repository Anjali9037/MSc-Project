from django.shortcuts import render
from .models import Post

import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect, csrf_exempt




def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

def landing_page(request):
    return render(request, 'blog/landing_page.html')


def data_addition(request):
    return render(request, 'blog/data_addition.html')



def submit_income(request):
    if request.method == 'POST':
        income_source = request.POST['income_source']
        income_amount = request.POST['income_amount']
        income_frequency = request.POST['income_frequency']
        
        # Load existing data or create a new DataFrame if the file doesn't exist
        try:
            income_df = pd.read_csv('income.csv')
        except FileNotFoundError:
            income_df = pd.DataFrame(columns=['Source', 'Amount', 'Frequency'])
        
        # Append new data to the DataFrame
        new_row = {'Source': income_source, 'Amount': income_amount, 'Frequency': income_frequency}
        income_df = income_df.append(new_row, ignore_index=True)
        
        # Save the DataFrame back to CSV
        income_df.to_csv('income.csv', index=False)
        
        return HttpResponse("Income submitted successfully!")
    else:
        return HttpResponse("Invalid request method!")

def submit_expense(request):
    if request.method == 'POST':
        expense_category = request.POST['expense_category']
        expense_amount = request.POST['expense_amount']
        expense_date = request.POST['expense_date']
        
        # Load existing data or create a new DataFrame if the file doesn't exist
        try:
            expense_df = pd.read_csv('expense.csv')
        except FileNotFoundError:
            expense_df = pd.DataFrame(columns=['Category', 'Amount', 'Date'])
        
        # Append new data to the DataFrame
        new_row = {'Category': expense_category, 'Amount': expense_amount, 'Date': expense_date}
        expense_df = expense_df.append(new_row, ignore_index=True)
        
        # Save the DataFrame back to CSV
        expense_df.to_csv('expense.csv', index=False)
        
        return HttpResponse("Expense submitted successfully!")
    else:
        return HttpResponse("Invalid request method!")
