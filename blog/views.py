from django.shortcuts import render
from .models import Post

import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json
from django.http import JsonResponse

from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client

# Your Twilio Account SID and Auth Token
account_sid = 'ACdae963df4752fa397fd157c06d4fee47'
auth_token = 'ec84d8890dcfca2518cb9b5849b5890d'
# Create a Twilio client
client = Client(account_sid, auth_token)




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
        expense_percentage = (total_expenses / total_income) * 100
        guidance_messages.append(f"Your expenses are exceeding 30% of your income. Current expense percentage: {expense_percentage:.2f}%. Consider reviewing your spending habits.")

    # Rule 2: Budgeting Tips
    categories = ['groceries', 'utilities', 'rent', 'Debt']  # Example categories
    for category in categories:
        category_expense = expense_df[expense_df['Category'] == category]['Amount'].sum()
        if category_expense > 0.1 * total_income:
            expense_percentage = (category_expense / total_income) * 100
            guidance_messages.append(f"Your {category} expenses are {expense_percentage:.2f}% of your total income. Consider adjusting your budget accordingly.")

    # Rule 3: Emergency Fund
    monthly_expenses = expense_df.groupby('Date')['Amount'].sum().mean()
    if not (3 * monthly_expenses <= total_income):
        guidance_messages.append("Establish an emergency fund equivalent to at least three months' worth of expenses.")

    # Rule 4: Debt Management
    high_interest_debt = expense_df[expense_df['Category'] == 'Debt']['Amount'].sum()
    if high_interest_debt > 0.2 * total_income:
        debt_percentage = (high_interest_debt / total_income) * 100
        guidance_messages.append(f"Your high-interest debt constitutes {debt_percentage:.2f}% of your total income. Prioritize paying it off to improve your financial health.")

    # Rule 5: Savings and Investments
    net_savings = total_income - total_expenses
    if net_savings > 0:
        guidance_messages.append("Consider investing a portion of your savings in low-cost index funds or retirement accounts to grow your wealth.")
    else:
        guidance_messages.append("Create a budget to track expenses closely and identify areas for potential savings to improve your financial situation.")

    # Additional Insights
    savings_rate = (net_savings / total_income) * 100
    guidance_messages.append(f"Your current savings rate is {savings_rate:.2f}%. Aim to increase this rate to build a more secure financial future.")

    expense_distribution = expense_df.groupby('Category')['Amount'].sum() / total_expenses * 100
    guidance_messages.append(f"Your expense distribution across categories: {expense_distribution.to_dict()}. Identify categories where you can potentially reduce spending to allocate more towards savings and investments.")

    income_stability = income_df['Amount'].std() / income_df['Amount'].mean() * 100
    if income_stability > 20:
        guidance_messages.append("Your income shows significant variability, which may make budgeting challenging. Consider exploring additional income sources or creating a more robust budgeting strategy.")
    else:
        guidance_messages.append("Your income stability is relatively consistent, providing a stable foundation for financial planning.")

    expense_variability = expense_df['Amount'].std() / expense_df['Amount'].mean() * 100
    if expense_variability > 20:
        guidance_messages.append("Your expenses exhibit significant variability, indicating potential challenges in budgeting and financial planning. Look for ways to stabilize your spending habits.")
    else:
        guidance_messages.append("Your expenses show relatively low variability, which can facilitate effective budgeting and financial planning.")

    debt_to_income_ratio = (high_interest_debt / total_income) * 100
    if debt_to_income_ratio > 50:
        guidance_messages.append(f"Your debt-to-income ratio is high ({debt_to_income_ratio:.2f}%), which may hinder your financial progress. Focus on paying down debt to reduce this ratio and improve financial stability.")
    else:
        guidance_messages.append(f"Your debt-to-income ratio is manageable ({debt_to_income_ratio:.2f}%), but continue to prioritize debt repayment to achieve long-term financial goals.")

    # savings_growth_rate = ((net_savings - initial_savings) / initial_savings) * 100  # Assuming initial_savings is known
    # if savings_growth_rate > 0:
    #     guidance_messages.append(f"Your savings are growing at a rate of {savings_growth_rate:.2f}%. Keep up the good work and consider increasing your savings rate to accelerate wealth accumulation.")
    # else:
    #     guidance_messages.append(f"Your savings are not currently growing. Review your budget and look for opportunities to increase savings and investment contributions.")

    expense_to_income_ratio_by_category = (expense_df.groupby('Category')['Amount'].sum() / total_income) * 100
    guidance_messages.append(f"Your expense-to-income ratio by category: {expense_to_income_ratio_by_category.to_dict()}. Identify categories where expenses are disproportionately high and consider adjustments to your budget.")

    # Calculate investment return rate and compare to benchmarks
    investment_return_rate = 0.08  # Example return rate
    benchmark_return_rate = 0.1  # Example benchmark return rate
    if investment_return_rate < benchmark_return_rate:
        guidance_messages.append("Your investment return rate is below the benchmark. Consider reviewing your investment strategy.")

    # Assess emergency fund adequacy against recommended thresholds
    recommended_emergency_fund = 3 * monthly_expenses
    if net_savings < recommended_emergency_fund:
        guidance_messages.append("Your emergency fund may not be adequate. Consider increasing your savings to ensure you have a sufficient safety net in case of unexpected expenses.")

    # Evaluate retirement readiness against target goals
    retirement_savings_goal = 500000  # Example retirement savings goal
    if net_savings < retirement_savings_goal:
        shortfall_amount = retirement_savings_goal - net_savings
        guidance_messages.append(f"Your retirement savings may be insufficient. You are currently {shortfall_amount:.2f} away from your retirement savings goal. Increase contributions to retirement accounts to bridge this gap.")

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


