from django import forms

class FormularioContacto(forms.Form):
    
    nombre = forms.CharField(
        label="Nombre",
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Tu nombre'})
    )

    email = forms.CharField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Tu de correo electrónico'})
    )

    contenido = forms.CharField(
        label="Contenido",
        widget=forms.Textarea(attrs={'placeholder': 'Escribe tu mensaje aquí'})
    )
