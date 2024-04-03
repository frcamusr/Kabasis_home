from django.forms import Form
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

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
    



