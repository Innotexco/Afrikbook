from django.urls import path


from account import views

app_name="account"

urlpatterns = [

    path('New-chart-of-account', views.new_chart_of_account, name='NewChartOfAccount'),
    path('view-Chart-of-Account', views.ViewChartOfAccount, name='ViewChartOfAccount'),
    path('view-Chart-of-Account_Details/<str:account_id>', views.ViewChartOfAccountDetails, name='ViewChartOfAccountDetails'),
    path('Account-Setup', views.AccountSetup, name='AccountSetup'),      
    path('InterAccountTransfer', views.InterAccountTransfer, name='InterAccountTransfer'),
    path('ViewInterAccountTransfer', views.ViewInterAccountTransfer, name='ViewInterAccountTransfer'),
    #  path('insert/', views.insert_data, name='insert_data'),

    path('account/<str:value>/', views.fetchaccounts, name='account'), #ajax
    path('account-name/<str:value>/', views.fetchaccountsname, name='account-name'), #ajax

    
    
]
