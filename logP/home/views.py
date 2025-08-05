
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import UserProfile, Book, Genre
from .forms import UserProfileForm, BookForm


def index(request):
    return render(request, 'home/index.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "❌ Email already in use.")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        UserProfile.objects.create(user=user)

        messages.success(request, "✅ Signup successful! Please log in.")
        return redirect('login')

    return render(request, 'home/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "❌ Invalid username or password.")
            return redirect('login')

    return render(request, 'home/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = None

    listed_books_count = Book.objects.filter(user=user).count()
    favourite_books_count = 0
    exchanged_books_count = 0

    context = {
        'profile': profile,
        'listed_books_count': listed_books_count,
        'favourite_books_count': favourite_books_count,
        'exchanged_books_count': exchanged_books_count,
        'user': user,
    }
    return render(request, 'home/dashboard.html', context)

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profile updated successfully!")
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'home/profile.html', {'form': form})

@login_required
def list_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.save()
            messages.success(request, "✅ Book listed successfully!")
            return redirect('dashboard')
    else:
        form = BookForm()
    return render(request, 'home/list_book.html', {'form': form})

# --- ✅ MODIFIED THIS VIEW TO ADD ADVANCED FILTERING ---
@login_required
def my_listed_books(request):
    # Start with ONLY the books that belong to the logged-in user.
    queryset = Book.objects.filter(user=request.user).order_by('-created_at')
    
    # Fetch all genres to populate the filter dropdown.
    genres = Genre.objects.all()

    # Get search/filter parameters from the URL.
    search_query = request.GET.get('q')
    selected_genre_id = request.GET.get('genre')
    selected_condition = request.GET.get('condition')

    # Apply filters if they exist.
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query)
        ).distinct()

    if selected_genre_id:
        queryset = queryset.filter(genre__id=selected_genre_id)

    if selected_condition:
        queryset = queryset.filter(condition=selected_condition)

    context = {
        'books': queryset,
        'genres': genres,
        'search_query': search_query,
        'selected_genre_id': int(selected_genre_id) if selected_genre_id else 0,
        'selected_condition': selected_condition,
    }
    return render(request, 'home/my_listed_books.html', context)

@login_required
def browse_books(request):
    queryset = Book.objects.exclude(user=request.user).order_by('-created_at')
    genres = Genre.objects.all()

    search_query = request.GET.get('q')
    selected_genre_id = request.GET.get('genre')
    selected_condition = request.GET.get('condition')

    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query)
        ).distinct()

    if selected_genre_id:
        queryset = queryset.filter(genre__id=selected_genre_id)

    if selected_condition:
        queryset = queryset.filter(condition=selected_condition)

    context = {
        'books': queryset,
        'genres': genres,
        'search_query': search_query,
        'selected_genre_id': int(selected_genre_id) if selected_genre_id else 0,
        'selected_condition': selected_condition,
    }
    return render(request, 'home/browse_books.html', context)

@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{book.title}' has been updated successfully.")
            return redirect('my_listed_books')
    else:
        form = BookForm(instance=book)

    context = {
        'form': form,
        'book': book
    }
    return render(request, 'home/edit_book.html', context)


@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)

    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f"'{book_title}' has been deleted successfully.")
        return redirect('my_listed_books')

    return redirect('my_listed_books')