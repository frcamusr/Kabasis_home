from django.db import models

# Create your models here.

from AutenticacionApp.models import CustomUser

class Categoria(models.Model):
    titulo = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.titulo
    

    
class Post(models.Model):
    titulo = models.CharField(max_length=20)
    contenido = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='blog', null=True, blank = True)
    autor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    categorias = models.ManyToManyField(Categoria)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return self.titulo