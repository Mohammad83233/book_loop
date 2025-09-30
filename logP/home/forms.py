from django import forms
from .models import UserProfile, Book, Review, Report

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 
            'last_name', 
            'gender', 
            'profile_pic', 
            'interested_genres', 
            'looking_genres',
            'location',
            'latitude',
            'longitude',
        ]
        widgets = {
            'interested_genres': forms.CheckboxSelectMultiple(),
            'looking_genres': forms.CheckboxSelectMultiple(),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'condition_rating', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'condition_rating': forms.RadioSelect,
        }
        labels = {
            'condition_rating': 'Book Condition (1=Poor, 5=Excellent)'
        }

class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        ('', 'Select a Rating'),
        (5, '★★★★★ Excellent'),(4, '★★★★☆ Good'),(3, '★★★☆☆ Average'),
        (2, '★★☆☆☆ Fair'),(1, '★☆☆☆☆ Poor'),
    ]
    book_rating = forms.ChoiceField(choices=RATING_CHOICES, label="How was the book's condition?")
    exchange_rating = forms.ChoiceField(choices=RATING_CHOICES, label="How was the exchange experience with the seller?")
    class Meta:
        model = Review
        fields = ['book_rating', 'exchange_rating', 'comment']
        widgets = { 'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your thoughts on the book and the exchange...'}), }
        labels = { 'comment': 'Additional Comments (Optional)', }

class SellerReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        ('', 'Select a Rating'),
        (5, '★★★★★ Excellent'),(4, '★★★★☆ Good'),(3, '★★★☆☆ Average'),
        (2, '★★☆☆☆ Fair'),(1, '★☆☆☆☆ Poor'),
    ]
    exchange_rating = forms.ChoiceField(choices=RATING_CHOICES, label="How was the exchange experience with the buyer?")
    class Meta:
        model = Review
        fields = ['exchange_rating', 'comment']
        widgets = { 'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Was the other user friendly and punctual?'}),}
        labels = { 'comment': 'Additional Comments (Optional)',}

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'details']
        widgets = {
            'details': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Please provide any additional details...'}),
        }
        labels = {
            'reason': 'Reason for Report',
            'details': 'Details (Optional)',
        }