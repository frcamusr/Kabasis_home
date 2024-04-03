from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Empresa, Area  # Importa tu modelo personalizado

from django.shortcuts import render, redirect,  get_object_or_404
from django.views.generic import View
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from django.contrib.auth.password_validation import password_validators_help_text_html

from collections import OrderedDict

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password


from django import forms
from django.db import IntegrityError
from .models import Area



import re
from django import forms  # Asegúrate de tener este import para usar forms.ValidationError

import re
from django import forms  # Asegúrate de tener este import para usar forms.ValidationError

from itertools import cycle

def validar_rut(rut):
    rut = rut.replace(".", "").replace("-", "")
    cuerpo, dv = rut[:-1], rut[-1].upper()

    # Asegurar que el rut tiene la longitud mínima esperada y que el cuerpo es numérico
    if len(cuerpo) < 7 or not cuerpo.isdigit() or dv not in "0123456789K":
        raise forms.ValidationError("El RUT debe estar en un formato correcto.")

    # Invertir el cuerpo para el cálculo
    cuerpo_reverso = map(int, reversed(cuerpo))

    # Calcular dígito verificador
    suma = sum(digito * factor for digito, factor in zip(cuerpo_reverso, cycle([2, 3, 4, 5, 6, 7])))
    resto = suma % 11
    dv_calculado = {10: 'K', 11: '0'}.get(11 - resto, str(11 - resto))

    if dv != dv_calculado:
        raise forms.ValidationError("El dígito verificador no es válido.")

    # Formatear el RUT correctamente
    rut_formateado = f"{int(cuerpo):,}".replace(",", ".") + "-" + dv

    return rut_formateado



