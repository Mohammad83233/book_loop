from django import forms
from .models import UserProfile, Book

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
            # --- ✅ ADDED THESE THREE FIELDS ---
            'location',
            'latitude',
            'longitude',
        ]
        widgets = {
            'interested_genres': forms.CheckboxSelectMultiple(),
            'looking_genres': forms.CheckboxSelectMultiple(),
            # --- ✅ ADDED WIDGETS TO HIDE LAT/LON ---
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'condition', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }