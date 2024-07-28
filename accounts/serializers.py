from rest_framework import serializers
from .models import CustomUser
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.db import IntegrityError
import logging
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
logger = logging.getLogger(__name__)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    UserRegistrationSerializer
    --------------------------

    This serializer handles the user registration process, including password validation and sending account activation emails.

    Attributes:
        password2 (CharField): Write-only field for password confirmation.
        password (CharField): Write-only field for the user's password with validation.
        
    Meta:
        model (CustomUser): The model associated with this serializer.
        fields (tuple): Fields included in the serialization process.
        extra_kwargs (dict): Extra settings for specific fields.
            - email: Validator to ensure email uniqueness.
            - date_joined: Read-only field.
            - is_active: Read-only field.

    Methods:
        validate(attrs): Validates that the password and password2 fields match.
        send_activation_email(user, request): Sends an account activation email to the user.
        create(validated_data): Creates a new user with the validated data.

    Usage:
        - This serializer is used for user registration, ensuring password matching and uniqueness of email.
        - Upon successful user creation, an account activation email is sent to the user.
    """
    password2 = serializers.CharField(write_only= True)
    password = serializers.CharField(write_only = True,validators= [validate_password])

    class Meta:
        model = CustomUser
        fields = ('email','password','password2','first_name','last_name','is_active','date_joined')
        extra_kwargs = {
            'email': {
                'validators': [UniqueValidator(queryset=CustomUser.objects.all(),message='Email is already exists')]
            },
            'date_joined':{
                'read_only':True
            },
            'is_active':{
                'read_only':True
            }
        }

    def validate(self, attrs):
        """
        validate(attrs)
        ---------------

        Validates that the password and password2 fields match.

        Parameters:
            attrs (dict): A dictionary containing the validated data from the serializer.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If the password and password2 fields do not match.
        """
        attrs = super().validate(attrs=attrs)
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({ 'password2' :'Password Does Not Match'})
        return attrs
    
    def send_activation_email(self,user,request):
        """
        send_activation_email(self, user, request)
        ------------------------------------------

        Sends an account activation email to the user.

        Parameters:
            user (CustomUser): The user instance for whom the activation email is to be sent.
            request (HttpRequest): The HTTP request object, used to construct the activation URL.

        Raises:
            serializers.ValidationError: If there is an error sending the activation email.
            
        Logs:
            - Logs an error message if the email fails to send, including the user email and the exception details.
        """
        try:
            token = user.generate_token()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            activation_link = reverse('activate-account', kwargs={'uidb64': uid, 'token': token})
            activation_url = f'http://{current_site.domain}{activation_link}'
            subject = 'Activate Account'
            message = f'Your Activation link is :\n {activation_url}'
            from_email =  settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            send_mail(
                subject=subject,
                from_email=from_email,
                message=message,
                recipient_list= recipient_list,
                fail_silently=True
            )
        except Exception as e:
            logger.error(f'Failed to send email to {user.email}: {e}')
            raise serializers.ValidationError({'email':'Failed to send activation email'})

    @transaction.atomic
    def create(self, validated_data):
        """
        create(self, validated_data)
        ----------------------------

        Creates a new user with the validated data and sends an account activation email.

        Parameters:
            validated_data (dict): The validated data from the serializer, excluding the password confirmation field.

        Returns:
            CustomUser: The newly created user instance.

        Raises:
            serializers.ValidationError: If an IntegrityError occurs indicating that the email already exists or if any other exception occurs.
            Exception: If the user creation fails for any unspecified reason.

        Logs:
            - Logs an error message if an IntegrityError occurs, indicating the issue.
            - Logs an error message if any other exception occurs during user creation.
            - Logs an info message upon successful user creation, including the user email.
        """
        try:
            validated_data.pop('password2')
            user = CustomUser.objects.create_user(**validated_data)
        except IntegrityError as e:
            logger.error(f'Integrity error {e}')
            raise serializers.ValidationError('Email is Already exists')
        except Exception as e:
            logger.error(f'Exception error {e}')
            raise serializers.ValidationError(f'Something went wrong')
        if user:
            logger.info(f'User with id  "{user.email}" is created successfully')
            self.send_activation_email(user=user,request= self.context.get('request'))
            return user
        else:
            raise Exception(f'Something Went Wrong')