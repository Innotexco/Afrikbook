from django.urls import path, include
from . import views


app_name = 'employee'

urlpatterns = [

    path('Employee', views.ViewEmployee, name='Employee'),
    path('NewEmployee', views.AddEmployee, name='NewEmployee'),
    path('update/employee/<int:id>/', views.UpdateEmployee, name='update-employee'),
    path('delete/employee/<int:id>/', views.DeleteEmployee, name='delete-employee'),
    
    path('Payroll', views.ViewPayroll, name='Payroll'),
    path('NewPayroll', views.AddPayroll, name='NewPayroll'),
    path('ViewUnapprovePayroll', views.ViewUnapprovePayroll, name='ViewUnapprovePayroll'),
    path('FetchUnapprovePayroll', views.FetchUnapprovedPayroll, name='FetchUnapprovePayroll'),
    path('ViewApprovePayroll', views.ViewApprovePayroll, name='ViewApprovePayroll'),
    path('FetchApprovedPayroll', views.FetchApprovedPayroll, name='FetchApprovedPayroll'),

    path('ApprovedPayrolls', views.ApprovedPayrolls, name='ApprovedPayrolls'),
    path('payrolls', views.Payrolls, name='payrolls'),
    path('payroll', views.Payroll, name='payroll'),
    path('payroll-date', views.payroll_filter_by_date, name='payroll-date'),

    path('SaveChanges', views.SaveChanges, name='SaveChanges'),
    path('Approvepayroll', views.ApprovePayroll, name='Approvepayroll'),
    path('ConfirmPayment', views.ConfirmPayment, name='ConfirmPayment'),
    path('ConfirmAllPayment', views.ConfirmAllPayment, name='ConfirmAllPayment'),

   
]