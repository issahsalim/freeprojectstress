from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from . models import *

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    
    phone = forms.CharField(max_length=10, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your phone number'
    }))
    
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter password'
    }))
    
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm password'
    }))
    
    school = forms.ModelChoiceField(
        queryset=Schools.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    profile_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'password1', 'password2', 
                 'first_name', 'last_name', 'school', 'profile_pic')
        
        widgets={
            'username':forms.TextInput(attrs={'class':'form-control','placeholder':'username'}),
            'first_name':forms.TextInput(attrs={'class':'form-control','placeholder':'first name'}),
            'last_name':forms.TextInput(attrs={'class':'form-control','placeholder':'last name'}),
        } 

    def clean(self):
        cleaned_data=super().clean()
        exist_mail=cleaned_data.get('email') 
        if CustomUser.objects.filter(email=exist_mail).exists():
            self.add_error('email','A user with this email already exist') 
        return cleaned_data  

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username or Email'
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class CustomProjectsForm(forms.ModelForm):

    project_category = forms.ModelChoiceField(
        queryset=projectcategory.objects.all(), 
        empty_label="---select category---",
        label="Project category"
    )

    class Meta:
        model=CustomProjects 
        fields=['project_title','project_description','project_category',
               'Technologies','estimated_budget','deadline','contact_info'] 

        widgets = {
            'project_title': forms.TextInput(attrs={
                'placeholder': 'project title',
                'style': 'padding-left: 30px;',
                'class': 'form-control'
            }),
            'project_description': forms.Textarea(attrs={
                'placeholder': 'Your project description',
                'style': 'padding-left: 30px;',
                'class': 'form-control'
            }), 
            'deadline': forms.DateInput(attrs={
                'type': 'date',
                'style': 'padding-left: 30px;',
                'class': 'form-control'
            }),
            'departure_time': forms.TimeInput(attrs={
                'type': 'time',
                'style': 'padding-left: 30px;',
                'class': 'form-control'
            }),
            'estimated_budget': forms.NumberInput(attrs={
                'placeholder': 'your budget',
                'style': 'padding-left: 30px;',
                'class': 'form-control'
            }), 
            'Technologies': forms.TextInput(attrs={
                'placeholder': 'Techonologies u want to used build, Its optional',
                'style': 'padding-left: 30px;',
                'class': 'form-control'
            }),  
            'contact_info': forms.TextInput(attrs={
                'placeholder': 'Contact information eg. email,phone number ect',
                'style': 'padding-left: 30px;',
                'class': 'form-control'
            }),
             
        }
    
    def clean(self):
        clean_data=super().clean() 
        budget=clean_data.get('estimated_budget') 
        if budget < 100:
            self.add_error('estimated_budget','Masa the amount you entered can not build any project so add some')
        return clean_data 
    
    def __init__(self, *args, **kwargs):
            super(CustomProjectsForm, self).__init__(*args, **kwargs)
            self.fields["contact_info"].disabled = True
    
 
 
class DeveloperProjectUploadForm(forms.ModelForm):
    agreement = forms.BooleanField(
        required=True,
        initial=False,
        widget=forms.CheckboxInput(attrs={'id': 'agreement-checkbox'})
    )
    
    class Meta:
        model = Project
        fields = [
            'name', 'category', 'description', 'price', 'course',
            'file', 'projectImage1', 'projectImage2', 'projectImage3',
            'features', 'tech_stack', 'demo_link', 'agreement'
        ]  
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'features': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'tech_stack': forms.TextInput(attrs={'class': 'form-control'}),
            'demo_link': forms.URLInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'projectImage1': forms.FileInput(attrs={'class': 'form-control'}),
            'projectImage2': forms.FileInput(attrs={'class': 'form-control'}),
            'projectImage3': forms.FileInput(attrs={'class': 'form-control'}),
        }
  

#  EDIT PROFILE
class ProfileEditForm(forms.ModelForm):


    class Meta:
        model = CustomUser 
        fields = ['username', 'email','profile_pic','first_name','last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

        

