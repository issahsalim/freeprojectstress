from django.contrib import admin,messages
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.contrib.auth.models import User
from django.core.mail import send_mail,send_mass_mail,EmailMessage,BadHeaderError
from django.conf import settings
import smtplib
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'school',) 
    list_filter = ( 'school',)
    fieldsets = UserAdmin.fieldsets + (  
        ('Additional Info', {'fields': ('phone', 'profile_pic', 'school', )}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Schools)
class SchoolsAdmin(admin.ModelAdmin):
    list_display=('name',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display=('uploaded_by','name','price','created_at','is_deleted','approve',)
    def save_model(self, request, obj, form, change):
        if not change:   
            obj.uploaded_by = request.user 
        super().save_model(request, obj, form, change)

        # notifying all user when i new project is uploaded 
        if change:
            get_uploader_mail=Project.objects.get(pk=obj.pk) 
            other_users_mail=list(CustomUser.objects.exclude(email=obj.uploaded_by.email).values_list('email',flat=True))
            get_approve_pro=Project.objects.filter(pk=obj.pk,approve=True) 
            if get_approve_pro:
                try:
                    subject=f"Congrat {get_uploader_mail.uploaded_by.username}"
                    message=f"""
                        Hello {get_uploader_mail.uploaded_by.username} your project {get_uploader_mail.name} has been approved!
                    """
                    from_mail=f"Free<{settings.EMAIL_HOST_USER}>" 
                    to_mail=[get_uploader_mail.uploaded_by.email]
                    try:
                        send_mail(
                            subject=subject, message=message,from_email=from_mail,recipient_list=to_mail,fail_silently=False
                        ) 
                    except BadHeaderError as e: 
                        self.message_user(request,f"{e} error happen", level=messages.error)
                    except smtplib.SMTPException as e:
                        self.message_user(request,f"{e} error occur",level=messages.error)
                    except Exception as e:
                        self.message_user(request,f"Error occur {e} try again",level=messages.error)
                except Exception as e: 
                    self.message_user(request,f"{e} error occur")
            
            


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display=('name',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'get_project_title',
        'get_project_owner',
        'get_buyer_username',
        'get_buyer_phone',
        'transaction_id',
        'amount',
        'payment_date',
        'is_paid',
        'get_project_owner_contact',
    )    
    search_fields=('project','amount','bought_by','payment_date','is_paid','transaction_id',) 
    
    def get_buyer_username(self, obj):
        return obj.bought_by.username
    get_buyer_username.short_description = "Buyer Username"

    def get_buyer_phone(self, obj):
        return getattr(obj.bought_by, "phone", "N/A")   
    get_buyer_phone.short_description = "Buyer Phone"

    def get_project_title(self, obj):
        return getattr(obj.project, "name", "N/A")
    get_project_title.short_description = "Project"

    def get_project_owner(self, obj):
        return obj.project.uploaded_by.username
    get_project_owner.short_description = "Uploaded By"

    def get_project_owner_contact(self, obj):
        return obj.project.uploaded_by.phone or "No number"
    get_project_owner_contact.short_description = "Owner Contact"


@admin.register(DownloadedProjects)
class DownloadedProjectAdmin(admin.ModelAdmin):
    list_display=('school','projects','downloaders','date')

admin.site.register (projectcategory)
@admin.register(CustomProjects)
class customprojectAdmin(admin.ModelAdmin):
    list_display=('project_title','project_category','estimated_budget','user','contact_info','deadline',)


admin.site.register(trying) 


admin.site.register(Agreement) 
