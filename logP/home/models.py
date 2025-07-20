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
        max_length=1,
        choices=[('M', 'Male'), ('F', 'Female')],
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

# ✅ Book model for listing books
class Book(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='book_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
