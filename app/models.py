from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings
from auditlog.registry import auditlog

class Schools(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
 
class Course(models.Model):
    name=models.CharField(max_length=50) 
    def __str__(self):
        return  self.name
    
class projectcategory(models.Model):
    name=models.CharField(max_length=50) 
    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=255)
    category=models.ForeignKey(projectcategory,on_delete=models.CASCADE) 
    description = models.TextField()
    price=models.DecimalField(max_digits=10,decimal_places=2) 
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    file=models.FileField(upload_to='uploads/projects/')
    uploaded_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE) 
    
    projectImage1=models.ImageField(upload_to='uploads/projectimages/',blank=True, null=True)
    projectImage2=models.ImageField(upload_to='uploads/projectimages/',blank=True, null=True)
    projectImage3=models.ImageField(upload_to='uploads/projectimages/',blank=True, null=True)

    features = models.TextField(blank=True, null=True)
    tech_stack = models.CharField(max_length=255, blank=True, null=True)
    demo_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    
    status=models.CharField(max_length=20, choices=[
        ('bought', 'Bought'), 
        ('pending', 'Pending'),  
    ], default='pending') 

    agreement=models.BooleanField(default=True)  
    is_deleted=models.BooleanField(default=False,null=True,blank=True)  
    approve=models.BooleanField(default=False,null=True,blank=True) 
    def __str__(self):
        return f"{self.name} {self.uploaded_by.username}"
    
auditlog.register(Project)


class CustomProjects(models.Model):
    project_title=models.CharField(max_length=50)
    project_description=models.TextField()
    project_category=models.ForeignKey(projectcategory,on_delete=models.CASCADE) 
    Technologies=models.CharField(max_length=50,) 
    estimated_budget=models.DecimalField(decimal_places=2, max_digits=10) 
    deadline=models.DateField()  
    contact_info=models.CharField(max_length=50) 
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)  

    def __str__(self): 
        return  self.project_title  


class Payment(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2,editable=False)
    payment_date = models.DateTimeField(auto_now_add=True,editable=False)
    transaction_id = models.CharField(max_length=100, unique=True,editable=False)
    is_paid = models.BooleanField(default=False,editable=False)
    bought_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT, editable=False, related_name="payments") 
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="payments")  
    def __str__(self):    
        return f"Payment {self.transaction_id} - {self.amount} by {self.bought_by.username} {self.bought_by.phone} {self.project} {self.is_paid} {self.project.uploaded_by.username}"  
    
auditlog.register(Payment)
    
class DownloadedProjects(models.Model):
    downloaders=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True) 
    school=models.ForeignKey(Schools,on_delete=models.CASCADE) 
    projects=models.ForeignKey(Project,on_delete=models.CASCADE) 
    date=models.DateTimeField(auto_now_add=True)  
    class Meta:
        verbose_name="Downlaoded Project"  

class trying(models.Model):
    extra=models.JSONField(default=dict, blank=True) 


class CustomUser(AbstractUser):
    phone = models.CharField( max_length=10, unique=True) 
    profile_pic = models.ImageField(upload_to='uploads/profile_pic/', null=True, blank=True)
    school = models.ForeignKey(Schools, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.username  
    

class Agreement(models.Model):
    agreementInfo=models.CharField(max_length=100) 
    

