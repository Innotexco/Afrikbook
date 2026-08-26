from django.urls import path, include
from . import views


app_name = 'journal'

urlpatterns = [

    path('NewJournal', views.NewJournal, name='NewJournal'),
    path('search-vendor-customer/', views.search_vendor_customer, name='search_vendor_customer'), #Ajax

    path('ViewJournal', views.ViewJournalEntry, name='ViewJournal'),
    path('ViewJournalItem/<str:invoice>/', views.ViewJournalEntryItem, name='ViewJournalItem'),
    path('Cancel_journal', views.Cancel_journal, name='Cancel_journal'),


    path('ViewLoan', views.ViewLoan, name='ViewLoan'),
    path('NewLoan', views.CreateLoan, name='NewLoan'),
    path('update/loan/<int:id>/', views.UpdateLoan, name='update-loan'),
    path('delete/loan/<int:id>/', views.DeleteLoan, name='delete-loan'),

    path('ReceivePayment', views.ReceivePayment, name='ReceivePayment'),

    path('item/<int:id>/', views.GetLoanDetails, name='loan-details'), #ajax
   
]