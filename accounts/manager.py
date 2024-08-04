"""
Module for custom managers in the authentication system.

This module defines a custom manager for the User model, where email is used
as the unique identifier for authentication instead of usernames.

Classes:
    UserCustomManager: Custom manager for creating regular users and superusers.
"""
from django.contrib.auth.models import BaseUserManager

class UserCustomManager(BaseUserManager):
    """
    Custom manager for User model where email is the unique identifiers
    for authentication instead of usernames.

    Methods
    -------
    create_user(email, password=None, **extra_fields)
        Creates and returns a regular user with the given email and password.
    
    create_superuser(email, password, **extra_fields)
        Creates and returns a superuser with the given email and password.
    """
    def create_user(self,email,password=None,**extra_field):
        """
        Create and return a regular user with the given email and password.

        Parameters
        ----------
        email : str
            The email address of the user.
        password : str, optional
            The password for the user (default is None).
        **extra_fields : dict
            Additional fields to set on the user.

        Returns
        -------
        user : User
            The created user instance.

        Raises
        ------
        ValueError
            If the email is not provided.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_field)
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self,email,password,**extra_field):
        """
        Create and return a superuser with the given email and password.

        Parameters
        ----------
        email : str
            The email address of the superuser.
        password : str
            The password for the superuser.
        **extra_fields : dict
            Additional fields to set on the superuser.

        Returns
        -------
        user : User
            The created superuser instance.

        Raises
        ------
        ValueError
            If is_staff or is_superuser are not set to True in extra_fields.
        """
        extra_field.setdefault('is_staff',True)
        extra_field.setdefault('is_superuser',True)
        extra_field.setdefault('is_email_verify',True)
        extra_field.setdefault('is_active',True)
        if extra_field.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_field.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email,password,**extra_field)
    