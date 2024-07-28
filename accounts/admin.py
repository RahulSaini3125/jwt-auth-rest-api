"""
Module for registering models with the Django admin interface.

This module defines the admin interface options for the CustomUser and Notes models.
It customizes the display, search, filter, and readonly fields for these models in the admin panel.

Classes:
    CustomUserAdmin: Admin interface options for the CustomUser model.
    CustomNoteAdmin: Admin interface options for the Notes model.
"""
from django.contrib import admin
from .models import CustomUser,Notes


class CustomUserAdmin(admin.ModelAdmin):
    """
    Admin interface options for the CustomUser model.
    
    Attributes:
        list_display (tuple): Fields to display in the list view.
        search_fields (tuple): Fields to include in the search functionality.
        list_filter (tuple): Fields to filter by in the list view.
        fieldsets (tuple): Fields to display in the detail view, organized by sections.
        readonly_fields (tuple): Fields to be set as read-only in the detail view.
    """
    list_display =('email',)
    search_fields = ('email','first_name','last_name')
    list_filter =('is_active','is_staff','is_superuser')
    fieldsets = (
        ('Personal info', {'fields': ('email','first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('email','first_name','last_name','date_joined','is_staff','is_superuser','last_login','is_active')


class CustomNoteAdmin(admin.ModelAdmin):
    """
    Admin interface options for the Notes model.
    
    Attributes:
        list_display (tuple): Fields to display in the list view.
        search_fields (tuple): Fields to include in the search functionality.
        list_filter (tuple): Fields to filter by in the list view.
        readonly_fields (tuple): Fields to be set as read-only in the detail view.
        fieldsets (tuple): Fields to display in the detail view, organized by sections.
    """
    list_display = ('notes',)
    search_fields = ('notes','notes_type')
    list_filter = ('create_date','created_by')
    readonly_fields = ('notes','notes_type','create_date','created_by')
    fieldsets = (
        ('Notes Information',{'fields': ('notes','notes_type','create_date')}),
        ('User Information', {'fields':('created_by',)})
    )

# Register your models here.
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(Notes,CustomNoteAdmin)