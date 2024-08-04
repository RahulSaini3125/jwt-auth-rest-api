# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserLoginSerializers
import logging
from rest_framework.serializers import ValidationError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import get_object_or_404
from .models import CustomUser
from .token import ExpiringTokenGenerator
from django.http import Http404
logger = logging.getLogger(__name__)

class user_registration(APIView):
    """
    UserRegistration view to handle user registration via POST requests.

    Methods:
        post(request): Validates and registers a new user.
    """
    def post(self,request):
        try:
            user_serializer = UserRegistrationSerializer( data=request.data,context ={'request':request})
            if user_serializer.is_valid():
                user = user_serializer.save()
                if user: 
                    return Response({'status':status.HTTP_201_CREATED,'message':'Success','email_verify':'Email is send to activate your account','data':user_serializer.data},status=status.HTTP_201_CREATED)
                else:
                    return Response({'status':status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,'error':user_serializer.errors},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            else:
                return Response({'status':status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,'error':user_serializer.errors},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except ValidationError as e:
            return Response({'status':status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,'error':e.detail,'message':'Failed to Create User'},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except Exception as e:
            logger.error(f'Exception error {e}')
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message': 'Something went wrong'
            },status=status.HTTP_400_BAD_REQUEST)
        
class ActivateAccount(APIView):
    """
    ActivateAccount view to handle account activation via GET requests.

    Methods:
        get(request, uidb64, token, *args, **kwargs): Activates user account if the token is valid.
    """
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(CustomUser, pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist,Http404):
            user = None
        if user is not None and ExpiringTokenGenerator.check_token(self,user = user,token=token):
            user.is_active = True
            user.is_email_verify = True
            user.save()
            return Response({'status':status.HTTP_200_OK,'message': 'Account activated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'status':status.HTTP_400_BAD_REQUEST,'message': 'Activation link is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        

class UserLogin(APIView):
    """
    UserLoginView handles the authentication of users.

    Endpoint: POST /login/

    Request Body Parameters:
    - email: The email address of the user (required).
    - password: The password of the user (required).

    Responses:
    - 202 Accepted:
        - Status: 202
        - Message: "Login successful"
        - Info: A dictionary containing:
            - email: The email address of the authenticated user.
            - access: The access token for the authenticated user.
            - refresh: The refresh token for the authenticated user.
    
    - 400 Bad Request:
        - Status: 400
        - Message: "Unsuccessful"
        - Error: A dictionary containing error messages for invalid fields.

    This view uses the UserLoginSerializers to validate and authenticate the user.
    On successful authentication, it returns JWT tokens (access and refresh) along with the user's email.
    """
    def post(self,request):
        loginserializer = UserLoginSerializers(data=request.data,context={'request':request})
        if loginserializer.is_valid():
            login_user = loginserializer.save()
            response_data = {
                'status':status.HTTP_202_ACCEPTED,
                'message': 'login successfull',
                'info':loginserializer.data
            }
            return Response(status=status.HTTP_202_ACCEPTED,data=response_data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={'status':status.HTTP_400_BAD_REQUEST,'message':'unsuccessfull','error':loginserializer.errors})