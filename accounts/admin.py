from django.contrib import admin
from .models import CustomUser,Notes
# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
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
    list_display = ('notes',)
    search_fields = ('notes','notes_type')
    list_filter = ('create_date','created_by')
    readonly_fields = ('notes','notes_type','create_date','created_by')
    fieldsets = (
        ('Notes Information',{'fields': ('notes','notes_type','create_date')}),
        ('User Information', {'fields':('created_by',)})
    )

admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(Notes,CustomNoteAdmin)