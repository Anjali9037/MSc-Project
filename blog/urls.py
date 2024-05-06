from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='blog-home'),
    path('about/', views.about, name='blog-about'),
    path('landing_page', views.landing_page, name='landing_page'),
    path('data_addition', views.data_addition, name='data_addition'),
    path('submit_income', views.submit_income, name='submit_income'),
    path('submit_expense', views.submit_expense, name='submit_expense'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('financial_guidance_view', views.financial_guidance_view, name='financial_guidance_view'),
    path('budget_setting', views.budget_setting, name='budget_setting'),
    path('save_budget', views.save_budget, name='save_budget'),
]