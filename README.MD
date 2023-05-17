How to integrate stripe payment getway in Django Rest Framework using webhook.


- pre requirements: 
    - djangorestframework==3.14.0
    - stripe==5.4.0
    - ngrok



STEP 1: 
    - Login into stripe test dashboard.
    - Take stripe secret key from the stripe dashboard.
        follow this URL: https://dashboard.stripe.com/test/apikeys


STEP 2:
    - Define stripe secret key in settings.py

        STRIPE_SECRET_KEY = "sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxVplI"



STEP 3:

    - Create new templates folder and create 2 success and failure html templates.
        
        ./templates/success.html

            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Success</title>
                </head>
                <body>
                    
                    <h1 style="color: green; text-align: center; margin-top: 100px;">Payment Done Successfully</h1>

                </body>
            </html>


        ./templates/failure.html

            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Failure</title>
                </head>
                <body>
                    
                    <h1 style="color: red; text-align: center; margin-top: 100px;">Payment Failed</h1>

                </body>
            </html>



    - Create success and failure page for redirecting based on payment status.

        app/views.py

            def payment_success_view(request):
            # Redirect when payment done successfylly.
            return render(request, "success.html")

            def payment_fail_view(request):
                # Redirect when payment failed.
                return render(request, "failure.html")


    - Create urls for created views.

        app/urls.py

            urlpatterns = [
                path("payment-success", views.payment_success_view, name= "payment_success"),
                path("payment-fail", views.payment_fail_view, name= "payment_fail"),
            ]



- NOTE: IN STRIPE PAYMENT 2 THINGS IS IMPORTANT
        - SESSION AND WEBHOOK

STEP 4:

    - Creating Session to pay throgh stripe.

        app/views.py

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

    
       
    - Create urls for created views.

        app/urls.py

            urlpatterns = [
                path("checkout", views.CreateCheckoutSession.as_view(), name= "checkout"),
            ]




STEP 5:

    - WEBHOOK
    
       USAGE: when payment is success or failure, end of the payment process webhook run automatically return payment process data in json format and get data from webhook and implement some logics if need.

        EX. 1 payment process done between 2 users om G-pay, and some reason payment block for 3 days, that time G-pay need to send request and check payment is success or not, and this is a very costly and cheap process
        to check status, so that time G-pay create one webhook, and webhook run when payment process is either success or fail, then return json response of perticular completed payment process.

       Advantages: Save bandwidth, cost, better performance and efficient


    - Create custom webhook for stripe payment

        app/views.py

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
                    

   
    - Create urls for created views.

        app/urls.py

            urlpatterns = [
                path("webhook", views.WebHook.as_view(), name= "webhook"),
            ]


STEP 6: 

    - NOTE: You are create webhook, but how to know stripe this webhook stripe need to use?.
        So, for that need to define webhook in stripe dashboard.

    - Search webhook in stripe dashboard and open it.
      Follw this URL: https://dashboard.stripe.com/test/webhooks

    - After that Add endpoint in webhook.
        NOTE: local url not work for webhook, for that you need to live you url
            here, we use ngrok for live webhook url

            FOR SETUP AND RUN NGROK, FOLLOW NGROK DOCUMENTATION

        EX.
            https://a569-103-90-96-62.ngrok-free.app/webhook


    - Select some event for stripe payment.
        - payment_intent.requires_action
        - payment_intent.succeeded

    - Click on Add endpoint

    - After successfully wenhook added, copy secret key of webhook and setup in settings.py

        EX. 
            STRIPE_WEBHOOK_KEY = "whsec_xxxxxxxxxxxxxxxxxxxxlPY7m" 



STEP 7:

    NOTE: Before run application, give access to ngrok host

    ./settings.py

        ALLOWED_HOSTS = ["*"]


    - Run application.

    - Now open /checkout API, there you got 1 url as a response, open it.
    - Insert payment detail and click on pay.
      
      NOTE: Visa card number for testing is 4242 4242 4242 4242



STEP 8:

    Refresh define webhook page, ther you see all the payment status and some informatic data, also you can print or user transaction data and use it.
