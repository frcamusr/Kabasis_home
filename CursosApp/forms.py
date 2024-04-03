from django import forms
from .models import Curso, UnidadCurso, Video


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'imagen', 'descripcion', 'orden']

    def __init__(self, *args, **kwargs):
        super(CursoForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  # Agregar la clase 'form-control' a cada campo

            if field_name == 'nombre':
                field.widget.attrs['placeholder'] = 'Nombre del curso'  # Agregar un marcador de posición para el campo 'nombre'

            # Puedes personalizar más cada campo si es necesario




class UnidadForm(forms.ModelForm):
    class Meta:
        model = UnidadCurso
        fields = ['curso', 'titulo', 'descripcion', 'orden', 'imagen']


    def __init__(self, *args, **kwargs):
        super(UnidadForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  # Agregar la clase 'form-control' a cada campo

            if field_name == 'titulo':
                field.widget.attrs['placeholder'] = 'Nombre unidad'  # Agregar un marcador de posición para el campo 'nombre'



#######contenido###########

from django.forms import Form
from django import forms

from .models import Curso, UnidadCurso

class QuestionForm(Form):
    # tipo de pregunta: texto o pregunta de opción múltiple
    question_type = forms.ChoiceField(
        choices=[('option', 'Opción múltiple'), ('text', 'Texto')],
        widget=forms.Select(attrs={'id': 'id_question_type'}), required=False
    )
    # Sí la pregunta es de texto
    text = forms.CharField(max_length=255)

    # Sí la pregunta es de opción múltiple
    option_a = forms.CharField(max_length=255, required=False)
    option_b = forms.CharField(max_length=255, required=False)
    option_c = forms.CharField(max_length=255, required=False)
    option_d = forms.CharField(max_length=255, required=False)

    # Sí la pregunta es de opción múltiple
    correct_answer = forms.ChoiceField(choices=[('', ''),('a', 'Opción A'), ('b', 'Opción B'), ('c', 'Opción C'), ('d', 'Opción D')], required=False)
    explicacion_correct = forms.CharField(max_length=255, required=False)
    
    # validar los datos del formulario y guardar la pregunta
    def clean(self):
        return super().clean()
    
    

class AnswerForm(Form):
    # Respuesta de texto
    text_answer = forms.CharField(max_length=500)

    # Respuesta de opción múltiple esta puede ser nula y es opcional solo si la pregunta es de opción múltiple
    option_answer = forms.ChoiceField(choices=[('a', 'Opción A'), ('b', 'Opción B'), ('c', 'Opción C'), ('d', 'Opción D')], required=False)

    
    
    # Validar los datos del formulario
    def clean(self):
        # Validar los datos del formulario
        return super().clean()
    

class VideoForm(forms.ModelForm):  # Cambio de Form a ModelForm
    class Meta:
        model = Video
        fields = ['titulo', 'video_url', 'descripcion', 'orden']
                
    def __init__(self, *args, **kwargs):
        super(VideoForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  # Agregar la clase 'form-control' a cada campo

            # Puedes agregar atributos específicos para el campo 'orden'
            if field_name == 'orden':
                field.widget.attrs['placeholder'] = 'Orden del video'  # Agregar un marcador de posición para 'orden'
                # Aquí puedes agregar más atributos específicos si es necesario

     


