from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
    path('signup/', views.signup, name='signup'),
    path('shows-and-events/', views.shows_and_events, name='shows-and-events'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('change-password/', views.change_password, name='change-password'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('new-password/', views.new_password, name='new-password'),
    path('profile/', views.profile, name='profile'),
    path('manager-add-event/', views.manager_add_event, name='manager-add-event'),
    path('manager-view-event/', views.manager_view_event, name='manager-view-event'),
    path('manager-edit-event/<int:pk>/', views.manager_edit_event, name='manager-edit-event'),
    path('manager-delete-event/<int:pk>/', views.manager_delete_event, name='manager-delete-event'),
    path('book-event/<int:pk>/', views.book_event, name='book-event'),
    path('myevents', views.myevents, name='myevents'),
    path('payment/<int:pk>/', views.payment, name='payment'),
    path('create-checkout-session/', views.create_checkout_session, name='payment'),
    path('success.html/', views.success,name='success'),
    path('cancel.html/', views.cancel,name='cancel'),
    path('ajax/validate_email/', views.validate_signup, name='validate_email')
]