##Formulario creación de usuarios personalizados
class CustomUserCreationForm(UserCreationForm):

    rut = forms.CharField(
        max_length=12,
        required=False,
        label="RUT",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[validar_rut],  # Aquí aplicas la validación
    )

    tipo_usuario = forms.ChoiceField(
        choices=CustomUser.TIPO_USUARIO_CHOICES,
        label="Tipo de Usuario",
        required=True,
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label="Imagen de Perfil"
    )

    razon_social = forms.ModelChoiceField(
        queryset=Empresa.objects.none(),
        label="Razón social",
        required=False,
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

    area = forms.ModelChoiceField(
        queryset=Area.objects.none(),
        label="Área",
        required=False,
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('current_user', None)
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        # Establecer y bloquear el tipo de usuario en 'Alumno'
        self.fields['tipo_usuario'].initial = 'Alumno'
        self.fields['tipo_usuario'].disabled = True

        # Cambiar el label de los campos first_name y last_name
        self.fields['first_name'].label = 'Nombres'
        self.fields['last_name'].label = 'Apellidos'


        # Filtrar las opciones de área según la empresa del usuario
        if user and user.empresa:
            self.fields['area'].queryset = Area.objects.filter(empresa=user.empresa)

        # Configurar el campo de empresa
        if user and user.tipo_usuario == 'Administrador Kabasis':
            self.fields['razon_social'].queryset = Empresa.objects.all()
        elif user and user.empresa:
            self.fields['razon_social'].queryset = Empresa.objects.filter(id=user.empresa.id)
            self.fields['razon_social'].initial = user.empresa
            self.fields['razon_social'].disabled = True  # Opcional: deshabilitar el campo para que no se pueda cambiar

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'tipo_usuario', 'first_name', 'last_name', 'rut', 'profile_picture', 'password1', 'password2']


##Formulario creación de usuarios personalizados tipo asistente
class CustomUserAsistenteCreationForm(UserCreationForm):

    rut = forms.CharField(
        max_length=12,  # Asegúrate de que coincida con la definición en tu modelo
        required=False,  # O ajusta según tus necesidades
        label="RUT",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )


    tipo_usuario = forms.ChoiceField(
        choices=CustomUser.TIPO_USUARIO_CHOICES,
        label="Tipo de Usuario",
        required=True,
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label="Imagen de Perfil"
    )

    razon_social = forms.ModelChoiceField(
        queryset=Empresa.objects.none(),
        label="Razón social",
        required=False,
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

    area = forms.ModelChoiceField(
        queryset=Area.objects.none(),
        label="Área",
        required=False,
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('current_user', None)
        super(CustomUserAsistenteCreationForm, self).__init__(*args, **kwargs)

        # Establecer y bloquear el tipo de usuario en 'Asistente Administrativo'
        self.fields['tipo_usuario'].initial = 'Asistente Administrativo'
        self.fields['tipo_usuario'].disabled = True

        # Cambiar el label de los campos first_name y last_name
        self.fields['first_name'].label = 'Nombres'
        self.fields['last_name'].label = 'Apellidos'


        # Filtrar las opciones de área según la empresa del usuario
        if user and user.empresa:
            self.fields['area'].queryset = Area.objects.filter(empresa=user.empresa)

        # Configurar el campo de empresa
        if user and user.tipo_usuario == 'Administrador Kabasis':
            self.fields['razon_social'].queryset = Empresa.objects.all()
        elif user and user.empresa:
            self.fields['razon_social'].queryset = Empresa.objects.filter(id=user.empresa.id)
            self.fields['razon_social'].initial = user.empresa
            self.fields['razon_social'].disabled = True  # Opcional: deshabilitar el campo para que no se pueda cambiar

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'rut', 'tipo_usuario', 'profile_picture', 'password1', 'password2']


##Formulario creación de usuarios personalizados
class CustomUserAdministradorCreationForm(UserCreationForm):

    rut = forms.CharField(
        max_length=12,  # Asegúrate de que coincida con la definición en tu modelo
        required=False,  # O ajusta según tus necesidades
        label="RUT",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    tipo_usuario = forms.ChoiceField(
        choices=CustomUser.TIPO_USUARIO_CHOICES,
        label="Tipo de Usuario",
        required=True,
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label="Imagen de Perfil"
    )

    razon_social = forms.ModelChoiceField(
        queryset=Empresa.objects.none(),
        label="Razón social",
        required=False,
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

    area = forms.ModelChoiceField(
        queryset=Area.objects.none(),
        label="Área",
        required=False,
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('current_user', None)
        super(CustomUserAdministradorCreationForm, self).__init__(*args, **kwargs)

        # Establecer y bloquear el tipo de usuario en 'Administrador'
        self.fields['tipo_usuario'].initial = 'Administrador'
        self.fields['tipo_usuario'].disabled = True

        # Cambiar el label de los campos first_name y last_name
        self.fields['first_name'].label = 'Nombres'
        self.fields['last_name'].label = 'Apellidos'

        # Filtrar las opciones de área según la empresa del usuario
        if user and user.empresa:
            self.fields['area'].queryset = Area.objects.filter(empresa=user.empresa)

        # Configurar el campo de empresa
        if user and user.tipo_usuario == 'Administrador Kabasis':
            self.fields['razon_social'].queryset = Empresa.objects.all()
        elif user and user.empresa:
            self.fields['razon_social'].queryset = Empresa.objects.filter(id=user.empresa.id)
            self.fields['razon_social'].initial = user.empresa
            self.fields['razon_social'].disabled = True  # Opcional: deshabilitar el campo para que no se pueda cambiar

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'rut', 'tipo_usuario', 'profile_picture', 'password1', 'password2']

##tarjeta ver perfil

User = get_user_model()

class UserProfileForm(forms.ModelForm):

    rut = forms.CharField(
        max_length=12,  # Asegúrate de que coincida con la definición en tu modelo
        required=False,  # O ajusta según tus necesidades
        label="RUT",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    current_password = forms.CharField(widget=forms.PasswordInput(), required=False, label="Contraseña Actual")
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False, label="Nueva Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False, label="Confirmar Nueva Contraseña")

    class Meta:
        model = User
        fields = ['username', 'profile_picture', 'first_name', 'last_name', 'rut', 'current_password', 'new_password', 'confirm_password']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['new_password'].help_text = password_validators_help_text_html()
        # Cambiar el label de los campos first_name y last_name
        self.fields['first_name'].label = 'Nombres'
        self.fields['last_name'].label = 'Apellidos'

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get("current_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', "Las nuevas contraseñas no coinciden.")

        if current_password:
            if not check_password(current_password, self.instance.password):
                self.add_error('current_password', "La contraseña actual no es correcta.")
            elif not new_password:
                self.add_error('new_password', "Debe introducir una nueva contraseña.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user


##formulario crear empresa


##formulario Áreas
class AreaForm(forms.Form):
    nombres = forms.CharField(
        label='Nombres de áreas',
        widget=forms.Textarea(attrs={          
            # Añade aquí cualquier atributo adicional que necesites
        })
    )

    def save(self, user, commit=True):
        nombres_areas = [nombre.strip().capitalize() for nombre in self.cleaned_data['nombres'].split(',')]
        areas_creadas = []
        for nombre in nombres_areas:
            if nombre:
                area, created = Area.objects.get_or_create(nombre=nombre, defaults={'empresa': user.empresa})
                if not created:
                    # Si el área ya existía y no está asignada a ninguna empresa, la asignamos.
                    # Si el área ya estaba asignada a otra empresa, puedes decidir si actualizarla o no.
                    if area.empresa is None:
                        area.empresa = user.empresa
                        area.save()
                areas_creadas.append(area)
        return areas_creadas
    

class AreaFormInicio(forms.Form):
    nombres = forms.CharField(
        label='Nombres de áreas',
        widget=forms.Textarea(attrs={          
            # Añade aquí cualquier atributo adicional que necesites
        })
    )

    def save(self, user, commit=True):
        nombres_areas = [nombre.strip().capitalize() for nombre in self.cleaned_data['nombres'].split(',')]
        areas_creadas = []
        for nombre in nombres_areas:
            if nombre:
                area, created = Area.objects.get_or_create(nombre=nombre, defaults={'empresa': user.empresa})
                if not created:
                    # Si el área ya existía y no está asignada a ninguna empresa, la asignamos.
                    # Si el área ya estaba asignada a otra empresa, puedes decidir si actualizarla o no.
                    if area.empresa is None:
                        area.empresa = user.empresa
                        area.save()
                areas_creadas.append(area)
        return areas_creadas


class CSVUploadForm(forms.Form):
    archivo_csv = forms.FileField(label='Archivo CSV o XLSX')  # Cambia la etiqueta aquí

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CSVUploadForm, self).__init__(*args, **kwargs)
        if user and user.empresa:
            self.fields['area'] = forms.ModelChoiceField(
                queryset=Area.objects.filter(empresa=user.empresa),
                required=False,
                empty_label="Seleccione el Área"
            )



#formulario editar usuario alumno
class CustomUserUpdateForm(forms.ModelForm):

    rut = forms.CharField(
        max_length=12,  # Asegúrate de que coincida con la definición en tu modelo
        required=False,  # O ajusta según tus necesidades
        label="RUT",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    razon_social = forms.CharField(required=False)  # Campo existente para el nombre de la empresa
    area = forms.ModelChoiceField(
        queryset=Area.objects.none(),  # Inicialmente el queryset está vacío
        required=False,
        label="Área"
    )

    password1 = forms.CharField(
        label='Nueva Contraseña', 
        widget=forms.PasswordInput, 
        required=False
    )
    password2 = forms.CharField(
        label='Confirmar Nueva Contraseña', 
        widget=forms.PasswordInput, 
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'rut', 'profile_picture', 'razon_social', 'area', 'password1', 'password2', 'is_certificado']

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(CustomUserUpdateForm, self).__init__(*args, **kwargs)

        # Cambiar el label de los campos first_name y last_name
        self.fields['first_name'].label = 'Nombres'
        self.fields['last_name'].label = 'Apellidos'

        # Configurar el valor inicial para nombre_empresa y area si existen
        if self.instance and self.instance.empresa:
            self.fields['razon_social'].initial = self.instance.empresa.razon_social
            self.fields['area'].queryset = Area.objects.filter(empresa=self.instance.empresa)  # Cambio aquí
            if self.instance.area:
                self.fields['area'].initial = self.instance.area

        # Restringir la edición del campo nombre_empresa si el usuario actual no es 'Administrador Kabasis'
        if current_user and current_user.tipo_usuario != 'Administrador Kabasis':
            self.fields['razon_social'].disabled = True

        # Condición para mostrar o no el campo 'is_certificado'
        if current_user and current_user.tipo_usuario == 'Administrador Kabasis':
            self.fields['is_certificado'] = forms.BooleanField(
                required=False,  # Ajusta según tus necesidades
                label="Certificado",
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            )
        else:
            # Si decides añadir 'is_certificado' a los fields de Meta por defecto, asegúrate de excluirlo dinámicamente si no se cumple la condición
            if 'is_certificado' in self.fields:
                self.fields.pop('is_certificado')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super(CustomUserUpdateForm, self).save(commit=False)
        
        # Actualizar la empresa relacionada si es necesario
        social_razon = self.cleaned_data.get('razon_social')
        if social_razon:
            empresa, created = Empresa.objects.get_or_create(razon_social=social_razon)
            user.empresa = empresa

        # Actualizar el área relacionada
        area_seleccionada = self.cleaned_data.get('area')
        if area_seleccionada:
            user.area = area_seleccionada

         # Actualiza la contraseña si se proporcionó una nueva
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user
    

#formulario editar usuario asistente
class CustomUserAsistenteUpdateForm(forms.ModelForm):

    rut = forms.CharField(
        max_length=12,  # Asegúrate de que coincida con la definición en tu modelo
        required=False,  # O ajusta según tus necesidades
        label="RUT",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    razon_social = forms.CharField(required=False, disabled=True)  # Campo deshabilitado para el nombre de la empresa
    area = forms.ModelChoiceField(
        queryset=Area.objects.none(),  # Inicialmente el queryset está vacío
        required=False,
        label="Área"
    )

    password1 = forms.CharField(
        label='Nueva Contraseña', 
        widget=forms.PasswordInput, 
        required=False
    )
    password2 = forms.CharField(
        label='Confirmar Nueva Contraseña', 
        widget=forms.PasswordInput, 
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'rut', 'profile_picture', 'razon_social', 'area', 'password1', 'password2']


    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(CustomUserAsistenteUpdateForm, self).__init__(*args, **kwargs)

        # Cambiar el label de los campos first_name y last_name
        self.fields['first_name'].label = 'Nombres'
        self.fields['last_name'].label = 'Apellidos'

        # Configurar el valor inicial para nombre_empresa y area si existen
        if self.instance and self.instance.empresa:
            self.fields['razon_social'].initial = self.instance.empresa.razon_social
            self.fields['area'].queryset = Area.objects.filter(empresas_asociadas=self.instance.empresa)
            if self.instance.area:
                self.fields['area'].initial = self.instance.area

        # Restringir la edición del campo nombre_empresa si el usuario actual no es 'Administrador Kabasis'
        if current_user and current_user.tipo_usuario != 'Administrador Kabasis':
            self.fields['razon_social'].disabled = True

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super(CustomUserAsistenteUpdateForm, self).save(commit=False)
        
        # Actualizar la empresa relacionada si es necesario
        social_razon = self.cleaned_data.get('razon_social')
        if social_razon:
            empresa, created = Empresa.objects.get_or_create(razon_social=social_razon)
            user.empresa = empresa

        # Actualizar el área relacionada
        area_seleccionada = self.cleaned_data.get('area')
        if area_seleccionada:
            user.area = area_seleccionada

         # Actualiza la contraseña si se proporcionó una nueva
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user
    

#formulario editar usuario Administrador 
class CustomUserAdministradorUpdateForm(forms.ModelForm):

    rut = forms.CharField(
        max_length=12,  # Asegúrate de que coincida con la definición en tu modelo
        required=False,  # O ajusta según tus necesidades
        label="RUT",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    razon_social = forms.CharField(required=False, disabled=True)  # Campo deshabilitado para el nombre de la empresa
    area = forms.ModelChoiceField(
        queryset=Area.objects.none(),  # Inicialmente el queryset está vacío
        required=False,
        label="Área"
    )

    password1 = forms.CharField(
        label='Nueva Contraseña', 
        widget=forms.PasswordInput, 
        required=False
    )
    password2 = forms.CharField(
        label='Confirmar Nueva Contraseña', 
        widget=forms.PasswordInput, 
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'rut', 'profile_picture', 'razon_social', 'area', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)

        super(CustomUserAdministradorUpdateForm, self).__init__(*args, **kwargs)

        # Cambiar el label de los campos first_name y last_name
        self.fields['first_name'].label = 'Nombres'
        self.fields['last_name'].label = 'Apellidos'

        # Configurar el valor inicial para razon_social y area si existen
        if self.instance and self.instance.empresa:
            self.fields['razon_social'].initial = self.instance.empresa.razon_social
            self.fields['area'].queryset = Area.objects.filter(empresas_asociadas=self.instance.empresa)
            if self.instance.area:
                self.fields['area'].initial = self.instance.area

        if current_user:
            # Lógica adicional basada en current_user
            pass


    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super(CustomUserAdministradorUpdateForm, self).save(commit=False)
        
        # Actualizar la empresa relacionada si es necesario
        social_razon = self.cleaned_data.get('razon_social')
        if social_razon:
            empresa, created = Empresa.objects.get_or_create(razon_social=social_razon)
            user.empresa = empresa

        # Actualizar el área relacionada
        area_seleccionada = self.cleaned_data.get('area')
        if area_seleccionada:
            user.area = area_seleccionada

         # Actualiza la contraseña si se proporcionó una nueva
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user



from captcha.fields import CaptchaField

#formulario de ingreso de usuarios Administradores
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico', required=True, widget=forms.TextInput(attrs={'placeholder': 'Ingrese su correo electrónico'}))
    username = forms.CharField(label='Nombre de usuario', required=True, widget=forms.TextInput(attrs={'placeholder': 'Ingrese su nombre de usuario'}))
    first_name = forms.CharField(label='Nombres', required=True, widget=forms.TextInput(attrs={'placeholder': 'Ingrese sus nombres'}))
    last_name = forms.CharField(label='Apellidos', required=True, widget=forms.TextInput(attrs={'placeholder': 'Ingrese sus apellidos'}))
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'}), required=True)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'placeholder': 'Confirme su contraseña'}), required=True)
    captcha = CaptchaField()
    rut = forms.CharField(
        max_length=12,  # Asegúrate de que coincida con la definición en tu modelo
        required=False,  # O ajusta según tus necesidades
        label="RUT",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'rut', 'password1', 'password2', 'captcha']

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

        #indicaciones para contraseña correcta
        self.fields['password1'].help_text = password_validators_help_text_html()

        # Cambiar el label de los campos first_name y last_name
        self.fields['first_name'].label = 'Nombres'
        self.fields['last_name'].label = 'Apellidos'

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden")

        return cleaned_data

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        user.tipo_usuario = 'Administrador'

        if commit:
            user.save()
        
        return user

##vista que maneja el html de enviar invitación de registro
###Invitación por correo 

import re
from django import forms
from .models import Area
import base64
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class EmailInvitationForm(forms.Form):
    email = forms.CharField(
        label='Correos electrónicos',
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Ingrese los correos electrónicos separados por comas o salto de línea'})
    )
    area = forms.ModelChoiceField(
        queryset=Area.objects.none(),
        label='Área',
        required=False
    )
    mensaje_personalizado = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Escribe aquí tu mensaje de invitación personalizado.'}),
        required=False,
        label='Mensaje Personalizado'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        selected_area_name = kwargs.pop('selected_area_name', None)
        super(EmailInvitationForm, self).__init__(*args, **kwargs)

        if user and user.empresa:
            self.fields['area'].queryset = Area.objects.filter(empresa=user.empresa)
            id_empresa_codificado = base64.urlsafe_b64encode(str(user.empresa.id).encode()).decode()
            self.fields['mensaje_personalizado'].initial = (
                f"Te invitamos a unirte a la área de {selected_area_name} en Kabasis. "
                f"Regístrate en http://192.168.1.38/autenticacion/form_invitacion/?empresa_id={id_empresa_codificado} y comienza a explorar cursos y recursos en seguridad digital."
                if selected_area_name else ""
            )

    def clean_email(self):
        emails = re.split(r'[,\n]+', self.cleaned_data['email'])
        valid_emails = []
        invalid_emails = []
        for email in emails:
            email = email.strip()
            if email:
                try:
                    validate_email(email) 
                    valid_emails.append(email)
                except ValidationError:
                    invalid_emails.append(email)
        if invalid_emails:
            raise forms.ValidationError(f"Los siguientes correos electrónicos son inválidos: {', '.join(invalid_emails)}")
        return valid_emails


#Formulario que registra un usuario con una empresa precargada este enviado por correo
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Area, Empresa  # Asume que estos son tus modelos

class UserAndEmpresaEmailForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico', required=True, widget=forms.TextInput(attrs={'placeholder': 'Ingrese su correo electrónico'}))
    username = forms.CharField(label='Nombre de usuario', required=True, widget=forms.TextInput(attrs={'placeholder': 'Ingrese su nombre de usuario'}))
    first_name = forms.CharField(label='Nombres', required=True, widget=forms.TextInput(attrs={'placeholder': 'Ingrese sus nombres'}))
    last_name = forms.CharField(label='Apellidos', required=True, widget=forms.TextInput(attrs={'placeholder': 'Ingrese sus apellidos'}))
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'}), required=True)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'placeholder': 'Confirme su contraseña'}), required=True)
    razon_social = forms.CharField(label='Razon social', required=True, widget=forms.TextInput(attrs={'placeholder': 'Ingrese el nombre de su empresa', 'readonly': 'readonly'}))
    rut = forms.CharField(
        label='RUT', 
        required=True, 
        validators=[validar_rut],  # Asegúrate de que validar_rut esté definida o importada
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese su RUT'})
    )
    
    # Nuevo campo para seleccionar el área
    area = forms.ModelChoiceField(
        queryset=Area.objects.none(),  # Inicializado vacío, se llenará en __init__
        label='Área',
        required=False,
        empty_label="Seleccione un área"
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'rut', 'password1', 'password2', 'razon_social', 'area']
        labels = {
            'email': 'Correo electrónico',
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
            'razon_social': 'Razon social',
        }

    def __init__(self, *args, **kwargs):
        self.empresa_id = kwargs.pop('empresa_id', None)
        # Captura y descarta el argumento area_id si está presente
        kwargs.pop('area_id', None)
        super(UserAndEmpresaEmailForm, self).__init__(*args, **kwargs)

        if self.empresa_id:
            try:
                empresa = Empresa.objects.get(id=self.empresa_id)
                self.fields['razon_social'].initial = empresa.razon_social
                self.fields['area'].queryset = Area.objects.filter(empresa_id=self.empresa_id)
            except Empresa.DoesNotExist:
                self.fields['area'].queryset = Area.objects.none()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        # Asignar tipo_usuario a 'Alumno'
        user.tipo_usuario = 'Alumno'

        user.rut = self.cleaned_data['rut']

        # Asigna el área seleccionada al usuario
        user.area = self.cleaned_data.get('area')

        # Asigna la empresa al usuario basado en el empresa_id capturado
        if self.empresa_id:
            try:
                empresa = Empresa.objects.get(id=self.empresa_id)
                user.empresa = empresa
            except Empresa.DoesNotExist:
                pass  # Aquí puedes manejar el error o simplemente omitir la asignación

        if commit:
            user.save()
            # Manejo adicional para guardar la imagen de perfil, si se incluye en el formulario
            if 'profile_picture' in self.files:
                user.profile_picture = self.files['profile_picture']
                user.save()

        return user
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')

        # Opcionalmente puedes aplicar aquí la función para formatear el RUT
        # rut = validar_rut(rut)

        # Verificar si ya existe un usuario con este RUT
        if CustomUser.objects.filter(rut=rut).exists():
            raise forms.ValidationError("Ya existe un usuario con este RUT.")

        # Retorna el RUT formateado o el RUT tal como lo ingresó el usuario
        return rut

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        try:
            validate_password(password1, self.instance)
        except ValidationError as e:
            self.add_error('password1', e)
        return password1


    # No necesitas el método clean_nombre_empresa, si solo estás pre-cargando este campo


#Formulario que registra una empresa y sus áreas
from django import forms
from .models import Empresa

from django import forms
from .models import Empresa, CustomUser  # Asegúrate de que estos modelos estén correctamente importados

class EmpresaForm(forms.ModelForm):
    razon_social = forms.CharField(
        label='Razón social', 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese la razón social de su empresa', 'class': 'form-control'})
    )
    giro = forms.ChoiceField(
        label='Giro', 
        choices=Empresa.GIROS_CHOICES,  # Asegúrate de que GIROS_CHOICES esté definido en tu modelo Empresa
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    numero_colaboradores = forms.IntegerField(
        label='Número de colaboradores', 
        required=True, 
        widget=forms.NumberInput(attrs={'placeholder': 'Número de colaboradores', 'class': 'form-control'})
    )
    

    class Meta:
        model = Empresa
        fields = ['razon_social', 'giro', 'numero_colaboradores']

    def clean_razon_social(self):
        razon_social = self.cleaned_data.get('razon_social')
        if razon_social:
            razon_social = razon_social.capitalize()  # Cambia la inicial a mayúscula
        return razon_social

    def save(self, commit=True, user=None):
        empresa = super(EmpresaForm, self).save(commit=False)
        empresa.save()

        if user and isinstance(user, CustomUser):
            user.empresa = empresa
            user.save()

        return empresa



##Formulario de login
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField

class CustomLoginForm(AuthenticationForm):
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        # Establecer el orden de los campos
        self.fields = OrderedDict([
            ('username', self.fields['username']),
            ('password', self.fields['password']),
            ('captcha', self.fields['captcha'])
        ])

        # Agregar clases a los widgets si es necesario
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    