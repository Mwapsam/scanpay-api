from django.urls import path

from api.mtn.payment_gateway import PaymentView


urlpatterns = [path("payment/", PaymentView.as_view(), name="payment")]
