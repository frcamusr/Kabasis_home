from django.urls import path
from . import views

urlpatterns = [

    path('', views.survey, name='survey'),
    path('crear_pregunta/', views.create_question, name='crear_pregunta'),
    path('preguntas/', views.preguntas, name='preguntas'),
    path('survey/formulario/', views.formulario, name='formulario'),
    path('pregunta/', views.pregunta_individual, name='primera_pregunta'),
    path('pregunta/<int:pregunta_id>/', views.pregunta_individual, name='nombre_vista_pregunta'),
    path('pregunta/<int:pregunta_id>/<int:contador>/', views.pregunta_individual, name='nombre_vista_pregunta'),
    path('resultado/', views.resultado, name='resultado'),
    # delete_question
    path('delete_question2/<int:id>/', views.delete_question2, name='delete_question2'),
    # actualizar pregunta usando el mismo formulario de crear pregunta
    path('update_question/<int:id>/', views.update_question, name='update_question'),   
    path('descripcion_survey/', views.descripcion_survey, name='descripcion_survey'),



    path('dashboardEmpresa/', views.dashboardEmpresa, name='dashboardEmpresa'),
    path('dashboardDetalle/', views.dashboardDetalle, name='dashboardDetalle'),
    path('dashboardArea/', views.dashboardArea, name='dashboardArea'),
    path('dashboardAlumno/', views.dashboardAlumno, name='dashboardAlumno'),
    path('dashboardSurvey/', views.dashboardSurvey, name='dashboardSurvey'),
 
]

