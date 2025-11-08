from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'bio')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Escribe una breve biografía...'}),
        }
        labels = {
            'profile_picture': 'Foto de perfil',
            'bio': 'Biografía',
        }
