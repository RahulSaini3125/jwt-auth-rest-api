"""
Module for defining models in the authentication system.

This module includes the definitions for the CustomUser and Notes models,
which are used to store user information and user-generated notes, respectively.

Classes:
    CustomUser: Extends AbstractBaseUser and PermissionsMixin to create a custom user model.
    Notes: Model to store notes created by users.
"""

from django.db import models
from .manager import UserCustomManager
from django.contrib.auth.models import PermissionsMixin,AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import IntegrityError,OperationalError
# Create your models here.

class CustomUser(AbstractBaseUser,PermissionsMixin):
    """
    CustomUser model extending AbstractBaseUser and PermissionsMixin.
    
    Attributes:
        email (EmailField): User's email address, used as the username field.
        first_name (CharField): User's first name, required.
        last_name (CharField): User's last name, optional.
        date_joined (DateTimeField): Timestamp when the user joined.
        is_active (BooleanField): Indicates if the user account is active.
        is_staff (BooleanField): Indicates if the user has staff status.
        is_superuser (BooleanField): Indicates if the user has superuser status.
    """
    email = models.EmailField(_('User Email'),unique=True)
    first_name = models.CharField(_('First Name'),max_length=10)
    last_name = models.CharField(_('Last Name'),max_length=10,blank=True)
    date_joined = models.DateTimeField(_('Date Joined'),auto_now_add=True)
    is_active = models.BooleanField(_('active'),default=True)
    is_staff = models.BooleanField(_('staff status'),default=False)
    is_superuser = models.BooleanField(_('super user'),default=False)

    objects = UserCustomManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    

class Notes(models.Model):
    """
    Notes model to store user notes.
    
    Attributes:
        notes (CharField): The note content.
        notes_type (CharField): The type of note, must be one of ['personal', 'work', 'other'].
        create_date (DateTimeField): Timestamp when the note was created.
        created_by (ForeignKey): Reference to the user who created the note.
    """
    NOTES_TYPE = [
        ('personal',_('personal')),
        ('work',_('work')),
        ('other',_('other'))
    ]
    notes = models.CharField(_('Notes'),max_length=1000)
    notes_type = models.CharField(_('Notes Type'),choices=NOTES_TYPE,max_length=15)
    create_date = models.DateTimeField(_('Created Date'),auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')

    @classmethod
    def create_note(cls,notes:str,type:str,user):
        """
        Class method to create a new note.
        
        Args:
            notes (str): The content of the note.
            type (str): The type of the note, must be one of ['personal', 'work', 'other'].
            user (CustomUser): The user creating the note.
        
        Raises:
            ValueError: If an invalid note type is provided.
            IntegrityError: If there is a database integrity error.
            OperationalError: If there is a database operational error.
            Exception: For any other exceptions.
        
        Returns:
            Notes: The created note instance.
        """
        valid_type = [type[0] for type in cls.NOTES_TYPE]
        if type not in valid_type:
            raise ValueError(f'Invalid Notes Type {type} provided')
        try:
            note = cls.objects.create(notes=notes,type=type,created_by=user)
            return note
        except InterruptedError as e:
            raise IntegrityError(f'Database intergrity error: {e}')
        except OperationalError as e:
            raise OperationalError(f'Database operational error: {e}')
        except Exception as e:
            raise Exception(f'An Exception error: {e}')