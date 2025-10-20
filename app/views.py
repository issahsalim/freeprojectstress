from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from .models import * 
import requests,uuid 
from django.http import HttpResponse, JsonResponse
from .utils import *
from django.core.mail import send_mail,EmailMessage,BadHeaderError
from requests.exceptions import ConnectionError
from django.contrib.auth.views import PasswordResetView 
from django.urls import reverse_lazy 
from django.contrib.auth import get_user_model
import smtplib 
from django.utils import timezone
from dotenv import load_dotenv 
import os 
load_dotenv()
User= get_user_model() 

class CustomPasswordResetView(PasswordResetView):
    template_name = 'reset_password.html'
    email_template_name = "email_reset_password.html"
    success_url = reverse_lazy('password_reset_done')  

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        
        if User.objects.filter(email=email).exists():
          
            return super().form_valid(form)
        else:
           
            messages.error(self.request, "Email does not match any account")
            return self.form_invalid(form)
   
   

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html', {'user': request.user})


def projects_view(request):
    project_download=[] 
    courses=Course.objects.all()  
    courseid=request.GET.get("course")
    if courseid: 
        all_projects=Project.objects.filter(course=courseid,approve=True,is_deleted=False)   
    else:  
        all_projects=Project.objects.filter(approve=True,is_deleted=False)  

    # try: 
    #     get_user=CustomUser.objects.get(username=request.user)
    #     user_shc=get_user.school 
    # except CustomUser.DoesNotExist:   
    #     messages.error(request,'Please provide all neccessary information during registration')
    #     return redirect('project_page') 
    
    for project in all_projects: 
        # if user_shc: 
        #     has_downloaded=DownloadedProjects.objects.filter(school=user_shc,projects=project).exists() 
        # else:     
        #     has_downloaded=None  

        project_download.append({
            'projects':project,
            # 'sch_already_downlaod':has_downloaded,
        }) 


    if request.method == 'POST':
        form=CustomProjectsForm(request.POST,request.FILES) 
        if form.is_valid():
            uploaded=request.FILE['file']

            try:
                compressed_content, compressed_size = compress_file_to_zip_in_memory(uploaded)
                instance = form.save(commit=False)
                instance.name = uploaded.name
                
                # save compressed file to the FileField (save=False to continue setting fields)
                instance.file.save(compressed_content.name, compressed_content, save=False)
                instance.compressed_size = compressed_size
                instance.save()
            except MemoryError:
                # fallback for huge file: use disk approach
                django_file, temp_in_path, temp_zip_path = compress_file_to_zip_on_disk(uploaded)
                instance = form.save(commit=False)
                instance.name = uploaded.name
                instance.file.save(f"{uploaded.name}.zip", django_file, save=False)
                instance.compressed_size = os.path.getsize(temp_zip_path)
                instance.save()
                # cleanup
                django_file.close()
                os.remove(temp_in_path)
                os.remove(temp_zip_path)  

            try:        
                 subject = "Request Project"
                 message = f"""A new project request from {request.user}. """
                 
                 from_email = f"Freeprojectstress <{settings.EMAIL_HOST_USER}>"
                 to_email = [settings.EMAIL_HOST_USER]
                 
                 send_mail(
                     subject=subject,
                     message=message,
                     from_email=from_email,
                     recipient_list=to_email,
                     fail_silently=False
                 ) 

            except BadHeaderError as e:
                messages.error(request,f"Error occur {e}")
                return redirect('project_page') 
            except smtplib.SMTPException as e:
                messages.error(request,f"{e} error occur")
                return redirect('project_page')
            except Exception as e:
                messages.info(request,f"Error occur {e} try again")
                return redirect('project_page')
            messages.info(request,' please wait about 5min for a review of you document')
            return redirect('project_page') 
    else: 

        form= CustomProjectsForm() 
    context=({ 
            "availiable_project_in_sch":project_download, 
            # "user_scho":user_shc ,
            'courses':courses, 
            'selected_course':courseid,
            'form':form 
        })  
    return render(request,'projects.html',context) 


