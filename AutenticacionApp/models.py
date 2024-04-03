from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from django.db.models.signals import pre_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Mantén el 'username' para fines de compatibilidad

    rut = models.CharField(
        max_length=12,  # Ajusta según la longitud máxima esperada para un RUT
        unique=True,    # Asegúrate de que cada RUT sea único
        null=True,      
        blank=False,     
        verbose_name="RUT"
    )


    TIPO_USUARIO_CHOICES = (
        ('', 'Selecciona el tipo de usuario'),  # Opción en blanco
        ('Administrador', 'Administrador'),
        ('Alumno', 'Alumno'),
        ('Administrador Kabasis', 'Administrador Kabasis'),
        ('Asistente Administrativo', 'Asistente Administrativo'),
              
    )

    tipo_usuario = models.CharField(
        max_length=50,
        choices=TIPO_USUARIO_CHOICES,
        default='',
        blank=True,
        verbose_name="Tipo de Usuario"
    )

    
    # Nuevo campo para la imagen de perfil
    profile_picture = models.ImageField(
        upload_to='usuarios/',  # Define la carpeta donde se guardarán las imágenes
        null=True,
        blank=True,
        verbose_name="Imagen de Perfil"
    )

    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE, null=True, blank=True)

    is_first_login = models.BooleanField(default=True)

    area = models.ForeignKey('Area', on_delete=models.SET_NULL, null=True, blank=True)

    # Nuevo campo para indicar si el usuario está certificado
    is_certificado = models.BooleanField(default=False, verbose_name="Está Certificado")

    
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Usuario Personalizado"
        verbose_name_plural = "Usuarios Personalizados"


##Verificar que el correo pertenezca al usuario en el registro
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class VerificationToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class Empresa(models.Model):
    GIROS_CHOICES = [
        ('Construccion', 'Construcción'),
        ('Comercial', 'Comercial o Comercio al por menor'),
        ('Manufacturero', 'Manufacturero'),
        ('Servicios', 'Servicios'),
        ('Tecnologia', 'Tecnología de la Información (TI)'),
        ('Alimenticio', 'Alimenticio'),
        ('Educativo', 'Educativo'),
        ('Salud', 'Salud y Cuidado Personal'),
        ('Financiero', 'Financiero'),
        ('Energia', 'Energía'),
        ('Transporte', 'Transporte y Logística'),
        ('Medios', 'Medios de Comunicación y Entretenimiento'),
    ]
    razon_social = models.CharField(max_length=50, unique=True) 
    giro = models.CharField(max_length=50, choices=GIROS_CHOICES)

    numero_colaboradores = models.IntegerField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    ESTADOS_DE_CUENTA = [
        ('activo', 'Activa'),
        ('inactivo', 'Inactiva'),
        # Puedes añadir más estados aquí
    ]

    estado_cuenta = models.CharField(max_length=20, choices=ESTADOS_DE_CUENTA, default='activa')


    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.razon_social
    


class Area(models.Model):

    nombre = models.CharField(max_length=100, unique=False)
    empresa = models.ForeignKey(
        Empresa, 
        related_name='areas_relacionadas',  # Un related_name único
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
    )    # Los campos 'created' y 'updated' pueden permanecer igual
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['nombre', 'empresa']]
        verbose_name = "Área"
        verbose_name_plural = "Áreas"

    def __str__(self):
        return self.nombre
    
