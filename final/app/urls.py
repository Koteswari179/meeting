# from django.contrib import admin
# from django.urls import path
# from app import views
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     # path('admin/', admin.site.urls),
#     path('signup/', views.signup_view, name='signup'),
#     # path('signin/', views.signin_view, name='signin'),
#     # path('dashboard/', views.dashboard, name='dashboard'),
#     path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),

#     path('signup/list/', views.signup_list, name='signup_list'),
#     path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
#     path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
#     path('login/', views.login_view, name='login'),
#     path('logout/', views.logout_view, name='logout'),
#     path('', views.home, name='home'),  # Home after login
    




#     path('forgot-password/', views.forgot_password_send_otp, name='forgot_password_send_otp'),
#     path('verify-otp/', views.verify_otp, name='verify_otp'),
#     path('create-new-password/', views.create_new_password, name='create_new_password'),



#     path("add-assignment/", views.add_assignment, name="add_assignment"),
#     path('assignments/edit/<int:pk>/', views.edit_assignment, name='edit_assignment'),
#     path('assignments/delete/<int:pk>/', views.delete_assignment, name='delete_assignment'),

#     path('assignments/', views.assignment_list, name='assignment_list'),

#     path("check-location/", views.check_location, name="check_location"),
#     path("get-location/", views.get_location, name="get_location"),
#     path('update-location/', views.update_location, name='update_location'),

#     path('meetings/', views.meetings_list, name='meetings_list'),
#     path('meeting/<int:id>/', views.meeting_detail, name='meeting_detail'),
#     path('meeting/<int:id>/edit/', views.edit_meeting, name='edit_meeting'),
#     path('meeting/<int:id>/delete/', views.delete_meeting, name='delete_meeting'),

#     path('download_meetings_pdf/', views.download_meetings_pdf, name='download_meetings_pdf'),




# ]

from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [

    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_send_otp, name='forgot_password_send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('create-new-password/', views.create_new_password, name='create_new_password'),

    # User management
    path('signup/list/', views.signup_list, name='signup_list'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

    # Dashboard
    path('', views.home, name='home'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),

    # Assignments
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('add-assignment/', views.add_assignment, name='add_assignment'),
    path('assignments/edit/<int:pk>/', views.edit_assignment, name='edit_assignment'),
    path('assignments/delete/<int:pk>/', views.delete_assignment, name='delete_assignment'),
    path('check-location/', views.check_location, name='check_location'),
    path('get-location/', views.get_location, name='get_location'),
    path('update-location/', views.update_location, name='update_location'),

    # Meetings
    path('meetings/', views.meetings_list, name='meetings_list'),
    path('meeting/<int:id>/', views.meeting_detail, name='meeting_detail'),
    path('meeting/<int:id>/edit/', views.edit_meeting, name='edit_meeting'),
    path('meeting/<int:id>/delete/', views.delete_meeting, name='delete_meeting'),
    path('download_meetings_pdf/', views.download_meetings_pdf, name='download_meetings_pdf'),
]
