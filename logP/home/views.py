
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import UserProfile, Book, Genre, ChatRoom, ChatMessage
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

@login_required
def my_listed_books(request):
    queryset = Book.objects.filter(user=request.user).order_by('-created_at')
    
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


# --- VIEWS FOR SIMPLE CHAT SYSTEM ---

@login_required
def start_chat(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.user == request.user:
        messages.error(request, "You cannot start a chat about your own book.")
        return redirect('browse_books')
    
    chat_room, created = ChatRoom.objects.get_or_create(
        book=book,
        buyer=request.user,
        seller=book.user
    )
    return redirect('chat_room', room_id=chat_room.id)

# --- ✅ MODIFIED THIS VIEW ---
@login_required
def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    if request.user != chat_room.buyer and request.user != chat_room.seller:
        messages.error(request, "You do not have permission to view this chat.")
        return redirect('dashboard')
    
    messages_list = ChatMessage.objects.filter(room=chat_room).order_by('timestamp')
    
    # Mark messages sent by the OTHER user as read
    ChatMessage.objects.filter(room=chat_room).exclude(sender=request.user).update(is_read=True)
    
    context = {
        'room': chat_room,
        'messages': messages_list
    }
    return render(request, 'home/simple_chat.html', context)

@login_required
def send_message(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    if request.method == 'POST':
        content = request.POST.get('message_content', '').strip()
        if content:
            ChatMessage.objects.create(
                room=chat_room,
                sender=request.user,
                message_content=content
            )
    return redirect('chat_room', room_id=room_id)

# --- ✅ MODIFIED THIS VIEW ---
@login_required
def my_chats(request):
    chat_rooms = ChatRoom.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).order_by('-created_at')

    for room in chat_rooms:
        room.unread_count = ChatMessage.objects.filter(
            room=room, is_read=False
        ).exclude(sender=request.user).count()

    context = {
        'chat_rooms': chat_rooms,
    }
    return render(request, 'home/my_chats.html', context)