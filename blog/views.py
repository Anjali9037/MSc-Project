from django.shortcuts import render
from .models import Post

import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json
from django.http import JsonResponse




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
        income_date = request.POST['income_date']
        # Load existing data or create a new DataFrame if the file doesn't exist
        try:
            income_df = pd.read_csv('income.csv')
        except FileNotFoundError:
            income_df = pd.DataFrame(columns=['Source', 'Amount', 'Frequency','income_date'])
        
        # Append new data to the DataFrame
        new_row = {'Source': income_source, 'Amount': income_amount, 'Frequency': income_frequency, 'income_date':income_date}
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
    


    from django.shortcuts import render

def dashboard(request):

    
    income_df = pd.read_csv("income.csv")
    print(income_df)


    income_df['income_date'] = pd.to_datetime(income_df['income_date'])

    # Extract month and year from 'income_date'
    income_df['month_year'] = income_df['income_date'].dt.strftime('%B %Y')

    # Group by month and year, and calculate the sum of 'Amount'
    monthly_income = income_df.groupby('month_year')['Amount'].sum().reset_index()

    

    
    expense_df = pd.read_csv("expense.csv")
    print(expense_df)

    # Convert 'Date' column to datetime format
    expense_df['Date'] = pd.to_datetime(expense_df['Date'])

    # Extract month and year from 'Date'
    expense_df['month_year'] = expense_df['Date'].dt.strftime('%B %Y')

    # Group by month and year, and calculate the sum of 'Amount'
    monthly_expenses = expense_df.groupby('month_year')['Amount'].sum().reset_index()

    monthly_data = pd.merge(monthly_income, monthly_expenses, on='month_year', suffixes=('_income', '_expense'))
    print(monthly_data)
    monthly_data["net_savings"] = monthly_data.Amount_income - monthly_data.Amount_expense

    income_list = list(monthly_data.Amount_income)
    expense_list = list(monthly_data.Amount_expense)
    month_list = list(monthly_data.month_year)
    net_savings_list  = list(monthly_data.net_savings)

    income_list_json = json.dumps(income_list)
    expense_list_json = json.dumps(expense_list)
    month_list_json = json.dumps(month_list)
    net_savings_list_json = json.dumps(net_savings_list)

    # Group expenses by category and calculate total amount for each category
    expense_category_data = expense_df.groupby('Category')['Amount'].sum().reset_index()

    # Convert the expense category data to JSON
    expense_category_data_json = expense_category_data.to_json(orient='records')
    print(expense_category_data_json)

    # Assume functions to calculate total income, total expenses, and net savings
    # total_income = income_df.Amount.sum() 
    # total_expenses = expense_df.Amount.sum() 
    # net_savings = total_income - total_expenses
    
    # Pass the data to the template
    context = {
        'total_income': income_list[-1],
        'total_expenses': expense_list[-1],
        'net_savings': net_savings_list[-1],
        'latest_month':month_list[-1],
        'income_list':income_list_json,
        'expense_list':expense_list_json,
        'month_list':month_list_json,
        'net_savings_list':net_savings_list_json,
        'expense_category_data_json':expense_category_data_json,

        # You can add more data here as needed for charts/graphs
    }
    
    return render(request, 'blog/dashboard.html', context)

# views.py



def calculate_financial_guidance(income_df, expense_df):
    guidance_messages = []

    # Rule 1: Income vs. Expense Analysis
    total_income = income_df['Amount'].sum()
    total_expenses = expense_df['Amount'].sum()
    if total_expenses > 0.3 * total_income:
        guidance_messages.append("Your expenses are exceeding 30% of your income. Review your spending habits.")

    # Rule 2: Budgeting Tips
    if expense_df[expense_df['Category'] == 'groceries']['Amount'].sum() > 0.1 * total_income:
        guidance_messages.append("Consider allocating some of your grocery budget to savings or investments.")
    if expense_df[expense_df['Category'] == 'utilities']['Amount'].sum() > 0.15 * total_income:
        guidance_messages.append("Try reducing utility expenses by conserving energy and water.")
    if expense_df[expense_df['Category'] == 'rent']['Amount'].sum() > 0.05 * total_income:
        guidance_messages.append("Explore options to reduce rent expenses, such as negotiating with the landlord.")

    # Rule 3: Emergency Fund
    monthly_expenses = expense_df.groupby('Date')['Amount'].sum().mean()
    if not (3 * monthly_expenses <= total_income):
        guidance_messages.append("Establish an emergency fund equivalent to at least three months' worth of expenses.")

    # Rule 4: Debt Management
    high_interest_debt = expense_df[expense_df['Category'] == 'Debt']['Amount'].sum()
    if high_interest_debt > 0.2 * total_income:
        guidance_messages.append("Prioritize paying off high-interest debts to reduce financial burden.")
    
    # Rule 5: Savings and Investments
    net_savings = total_income - total_expenses
    if net_savings > 0:
        guidance_messages.append("Consider investing a portion of your savings in low-cost index funds or retirement accounts.")
    else:
        guidance_messages.append("Create a budget to track expenses closely and identify areas for potential savings.")

    # Rule 6: Financial Goals
    specific_goals = ['Buy a home', 'Save for a vacation']  # Example goals
    for goal in specific_goals:
        guidance_messages.append(f"Here are some tips to achieve your goal of '{goal}': [Tips here]")

    # Rule 7: Regular Financial Check-ins
    guidance_messages.append("Remember to review your finances regularly to track progress towards your goals.")

    return guidance_messages

def financial_guidance_view(request):
    # Load income and expense data from CSV files
    income_df = pd.read_csv('income.csv')
    expense_df = pd.read_csv('expense.csv')

    # Calculate financial guidance messages
    guidance_messages = calculate_financial_guidance(income_df, expense_df)

    # Pass guidance messages to the template for rendering
    context = {'guidance_messages': guidance_messages}
    return render(request, 'blog/financial_guidance.html', context)


def budget_setting(request):
    return render(request, 'blog/budget_setting.html')

@csrf_exempt
def save_budget(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        category = data['category']
        budget = data['budget']

        # Read existing budget data from CSV file
        try:
            budget_df = pd.read_csv('budget.csv')
        except FileNotFoundError:
            budget_df = pd.DataFrame()

        # Update budget value for the selected category
        budget_df.at[0, category] = budget

        # Write DataFrame back to CSV file
        budget_df.to_csv('budget.csv', index=False)

        return JsonResponse({'message': 'Budget saved successfully!'})

    return JsonResponse({'message': 'Invalid request method.'})