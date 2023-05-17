from django.shortcuts import render
import stripe
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
import time
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.


def payment_success_view(request):
    # Redirect when payment done successfylly.
    return render(request, "success.html")

def payment_fail_view(request):
    # Redirect when payment failed.
    return render(request, "failure.html")


class CreateCheckoutSession(APIView):
    
  def post(self, request):
    
    print("\n\n \t checkout session started... \n\n")  
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                'price_data': {
                    "currency": "inr",
                    "unit_amount": 4324,
                    "product_data": {
                        "name": "Test Product"
                    },
                },
                    "quantity": 1,
                },
            ],
            mode='payment',
            
            
            success_url= f"http://127.0.0.1:8000/payment-success",
            cancel_url= f"http://127.0.0.1:8000/payment-fail",
        
           
        )
        
        print("\n Session Created... \n")
        
        print(checkout_session,"\n\n\n\n\n\n")
        return Response ({
            "url": checkout_session.url,
            "status": status.HTTP_303_SEE_OTHER
        })
    except Exception as e:
        print("\n\n-------->>>>>>\t\t",e)
        return Response(status= 404, exception=e)

    # return Response(status= status.HTTP_303_SEE_OTHER)
   


class WebHook(APIView):
    
    def post (self, *args, **kwargs):
        
        # Retrieve the request body and signature
        request_data = self.request.body.decode('utf-8')
        request_signature = self.request.META['HTTP_STRIPE_SIGNATURE']
        webhook_secret = settings.STRIPE_WEBHOOK_KEY
        try:
            # Verify the signature and extract the event data
            event = stripe.Webhook.construct_event(
                payload=request_data,
                sig_header=request_signature,
                secret=webhook_secret
            )
        except ValueError as e:
            # Invalid payload
            return Response(e)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return Response(e)

        # Handle the event based on its type
        if event.type == 'payment_intent.succeeded':
            
            # Payment succeeded, update your database or do other necessary tasks
            payment_intent = event.data.object
            
            print('\n\n\n Payment succeeded:', payment_intent.id)
            print("\n\n", payment_intent, "\n\n")
            return Response({"status": payment_intent.status})
        
        
        elif event.type == 'payment_intent.payment_failed':
        
            # Payment failed, take necessary actions to notify the user
            payment_intent = event.data.object
            
            print('\n\n Payment failed:', payment_intent.id)
            return Response({"status": payment_intent.status})
        
 