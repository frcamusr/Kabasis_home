from django.shortcuts import render, redirect, get_object_or_404
from .forms import CursoForm, UnidadForm, VideoForm, QuestionForm, AnswerForm
from .models import Curso, Progreso, UnidadCurso, QuestionContent, AnswerContent, QuizContent, Video, UnidadCurso, QuizProgreso, ProgresoUnidad
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from itertools import chain
from django.db import transaction
from django.db.models import Max

from AutenticacionApp.models import CustomUser

from django.db.models import Count
from django.contrib.auth import get_user_model


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.utils.formats import date_format
from django.utils import translation
import datetime
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph


def cursos(request):
    cursos = Curso.objects.all()
    data = {

        'cursos': cursos
    }
    return render(request, "CursosApp/cursos.html", data)


def agregar_curso(request):

    data = {
        'form': CursoForm()

    }

    if request.method == 'POST':
        formulario = CursoForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Curso creado con éxito.')
        else: 
            data["form"] = formulario
    
    return render(request, "CursosApp/agregar_curso.html", data)


def listar_curso(request):
    cursos = Curso.objects.all()

    data = {
        'cursos': cursos
    }

    return render(request, "CursosApp/listar_curso.html", data)


def modificar_curso(request, id):

    curso = get_object_or_404(Curso, id=id)

    data= {
        'form': CursoForm(instance = curso)
    }

    if request.method == 'POST':
        formulario = CursoForm(data=request.POST, instance=curso, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Curso actualizado correctamente")
            return redirect(to="listar_curso")
        
        data["form"] = formulario
    
    return render(request, "CursosApp/modificar_curso.html", data)

def eliminar_curso(request, id):
    curso = get_object_or_404(Curso, id=id)
    curso.delete()
    messages.success(request, 'Curso eliminado con éxito.')
    return redirect(to="listar_curso")


@login_required
def ver_curso(request, id):
        # Verifica si hay cursos en la base de datos
    if not Curso.objects.exists():
        # Verifica si el usuario es un Administrador Kabasis
        if request.user.tipo_usuario == 'Administrador Kabasis':
            # Redirige al formulario de creación de cursos
            return redirect('agregar_curso')
        if request.user.tipo_usuario == 'Administrador' or 'Alumno':
            # Muestra un mensaje de advertencia
            messages.success(request, "WARNING:Aún no se crean cursos en la plataforma")
            # Redirige al home
            return redirect('Home')  # Asegúrate de reemplazar 'nombre_de_tu_url_home' con el nombre real de tu URL de home

    # Si hay cursos, toma el primero disponible
    curso = Curso.objects.first()
    
    unidades = UnidadCurso.objects.filter(curso=curso).order_by('orden')
    
    # prueba
    
    # Intenta obtener el progreso para la última unidad aprobada y calcula la siguiente unidad
    ultima_unidad_aprobada_orden = ProgresoUnidad.objects.filter(
        user=request.user, 
        unidad__curso=curso, 
        aprobado=True
    ).aggregate(Max('unidad__orden'))['unidad__orden__max'] or 0

    unidad_siguiente = UnidadCurso.objects.filter(
        curso=curso, 
        orden__gt=ultima_unidad_aprobada_orden
    ).order_by('orden').first()
    
    if unidad_siguiente and Progreso.objects.filter(user=request.user).exists():
        
        try:
            progreso_unidad_actual = Progreso.objects.get(
                user=request.user,
                unidad=unidad_siguiente
            )

            # Contando el contenido aprobado
            videos_vistos_count = progreso_unidad_actual.videos_vistos.count()
            quizzes_aprobados_count = QuizProgreso.objects.filter(
                progreso=progreso_unidad_actual, 
                aprobado=True
            ).count()

            contenido_avance = videos_vistos_count + quizzes_aprobados_count

            total_contenidos_unidad = QuizContent.objects.filter(unidad=unidad_siguiente).count() + Video.objects.filter(unidad=unidad_siguiente).count()

            if total_contenidos_unidad == contenido_avance:
                # Marca la unidad como aprobada
                ProgresoUnidad.objects.update_or_create(
                    user=request.user, 
                    unidad=unidad_siguiente,
                    defaults={'aprobado': True}
                )
        
        except Progreso.DoesNotExist:
        # Manejar el caso en que no existe un progreso para la unidad_siguiente
        # Podrías redirigir al usuario, mostrar un mensaje, etc.
            print("esta pasando por aqui")




    # Obtener los IDs de las unidades aprobadas por el usuario
    ids_unidades_aprobadas = ProgresoUnidad.objects.filter(
        user=request.user, 
        unidad__curso=curso, 
        aprobado=True
    ).values_list('unidad_id', flat=True)
    
    # Marcar cada unidad como aprobada o no
    for unidad in unidades:
        unidad.aprobada = unidad.id in ids_unidades_aprobadas

    quiz = QuizContent.objects.filter(curso=curso).order_by('orden')
    video = Video.objects.filter(curso=curso).order_by('orden')
    
    data = {
        'curso': curso,
        'unidades': unidades,
        'quiz': quiz, 
        'video': video,
        'unidad_siguiente':unidad_siguiente,
        # No necesitas enviar 'aprobados' como un conteo separado ahora
    }

    return render(request, 'CursosApp/ver_curso.html', data)



def obtener_contenidos(request):
    usuario = request.user
    unidad_id = request.GET.get('unidad_id', None)
    if unidad_id is not None:
        try:
            unidad = UnidadCurso.objects.get(id=unidad_id)
        except UnidadCurso.DoesNotExist:
            return JsonResponse({'error': 'Unidad no encontrada'}, status=404)

        quizzes = QuizContent.objects.filter(unidad=unidad).order_by('orden')
        videos = Video.objects.filter(unidad=unidad).order_by('orden')
        contenidos = sorted(list(quizzes) + list(videos), key=lambda contenido: contenido.orden)
        
        data = []
        for contenido in contenidos:
            contenido_dict = {
                'id': contenido.id,
                'titulo': contenido.titulo,
                'visto': False
            }
            if isinstance(contenido, Video):
                contenido_dict['video_url'] = contenido.video_url
                contenido_dict['visto'] = Progreso.objects.filter(
                    user=usuario,
                    unidad=contenido.unidad,
                    videos_vistos=contenido).exists()
            elif isinstance(contenido, QuizContent):
                # Verifica si el quiz ha sido completado y aprobado
                progreso = Progreso.objects.filter(user=usuario, unidad=contenido.unidad).first()
                if progreso:
                    quiz_progreso = QuizProgreso.objects.filter(
                        progreso=progreso, 
                        quiz=contenido, 
                        aprobado=True
                    ).exists()
                    contenido_dict['visto'] = quiz_progreso

            data.append(contenido_dict)

        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Solicitud inválida'}, status=400)



############################## UNIDADES ######################################


def agregar_unidad(request):
    if request.method == 'POST':
        formulario = UnidadForm(request.POST, request.FILES)
        if formulario.is_valid():
            unidad = formulario.save(commit=False)  # No guardar inmediatamente para asignar curso
            curso_id = request.POST.get('curso')  # Asumiendo que el campo del formulario se llama 'curso'

            # Concatenar el nombre del curso al título de la unidad
            unidad.titulo = f"{unidad.titulo}"

            unidad.save()  # Ahora guarda la unidad con el curso asignado y el nombre modificado
            messages.success(request, 'Unidad creada con éxito.')
            formulario = UnidadForm() 
        else:
            messages.error(request, 'Error al crear la unidad. Por favor, verifica el formulario.')
    else:
        formulario = UnidadForm()

    data = {'form': formulario}
    return render(request, "unidades/agregar_unidad.html", data)


@login_required
def listar_unidad(request, id):
    curso = Curso.objects.get(pk=id)
    unidades = UnidadCurso.objects.filter(curso=curso).order_by('orden')

    # Calcula los márgenes para los botones restantes
    margen_izquierdo = [(unidad.orden - 2) * 100 for unidad in unidades[2:]]

    data = {
        'curso': curso,
        'unidades': unidades,
        'margen_izquierdo': margen_izquierdo,
    }

    return render(request, 'unidades/listar_unidad.html', data)


def eliminar_unidad(request, id):
    unidad = get_object_or_404(UnidadCurso, pk=id)
    curso_id = unidad.curso.id  # Obtiene el ID del curso al que pertenece la unidad
    unidad.delete()
    
    # Modifica la siguiente línea para pasar el ID correctamente
    return redirect('listar_unidad', id=curso_id)


def modificar_unidad(request, id):
    unidad = get_object_or_404(UnidadCurso, id=id)
    curso_id = unidad.curso.id  # Obtiene el ID del curso al que pertenece la unidad

    data = {
        'form': UnidadForm(instance=unidad)
    }

    if request.method == 'POST':
        formulario = UnidadForm(data=request.POST, instance=unidad, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Unidad actualizada correctamente")
            
            # Redirige a la vista 'listar_unidad' con el ID del curso como parámetro
            return redirect('listar_unidad', id=curso_id)

        data["form"] = formulario

    return render(request, "unidades/modificar_unidad.html", data)


def ver_video(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    idCurso = video.curso_id

    return render(request, 'video/ver_videos.html', {'video': video , 'idCurso': idCurso})


#################CONTENIDO#################

# Preguntas: crear, eliminar y actualizar
# Preguntas: crear, eliminar y actualizar
def crear_question(request, id):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            # Crear una nueva instancia de Question y asignar el quiz
            question = QuestionContent(quiz_id=id)
            question.question_type = form.cleaned_data['question_type']
            question.text = form.cleaned_data['text']
            question.option_a = form.cleaned_data['option_a']
            question.option_b = form.cleaned_data['option_b']
            question.option_c = form.cleaned_data['option_c']
            question.option_d = form.cleaned_data['option_d']
            question.correct_answer = form.cleaned_data['correct_answer']
            question.explicacion_correct = form.cleaned_data['explicacion_correct']
            question.save()
            # Redirigir a la página del quiz
            return redirect(reverse('listar_quiz', args=[id]))
    else:
        form = QuestionForm()
    return render(request, 'quiz/crear_preguntaContent.html', {'form': form, 'id_quiz': id})


def delete_question(request, id):
    question = QuestionContent.objects.get(id=id)

    question.delete()
    return redirect(reverse('listar_quiz', args=[question.quiz_id]))


# def update_question, este tendra un formulario para actualizar la pregunta
def update_question(request, id):

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        question = QuestionContent.objects.get(id=id)
        tipo = question.question_type

        if form.is_valid():
            # guardar la pregunta y sus opciones, usando el id de la pregunta

            if tipo == 'text':
                #form = QuestionForm(initial={'text': question.text})
                # guardar las preguntas con el formulario de texto
                question.text = form.cleaned_data['text']
                question.save()
                return redirect(reverse('listar_quiz', args=[question.quiz_id]))

            else:
                #form = QuestionForm(initial={'text': question.text, 'option_a': question.option_a, 'option_b': question.option_b, 'option_c': question.option_c, 'option_d': question.option_d, 'correct_answer': question.correct_answer})

                question.text = form.cleaned_data['text']
                question.option_a = form.cleaned_data['option_a']
                question.option_b = form.cleaned_data['option_b']
                question.option_c = form.cleaned_data['option_c']
                question.option_d = form.cleaned_data['option_d']
                question.correct_answer = form.cleaned_data['correct_answer']
                question.explicacion_correct = form.cleaned_data['explicacion_correct']
                question.save()
                return redirect(reverse('listar_quiz', args=[question.quiz_id]))
        else:
            if tipo == 'text':
                form = QuestionForm(initial={'text': question.text})
            else:
                form = QuestionForm(initial={'text': question.text, 'option_a': question.option_a, 'option_b': question.option_b, 'option_c': question.option_c, 'option_d': question.option_d, 'correct_answer': question.correct_answer , 'explicacion_correct': question.explicacion_correct})
        
   
    return render(request, 'update_question.html', {'form': form, 'question': question, 'tipo': tipo})


# mostrar los enlaces de todos los quiz creados para cada unidad y curso:
def listar_material(request, idCurso, unidad):
    quizzes = QuizContent.objects.filter(curso_id=idCurso, unidad_id=unidad)
    video = Video.objects.filter(curso_id=idCurso, unidad_id=unidad)

    # Combina ambas consultas y ordena por el campo 'orden'
    content_list = sorted(chain(quizzes, video), key=lambda x: x.orden)

    # Obtener valores únicos de orden
    order_values = set(content.orden for content in content_list)

    idCurso = idCurso
    unidad = unidad

    return render(request, 'admContenido/listar_material.html', {'content_list': content_list, 'idCurso': idCurso, 'unidad': unidad, 'order_values': order_values})


def actualizar_orden(request, model_name, content_id, new_order):
    model_mapping = {
        'quiz': QuizContent,
        'video': Video,
    }

    model_class = model_mapping.get(model_name)
    

    if not model_class:
        return JsonResponse({'status': 'error', 'message': 'Modelo no válido'})

    content = get_object_or_404(model_class, id=content_id)

    # Guardar el orden antiguo antes de actualizarlo
    old_order = content.orden

    # Buscar si existe algún contenido con el nuevo orden
    

    if QuizContent.objects.filter(orden=new_order).first():
        # Intercambiar los órdenes inmediatamente
        existing_content = QuizContent.objects.get(orden=new_order)
        existing_content.orden = old_order 
        existing_content.save()


    if Video.objects.filter(orden=new_order).first():
        # Intercambiar los órdenes
        existing_content = Video.objects.get(orden=new_order)
        existing_content.orden = old_order
        existing_content.save()

    # Actualizar el campo de orden
    content.orden = new_order
    content.save()

    return JsonResponse({'status': 'success', 'new_order': new_order})


#Quiz: crear, editar, eliminar y listar
def crear_quiz(request, idCurso, unidad):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        orden = request.POST.get('orden')

        # Crear instancia del modelo con los datos del formulario
        quiz = QuizContent(
            curso_id=idCurso,
            unidad_id=unidad,
            titulo=titulo,
            descripcion=descripcion,
            orden=orden
        )
        quiz.save()

        # Redireccionar a donde desees después de guardar el quiz
        return redirect(reverse('listar_material', args=[idCurso, unidad]))

    # Renderizar el formulario para la creación del quiz
    return render(request, 'quiz/crear_quiz.html', {'idCurso': idCurso, 'unidad': unidad})


# edit_quiz solo envia a la lista de quiz
def edit_quiz(request, id):
    quiz = QuizContent.objects.get(id=id)
    idCurso = quiz.curso_id
    unidad = quiz.unidad_id
    return redirect(reverse('listar_quiz', args=[quiz.id]))

def editar_info_quiz(request, id):
    quiz = get_object_or_404(QuizContent, id=id)

    if request.method == 'POST':
        # Actualizar los campos necesarios
        quiz.titulo = request.POST.get('titulo')
        quiz.descripcion = request.POST.get('descripcion')
        quiz.orden = request.POST.get('orden')
        quiz.save()
        
        return redirect(reverse('listar_quiz' , args=[quiz.id]))

    return render(request, 'quiz/editar_info_quiz.html', {'quiz': quiz})

def update_orders_after_delete(model_class, deleted_order):
    # Obtener todos los elementos con un orden mayor al eliminado
    # si model_class es QuizContent, entonces ver si existen videos y quiz con orden mayor al eliminado y restarle 1


    quizs = QuizContent.objects.filter(orden__gt=deleted_order)
    videos = Video.objects.filter(orden__gt=deleted_order)

    # Actualizar el orden de los quiz
    for quiz in quizs:
        quiz.orden -= 1
        quiz.save()
    
    # Actualizar el orden de los videos
    for video in videos:
        video.orden -= 1
        video.save()


# Eliminar quiz y sus preguntas
def delete_quiz(request, id):
    quiz = QuizContent.objects.get(id=id)
    quiz.delete()
    return redirect(reverse('listar_material', args=[quiz.curso_id, quiz.unidad_id]))

def listar_quiz(request, id):
    quiz = QuizContent.objects.get(id=id)
    idCurso = quiz.curso_id
    unidad = quiz.unidad_id
    questions = QuestionContent.objects.filter(quiz_id=id)
    return render(request, 'quiz/listar_quiz.html', {'questions': questions, 'quiz':quiz ,'idCurso': idCurso, 'unidad': unidad})


@login_required
def formulario2(request, id):
    questions = QuestionContent.objects.filter(quiz_id=id)
    total_respuestas = 0
    respuesta_correcta = 0
    todas_preguntas_texto = all(pregunta.question_type == 'text' for pregunta in questions)
    if request.method == 'POST':
        with transaction.atomic():  # Asegura que las operaciones sean atómicas
            for pregunta in questions:
                question_id = request.POST.get(f'question_id_{pregunta.id}')
                text_answer = request.POST.get(f'text_answer_{pregunta.id}')
                option_answer = request.POST.get(f'option_answer_{pregunta.id}')

                # Verifica si ya existe una respuesta para esta pregunta y usuario
                answer, created = AnswerContent.objects.get_or_create(
                    question_id=question_id,
                    user=request.user,
                    defaults={
                        'text_answer': text_answer,
                        'option_answer': option_answer if option_answer in ['a', 'b', 'c', 'd'] else None
                    }
                )

                # Si la respuesta ya existía y se está actualizando
                if not created:
                    answer.text_answer = text_answer
                    if option_answer in ['a', 'b', 'c', 'd']:
                        answer.option_answer = option_answer
                answer.save()

                # Lógica para contar respuestas correctas
                if option_answer in ['a', 'b', 'c', 'd']:
                    total_respuestas += 1
                    correct_answer = pregunta.correct_answer  # Ya tienes el objeto, no es necesario obtenerlo de nuevo
                    if option_answer == correct_answer:
                        respuesta_correcta += 1
                if not option_answer:
                    total_respuestas += 1
                    respuesta_correcta += 1
                    
                    #if text_answer:
                    # aqui, si las preguntas son de texto, esto quiere decir que son preguntas abiertas y por lo tanto,
                    # lo que responda el usuario no sera calificado, por lo tanto en el caso de que fuese text_answer,
                    # no deberia llevar a feedback, si no a ver_curso y ver el curso correspondiente, además 
                    # si el quiz es solo pregunta de texto y por lo tanto respuesta de texto, debe aprobarse el quiz
                    # una vez que lo responda

            # Calcular porcentaje de respuestas correctas
            porcentaje = int((respuesta_correcta / total_respuestas) * 100) if total_respuestas > 0 else 0

            quiz = get_object_or_404(QuizContent, id=id)
            progreso, created = Progreso.objects.get_or_create(user=request.user, unidad=quiz.unidad)
            quiz_progreso, created = QuizProgreso.objects.get_or_create(progreso=progreso, quiz=quiz)
            porcent = porcentaje
            if not quiz_progreso.aprobado:
                quiz_progreso.porcentaje = porcentaje
                quiz_progreso.aprobado = porcentaje >= 80
                quiz_progreso.intentos += 1

                # Actualizar el progreso sin borrarlo aquí
                quiz_progreso.save()

            request.session['porcent'] = float(porcent)  # Convierte Decimal a float

            # Redirección basada en el tipo de preguntas
            if todas_preguntas_texto:
                # Redirige a 'ver_curso' si todas las preguntas son de texto
                return redirect(reverse('ver_curso', args=[quiz.unidad.curso.id]))
            else:
                # Redirige a 'feedback' si hay preguntas de opción
                return redirect(reverse('feedback', args=[id]))
    else:
        form = AnswerForm()

    return render(request, 'admContenido/formulario.html', {'form': form, 'questions': questions})


@login_required
def feedback(request, id):
    quiz = get_object_or_404(QuizContent, id=id)
    questions = QuestionContent.objects.filter(quiz=quiz)
    respuestas = AnswerContent.objects.filter(user=request.user, question__quiz=quiz)

    
    try:
        unidad = get_object_or_404(UnidadCurso, quizcontent=quiz)
        progreso = Progreso.objects.get(user=request.user, unidad=quiz.unidad)
        quiz_progreso = QuizProgreso.objects.get(progreso=progreso, quiz=quiz)
        porcent = request.session.get('porcent', None)
        if 'porcent' in request.session:
            del request.session['porcent']
        if quiz_progreso.aprobado:
            quiz_progreso.porcentaje = porcent

        if quiz_progreso.intentos == 3 and not quiz_progreso.aprobado:
            # Recolecta la información necesaria para el feedback antes de borrar
            feedback_data = {
                'questions': questions,
                'respuestas': respuestas,
                'quiz_progreso': quiz_progreso
            }

            # Procede a borrar los registros
            quiz_progreso.delete()
            progreso.videos_vistos.clear()
            progreso.delete()

            # Envía la información recolectada al template para el feedback
            return render(request, 'admContenido/feedback.html', feedback_data)
        

    except (Progreso.DoesNotExist, QuizProgreso.DoesNotExist):
        # Manejo de caso en que no existan registros debido al borrado en intentos previos
        feedback_data = {
            'questions': questions,
            'respuestas': respuestas,
            'quiz_progreso': quiz_progreso
        }

    return render(request, 'admContenido/feedback.html', {
        'questions': questions,
        'respuestas': respuestas,
        'quiz_progreso': quiz_progreso
    })



# definimos la vista previa del quiz, este debe ser igual al formulario pero sin el boton de enviar y sin guardar las respuestas
def vista_previa(request, id):
    # Obtener todas las preguntas
    questions = QuestionContent.objects.filter(quiz_id=id)

    # Puedes hacer lo que necesites con las preguntas para la vista previa,
    # como pasarlas al template y renderizarlas

    return render(request, 'admContenido/vista_previa.html', {'id':id,'questions': questions})


def editContenido(request):
    cursos = Curso.objects.all()
    Unidad = UnidadCurso.objects.all()
    
    data = {

        'cursos': cursos,
        'unidad': Unidad,
    }
    return render(request, "admContenido/editContenido.html" , data)


def obtener_unidades(request, curso_id):
    unidades = UnidadCurso.objects.filter(curso_id=curso_id).values('id','titulo')
    curso_nombre = Curso.objects.get(id=curso_id).nombre
    
    data = {
        'cursoNombre': curso_nombre,
        'unidades': list(unidades)
    }
    
    return JsonResponse(data)


# por cada unidad y curso enlistar los contenidos, quiz, videos y actividades desde la base de datos y modelos
def obtener_contenido(request, unidad_id):
    # obtener el contenido de la unidad
    # obtener los videos de la unidad
    # obtener los quiz de la unidad
    quiz = QuizContent.objects.filter(unidad_id=unidad_id).values('id','question_id')
    # listar lo anterior para mostrarlo en la vista
    data = {
        
        'quiz': list(quiz),
    }
    # retornar la data en formato json para que pueda ser leida por javascript
    return JsonResponse(data)


############Video######################
def crear_video(request, idCurso, unidad):
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            # Crear una nueva instancia de Contenido y asignar el curso y unidad
            video = Video(curso_id=idCurso, unidad_id=unidad)
            video.titulo = form.cleaned_data['titulo']
            video.video_url = form.cleaned_data['video_url']
            video.descripcion = form.cleaned_data['descripcion']
            video.orden = form.cleaned_data['orden']
            video.save()
            # Redirigir a la página del quiz
            return redirect(reverse('listar_material', args=[idCurso, unidad]))
    else:
        form = VideoForm()
    return render(request, 'video/crear_video.html', {'form': form, 'idCurso': idCurso, 'unidad': unidad})


def agregar_video(request):
    if request.method == 'POST':
        formulario = VideoForm(request.POST, request.FILES)
        if formulario.is_valid():
            video = formulario.save(commit=False)  # No guardar inmediatamente para asignar curso
            unidad_id = request.POST.get('unidad')  # Asumiendo que el campo del formulario se llama 'curso'
            unidad = UnidadCurso.objects.get(pk=unidad_id)  # Obtén el curso correspondiente desde la base de datos
            # Concatenar el nombre del curso al título de la unidad
            video.titulo = f"{unidad.titulo} - {video.titulo}"
            video.unidad = unidad  # Asignar el curso al que pertenece esta unidad
            video.save()  # Ahora guarda la unidad con el curso asignado y el nombre modificado
            messages.success(request, 'video creado con éxito.')
            formulario = VideoForm() 
        else:
            messages.error(request, 'Error al crear el video. Por favor, verifica el formulario.')
    else:
        formulario = VideoForm()

    data = {'form': formulario}
    return render(request, "video/agregar_video.html", data)


def listar_video(request, id=None):
    if id:
        videos = Video.objects.filter(unidad__curso_id=id)
    else:
        videos = Video.objects.all()

    data = {
        'videos': videos,
    }

    return render(request, 'video/listar_video.html', data)



def eliminar_video(request, id):
    video = get_object_or_404(Video, pk=id)
    deleted_video_order = Video.objects.get(id=id).orden
    unidad_id = video.unidad.id  # Obtiene el ID del curso al que pertenece la unidad

    video.delete()
    update_orders_after_delete(Video, deleted_video_order)
    messages.success(request, "video eliminado correctamente")
    # Modifica la siguiente línea para pasar el ID correctamente
    # return a listar_material con el idCurso y unidad
    return redirect('listar_material', idCurso=video.curso.id, unidad=unidad_id)




def editar_video(request, id):
    video = Video.objects.get(id=id)
    idCurso = video.curso_id
    unidad = video.unidad_id

    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video)  # Utiliza instance=video aquí
        if form.is_valid():
            form.save()
            return redirect(reverse('listar_material', args=[idCurso, unidad]))
    else:
        form = VideoForm(instance=video)  # Y aquí también

    return render(request, 'video/modificar_video.html', {'form': form, 'idCurso': idCurso, 'unidad': unidad})




def update_progress(request):
    video_id = request.POST.get('video_id')
    user = request.user

    try:
        video = Video.objects.get(id=video_id)
        progreso, created = Progreso.objects.get_or_create(user=user, unidad=video.unidad)
        progreso.videos_vistos.add(video)
        progreso.save()

        return JsonResponse({'status': 'success', 'message': 'Progreso actualizado.'})
    except Video.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Video no encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    


import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.utils.formats import date_format
from django.utils import translation
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from PIL import Image
from reportlab.lib.utils import ImageReader


@login_required
def descargar_certificado(request):
    usuario = request.user


    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Certificado_Kabasis.pdf"'


    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    #Añadir logo
    logo_path = finders.find('KabasisWebApp/img/logo_original.png')
    if logo_path:
        logo_width = 250
        logo_height = 250
        logo_x = (width - logo_width) / 2
        logo_y = height - logo_height - -30
        p.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')

    #Título
    p.setFont("Times-Roman", 24)
    title_y = logo_y - 0
    p.drawCentredString(width / 2, title_y, "Certificado de Finalización")


    # Texto justificado
    style = ParagraphStyle(name='Justify', alignment=4, fontSize=12, leading=14, fontName="Times-Roman")
    text = (f"Este certificado verifica que {usuario.first_name} {usuario.last_name} con RUT: {getattr(usuario, 'rut', 'No especificado')} "
            "ha completado satisfactoriamente el curso de Cybersecurity Essentials ofrecido por Kabasis. Este logro demuestra "
            "un entendimiento fundamental de los principios de ciberseguridad y buenas prácticas, incluyendo la protección contra amenazas "
            "y la seguridad en redes e internet. Este conocimiento equipa al titular para enfrentar los retos de seguridad en el ámbito digital actual.")
    paragraph = Paragraph(text, style)
    paragraph.wrapOn(p, width - 100, height)
    paragraph.drawOn(p, 50, title_y - 100)  # Ajusta la posición vertical según necesites


    # Asegura que la localización esté en español para la fecha
    translation.activate('es')
    fecha_descarga = date_format(datetime.datetime.now(), "DATE_FORMAT")
    p.setFont("Times-Roman", 10)
    p.drawString(50, 410, f"Santiago (Chile), {fecha_descarga}") #primer valor ancho, segundo valor alto de la fecha


    # Dibujar un marco alrededor del contenido
    # Ajusta estos valores según sea necesario para que el marco se ajuste bien alrededor de tu contenido
    marco_margen_x = 37 #a menor el número más angosto 
    marco_margen_y = 20 
    marco_ancho = width - 2 * marco_margen_x
    marco_altura = height - 1 * marco_margen_y - 26  # Ajuste adicional en la altura si es necesario #marco_margen_y a menor número más alto
    p.rect(marco_margen_x, marco_margen_y, marco_ancho, marco_altura)


    # Añadir la firma
    firma_path = finders.find('KabasisWebApp/img/firmanofondo.png')
    firma_x = width - 190  # Posición en el ancho
    firma_y = height - 480  # Posición en el alto
    firma_width = 100  # El ancho de la firma
    firma_height = 50  # La altura de la firma
    p.drawImage(firma_path, firma_x, firma_y, width=firma_width, height=firma_height, preserveAspectRatio=True, mask='auto')

    # Coordenadas para la línea debajo de la firma
    inicio_linea_x = firma_x
    fin_linea_x = firma_x + firma_width
    linea_y = firma_y - -15  # Ajusta este valor para cambiar la distancia vertical de la línea respecto a la firma

    # Dibujar la línea
    p.line(inicio_linea_x, linea_y, fin_linea_x, linea_y)



    # Añadir el timbre
    timbre_path = finders.find('KabasisWebApp/img/timbrenofondo.png')  # Asegúrate de cambiar esto por la ruta real
    timbre_x = width - 290  # Ajusta según sea necesario #posición en el ancho
    timbre_y = height - 500  # Ajusta según sea necesario #posición en el alto
    p.drawImage(timbre_path, timbre_x, timbre_y, width=100, height=80, preserveAspectRatio=True, mask='auto')



    # Establece la fuente para la firma
    p.setFont("Times-Roman", 10)
    # Texto de la firma y cargo
    nombre_firma = "Juan Jose Rojas Fuenzalida"
    cargo_firma = "Gerente General"
    # Calcular el ancho del texto del nombre y del cargo
    ancho_nombre = p.stringWidth(nombre_firma, "Times-Roman", 10)
    ancho_cargo = p.stringWidth(cargo_firma, "Times-Roman", 10)
    # Coordenadas iniciales para el nombre (se mantiene centrado como está)
    firma_x_text = width - 194  # Ancho del nombre y cargo
    # Coordenadas para el nombre
    firma_y_text_nombre = height - 480  #Alto para el nombre y cargo
    # Ajustar la posición x del cargo para que quede centrado respecto al nombre
    diferencia_ancho = (ancho_nombre - ancho_cargo) / 2
    firma_x_text_cargo = firma_x_text + diferencia_ancho  # Ajusta la posición x del cargo basado en la diferencia
    # Posición 'y' para el cargo, un poco más abajo que el nombre
    firma_y_text_cargo = firma_y_text_nombre - 15  # Ajusta según sea necesario para el cargo, 15 puntos más abajo
    # Dibuja el nombre
    p.drawString(firma_x_text, firma_y_text_nombre, nombre_firma)
    # Dibuja el cargo, ajustando la posición x para centrarlo con respecto al nombre
    p.drawString(firma_x_text_cargo, firma_y_text_cargo, cargo_firma)
    
    # Generar el código QR
    qr_data = f"http://192.168.1.10:8000/cursos/verificar_certificado?usuario_id={usuario.id}"
    qr = qrcode.make(qr_data)
    qr_temp = BytesIO()
    qr.save(qr_temp, format="PNG")
    qr_temp.seek(0)  # Volver al comienzo del BytesIO para lectura

    # Convertir BytesIO en una imagen PIL para que ReportLab pueda manejarlo
    qr_image = Image.open(qr_temp)
    qr_final = ImageReader(qr_image)

    # Definir posición y tamaño del QR en el PDF
    qr_size = 100  # Tamaño del QR en el PDF
    qr_x_position = width - qr_size - 420  # Margen derecho
    qr_y_position = 150  # Margen inferior

    # Añadir el QR al PDF
    p.drawImage(qr_final, qr_x_position, qr_y_position, qr_size, qr_size)

    # Texto debajo del QR
    texto_qr = "Para verificar la validez del presente certificado debe escanear el Código QR."
    # Ajusta la posición 'y' para colocar el texto debajo del QR
    texto_qr_y_position = qr_y_position - 50  # Ajusta este valor según sea necesario
    p.setFont("Times-Roman", 10)  # Ajusta el tamaño de fuente según sea necesario
    # Ajusta la posición 'x' para mover el texto a la izquierda
    texto_qr_x_position = qr_x_position - 40  # Ajusta este valor para mover el texto más a la izquierda
    p.drawString(texto_qr_x_position, texto_qr_y_position, texto_qr)

   
    # Definir una nueva posición 'x' para el texto, moviéndolo más a la izquierda
    texto_x_position = 50  # movimiento horizontal

    # Texto dividido en dos partes para introducir un salto de línea manualmente
    texto_certificacion_parte1 = "Las Certificaciones emitidas a través de esta página, son otorgadas bajo Firma Electrónica Avanzada, en conformidad a"
    texto_certificacion_parte2 = "lo dispuesto en la Ley N° 19.799 y su Reglamento."

    # Ajustar la posición 'y' para el espacio entre los textos
    texto_certificacion_y_position = texto_qr_y_position - 45  

    # Dibujar la primera parte del texto de certificación más a la izquierda
    p.drawString(texto_x_position, texto_certificacion_y_position, texto_certificacion_parte1)

    # Calcular la nueva posición 'y' para la segunda parte del texto
    interlineado = 15  # Ajusta según sea necesario
    texto_certificacion_y_position2 = texto_certificacion_y_position - interlineado

    # Dibujar la segunda parte del texto de certificación más a la izquierda
    p.drawString(texto_x_position, texto_certificacion_y_position2, texto_certificacion_parte2)


    # Finalizar el PDF
    p.showPage()
    p.save()

    return response


from django.shortcuts import render
from django.http import HttpResponse
# Asegúrate de importar tu modelo CustomUser


from django.shortcuts import render
from .models import CustomUser

def verificar_certificado(request):
    usuario_id = request.GET.get('usuario_id')
    mensaje = "El certificado no es válido o no se encontró el usuario."
    usuario = None

    if usuario_id:
        try:
            usuario = CustomUser.objects.get(pk=usuario_id, is_certificado=True)
            mensaje = ""  # No es necesario mostrar un mensaje de error si el usuario está certificado
        except CustomUser.DoesNotExist:
            pass  # Mantener mensaje de error predeterminado

    return render(request, 'certificado/verificar_certificado.html', {'usuario': usuario, 'mensaje': mensaje})











    


