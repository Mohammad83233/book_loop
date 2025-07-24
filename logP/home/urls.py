from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),

    # ✅ Route for listing a book
    path('list-book/', views.list_book, name='list_book'),

    # ✅ New route for viewing user's listed books
    path('my-listed-books/', views.my_listed_books, name='my_listed_books'),
]

