from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('list-book/', views.list_book, name='list_book'),
    path('my-listed-books/', views.my_listed_books, name='my_listed_books'),
    path('browse/', views.browse_books, name='browse_books'),

    # --- ✅ ADDED URLS FOR EDIT AND DELETE ---
    path('book/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('book/delete/<int:book_id>/', views.delete_book, name='delete_book'),


    # --- PASSWORD RESET URLS ---

    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='home/password_reset_form.html'
         ),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='home/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='home/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='home/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]