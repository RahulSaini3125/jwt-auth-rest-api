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
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
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
        

class UserLoginSerializers(serializers.Serializer):
    """
    UserLoginSerializers handles the validation and creation of tokens for user authentication.

    Fields:
    - email: The email address of the user (required).
    - password: The password of the user (required, write-only, min length 8).
    - access: The access token for the authenticated user (read-only).
    - refresh: The refresh token for the authenticated user (read-only).

    Validation:
    - Checks if both email and password are provided.
    - Authenticates the user using the provided email and password.
    - Ensures the user exists, has verified their email, and is active.

    Raises:
    - ValidationError if the email or password is missing.
    - ValidationError if the user does not exist.
    - ValidationError if the login credentials are invalid.
    - ValidationError if the email is not verified.
    - ValidationError if the user is deactivated.

    Create:
    - Generates JWT tokens (access and refresh) for the authenticated user.
    """
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        """
        Validates the provided email and password.

        Validation Steps:
        - Checks if both email and password are provided.
        - Attempts to authenticate the user using the provided email and password.
        - Ensures the user exists, has verified their email, and is active.

        Raises:
        - ValidationError if the email or password is missing.
        - ValidationError if the user does not exist.
        - ValidationError if the login credentials are invalid.
        - ValidationError if the email is not verified.
        - ValidationError if the user is deactivated.

        Returns:
        - A dictionary containing the validated user.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError({'login':'User with this email does not exist'})
            user = authenticate(request=self.context.get('request'),email= email,password= password)
            if user is None:
                raise serializers.ValidationError({'login':'Invalid login credentials'})
            if not user.is_email_verify:
                raise serializers.ValidationError({'email':'please verify your email'})
            if not user.is_active:
                raise serializers.ValidationError({'user':'User is deactivated'})
            attrs['user']= user
            return attrs
        else:
            raise serializers.ValidationError({'email':'field is required','password':'field is required'})
        
    def create(self, validated_data):
        """
        Creates and returns JWT tokens for the authenticated user.

        Steps:
        - Generates a refresh token for the authenticated user.
        - Generates an access token from the refresh token.
        - Adds the tokens to the validated data dictionary.

        Returns:
        - A dictionary containing the refresh and access tokens.
        """
        user = validated_data.get('user')
        refresh = RefreshToken.for_user(user)
        validated_data['refresh'] = str(refresh)
        validated_data['access'] = str(refresh.access_token)
        return validated_data