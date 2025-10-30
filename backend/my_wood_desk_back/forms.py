from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión personalizado."""

    username = forms.CharField(
        label=_('Usuario o Email'),
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu usuario o email',
            'autofocus': True
        })
    )

    password = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña'
        })
    )

    remember_me = forms.BooleanField(
        label=_('Recordarme'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username'),
            Field('password'),
            Field('remember_me', css_class='form-check'),
            HTML('<div class="d-grid gap-2 mt-3">'),
            Submit('submit', 'Iniciar Sesión', css_class='btn btn-primary'),
            HTML('</div>'),
            HTML('<div class="text-center mt-3"><a href="{% url \'register\' %}">¿No tienes cuenta? Regístrate</a></div>')
        )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Permitir login con email o username
            user = authenticate(username=username, password=password)

            if user is None:
                # Intenta autenticar por email
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass

            if user is None:
                raise forms.ValidationError(
                    _('Usuario/email o contraseña incorrectos.'),
                    code='invalid_login'
                )
            elif not user.is_active:
                raise forms.ValidationError(
                    _('Esta cuenta está desactivada.'),
                    code='inactive'
                )

            self.user_cache = user

        return self.cleaned_data


# Con UserCreationForm se usa PasswordInput, aplica validaciones de seguridad
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label=_('Email'),
        required=True,
        help_text=_('Requerido. Ingresa un email válido.'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Elige un nombre de usuario'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases Bootstrap a los campos de contraseña
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirma contraseña'})

        # Crispy forms helper para controlar layout y botón
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username'),
            Field('email'),
            Field('password1'),
            Field('password2'),
            HTML('<div class="d-grid gap-2 mt-3">'),
            Submit('submit', 'Registrarse', css_class='btn btn-primary'),
            HTML('</div>'),
            HTML('<div class="text-center mt-3"><a href="{% url \'login\' %}">¿Ya tienes cuenta? Inicia sesión</a></div>')
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Este email ya está registrado.'))
        return email
