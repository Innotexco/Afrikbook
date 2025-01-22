from account.forms import *
from account.models import *

def checkType(request, id):
    if id is "1":
        return "Assets"
    elif id is "2":
        return "Liability"
    elif id is "3":
        return "Equity"
    elif id is "4":
        return "Income"
    elif id is "6":
        return "Expenses"
    else:
        return False
    
    
def checkAccountType(request, type):
    if type == "Assets":
        return Assets_account
    elif type == "Expenses":
        return Expenses_account
    elif type == "Liability":
        return Liability_account
    elif type == "Equity":
        return Equity_account
    elif type == "Income":
        return Income_account
    else:
        return chart_of_account