# def budget_setting(request):
#     # Read budget data from CSV file
#     try:
#         budget_df = pd.read_csv('budget.csv')
#     except FileNotFoundError:
#         budget_df = pd.DataFrame()

#     # Convert DataFrame to HTML table
#     budget_table = budget_df.to_html(classes='table table-striped', index=False)

#     return render(request, 'blog/budget_setting.html', {'budget_table': budget_table})

def budget_setting(request):
    # Read budget data
    try:
        budget_df = pd.read_csv('budget.csv')
    except FileNotFoundError:
        budget_df = pd.DataFrame(columns=['Category', 'Budget'])

    # Read expense data
    try:
        expense_df = pd.read_csv('expense.csv')
    except FileNotFoundError:
        expense_df = pd.DataFrame(columns=['Category', 'Amount', 'Date'])

    expense_df['Date'] = pd.to_datetime(expense_df['Date'])

# Get the latest month and year from the DataFrame
    latest_month = expense_df['Date'].dt.month.max()
    latest_year = expense_df['Date'].dt.year.max()

    # Filter the DataFrame to include only rows from the latest month
    latest_month_expenses = expense_df[
        (expense_df['Date'].dt.month == latest_month) & 
        (expense_df['Date'].dt.year == latest_year)
    ]

    # Get unique categories from budget
    categories = budget_df['Category'].unique()

    # Prepare the budget table HTML
    budget_table_html = '<table class="budget-table"><tr><th>Category</th><th>Budget</th><th>Latest Month Expense</th></tr>'
    for category in categories:
        # Get budget value for the category
        budget_value = budget_df[budget_df['Category'] == category]['Budget'].iloc[0]

        # Get latest month expense for the category
        latest_month_expense = latest_month_expenses[(latest_month_expenses['Category'] == category) ]['Amount'].sum()

         # Check if expense exceeds budget and send SMS
        if latest_month_expense > budget_value:
            message_body = f"Your expenses for {category} have exceeded the budget! Current expense: {latest_month_expense}, Budget: {budget_value}"
            send_sms('+447384129096', message_body) 

        # Determine background color based on comparison
        if latest_month_expense < budget_value:
            bg_color = 'expense-green'
        elif latest_month_expense == budget_value:
            bg_color = 'expense-yellow'
        else:
            bg_color = 'expense-red'

        # Append row to the budget table HTML
        budget_table_html += f'<tr><td>{category}</td><td>{budget_value}</td><td class="expense {bg_color}">{latest_month_expense}</td></tr>'
    budget_table_html += '</table>'

    # Pass the budget table HTML to the template
    context = {'budget_table': budget_table_html}
    return render(request, 'blog/budget_setting.html', context)

def send_sms(recipient_number, message_body):
    try:
        # Send the SMS message
        message = client.messages.create(
            body=message_body,
            from_='+447361582856',  # Replace with your Twilio phone number
            to=recipient_number
        )
        print(f"Message sent successfully! SID: {message.sid}")
    except Exception as e:
        print(f"Error sending message: {str(e)}")


@csrf_exempt
def save_budget(request):
    if request.method == 'POST':
        data = request.POST
        category = data['category']
        budget = data['budget']

        # Read existing budget data from CSV file
        try:
            budget_df = pd.read_csv('budget.csv')
        except FileNotFoundError:
            budget_df = pd.DataFrame()

        # Update budget value for the selected category
        new_row = budget_df.head(1)
        new_row["Category"]=category
        new_row["Budget"]=budget
        budget_df=budget_df.append(new_row)
        budget_df=budget_df.drop_duplicates(subset=['Category'],keep='last')

        # Write DataFrame back to CSV file
        budget_df.to_csv('budget.csv', index=False)

        return JsonResponse({'message': 'Budget saved successfully!'})

    return JsonResponse({'message': 'Invalid request method.'})