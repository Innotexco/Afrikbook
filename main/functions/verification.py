"""Script used to define the paystack Verification class."""

from paystackapi.base import PayStackBase
import requests
from django.conf import settings
from django.http import JsonResponse
from main.models import User, Billing, SubHistory
from datetime import datetime, date, timedelta
from settings.models import company_table
import re



class Verification(PayStackBase):

    def verify_card(email, amount, card_details):
        """
        Verify a debit/credit card using Paystack API.

        :param email: Customer's email address
        :param amount: Amount in kobo (smallest currency unit)
        :param card_details: Dictionary containing card information
        :return: Response from Paystack
        """
        url = "https://api.paystack.co/charge"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "amount": amount,  # in kobo; e.g., 1000 kobo = ₦10
            "card": card_details
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.status_code
        except requests.exceptions.RequestException as e:
            return {"status": False, "message": str(e)}
        

    def initialize_payment(request, email, amount):
        # if request.method == "POST":
        # email = request.POST.get("email")
        amount = float(amount) * 100  # Convert to Kobo
        callback_url = "https://console.afrikbook.com/Verify-Payment"
        # Call Paystack Initialize API
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "email": email,
            "amount": int(amount),
            "callback_url": callback_url,
        }

        try:
            response = requests.post(
                "https://api.paystack.co/transaction/initialize", json=data, headers=headers
            )
            response_data = response.json()
            if response_data["status"]:
                # print(response_data)
                # verify = Verification.verify_payment(request, response_data["data"]["reference"])
                # Save payment details
                # Payment.objects.create(
                #     email=email, amount=amount / 100, reference=response_data["data"]["reference"]
                # )
                # # Redirect to Paystack payment page
                # return redirect(response_data["data"]["authorization_url"])
                return response_data
            else:
                return 404
        except requests.exceptions.RequestException as e:
            return {"status": False, "message": str(e)}

            
    
    def verify_payment(request, reference):
        # reference = request.GET.get("reference")
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.get(
                f"https://api.paystack.co/transaction/verify/{reference}", headers=headers
            )
            response_data = response.json()

            if response_data["status"] and response_data["data"]["status"] == "success":
                # payment = Payment.objects.get(reference=reference)
                # payment.verified = True
                # payment.save()
                return response
            else:
                return response
        except requests.exceptions.RequestException as e:
            return JsonResponse(e.response, safe=False, status=500)
    
    def verify_email(request):
        data = request.GET.get('email')
        Email = User.objects.filter(email=data)

        if not re.match(r"[^@]+@[^@]+\.[^@]+", data):
           return JsonResponse({'error_msg':"Email is not valid"})
        if Email.exists():
            return JsonResponse({'error_msg':"Email already exists"})
        
        return JsonResponse({"Valid": True})
    
    def verify_username(request):
        data = request.GET.get('username')
        username = User.objects.filter(username=data)
    
        if username.exists():
            return JsonResponse({'error_msg':"Username already exists"})
        return JsonResponse({"Valid": True})
    
    def verify_phone(request):
        data = request.GET.get('phone')
        Email = company_table.objects.filter(phone=data)

    
        if Email.exists():
            return JsonResponse({'error_msg':"Phone number already exists"})
        return JsonResponse({"Valid": True})






def add_user(request):

    try:
        if request.user.is_authenticated:
            user =  User.objects.filter(company_id=request.user.company_id.id).count()
            plan = Billing.objects.get(company=request.user.company_id.id).plan
            
            if plan == "Micro Business":
                return True if user < 2 else False
            elif plan == "Small Business":
                return True if user < 4 else False
            elif plan == "Medium Business":
                return True if user < 6 else False
            elif plan == "Large Business":
                return True if user < 50 else False
            else:
                return False
        else:
            return True
    except Billing.DoesNotExist:
        return True
    
def check_sub(request, id):
    try:
        sub = Billing.objects.get(company=id)
        on = sub.date.date()
        plan = sub.subscription
        created_date = datetime.strptime(str(on), "%Y-%m-%d")
        if sub.subscription == "Free":
            # Calculate the new month and year
            new_month = created_date.month + 6
            new_year = created_date.year + (new_month - 1) // 12
            new_month = (new_month - 1) % 12 + 1

            # Create the new date
            next_year_date = created_date.replace(year=new_year, month=new_month)
        else:   
            next_year_date = created_date.replace(year=created_date.year + int(plan))

        today = date.today()
        current_date = datetime.strptime(str(today), "%Y-%m-%d")

        # Calculate the difference
        remaining_days = (next_year_date - current_date).days
      
    except Billing.DoesNotExist:
        remaining_days = 0
        plan = 'None'
   
    return remaining_days, plan

def check_sub_history(request, id,  company_id):
    try:
        sub = SubHistory.objects.get(id=id, company=company_id)
        on = sub.date.date()
        plan = sub.subscription
        created_date = datetime.strptime(str(on), "%Y-%m-%d")
        if sub.subscription == "Free":
            # Calculate the new month and year
            new_month = created_date.month + 6
            new_year = created_date.year + (new_month - 1) // 12
            new_month = (new_month - 1) % 12 + 1

            # Create the new date
            next_year_date = created_date.replace(year=new_year, month=new_month)
        else:   
            next_year_date = created_date.replace(year=created_date.year + int(plan))

        today = date.today()
        current_date = datetime.strptime(str(today), "%Y-%m-%d")

        # Calculate the difference
        remaining_days = (next_year_date - current_date).days
      
    except Billing.DoesNotExist:
        remaining_days = 0
        plan = 'None'
   
    return remaining_days, plan




# def VerifyEmail(request):
#     email = request.GET.get('email')
#     code = request.GET.get('code')
#     title = "Email Verification"
#     message = f"""
#                     <div style="display: flex; justify-content: center; align-items: center; padding: 8px; text-align: center;">
#                         <div style="padding: 16px; width: fit-content; margin: auto;">
#                             <div style="margin-bottom: 24px; text-align: center;">
#                                 <img
#                                     alt="Contact"
#                                     loading="lazy"
#                                     decoding="async"
#                                     style="height: 80px; width: 80px; border: 1px solid #e2e8f0; border-radius: 9999px; display: block; margin: auto;"
#                                     src="http://account.afrikbook.com/static/logo/log.png"
#                                 />
#                             </div>
#                             <div style="text-align: center;">
#                                 <p>Hello</p>
#                                 <p>Your verification code is</p>
#                                 <h1>{code}</h1>
#                             </div>
#                             <div style="margin-top: 24px; text-align: center;">
#                                 <p>© 2023 Afrikbook™. All Rights Reserved.</p>
#                                 <p><a href="account.afrikbook.com" style="color: #007BFF;">Afrikbook.com</a></p>
#                             </div>
#                         </div>
#                     </div>
#                 """

#     send = send_email([email], title, message)
    
#     return JsonResponse(send, safe=False)
