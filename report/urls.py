from django.urls import path


from report import views

app_name="report"

urlpatterns = [
    path('sales-report', views.SalesReport, name='SalesReport'),
    # path('stock-in-report', views.StockInReport, name='StockInReport'),
    path('stock-in-report', views.WarehouseStockinReport, name='WarehouseStockinReport'),
    path('purchase-invoices', views.PurchaseInvoice, name='PurchaseInvoice'),
    path('payroll-report', views.PayrollReport, name='PayrollReport'),
    path('Profit-Loss-Statement', views.ProfitLossStatement, name='ProfitLossStatement'),
    path('Account-Series-Report', views.AccountSeriesReport, name='AccountSeriesReport'),
    path('receivables', views.Receivables, name='Receivables'),
    path('aged-receivable', views.AgedReceivables, name='AgedReceivables'),
    path('aged-payable', views.AgedPayable, name='AgedPayable'),
    path('expired-items', views.ExpiredItems, name='ExpiredItems'),
    path('customer-ledger', views.CustomerLedger, name='CustomerLedger'),
    path('view-customer-ledger/<str:code>/<str:invoice>', views.ViewCustomerLedger, name='ViewCustomerLedger'),
    path('sales-ledger', views.SalesLedger, name='SalesLedger'),
    path('edit-sales-ledger-date', views.EditSalesLedgerDate, name='EditSalesLedgerDate'),
    path('purchase-ledger', views.PurchaseLedger, name='PurchaseLedger'),
    path('edit-purchase-ledger-date', views.EditPurchaseLedgerDate, name='EditPurchaseLedgerDate'),
    path('vendor-ledger', views.VendorLedger, name='VendorLedger'),
    path('view-vendor-ledger/<int:code>/<str:invoice>', views.ViewVendorLedger, name='ViewVendorLedger'),
    path('payables', views.Payables, name='Payables'),
    path('Balance-Sheet', views.BalanceSheet, name='BalanceSheet'),
    path('Trial-Balance', views.TrialBalance, name='TrialBalance'),
    path('outlet-stockin-report', views.OutletStockinReport, name='OutletStockinReport'),
    path('check-stock-condition', views.CheckStockCondition, name='CheckStockCondition'),
    path('outlet-stock-report', views.OutletStockLevelReport, name='OutletStockLevelReport'),
    path('warehouse-stock-report', views.WarehouseStockLevelReport, name='WarehouseStockLevelReport'),

    path('cusinvoice/<str:code>/<str:cusID>/', views.GetCustomerDetailsAndInvoice, name='customer-details'), #ajax
    path('view-sales-ledger/<str:code>/', views.ViewSalesLadger, name='view-sales-ledger'), #ajax
    path('view-sales/<str:code>/', views.ViewSales, name='view-sales'), #ajax
    path('view-purchase-ledger/<str:code>/', views.ViewPurchaseLadger, name='view-purchase-ledger'), #ajax
    path('view-purchase/<str:code>/', views.ViewPurchase, name='view-purchase'), #ajax
    path('report-payroll-date', views.report_payroll_filter_by_date, name='report-payroll-date'),#ajax

    path('generate_excel', views.report_payroll_filter_by_date, name='generate_excel'),#ajax
    path('stock-adjustment-history', views.StockAdjustmentHistory, name='StockAdjustmentHistory'),
    path('purchase-adjustment-history', views.PurchaseAdjustmentHistory, name='PurchaseAdjustmentHistory'),

    
    path('HourlySalesReport', views.HourlySalesReport, name='HourlySalesReport'),
    path('DailySalesReport', views.DailySalesReport, name='DailySalesReport'),
    path('MonthlySalesReport', views.MonthlySalesReport, name='MonthlySalesReport'),
    path('QuaterlySalesReport', views.QuaterlySalesReport, name='QuaterlySalesReport'),
    path('YearlySalesReport', views.YearlySalesReport, name='YearlySalesReport'),
    
    path('CustomerMonthlySalesReport', views.CustomerMonthlySalesReport, name='CustomerMonthlySalesReport'),
    path('CustomerQuaterlySalesReport', views.CustomerQuaterlySalesReport, name='CustomerQuaterlySalesReport'),
    path('CustomerYearlySalesReport', views.CustomerYearlySalesReport, name='CustomerYearlySalesReport'),
    
    path('SalesPersonMonthlySalesReport', views.SalesPersonMonthlySalesReport, name='SalesPersonMonthlySalesReport'),
    path('SalesPersonQuaterlySalesReport', views.SalesPersonQuaterlySalesReport, name='SalesPersonQuaterlySalesReport'),
    path('SalesPersonYearlySalesReport', views.SalesPersonYearlySalesReport, name='SalesPersonYearlySalesReport'),

    path('export/', views.export_sales_report_to_excel, name='export_sales_report'),

]
