from django.db import models
from django.conf import settings

class Question(models.Model):
    # crear el campo question_type con solo las opciones de texto y opción múltiple
    question_type = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
    option_a = models.CharField(max_length=255, null=True )
    option_b = models.CharField(max_length=255 , null=True)
    option_c = models.CharField(max_length=255, null=True)
    option_d = models.CharField(max_length=255, null=True)
    correct_answer = models.CharField(max_length=1, null=True)
    factor_kabasis = models.CharField(max_length=255, null=True)
    dimension_kabasis = models.CharField(max_length=255, null=True)
    item_kabasis = models.CharField(max_length=255, null=True)
    def __str__(self):
        return self.id
    
# crear el modelo Answer con los campos question, user, text_answer y option_answer
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text_answer = models.CharField(max_length=255, null=True)
    #option answer puede ser nulo
    option_answer = models.CharField(max_length=1, null=True)
    def __str__(self):
        return self.id

# puntaje obtenido en la encuesta
class Puntaje(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    porcentaje = models.IntegerField(null=True)
    porcentaje_conducta = models.IntegerField(null=True)
    porcentaje_conocimientos = models.IntegerField(null=True)
    porcentaje_actitud = models.IntegerField(null=True)
    porcentaje_seg_exterior = models.IntegerField(null=True)
    porcentaje_seg_computador = models.IntegerField(null=True)
    porcentaje_contrasena = models.IntegerField(null=True)
    porcentaje_navegar = models.IntegerField(null=True)
    porcentaje_correos = models.IntegerField(null=True)
    porcentaje_sitios_seg = models.IntegerField(null=True)
    porcentaje_hackers = models.IntegerField(null=True)
    porcentaje_virus = models.IntegerField(null=True)
    porcentaje_denuncia = models.IntegerField(null=True)
    porcentaje_entrenamiento = models.IntegerField(null=True)
    porcentaje_riesgos = models.IntegerField(null=True)
    porcentaje_politicas = models.IntegerField(null=True)
    porcentaje_compromiso = models.IntegerField(null=True)
    porcentaje_disuasion = models.IntegerField(null=True)
    def __str__(self):
        return self.id

    

