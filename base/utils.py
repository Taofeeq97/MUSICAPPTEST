import json
import requests
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from base.base_crud import AbstractCRUD
from booking.models import Booking, Payment


class BookCRUD(AbstractCRUD):
    model = Booking

class PaymentCRUD(AbstractCRUD):
    model=Payment


import requests
import base64
from django.conf import settings
from urllib.parse import urlencode

class MonnifyClient:
    def __init__(self):
        self.base_url = settings.MONNIFY_BASE_URL
        self.api_key = settings.MONNIFY_API_KEY
        self.client_secret = settings.MONNIFY_SECRET_KEY
        self.contract_code = settings.MONNIFY_CONTRACT_CODE
        self.access_token = None

    def _get_auth_headers(self):
        """Generate proper authentication headers"""
        if not self.access_token:
            self._authenticate()
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

    def _authenticate(self):
        """Authenticate with Monnify and get access token"""
        auth_string = f"{self.api_key}:{self.client_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_auth}"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            self.access_token = response.json()['responseBody']['accessToken']
        except Exception as e:
            raise Exception(f"Monnify authentication failed: {str(e)}")

    def generate_checkout_url(self, booking, user):
        """Generate payment checkout URL"""
        try:
            if not self.access_token:
                self._authenticate()

            payload = {
                "amount": str(booking.amount),
                "customerName": user.get_full_name() or user.email.split('@')[0],
                "customerEmail": user.email,
                "paymentReference": str(booking.id),
                "paymentDescription": f"Booking Payment - {booking.event.title}",
                "currencyCode": "NGN",
                "contractCode": self.contract_code,
                "redirectUrl": f"{settings.FRONTEND_URL}/payment/callback?{urlencode({'booking_id': str(booking.id)})}",
                "paymentMethods": ["CARD", "ACCOUNT_TRANSFER"]
            }

            response = requests.post(
                f"{self.base_url}/merchant/transactions/init-transaction",
                headers=self._get_auth_headers(),
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('requestSuccessful', False):
                return {
                    'checkout_url': data['responseBody']['checkoutUrl'],
                    'transaction_reference': data['responseBody']['transactionReference']
                }
                
            raise Exception(data.get('responseMessage', 'Payment initiation failed'))
                
        except Exception as e:
            raise Exception(f"Payment processing failed: {str(e)}")

    def verify_payment(self, transaction_reference):
        """Verify payment status"""
        try:
            if not self.access_token:
                self._authenticate()

            response = requests.get(
                f"https://sandbox.monnify.com/api/v2/transactions/{transaction_reference}",
                headers=self._get_auth_headers(),
                timeout=10
            )
            print(response)
            response.raise_for_status()
            
            data = response.json()
            if data.get('requestSuccessful', False):
                payment_status = data['responseBody']['paymentStatus']
                return {
                    'status': payment_status,
                    'amount_paid': data['responseBody']['amountPaid'],
                    'paid_on': data['responseBody']['paidOn'],
                    'transaction_reference': transaction_reference
                }
            raise Exception(data.get('responseMessage', 'Payment verification failed'))
                
        except Exception as e:
            raise Exception(f"Payment verification failed: {str(e)}")

    def confirm_payment(self, transaction_reference):
        """Confirm and finalize payment"""
        try:
            print("hellooo")
            verification = self.verify_payment(transaction_reference)
            print(verification)
            
            if verification['status'] == 'PAID':
                return {
                    'success': True,
                    'transaction': verification
                }
            
            return {
                'success': False,
                'message': f"Payment not completed. Status: {verification['status']}"
            }
                
        except Exception as e:
            raise Exception(f"Payment confirmation failed: {str(e)}")
        

class CustomPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100 

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "message": "Success",
            "data": {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data
            }
        })

