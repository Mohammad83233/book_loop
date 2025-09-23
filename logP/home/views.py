from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
import requests
from collections import Counter

from .models import UserProfile, Book, Genre, ChatRoom, ChatMessage, FriendRequest, Review, UserTasteProfile,Report
from .forms import UserProfileForm, BookForm, ReviewForm, SellerReviewForm,ReportForm


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
    favourite_books_count = user.favorite_books.count()
    exchanged_books_count = Book.objects.filter(user=user, status='Exchanged').count()
    friend_request_count = FriendRequest.objects.filter(to_user=user).count()

    context = {
        'profile': profile,
        'listed_books_count': listed_books_count,
        'favourite_books_count': favourite_books_count,
        'exchanged_books_count': exchanged_books_count,
        'friend_request_count': friend_request_count,
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
            messages.success(request, f"'{book.title}' has been successfully listed!")
            return redirect('my_listed_books')
        else:
            messages.error(request, "The form details were invalid. Please try again.")
    
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
    user = request.user
    user_profile = get_object_or_404(UserProfile, user=user)
    genres = Genre.objects.all()

    # --- 1. GATHER USER'S PREFERENCE DATA ---
    taste_profile, created = UserTasteProfile.objects.get_or_create(user=user)
    preferred_genres = taste_profile.preferred_genres
    preferred_authors = taste_profile.preferred_authors
    stated_genres = list(user_profile.interested_genres.all()) + list(user_profile.looking_genres.all())
    stated_genre_names = [genre.name for genre in stated_genres]

    # --- 2. GET AND SCORE ALL BOOKS ---
    all_books = Book.objects.filter(status='Available').exclude(user=user).annotate(
        average_rating=Avg('reviews__book_rating'),
        review_count=Count('reviews')
    )

    scored_books = []
    for book in all_books:
        score = 0
        # High Priority Scoring
        if book.genre and book.genre.name in preferred_genres: score += 50
        if book.author in preferred_authors: score += 40
        # Low Priority Scoring
        if book.genre and book.genre.name in stated_genre_names: score += 10
        
        scored_books.append({'book': book, 'score': score})

    # --- 3. SORT ALL BOOKS BY AI SCORE ---
    sorted_books = sorted(scored_books, key=lambda x: x['score'], reverse=True)
    
    # This is now a sorted list of all book objects, with the best matches first
    queryset_list = [item['book'] for item in sorted_books]
    
    # --- 4. APPLY USER FILTERS (IF ANY) ---
    search_query = request.GET.get('q')
    selected_genre_id = request.GET.get('genre')
    selected_condition = request.GET.get('condition')

    if search_query:
        queryset_list = [
            book for book in queryset_list 
            if search_query.lower() in book.title.lower() or search_query.lower() in book.author.lower()
        ]
    if selected_genre_id:
        queryset_list = [
            book for book in queryset_list 
            if book.genre and book.genre.id == int(selected_genre_id)
        ]
    if selected_condition:
        queryset_list = [
            book for book in queryset_list 
            if book.condition == selected_condition
        ]

    context = {
        'books': queryset_list,
        'genres': genres,
        'page_title': "Browse & Discover Books",
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
    return render(request, 'home/edit_book.html', {'form': form, 'book': book})

@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    if request.method == 'POST':
        book.delete()
        messages.success(request, f"'{book.title}' has been deleted.")
        return redirect('my_listed_books')
    return redirect('my_listed_books')

# --- HELPER FUNCTION FOR AI ---
def update_taste_profile(user):
    taste_profile, created = UserTasteProfile.objects.get_or_create(user=user)
    interacted_books = Book.objects.filter(Q(favorited_by=user) | Q(exchanged_with=user)).distinct()
    if not interacted_books.exists(): return
    genre_counts = Counter(book.genre.name for book in interacted_books if book.genre)
    author_counts = Counter(book.author for book in interacted_books)
    taste_profile.preferred_genres = [genre for genre, count in genre_counts.most_common(5)]
    taste_profile.preferred_authors = [author for author, count in author_counts.most_common(5)]
    taste_profile.save()

# --- CHAT VIEWS ---
@login_required
def start_chat(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.user == request.user:
        messages.error(request, "You cannot chat about your own book.")
        return redirect('browse_books')
    chat_room, created = ChatRoom.objects.get_or_create(book=book, buyer=request.user, seller=book.user)
    return redirect('chat_room', room_id=chat_room.id)

@login_required
def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    if request.user != chat_room.buyer and request.user != chat_room.seller:
        messages.error(request, "You do not have permission to view this chat.")
        return redirect('dashboard')
    messages_list = ChatMessage.objects.filter(room=chat_room).order_by('timestamp')
    messages_list.exclude(sender=request.user).update(is_read=True)
    return render(request, 'home/simple_chat.html', {'room': chat_room, 'messages': messages_list})

@login_required
def send_message(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    if request.method == 'POST':
        content = request.POST.get('message_content', '').strip()
        if content:
            ChatMessage.objects.create(room=chat_room, sender=request.user, message_content=content)
    return redirect('chat_room', room_id=room_id)

@login_required
def my_chats(request):
    chat_rooms = ChatRoom.objects.filter(
        Q(buyer=request.user, buyer_deleted=False) | Q(seller=request.user, seller_deleted=False)
    ).distinct().order_by('-created_at')
    for room in chat_rooms:
        room.unread_count = ChatMessage.objects.filter(room=room, is_read=False).exclude(sender=request.user).count()
    return render(request, 'home/my_chats.html', {'chat_rooms': chat_rooms})

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
        messages.success(request, "Conversation removed.")
        return redirect('my_chats')
    return redirect('my_chats')

# --- BOOK STATUS & EXCHANGE VIEWS ---
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
            messages.success(request, f"'{book.title}' marked as exchanged.")
            update_taste_profile(chat_room.buyer)
        else:
            book.status = 'Available'
            book.exchanged_with = None
            messages.success(request, f"'{book.title}' is now available again.")
        book.save()
    return redirect('chat_room', room_id=room_id)

@login_required
def my_exchange_history(request):
    given_books = Book.objects.filter(user=request.user, status='Exchanged').order_by('-created_at')
    for book in given_books:
        book.has_been_reviewed = Review.objects.filter(book=book, reviewer=request.user, review_type='seller_review').exists()
    received_books = Book.objects.filter(exchanged_with=request.user).order_by('-created_at')
    for book in received_books:
        book.has_been_reviewed = Review.objects.filter(book=book, reviewer=request.user, review_type='buyer_review').exists()
    return render(request, 'home/my_exchange_history.html', {'given_books': given_books, 'received_books': received_books})

# --- FAVORITES VIEWS ---
@login_required
def toggle_favorite(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        if book.favorited_by.filter(id=request.user.id).exists():
            book.favorited_by.remove(request.user)
        else:
            book.favorited_by.add(request.user)
        update_taste_profile(request.user)
    return redirect(request.POST.get('next', 'browse_books'))

@login_required
def my_favorite_books(request):
    favorite_books = request.user.favorite_books.all()
    return render(request, 'home/my_favorite_books.html', {'books': favorite_books})

# --- FRIENDSHIP & PROFILE VIEWS ---
@login_required
def public_profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=profile_user)
    logged_in_user_profile = request.user.userprofile
    are_friends = logged_in_user_profile.friends.filter(id=profile_user.id).exists()
    request_sent = FriendRequest.objects.filter(from_user=request.user, to_user=profile_user).exists()
    request_received = FriendRequest.objects.filter(from_user=profile_user, to_user=request.user).exists()
    reviews = Review.objects.filter(reviewed_user=profile_user).order_by('-created_at')
    avg_ratings = reviews.aggregate(avg_book=Avg('book_rating'), avg_exchange=Avg('exchange_rating'))
    context = {
        'profile': profile, 'are_friends': are_friends, 'request_sent': request_sent,
        'request_received': request_received, 'reviews': reviews,
        'avg_book_rating': avg_ratings['avg_book'],
        'avg_exchange_rating': avg_ratings['avg_exchange'],
    }
    return render(request, 'home/public_profile.html', context)

@login_required
def send_friend_request(request, username):
    to_user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        if to_user == request.user:
            messages.error(request, "You cannot send a friend request to yourself.")
        elif not FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
            FriendRequest.objects.create(from_user=request.user, to_user=to_user)
            messages.success(request, f"Friend request sent to {username}.")
        else:
            messages.warning(request, f"You have already sent a friend request to {username}.")
    return redirect('public_profile', username=username)

@login_required
def my_friend_requests(request):
    friend_requests = FriendRequest.objects.filter(to_user=request.user)
    return render(request, 'home/my_friend_requests.html', {'friend_requests': friend_requests})

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    if request.method == 'POST':
        friend_request.from_user.userprofile.friends.add(request.user)
        request.user.userprofile.friends.add(friend_request.from_user)
        friend_request.delete()
        messages.success(request, f"You are now friends with {friend_request.from_user.username}.")
    return redirect('my_friend_requests')

@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    if request.method == 'POST':
        friend_request.delete()
        messages.info(request, f"Friend request from {friend_request.from_user.username} declined.")
    return redirect('my_friend_requests')

# --- MAP & REVIEW VIEWS ---
@login_required
def friend_map_view(request):
    current_user_profile = get_object_or_404(UserProfile, user=request.user)
    friends = current_user_profile.friends.all()
    friend_ids = [friend.id for friend in friends]
    stranger_profiles = UserProfile.objects.exclude(
        Q(user=request.user) | Q(user__id__in=friend_ids)
    ).exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    users_data = []
    for friend_user in friends:
        friend_profile = friend_user.userprofile
        if friend_profile.latitude and friend_profile.longitude:
            users_data.append({
                'username': friend_profile.user.username, 'lat': friend_profile.latitude,
                'lng': friend_profile.longitude, 'is_friend': True, 'location': friend_profile.location,
            })
    for other_profile in stranger_profiles:
        users_data.append({
            'username': other_profile.user.username, 'lat': other_profile.latitude,
            'lng': other_profile.longitude, 'is_friend': False, 'location': other_profile.location,
        })
    context = {
        'current_user_lat': current_user_profile.latitude,
        'current_user_lng': current_user_profile.longitude,
        'users_data': users_data,
    }
    return render(request, 'home/friend_map.html', context)

@login_required
def user_books_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    books = Book.objects.filter(user=profile_user, status='Available').order_by('-created_at')
    return render(request, 'home/user_books.html', {'profile_user': profile_user, 'books': books})

@login_required
def leave_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    review_type = request.GET.get('type')

    person_being_reviewed = None

    if review_type == 'buyer_review' and request.user == book.exchanged_with:
        reviewer = request.user
        reviewed_user = book.user
        person_being_reviewed = reviewed_user
        form_class = ReviewForm
    elif review_type == 'seller_review' and request.user == book.user:
        reviewer = request.user
        reviewed_user = book.exchanged_with
        person_being_reviewed = reviewed_user
        form_class = SellerReviewForm
    else:
        messages.error(request, "You do not have permission to leave this review.")
        return redirect('my_exchange_history')

    if Review.objects.filter(book=book, reviewer=reviewer, review_type=review_type).exists():
        messages.warning(request, "You have already submitted this review.")
        return redirect('my_exchange_history')

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.reviewed_user = reviewed_user
            review.reviewer = reviewer
            review.review_type = review_type
            if review_type == 'seller_review':
                review.book_rating = None
            review.save()
            messages.success(request, "Your review has been submitted.")
            return redirect('public_profile', username=reviewed_user.username)
    else:
        form = form_class()
    
    return render(request, 'home/leave_review.html', {'form': form, 'book': book, 'person_being_reviewed': person_being_reviewed})

@login_required
def report_user(request, username):
    reported_user = get_object_or_404(User, username=username)

    # A user cannot report themselves
    if reported_user == request.user:
        messages.error(request, "You cannot report yourself.")
        return redirect('public_profile', username=username)

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reported_user = reported_user
            report.reporting_user = request.user
            report.save()
            messages.success(request, f"Your report against {username} has been submitted. Our admin team will review it shortly.")
            return redirect('public_profile', username=username)
    else:
        form = ReportForm()
    
    context = {
        'form': form,
        'reported_user': reported_user,
    }
    return render(request, 'home/report_user.html', context)