def project_details(request, id):
    try: 
            project = Project.objects.get(id=id) 
            if request.user.is_authenticated: 
                try: 
                    user_info=CustomUser.objects.get(username=request.user)
                except CustomUser.DoesNotExist: 
                    messages.info(request,'Provide all info during registration') 
                    return redirect('project_page')   
                user_school=user_info.school  
                total_download=DownloadedProjects.objects.filter(projects=project,school=user_school).count() 
                view_downlaoder=DownloadedProjects.objects.filter(projects=project,school=user_school)
                has_paid = project.payments.filter(bought_by=request.user, is_paid=True).exists() 
                if not has_paid:    
                        transaction_id = str(uuid.uuid4())
                        Payment.objects.create( 
                            amount=project.price, 
                            transaction_id=transaction_id,  
                            is_paid=False, 
                            bought_by=request.user, 
                            project=project   
                        )     

                else: 
                        transaction_id=None 

                return render(request, "project_details.html", {
                        "project_details": project, 
                        "transaction_id": transaction_id, 
                        "PAYSTACK_PUBLIC_KEY": os.getenv("PAYSTACK_PUBLIC_KEY"),
                        'is_paid':has_paid ,
                        'total_download':total_download,
                        'downloaders':view_downlaoder 
                    })    
            return render(request,'project_details.html',{"project_details": project})
    except Project.DoesNotExist:
            messages.error(request,'No such project exit')
            return redirect('project_page')  
        
    # return render(request, "project_details.html", {
    #     "project_details": project,
    #     "paid": has_paid,
    # })


@login_required
def paymentview(request,project_id):
    user=request.user  
    projectid=Project.objects.get(id=project_id)

    transaction_id=str(uuid.uuid4()) 

    payment=Payment.objects.create(
        amount= projectid.price,
        transaction_id=transaction_id,
        is_paid=False,
        bought_by=user,
        project=projectid, 
    ) 

    headers = {
        "Authorization": f"Bearer {os.getenv('PAYSTACK_SECRET_KEY')}",
        "Content-Type": "application/json",
    }  

    data={
        'email':user.email,
        'amount':int(payment.amount*100),
        'reference':transaction_id,  
        "callback_url": "http://127.0.0.1:8000/payment/verify/",
    }

    try:
        response=requests.post({os.getenv("PAYSTACK_INITIALIZE_URL")},json=data,headers=headers) 
        res_data=response.json() 
    except ConnectionError as e:   
        messages.error(request,"⚠️Internet Connection lost or loss internet. Try again:", e)
        return redirect('project_page')
    except Exception as e:  
        messages.error(request,f"Something went wrong {e}")
        return redirect('project_page')

    if res_data['status']:
        auth_url = res_data['data']['authorization_url']
        return redirect(auth_url)
    else: 
        return redirect("payment_failed")

@login_required
def verify_payment(request):
    reference = request.GET.get("reference")

    
    headers = {"Authorization": f"Bearer {os.getenv('PAYSTACK_SECRET_KEY')}"} 
    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    res_data = response.json()

    if res_data['status'] and res_data['data']['status'] == "success":
        
        try:  
            payment = Payment.objects.get(transaction_id=reference)
            payment.is_paid = True  
            payment.save()  
            
            if request.user.school: 
                download_proj_in_schoo=DownloadedProjects.objects.create(
                    school=request.user.school,
                    projects=payment.project,
                    downloaders=request.user
                )     
                download_proj_in_schoo.save() 
            else:
                messages.info(request,'Please make sure u have all required info')
                return redirect('dashboard') 

            # sending email to develop when his/her project is bought 
            user_project_id=payment.project.id 
            try:
                auto_assign_status=Project.objects.get(id=user_project_id)
            except Project.DoesNotExist:
                messages.error(request,"Counld not get info of the uploader")
                return redirect('project_page') 
            auto_assign_status.status="Bought"
            auto_assign_status.save()   
            get_mail=Payment.objects.filter(project=user_project_id).first() 
            try:     
                sendmail=EmailMessage( 
                    subject=f"Congrat {get_mail.project.uploaded_by.username}",
                    body=f"{request.user.username} bought {get_mail.project.name} you project ",
                    from_email=settings.EMAIL_HOST_USER, 
                    to=[get_mail.project.uploaded_by.email],
                    bcc=['nanagrrr@proton.me'],
                      
                )   
                sendmail.send()
                
            except Exception as e:
                print(e) 

            return JsonResponse({"status":"success"})
        except Payment.DoesNotExist:
             return JsonResponse({"status": "failed", "error": "Payment not found with the transaction id"})

    else: 
        return JsonResponse({"status": "failed", "error": "Verification failed"})

@login_required
def payment_fail(request):
    return render(request,'paymentfail.html')

@login_required
def receipt(request):
    user_receipt=Payment.objects.filter(bought_by=request.user,is_paid=True) 
    return render(request,'receipt.html',{'receipt':user_receipt})  
    

