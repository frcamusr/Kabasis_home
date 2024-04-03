from django.urls import path

from CursosApp import views


urlpatterns = [
    path('',views.cursos, name="Cursos"),
    
    path('agregar_curso/', views.agregar_curso, name="agregar_curso"),

    path('listar_curso/', views.listar_curso, name="listar_curso"),

    path('modificar_curso/<id>/', views.modificar_curso, name="modificar_curso"),

    path('eliminar_curso/<id>/', views.eliminar_curso, name="eliminar_curso"),

    path('ver_curso/<id>/', views.ver_curso, name='ver_curso'),

    path('obtener_contenidos/', views.obtener_contenidos, name='obtener_contenidos'),

    path('agregar_unidad/', views.agregar_unidad, name="agregar_unidad"),

    path('listar_unidad/<id>/', views.listar_unidad, name="listar_unidad"),

    path('eliminar_unidad/<id>/', views.eliminar_unidad, name="eliminar_unidad"),

    path('modificar_unidad/<id>/', views.modificar_unidad, name="modificar_unidad"),



    path('ver_video/<int:video_id>/', views.ver_video, name='ver_video'),



    ##Survey##

     # por el momento no uso este url:path('preguntas/', views.preguntas, name='preguntas'),


    # URL para Pregunta
    # crear pregunta solo usando el id del quiz
    path('crear_preguntaContent/<int:id>/', views.crear_question, name='crear_preguntaContent'),  


    path('delete_question/<int:id>/', views.delete_question, name='delete_question'),
    # actualizar pregunta usando el mismo formulario de crear pregunta
    path('update_question/<int:id>/', views.update_question, name='update_question'),    



    # URL para Quiz
    # path para crear_quiz
    path('crear_quiz/<int:idCurso>/<int:unidad>/', views.crear_quiz, name='crear_quiz'),
    # path para editar quiz
    path('editar_quiz/<int:id>/', views.edit_quiz, name='editar_quiz'),
    # path para eliminar quiz
    path('eliminar_quiz/<int:id>/', views.delete_quiz, name='eliminar_quiz'),
    # quiz con id como parametro para listar las preguntas
    path('listar_quiz/<int:id>/', views.listar_quiz, name='listar_quiz'),

 
    # Responder Usuario
    # formulario y agradecimientos
    path('formulario2/<int:id>/', views.formulario2, name='formulario2'),
    path('vista_previa/<int:id>/', views.vista_previa, name='vista_previa'),

    path('feedback/<int:id>/', views.feedback, name='feedback'),


    #  path para listar todo el material de la unidad
    path('listar_material/<int:idCurso>/<int:unidad>/', views.listar_material, name='listar_material'),
    path('actualizar_orden/<str:model_name>/<int:content_id>/<int:new_order>/', views.actualizar_orden, name='actualizar_orden'),
    path('editContenido',views.editContenido, name="editContenido"),
    
    path('obtener_unidades/<int:curso_id>/', views.obtener_unidades, name="obtener_unidades"),

    path('crear_video/<int:idCurso>/<int:unidad>/', views.crear_video, name='crear_video'),

    path('agregar_video/', views.agregar_video, name="agregar_video"),
    path('listar_video/<id>/', views.listar_video, name="listar_video"),
    path('eliminar_video/<id>/', views.eliminar_video, name="eliminar_video"),
    path('editar_video/<int:id>/', views.editar_video, name='editar_video'),
    
    
    #progreso
    path('actualizar-progreso/', views.update_progress, name='actualizar_progreso'),
    
    #Descargar certificado
    path('descargar-certificado/', views.descargar_certificado, name='descargar_certificado'),

    #Verificar certificado
    path('verificar_certificado/', views.verificar_certificado, name='verificar_certificado'),


]

