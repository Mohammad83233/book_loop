
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
    exchanged_books_count = Book.objects.filter(user=user, status='Exchanged').count()

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

@login_required
def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    if request.user != chat_room.buyer and request.user != chat_room.seller:
        messages.error(request, "You do not have permission to view this chat.")
        return redirect('dashboard')
    
    messages_list = ChatMessage.objects.filter(room=chat_room).order_by('timestamp')
    
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

@login_required
def my_chats(request):
    chat_rooms = ChatRoom.objects.filter(
        Q(buyer=request.user, buyer_deleted=False) | 
        Q(seller=request.user, seller_deleted=False)
    ).distinct().order_by('-created_at')

    for room in chat_rooms:
        room.unread_count = ChatMessage.objects.filter(
            room=room, is_read=False
        ).exclude(sender=request.user).count()

    context = {
        'chat_rooms': chat_rooms,
    }
    return render(request, 'home/my_chats.html', context)

@login_required
def delete_chat(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    if request.user != chat_room.buyer and request.user != chat_room.seller:
        messages.error(request, "You do not have permission to modify this chat.")
        return redirect('my_chats')

    if request.method == 'POST':
        if request.user == chat_room.buyer:
            chat_room.buyer_deleted = True
        elif request.user == chat_room.seller:
            chat_room.seller_deleted = True
        
        chat_room.save()
        
        if chat_room.buyer_deleted and chat_room.seller_deleted:
            chat_room.delete()

        messages.success(request, "Conversation has been removed from your view.")
        return redirect('my_chats')

    return redirect('my_chats')

@login_required
def mark_as_exchanged(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    book = chat_room.book

    if request.user != book.user:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('chat_room', room_id=room_id)
    
    if request.method == 'POST':
        if book.status == 'Available':
            book.status = 'Exchanged'
            book.exchanged_with = chat_room.buyer
            messages.success(request, f"'{book.title}' has been marked as Exchanged with {chat_room.buyer.username}.")
        else:
            book.status = 'Available'
            book.exchanged_with = None
            messages.success(request, f"'{book.title}' is now available for exchange again.")
        
        book.save()

    return redirect('chat_room', room_id=room_id)

@login_required
def my_exchanged_books(request):
    exchanged_books = Book.objects.filter(
        user=request.user,
        status='Exchanged'
    ).order_by('-created_at')

    context = {
        'books': exchanged_books,
    }
    return render(request, 'home/my_exchanged_books.html', context)

@login_required
def toggle_favorite(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        if book.favorited_by.filter(id=request.user.id).exists():
            book.favorited_by.remove(request.user)
            messages.success(request, f"'{book.title}' removed from your favorites.")
        else:
            book.favorited_by.add(request.user)
            messages.success(request, f"'{book.title}' added to your favorites.")
            
    return redirect('browse_books')

# --- ✅ ADDED NEW VIEW FOR FAVORITE BOOKS LIST ---
@login_required
def my_favorite_books(request):
    favorite_books = request.user.favorite_books.all()
    context = {
        'books': favorite_books
    }
    return render(request, 'home/my_favorite_books.html', context)