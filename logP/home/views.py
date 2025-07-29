
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q  # ✅ Import the Q object for complex lookups

from .models import UserProfile, Book
from .forms import UserProfileForm, BookForm

# ... (all your existing views like index, signup_view, login_view, etc. remain unchanged) ...

def index(request):
    return render(request, 'home/index.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "❌ Email already in use.")
            return redirect('signup')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Create user profile
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

    # ✅ Real count from DB
    listed_books_count = Book.objects.filter(user=user).count()

    # ❌ Dummy values (you can replace later)
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
    # Create or fetch the profile
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

@login_required
def my_listed_books(request):
    books = Book.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'home/my_listed_books.html', {'books': books})


# --- ✅ STEP 2 COMPLETE: Added the view for the marketplace page ---
@login_required
def browse_books(request):
    """
    This view displays all books listed by other users and handles the search functionality.
    """
    # Get the search query from the form submission. The name 'q' is a common convention.
    query = request.GET.get('q')

    # Start with a base queryset of all books, excluding those owned by the current user.
    books = Book.objects.exclude(user=request.user)

    # If the user submitted a search query, filter the queryset.
    if query:
        # Use a Q object to search across two fields: title and author.
        # The '|' (pipe) acts as an OR operator.
        # '__icontains' makes the search case-insensitive.
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        ).distinct()

    # Pass the final queryset and the query itself to the template.
    context = {
        'books': books,
        'query': query,
    }
    return render(request, 'home/browse_books.html', context)