@login_required
def upload_project(request):
    if request.method == 'POST':
        form = DeveloperProjectUploadForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.uploaded_by = request.user
            project_name=request.POST['name']
              
            project.save()
            try:
                send_mail(
                        subject="A new project",
                        message=f"A new project has been uploaded project name {project_name}",
                        from_email=f"Project Upload <{settings.EMAIL_HOST_USER}>",
                        recipient_list=[settings.EMAIL_HOST_USER],
                        fail_silently=False 
                )
            except BadHeaderError as e:
                messages.error(request,f"Error occur {e}")
                return redirect('project_page') 
            
            except smtplib.SMTPException as e:
                messages.error(request,f"{e} error occur")
                return redirect('project_page')
            
            except Exception as e:
                print(e) 
            messages.success(request, 'Project uploaded successfully! We will notify you when it approved. Thank You')
            return redirect('project_page')
              
        else: 
            messages.error(request, 'Please correct the errors below.')
            return redirect('upload_project') 
    else: 
        agreement=Agreement.objects.all()
        form = DeveloperProjectUploadForm()
        
    return render(request, 'upload_project.html', {'form': form,'agreement':agreement}) 

@login_required
def developersProject(request):
    your_uploaded_project=Project.objects.filter(uploaded_by=request.user,is_deleted=False) 
     
    return render(request,'my_projects.html',{'my_projects':your_uploaded_project})
    
@login_required
def myproject_customers(request,id):
    try:
        project_info=Project.objects.get(id=id) 
    except Project.DoesNotExist:
        messages.error(request,"Your project could not be found. Contact the support team")  
        return redirect('project_page') 
    users_who_bought_project=Payment.objects.filter(project=project_info,is_paid=True) 
    return render(request,'my_customers.html',{'my_customers':users_who_bought_project,'project_info':project_info})

@login_required
def deleteProject(request,project_id):  
    my_project=Project.objects.get(id=project_id) 
    my_project.is_deleted="True" 
    my_project.save()  
    try:     
        send_mail( 
            subject=f"PROJECT DELETED",
            message=f"{request.user} has deleted his project {my_project.name}",
            from_email=f"PROJECT DELETED<{settings.EMAIL_HOST_USER}>", 
            recipient_list=[settings.EMAIL_HOST_USER] 
        )   
    except BadHeaderError as e:
                messages.error(request,f"Error occur {e}")
                return redirect('project_page') 
    except smtplib.SMTPException as e:
                messages.error(request,f"{e} error occur")
                return redirect('project_page')  
    except Exception as e:
            messages.error(request,f"Error occur {e}") 
    messages.info(request,'Project deleted')  
    return redirect('my_uploaded_projects') 

@login_required
def update_project(request,id):
    myproject=get_object_or_404(Project,id=id)
    if request.method=='POST':  
        form=DeveloperProjectUploadForm(request.POST, instance=myproject) 
        if form.is_valid():  
            form.save() 
            messages.info(request,'Project updated')
            return redirect('project_page') 
        else: 
            messages.error(request,'an error occur please try again')
            return redirect('edit_project') 

    else:
        form=DeveloperProjectUploadForm(instance=myproject)
        return render(request,'edit_project.html',{'form':form})


@login_required
def download_receipt(request,payment_id):
    payment=Payment.objects.get(id=payment_id) 
    if payment.bought_by != request.user and not request.user.is_staff:
        return HttpResponse("Forbidden", status=403)

    context = { 
        "payment": payment 
    }

    pdf_bytes = render_to_pdf("receipt_dpf.html", context)  
    if pdf_bytes:
        filename = f"receipt_{payment.transaction_id}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    return HttpResponse("Error generating PDF", status=500)


# profile editing
@login_required
def profile(request):
    return render(request, 'dashboard.html', {'user': request.user})


# edit profile view 
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')  
    else: 
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form})


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('project_page')


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)

            user.save()
            
            # Authenticate and login the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:  
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

# new authentication 
def auth_view(request):
    if request.user.is_authenticated:
        return redirect('project_page')  
    
    login_form = CustomAuthenticationForm()
    signup_form = CustomUserCreationForm()
    
    if request.method == 'POST':   
        if 'login' in request.POST:  
            login_form = CustomAuthenticationForm(request, data=request.POST)
            if login_form.is_valid():    
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:   
                    login(request, user) 
                    messages.success(request, f"Welcome back, {username}!")
                    return redirect('dashboard')   
                else:  
                    messages.error(request, "Invalid username or password.")
            else:   
                messages.error(request, "Invalid username or password.")
                
        elif 'signup' in request.POST: 
            signup_form = CustomUserCreationForm(request.POST, request.FILES)
            if signup_form.is_valid(): 
                user = signup_form.save()
                login(request, user) 
                messages.success(request, f"Account created successfully! Welcome, {user.username}!")
                return redirect('dashboard')  
            else: 
                messages.error(request, "Error occur. Please click on the create account again to correct the errors .")
    
    return render(request, 'auth.html', {
        'login_form': login_form, 
        'signup_form': signup_form
    })


# current purechases
 
@login_required
def todays_purchases(request):
    today = timezone.now().date()
    payments = Payment.objects.filter(
        payment_date__date=today,
        is_paid=True
    ) 
    return render(request, 'todays_purchases.html', {'payments': payments})
