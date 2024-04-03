from django.db import models
from django.conf import settings

from AutenticacionApp.models import CustomUser

# Create your models here.

class Curso(models.Model):
    nombre = models.CharField(max_length=80)
    imagen = models.ImageField(upload_to="cursos", null=True, blank=True)
    descripcion = models.TextField(max_length=500)
    orden = models.PositiveIntegerField(null=True, blank=True)


    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def __str__(self):
        return self.nombre
    

# Modelo para la tabla de Unidades de un Curso
class UnidadCurso(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to="unidades", null=True, blank=True)
    descripcion = models.TextField()
    orden = models.PositiveIntegerField()
    margen_izquierdo = models.IntegerField(default=0)


    def __str__(self):
        return self.titulo

# Modelo para la tabla de Videos relacionados con las unidades
from django.db import models
from urllib.parse import urlparse, parse_qs
from django.contrib.auth.models import User

class Video(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    unidad = models.ForeignKey(UnidadCurso, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    video_url = models.URLField()
    descripcion = models.TextField()
    orden = models.PositiveIntegerField()
    

    #Función que transforma la url completa del video de youtube en una url embebida
    def get_embedded_url(self):
        video_id = self.get_video_id()
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return ""

    def get_video_id(self):
        url = urlparse(self.video_url)
        if 'v' in parse_qs(url.query):
            return parse_qs(url.query)['v'][0]
        return ""
##################################

class QuizContent(models.Model):
    #relacion uno a muchos entre question y quiz, además tiene los atributos id, question_id curso, unidad
    id=models.AutoField(primary_key=True)
    #titulo
    titulo = models.CharField(max_length=255)
    #descripcion
    descripcion = models.TextField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    unidad = models.ForeignKey(UnidadCurso, on_delete=models.CASCADE)
    # orden puede ser nulo
    orden = models.PositiveIntegerField(null=True)
    def __str__(self):
        return self.id



class QuestionContent(models.Model):
    QUESTION_TYPES = [
        ('option', 'Opción múltiple'),
        ('text', 'Texto'),
    ]
    # clave foranea QuizContent
    quiz = models.ForeignKey(QuizContent, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=255, choices=QUESTION_TYPES)
    text = models.CharField(max_length=255)
    option_a = models.CharField(max_length=255, null=True)
    option_b = models.CharField(max_length=255, null=True)
    option_c = models.CharField(max_length=255, null=True)
    option_d = models.CharField(max_length=255, null=True)
    correct_answer = models.CharField(max_length=1, null=False)
    explicacion_correct = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.text
    
# crear el modelo Answer con los campos question, user, text_answer y option_answer
class AnswerContent(models.Model):
    id=models.AutoField(primary_key=True)
    question = models.ForeignKey(QuestionContent, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text_answer = models.CharField(max_length=255, null=True)
    #option answer puede ser nulo
    option_answer = models.CharField(max_length=1, null=True)
    def __str__(self):
        return self.id
    
# crear el modelo contenido con los campos id, titulo, contenido, unidad, curso y una relación uno a muchos entre unidad y contenido
class Progreso(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    unidad = models.ForeignKey(UnidadCurso, on_delete=models.CASCADE)
    videos_vistos = models.ManyToManyField(Video, blank=True)
    quizzes_completados = models.ManyToManyField(QuizContent, through='QuizProgreso', blank=True)

    class Meta:
        unique_together = ('user', 'unidad')
        verbose_name = "Progreso"
        verbose_name_plural = "Progresos"

    def __str__(self):
        return f"Progreso de {self.user.username} en {self.unidad.titulo}"

class QuizProgreso(models.Model):
    progreso = models.ForeignKey(Progreso, on_delete=models.CASCADE)
    quiz = models.ForeignKey(QuizContent, on_delete=models.CASCADE)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=0, null=True)
    intentos =models.IntegerField(default=0)
    aprobado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('progreso', 'quiz')

    def __str__(self):
        return f"{self.progreso.user.username} - {self.quiz.titulo} - {'Aprobado' if self.aprobado else 'No Aprobado'}"



class ProgresoUnidad(models.Model):
    unidad = models.ForeignKey(UnidadCurso, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    aprobado = models.BooleanField(default=False)


    


