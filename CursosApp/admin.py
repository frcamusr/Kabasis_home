from django.contrib import admin
from .models import Curso, UnidadCurso, Video

# Register your models here.


class CursoAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')

admin.site.register(Curso)

@admin.register(UnidadCurso)
class UnidadCursoAdmin(admin.ModelAdmin):
    list_display = ('curso', 'titulo', 'orden')
    
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('unidad', 'titulo')
    
    
