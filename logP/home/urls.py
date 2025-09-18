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
    path('my-favorites/', views.my_favorite_books, name='my_favorite_books'),
    path('user/<str:username>/', views.public_profile_view, name='public_profile'),

    # --- ✅ ADDED URL FOR SENDING A FRIEND REQUEST ---
    path('friend-request/send/<str:username>/', views.send_friend_request, name='send_friend_request'),

    path('friend-requests/', views.my_friend_requests, name='my_friend_requests'),

    path('friend-request/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend-request/decline/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('map/', views.friend_map_view, name='friend_map'),
    


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