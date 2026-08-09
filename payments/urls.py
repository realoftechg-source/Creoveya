from django.urls import path

from payments import views

app_name = 'payments'

urlpatterns = [
    path('credits/', views.credits_view, name='credits'),
    path('credits/purchase/<str:package_name>/', views.purchase_credits_view, name='purchase_credits'),
    path('', views.billing_view, name='billing'),
    path('change-plan/<str:plan_key>/', views.change_plan_view, name='change_plan'),
    path('transactions/', views.transactions_view, name='transactions'),
]
