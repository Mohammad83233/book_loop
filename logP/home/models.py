from django.db import models
from django.contrib.auth.models import User

# Genre model to hold available genres
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# UserProfile model linked to Django's built-in User
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female')],
        blank=True
    )

    profile_pic = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )

    interested_genres = models.ManyToManyField(
        Genre,
        related_name='interested_users',
        blank=True
    )

    looking_genres = models.ManyToManyField(
        Genre,
        related_name='looking_users',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

# Book model for listing books
class Book(models.Model):
    CONDITION_CHOICES = [
        ('New', 'New'),
        ('Like New', 'Like New'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Exchanged', 'Exchanged'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='book_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Available')
    
    # --- ✅ ADDED THIS FIELD ---
    exchanged_with = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_books'
    )

    def __str__(self):
        return self.title

# --- CHAT MODELS ---

class ChatRoom(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chat_rooms')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_buyer')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_seller')
    created_at = models.DateTimeField(auto_now_add=True)
    
    buyer_deleted = models.BooleanField(default=False)
    seller_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.book.title} - Chat ({self.buyer.username} & {self.seller.username})"

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.message_content[:30]}"