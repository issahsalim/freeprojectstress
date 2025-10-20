from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    path('', views.projects_view, name="project_page"), 
    path('signup/', views.signup_view, name='signup'),
    path('auth/',views.auth_view,name='auth'), 
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('project_details/<int:id>/', views.project_details, name='project_details'),
    path('buy/<int:project_id>/',views.paymentview,name="buy_project"),
    path("payment/verify/", views.verify_payment, name="verify_payment"),
    path('payment_failed',views.payment_fail,name="payment_failed"), 
    path('receipt',views.receipt,name="receipt"), 
    path('downlaodreceipt/<int:payment_id>/pdf/', views.download_receipt, name='download_receipt'),
    path('upload/', views.upload_project, name='upload_project'),
    path('delete_project/<int:project_id>/', views.deleteProject, name='delete_project'), 
    path('my_uploaded_projects',views.developersProject,name="my_uploaded_projects"), 
    path('update_project/<int:id>/',views.update_project,name="update_project"), 
    path('profile/',views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('my_customers/<int:id>/',views.myproject_customers,name='my_customers'), 
    path('todays-purchases/', views.todays_purchases, name='todays_purchases'),
    
    # Password reset URLs 
    path('password_reset/',views.CustomPasswordResetView.as_view( 
         template_name='reset_password.html',
         email_template_name="email_reset_password.html", 
         html_email_template_name="email_reset_password.html",
     ),name='password_reset'),  
    
    
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(
         template_name="reset_password_done.html",
     
     ),name="password_reset_done"),

    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(
         template_name="reset_password_confirm.html"
     ),name="password_reset_confirm"),

    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(
          template_name="reset_password_complete.html"  
     ),name='password_reset_complete'),


]

