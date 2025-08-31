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
    path('book/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('book/delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('chat/start/<int:book_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/send/<int:room_id>/', views.send_message, name='send_message'),
    path('my-chats/', views.my_chats, name='my_chats'),
    path('chat/delete/<int:room_id>/', views.delete_chat, name='delete_chat'),
    path('chat/mark_exchanged/<int:room_id>/', views.mark_as_exchanged, name='mark_as_exchanged'),
    path('my-exchanged-books/', views.my_exchanged_books, name='my_exchanged_books'),
    path('book/favorite/<int:book_id>/', views.toggle_favorite, name='toggle_favorite'),

    # --- ✅ ADDED URL FOR FAVORITE BOOKS LIST PAGE ---
    path('my-favorites/', views.my_favorite_books, name='my_favorite_books'),


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