
from django.urls import path
from .import views

urlpatterns = [
     # success
     path("payment-success", views.payment_success_view, name= "payment_success"),
     # failure
     path("payment-fail", views.payment_fail_view, name= "payment_fail"),
     
     # session
     path("checkout", views.CreateCheckoutSession.as_view(), name= "checkout"),
     
     # webhook
     path("webhook", views.WebHook.as_view(), name= "webhook"),
]
