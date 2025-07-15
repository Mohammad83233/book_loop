from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'first_name',
            'last_name',
            'gender',
            'profile_pic',
            'interested_genres',
            'looking_genres'
        ]
        widgets = {
            'interested_genres': forms.CheckboxSelectMultiple(),
            'looking_genres': forms.CheckboxSelectMultiple(),
        }
