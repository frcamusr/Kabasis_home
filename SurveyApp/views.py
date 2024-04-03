import json
import math
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import QuestionForm, AnswerForm
from .models import Question, Answer, Puntaje
from django.contrib.auth.decorators import login_required
from CursosApp.models import Curso, UnidadCurso, ProgresoUnidad, Progreso, Video, QuizContent, QuizProgreso
from metodoPago.models import RegistroTransaccion, PlanPago
from AutenticacionApp.models import CustomUser, Area
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect





@login_required
def survey(request):
    # si el usuario ya ha completado el formulario, redirigir a la pagina home
    usuario_ya_completo_formulario = Answer.objects.filter(user=request.user).exists()
    if usuario_ya_completo_formulario:
        # este debe enviar a la pagina kabasisWeb.urls a la vista vacia
        return HttpResponseRedirect('/cursos/ver_curso/1/')
    else:
        return render(request, 'completarSurvey.html')






def preguntas(request):
    questions = Question.objects.all()
    return render(request, 'preguntas.html', {'questions': questions})


def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            # Guardar la pregunta y sus opciones
            question = Question()
            question.question_type = form.cleaned_data['question_type']
            question.text = form.cleaned_data['text']
            question.option_a = form.cleaned_data['option_a']
            question.option_b = form.cleaned_data['option_b']
            question.option_c = form.cleaned_data['option_c']
            question.option_d = form.cleaned_data['option_d']
            question.correct_answer = form.cleaned_data['correct_answer']
            question.save()
        return redirect('preguntas')
    else:
        form = QuestionForm()
    return render(request, 'crear_pregunta.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import Question, Answer

@login_required
def formulario(request):
    # Verificar si el usuario ya ha completado el formulario
    usuario_ya_completo_formulario = Answer.objects.filter(user=request.user).exists()
    if usuario_ya_completo_formulario:
        # Si el usuario ya ha completado el formulario, redirige a la página de resultado
        return redirect('resultado')  # Reemplaza con el nombre de tu vista de resultado

    # Obtener todas las preguntas
    questions = Question.objects.all()

    if request.method == 'POST':
        # Procesar respuestas del formulario
        for pregunta in questions:
            question_id = request.POST.get(f'question_id_{pregunta.id}')
            text_answer = request.POST.get(f'text_answer_{pregunta.id}')
            option_answer = request.POST.get(f'option_answer_{pregunta.id}')

            # Guardar la respuesta
            answer = Answer()
            answer.question = Question.objects.get(id=question_id)
            answer.user = request.user
            answer.text_answer = text_answer

            # Verificar si option_answer es una opción válida (a, b, c, d)
            if option_answer in ['a', 'b', 'c', 'd']:
                answer.option_answer = option_answer

            answer.save()

        # Redirigir a la página de resultado después de procesar el formulario
        return redirect('resultado')  # Reemplaza con el nombre de tu vista de resultado

    return render(request, 'formulario.html', {'questions': questions})


from django.shortcuts import render, redirect, get_object_or_404




@login_required
def pregunta_individual(request, pregunta_id=None, contador = None):
    usuario_ya_completo_formulario = Puntaje.objects.filter(user=request.user).exists()
    if usuario_ya_completo_formulario:
        return redirect('resultado')
    
    total_preguntas = Question.objects.count()+1  # Obtener el total de preguntas

    if pregunta_id is None:
        pregunta = Question.objects.first()
        preguntas_respondidas = 0  # Asumir que la primera pregunta es la primera respondida si existe alguna pregunta
        contador = 1
    else:
        pregunta = get_object_or_404(Question, id=pregunta_id)
        preguntas_respondidas = Question.objects.filter(id__lte=pregunta.id).count()


    if request.method == 'POST':
        text_answer = request.POST.get(f'text_answer_{pregunta.id}')
        option_answer = request.POST.get(f'option_answer_{pregunta.id}')
        # Crear y guardar la respuesta
        answer, created = Answer.objects.update_or_create(
            question_id=pregunta.id,
            user=request.user,
            defaults={'text_answer': text_answer, 'option_answer': option_answer}
        )

        # Decidir qué hacer después de guardar la respuesta
        next_question = Question.objects.filter(id__gt=pregunta.id).first()
        if next_question:
            return redirect('nombre_vista_pregunta', pregunta_id=next_question.id, contador = contador+1)
        else:
            return redirect('resultado')

    # Para el botón de volver, simplemente necesitas identificar la pregunta anterior
    previous_question = Question.objects.filter(id__lt=pregunta.id).last()
    numeracion_pregunta = contador-1
    # Creamos una variable para el total de preguntas en Question

    
    porcentaje = (preguntas_respondidas / total_preguntas) * 100

    # Redondeamos el porcentaje sin decimales
    porcentaje = math.trunc(porcentaje)
    # Convertimos el porcentaje a entero
    porcentaje = int(porcentaje)

    # Actualizar el contexto para incluir el total de preguntas y las preguntas respondidas
    context = {
        'pregunta': pregunta,
        'previous_question': previous_question,
        'porcentaje': porcentaje,
        'contador':contador,
        'numeracion_pregunta': numeracion_pregunta
    }

    return render(request, 'formulariodos.html', context)




def delete_question2(request, id):
    question = Question.objects.get(id=id)
    question.delete()
    return redirect('preguntas')


# def resultado, este mostrara el porcentaje de respuestas correctas comparando answer.option_answer con question.correct_answer y recibiendo el id del usuario

def resultado(request):
    # Inicializamos las variables de factor
    correct_conocimiento = correct_actitud = correct_conducta = 0
    # inicializamos las variables de dimensión
    correct_seg_exterior = correct_seg_computador = correct_constrasena = correct_navegar = correct_correos = 0
    correct_sitios_seg = correct_hackers = correct_virus = correct_denuncia = correct_entrenamiento = correct_riesgos =  0 
    correct_politicas = correct_compromiso = correct_disuasion = 0

    # Obtener el usuario que está respondiendo y sus respuestas
    user = request.user
    answers_user = Answer.objects.filter(user=user)

    # contar el cantidad de preguntas por dimensión
    cantidad_seg_exterior = Question.objects.filter(dimension_kabasis='seg_exterior')
    cantidad_seg_computador = Question.objects.filter(dimension_kabasis='seg_computador')
    cantidad_contrasena = Question.objects.filter(dimension_kabasis='contraseñas')
    cantidad_navegar = Question.objects.filter(dimension_kabasis='navegar')
    cantidad_correos = Question.objects.filter(dimension_kabasis='correos')
    cantidad_sitios_seg = Question.objects.filter(dimension_kabasis='sitios_seg')
    cantidad_hackers = Question.objects.filter(dimension_kabasis='hackers')
    cantidad_virus = Question.objects.filter(dimension_kabasis='virus')
    cantidad_denuncia = Question.objects.filter(dimension_kabasis='denuncia')
    cantidad_entrenamiento = Question.objects.filter(dimension_kabasis='entrenamiento')
    cantidad_riesgos = Question.objects.filter(dimension_kabasis='riesgos')
    cantidad_politicas = Question.objects.filter(dimension_kabasis='politicas')
    cantidad_compromiso = Question.objects.filter(dimension_kabasis='compromiso')
    cantidad_disuasion = Question.objects.filter(dimension_kabasis='disuasion')




    # Contar el total de preguntas por factor
    cantidad_conocimiento = Question.objects.filter(factor_kabasis='conocimiento').count()
    cantidad_actitud = Question.objects.filter(factor_kabasis='actitud').count()
    cantidad_conducta = Question.objects.filter(factor_kabasis='conducta').count()

    # Contar respuestas correctas totales y por área
    correct_answers = 0
    for answer in answers_user:
        if answer.option_answer == answer.question.correct_answer:
            correct_answers += 1
            # Incrementar el contador por área según corresponda
            if answer.question.dimension_kabasis == 'seg_exterior':
                correct_seg_exterior += 1
            elif answer.question.dimension_kabasis == 'seg_computador':
                correct_seg_computador += 1
            elif answer.question.dimension_kabasis == 'contraseñas':
                correct_constrasena += 1
            if answer.question.dimension_kabasis == 'navegar':
                correct_navegar += 1
            elif answer.question.dimension_kabasis == 'correos':
                correct_correos += 1
            elif answer.question.dimension_kabasis == 'sitios_seg':
                correct_sitios_seg += 1
            if answer.question.dimension_kabasis == 'hackers':
                correct_hackers += 1
            elif answer.question.dimension_kabasis == 'virus':
                correct_virus += 1
            elif answer.question.dimension_kabasis == 'denuncia':
                correct_denuncia += 1
            if answer.question.dimension_kabasis == 'entrenamiento':
                correct_entrenamiento += 1
            elif answer.question.dimension_kabasis == 'riesgos':
                correct_riesgos += 1
            elif answer.question.dimension_kabasis == 'politicas':
                correct_politicas += 1
            elif answer.question.dimension_kabasis == 'compromiso':
                correct_compromiso += 1
            elif answer.question.dimension_kabasis == 'disuasion':
                correct_disuasion += 1

    # Calcular porcentaje por dimensión
    porcentaje_seg_exterior = int(round(correct_seg_exterior / cantidad_seg_exterior.count() * 100, 0)) if cantidad_seg_exterior.count() > 0 else 0
    porcentaje_seg_computador = int(round(correct_seg_computador / cantidad_seg_computador.count() * 100, 0)) if cantidad_seg_computador.count() > 0 else 0
    porcentaje_contrasena = int(round(correct_constrasena / cantidad_contrasena.count() * 100, 0)) if cantidad_contrasena.count() > 0 else 0
    porcentaje_navegar = int(round(correct_navegar / cantidad_navegar.count() * 100, 0)) if cantidad_navegar.count() > 0 else 0
    porcentaje_correos = int(round(correct_correos / cantidad_correos.count() * 100, 0)) if cantidad_correos.count() > 0 else 0
    porcentaje_sitios_seg = int(round(correct_sitios_seg / cantidad_sitios_seg.count() * 100, 0)) if cantidad_sitios_seg.count() > 0 else 0
    porcentaje_hackers = int(round(correct_hackers / cantidad_hackers.count() * 100, 0)) if cantidad_hackers.count() > 0 else 0
    porcentaje_virus = int(round(correct_virus / cantidad_virus.count() * 100, 0)) if cantidad_virus.count() > 0 else 0
    porcentaje_denuncia = int(round(correct_denuncia / cantidad_denuncia.count() * 100, 0)) if cantidad_denuncia.count() > 0 else 0
    porcentaje_entrenamiento = int(round(correct_entrenamiento / cantidad_entrenamiento.count() * 100, 0)) if cantidad_entrenamiento.count() > 0 else 0
    porcentaje_riesgos = int(round(correct_riesgos / cantidad_riesgos.count() * 100, 0)) if cantidad_riesgos.count() > 0 else 0
    porcentaje_politicas = int(round(correct_politicas / cantidad_politicas.count() * 100, 0)) if cantidad_politicas.count() > 0 else 0
    porcentaje_compromiso = int(round(correct_compromiso / cantidad_compromiso.count() * 100, 0)) if cantidad_compromiso.count() > 0 else 0
    porcentaje_disuasion = int(round(correct_disuasion / cantidad_disuasion.count() * 100, 0)) if cantidad_disuasion.count() > 0 else 0




    # Calcular porcentajes por área
    porcentaje_conocimiento = int(round((porcentaje_sitios_seg + porcentaje_hackers + porcentaje_virus)/3,0))
    porcentaje_actitud = int(round((porcentaje_denuncia+porcentaje_entrenamiento+porcentaje_riesgos+porcentaje_politicas+porcentaje_compromiso+porcentaje_disuasion)/6,0))
    porcentaje_conducta = int(round((porcentaje_seg_exterior + porcentaje_seg_computador + porcentaje_contrasena + porcentaje_navegar + porcentaje_correos)/5,0))

    # Calcular porcentaje total
    porcentaje=int(round((porcentaje_conocimiento+porcentaje_actitud+porcentaje_conducta)/3,0))

    # Actualizar o crear el registro en Puntaje para el usuario actual con los nuevos valores
    Puntaje.objects.update_or_create(
        user=user,
        defaults={
            'porcentaje': porcentaje,
            'porcentaje_conocimientos': porcentaje_conocimiento,
            'porcentaje_actitud': porcentaje_actitud,
            'porcentaje_conducta': porcentaje_conducta,
            'porcentaje_seg_exterior': porcentaje_seg_exterior,
            'porcentaje_seg_computador': porcentaje_seg_computador,
            'porcentaje_contrasena': porcentaje_contrasena,
            'porcentaje_navegar': porcentaje_navegar,
            'porcentaje_correos': porcentaje_correos,
            'porcentaje_sitios_seg': porcentaje_sitios_seg,
            'porcentaje_hackers': porcentaje_hackers,
            'porcentaje_virus': porcentaje_virus,
            'porcentaje_denuncia': porcentaje_denuncia,
            'porcentaje_entrenamiento': porcentaje_entrenamiento,
            'porcentaje_riesgos': porcentaje_riesgos,
            'porcentaje_politicas': porcentaje_politicas,
            'porcentaje_compromiso': porcentaje_compromiso,
            'porcentaje_disuasion': porcentaje_disuasion,


        }
    )
    
    # Suponiendo que ya tienes la variable 'puntaje' y una forma de obtener 'unidades'

    # unidades_aprob = 0

    # # Verificar si en la tabla UnidadCurso existen registros
    # # (Reemplaza 'UnidadCurso.objects.all()' con tu método para obtener unidades)
    # unidades = UnidadCurso.objects.all()

    # if unidades:
    #     cantidad_unidades = len(unidades)
    #     if 10 < porcentaje < 20:
    #         unidades_aprob = int(cantidad_unidades * 0.1)
    #     elif 20 < porcentaje < 30:
    #         unidades_aprob = int(cantidad_unidades * 0.2)
    #     elif 30 < porcentaje < 40:
    #         unidades_aprob = int(cantidad_unidades * 0.3)
    #     elif 40 < porcentaje < 50:
    #         unidades_aprob = int(cantidad_unidades * 0.4)
    #     elif 50 < porcentaje < 60:
    #         unidades_aprob = int(cantidad_unidades * 0.5)
    #     elif 60 < porcentaje < 70:
    #         unidades_aprob = int(cantidad_unidades * 0.6)
    #     elif 70 < porcentaje < 80:
    #         unidades_aprob = int(cantidad_unidades * 0.7)
    #     elif 80 < porcentaje < 90:
    #         unidades_aprob = int(cantidad_unidades * 0.8)
    #     elif porcentaje > 90:
    #         unidades_aprob = int(cantidad_unidades * 0.9)


    # if Puntaje.objects.filter(user=user).exists() and unidades_aprob != 0:
    #     for i in range(1, unidades_aprob + 1):
    #         # Buscar la unidad con el orden actual
    #         unidad = UnidadCurso.objects.filter(orden=i).first()

    #         if unidad:
    #             # Crear un nuevo ProgresoUnidad
    #             progreso_unidad = ProgresoUnidad()
    #             progreso_unidad.unidad = unidad
    #             progreso_unidad.user = user
    #             progreso_unidad.aprobado = True
    #             progreso_unidad.save()
   

        
    # Antes de retornar, incluir los porcentajes por área en el contexto
    context = {
        'porcentaje': porcentaje,
        'porcentaje_actitud': porcentaje_actitud,
        'porcentaje_conducta': porcentaje_conducta,
        'porcentaje_conocimientos': porcentaje_conocimiento,  # Asegúrate que este nombre coincida con tu backend
        'porcentaje_seg_exterior': porcentaje_seg_exterior,
        'porcentaje_seg_computador': porcentaje_seg_computador,
        'porcentaje_contrasena': porcentaje_contrasena,
        'porcentaje_navegar': porcentaje_navegar,
        'porcentaje_correos': porcentaje_correos,
        'porcentaje_sitios_seg': porcentaje_sitios_seg,
        'porcentaje_hackers': porcentaje_hackers,
        'porcentaje_virus': porcentaje_virus,
        'porcentaje_denuncia': porcentaje_denuncia,
        'porcentaje_entrenamiento': porcentaje_entrenamiento,
        'porcentaje_riesgos': porcentaje_riesgos,
        'porcentaje_politicas': porcentaje_politicas,
        'porcentaje_compromiso': porcentaje_compromiso,
        'porcentaje_disuasion': porcentaje_disuasion,
    }

    # Retornamos el porcentaje junto con los porcentajes por área
    return render(request, 'resultado.html', context)








# def update_question, este tendra un formulario para actualizar la pregunta
def update_question(request, id):

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        question = Question.objects.get(id=id)
        tipo = question.question_type
 
        
        if form.is_valid():
            # guardar la pregunta y sus opciones, usando el id de la pregunta
            if tipo == 'text':
                #form = QuestionForm(initial={'text': question.text})
                # guardar las preguntas con el formulario de texto
                question.text = form.cleaned_data['text']
                question.save()
                return redirect('preguntas')

            else:
                #form = QuestionForm(initial={'text': question.text, 'option_a': question.option_a, 'option_b': question.option_b, 'option_c': question.option_c, 'option_d': question.option_d, 'correct_answer': question.correct_answer})
                question.text = form.cleaned_data['text']
                question.option_a = form.cleaned_data['option_a']
                question.option_b = form.cleaned_data['option_b']
                question.option_c = form.cleaned_data['option_c']
                question.option_d = form.cleaned_data['option_d']
                question.correct_answer = form.cleaned_data['correct_answer']
                question.save()
                return redirect('preguntas')
        else:
            if tipo == 'text':
                form = QuestionForm(initial={'text': question.text})
            else:
                form = QuestionForm(initial={'text': question.text, 'option_a': question.option_a, 'option_b': question.option_b, 'option_c': question.option_c, 'option_d': question.option_d, 'correct_answer': question.correct_answer})
        
   
    return render(request, 'update_question.html', {'form': form, 'question': question, 'tipo': tipo})


def descripcion_survey(request):
    return render(request, 'descripcion_survey.html')


def avanceUnidades(usuario):
    dato_alumno = []
    cantidad_unidad = UnidadCurso.objects.count()
    ultimaUnidadAprobada = ProgresoUnidad.objects.filter(
        user=usuario, aprobado=True
    ).order_by('unidad_id')
    ultimaUnidadAprobada = ultimaUnidadAprobada.last()
    if ultimaUnidadAprobada==None:
        for unidad in range(1,cantidad_unidad+1):
            dato_alumno.append((unidad,0))
        return dato_alumno
    ultimaUnidadAprobada = ultimaUnidadAprobada.unidad_id
    print(f'ultima unidad aprobada del usuario es : {ultimaUnidadAprobada}')
    if not ultimaUnidadAprobada:
        unidad_actual = 1
    else:
        unidad_actual = ultimaUnidadAprobada + 1

    contador_visto = 0
    contador_total = 0
    progreso_ultima = Progreso.objects.filter(
        user=usuario
    ).order_by('id')
    progreso_ultima = progreso_ultima.last()
    progresoUltimaUnidad = progreso_ultima.unidad_id
    if not progreso_ultima:
        for unidad in range(1,cantidad_unidad+1):
            dato_alumno.append((unidad,0))
        return dato_alumno
    if progresoUltimaUnidad == ultimaUnidadAprobada:
        for unidad in range(1,cantidad_unidad+1):
            if unidad <= ultimaUnidadAprobada:
                dato_alumno.append((unidad,100))
            if unidad > ultimaUnidadAprobada:
                dato_alumno.append((unidad,0))
        return dato_alumno
    if progresoUltimaUnidad == unidad_actual:
        videos_vistos = progreso_ultima.videos_vistos.all()
        for videos in videos_vistos:
            contador_visto+=1
        quiz_realizado = QuizProgreso.objects.filter(
            progreso_id=progreso_ultima.id
        )
        for quiz in quiz_realizado:
            contador_visto+=1    
        total_videos = Video.objects.filter(
            unidad_id=unidad_actual
        )
        for videos in total_videos:
            contador_total+=1
        quiz_total = QuizContent.objects.filter(
            unidad_id=unidad_actual
        )
        for quiz in quiz_total:
            contador_total+=1
        ultimo = int(round(contador_visto*100/contador_total,0))
        for unidad in range(1,cantidad_unidad+1):
            if unidad <= ultimaUnidadAprobada:
                dato_alumno.append((unidad, 100))
            if unidad == unidad_actual:
                dato_alumno.append((unidad_actual,ultimo))
            if unidad > unidad_actual:
                dato_alumno.append((unidad,0))
        return dato_alumno






def dashboardEmpresa(request):
    return render(request, 'dashboard/dashboardEmpresa.html')


def dashboardDetalle(request):

    
    maximo_alumno = None
    empresa_id_actual = request.user.empresa_id
    invitados = registrado =0
    nombreNoRegistrados = []
    nombreRegistrados = []


    usuario = CustomUser.objects.get(
        tipo_usuario='Administrador',
        empresa_id=empresa_id_actual
    )
    transaccion = RegistroTransaccion.objects.get(usuario_id=usuario)
    plan = PlanPago.objects.get(id=transaccion.id_plan_id)
    if (plan != None):
        maximo_alumno=plan.alumnos
    


    usuarios_alumnos = CustomUser.objects.filter(
        tipo_usuario='Alumno',
        empresa_id=empresa_id_actual
    )

    for usuario in usuarios_alumnos:
        invitados+=1
        if not usuario.is_first_login:
            registrado+=1
            nombreRegistrados.append((usuario.username, usuario.email))
        if usuario.last_login == None:
            nombreNoRegistrados.append((usuario.username, usuario.email))


    #1 para las invitaciones disponibles: invitaciones enviadas - Maximo alumnos permitidos
    disponibles = maximo_alumno - invitados


    porcentaje_enviado = int(round((invitados/maximo_alumno)*100,0)) if maximo_alumno>0 else 0
    porcentaje_registrado = int(round((registrado/invitados)*100,0)) if invitados > 0 else 0
    print(porcentaje_registrado)



    # Inicializa contadores para cada opción de cada pregunta
    opciones_edad = {'a': 0, 'b': 0, 'c': 0, 'd': 0}
    opciones_genero = {'a': 0, 'b': 0, 'c': 0}
    opciones_anhos = {'a': 0, 'b': 0, 'c': 0, 'd': 0}
    opciones_estudios = {'a': 0, 'b': 0, 'c': 0}

    respuestas_relevantes = Answer.objects.filter(user__tipo_usuario='Alumno', user__empresa_id=empresa_id_actual)

    # Procesa respuestas para la pregunta de edad
    for respuesta in respuestas_relevantes.filter(question__text='Por favor indique su edad'):
        if respuesta.option_answer in opciones_edad:
            opciones_edad[respuesta.option_answer] += 1

    # Procesa respuestas para la pregunta de género
    for respuesta in respuestas_relevantes.filter(question__text='Por favor indique su Género'):
        if respuesta.option_answer in opciones_genero:
            opciones_genero[respuesta.option_answer] += 1

    # Procesa respuestas para la pregunta de años en la organización
    for respuesta in respuestas_relevantes.filter(question__text='¿Cuántos años lleva trabajando en su organización actual?'):
        if respuesta.option_answer in opciones_anhos:
            opciones_anhos[respuesta.option_answer] += 1

    # Procesa respuestas para la pregunta de nivel de estudios
    for respuesta in respuestas_relevantes.filter(question__text='¿Cuál es su nivel de estudios?'):
        if respuesta.option_answer in opciones_estudios:
            opciones_estudios[respuesta.option_answer] += 1

    # Convierte los contadores a arreglos
    arreglo_edades = [opciones_edad['a'], opciones_edad['b'], opciones_edad['c'], opciones_edad['d']]
    arreglo_genero = [opciones_genero['a'], opciones_genero['b'], opciones_genero['c']]
    arreglo_anhos = [opciones_anhos['a'], opciones_anhos['b'], opciones_anhos['c'], opciones_anhos['d']]
    arreglo_estudios = [opciones_estudios['a'], opciones_estudios['b'], opciones_estudios['c']]

    context = {
        'arreglo_edades': arreglo_edades,
        'arreglo_genero': arreglo_genero,
        'arreglo_anhos': arreglo_anhos,
        'arreglo_estudios': arreglo_estudios,
        'maximo_alumno': maximo_alumno,
        'invitados': invitados,
        'registrado': registrado,
        'disponibles': disponibles,
        'porcentaje_enviado': porcentaje_enviado,
        'porcentaje_registrado': porcentaje_registrado,
        'nombreNoRegistrados': nombreNoRegistrados,
        'nombreRegistrados': nombreRegistrados,
    }

    return render(request, 'dashboard/dashboardDetalle.html', context)




def dashboardArea(request):
    infoAreas = []
    empresa_id_actual = request.user.empresa_id
    # Se espera desde el usuario, filtrar por empresa y luego comenzar a filtrar por Area
    areas = Area.objects.filter(
        empresa_id=empresa_id_actual
    )
    unidad = UnidadCurso.objects.count()
    for area in areas:
        avanceArea = []
        contador = 0
        alumnos = CustomUser.objects.filter(area_id=area)
        for alumno in alumnos:
            datoAlumno = avanceUnidades(alumno.id)
            suma_avances = sum(avance for _, avance in datoAlumno)
            promedio_avance = suma_avances / unidad if unidad > 0 else 0
            avanceArea.append(promedio_avance)
            contador+=1
        promedio = sum(avanceArea)/contador if contador >0 else 0
        infoAreas.append((area.nombre,promedio))
    print(infoAreas)
    infoAreas = json.dumps(infoAreas)

    context= {
        'infoAreas':infoAreas,
    }

    return render(request, 'dashboard/dashboardArea.html', context)


    
from django.core.serializers.json import DjangoJSONEncoder
import json
def dashboardAlumno(request):
    
    dato_alumno = avanceUnidades(request.user)
    print(dato_alumno)

    # Serializar el dato_alumno para enviarlo al template
    dato_alumno_json = json.dumps(dato_alumno, cls=DjangoJSONEncoder)
    print(dato_alumno_json)

    empresa_id_actual = request.user.empresa_id




    usuarios = CustomUser.objects.filter(
        tipo_usuario='Alumno',
        empresa_id=empresa_id_actual
    )

    datos_admin = []

    for usu in usuarios:
        datoAlumno = avanceUnidades(usu)
        suma_avances = sum(avance for _, avance in datoAlumno)
        unidades = len(dato_alumno)
        promedio_avance = suma_avances / unidades if unidades > 0 else 0
        datos_admin.append((usu.username,promedio_avance))
    print(datos_admin)


    datos_admin = json.dumps(datos_admin)

 


    context = {
        'datos_admin': datos_admin,
        'dato_alumno_json': dato_alumno_json,
        }
    return render(request, 'dashboard/dashboardAlumno.html', context)




def dashboardSurvey(request):
    porcentaje_actitud = porcentaje_conducta = porcentaje_conocimientos = alumnos = 0
    porcentaje_compromiso=porcentaje_contrasena=porcentaje_correos=porcentaje_denuncia=porcentaje_disuasion=porcentaje_entrenamiento=0
    porcentaje_hackers=porcentaje_navegar=porcentaje_politicas=porcentaje_riesgos=porcentaje_seg_computador=porcentaje_seg_exterior=0
    porcentaje_sitios_seg=porcentaje_virus=0
    empresa_id_actual = request.user.empresa_id

    puntajes = Puntaje.objects.filter(
        user__tipo_usuario='Alumno',
        user__empresa_id=empresa_id_actual)
    
    for puntaje in puntajes:
        porcentaje_actitud += puntaje.porcentaje_actitud
        porcentaje_conducta += puntaje.porcentaje_conducta
        porcentaje_conocimientos += puntaje.porcentaje_conocimientos

        porcentaje_compromiso += puntaje.porcentaje_compromiso
        porcentaje_contrasena += puntaje.porcentaje_contrasena
        porcentaje_correos += puntaje.porcentaje_correos
        porcentaje_denuncia += puntaje.porcentaje_denuncia
        porcentaje_disuasion += puntaje.porcentaje_disuasion
        porcentaje_entrenamiento += puntaje.porcentaje_entrenamiento
        porcentaje_hackers += puntaje.porcentaje_hackers
        porcentaje_navegar += puntaje.porcentaje_navegar
        porcentaje_politicas += puntaje.porcentaje_politicas
        porcentaje_riesgos += puntaje.porcentaje_riesgos
        porcentaje_seg_computador += puntaje.porcentaje_seg_computador
        porcentaje_seg_exterior += puntaje.porcentaje_seg_exterior
        porcentaje_sitios_seg += puntaje.porcentaje_sitios_seg
        porcentaje_virus += puntaje.porcentaje_virus



        alumnos+=1



    promedio_actitud = int(round(porcentaje_actitud/alumnos,0)) if alumnos > 0 else None
    promedio_conducta = int(round(porcentaje_conducta/alumnos,0)) if alumnos > 0 else None
    promedio_conocimientos = int(round(porcentaje_conocimientos/alumnos,0)) if alumnos > 0 else None

    promedio_compromiso = int(round(porcentaje_compromiso/alumnos,0)) if alumnos > 0 else None
    promedio_contrasena = int(round(porcentaje_contrasena/alumnos,0)) if alumnos > 0 else None
    promedio_correos = int(round(porcentaje_correos/alumnos,0)) if alumnos > 0 else None
    promedio_denuncia = int(round(porcentaje_denuncia/alumnos,0)) if alumnos > 0 else None
    promedio_disuasion = int(round(porcentaje_disuasion/alumnos,0)) if alumnos > 0 else None
    promedio_entrenamiento = int(round(porcentaje_entrenamiento/alumnos,0)) if alumnos > 0 else None
    promedio_hackers = int(round(porcentaje_hackers/alumnos,0)) if alumnos > 0 else None
    promedio_navegar = int(round(porcentaje_navegar/alumnos,0)) if alumnos > 0 else None
    promedio_politicas = int(round(porcentaje_politicas/alumnos,0)) if alumnos > 0 else None
    promedio_riesgos = int(round(porcentaje_riesgos/alumnos,0)) if alumnos > 0 else None
    promedio_seg_computador = int(round(porcentaje_seg_computador/alumnos,0)) if alumnos > 0 else None
    promedio_seg_exterior = int(round(porcentaje_seg_exterior/alumnos,0)) if alumnos > 0 else None
    promedio_sitios_seg = int(round(porcentaje_sitios_seg/alumnos,0)) if alumnos > 0 else None
    promedio_virus = int(round(porcentaje_virus/alumnos,0)) if alumnos > 0 else None



    respuestas_relevantes = Answer.objects.filter(user__tipo_usuario='Alumno', user__empresa_id=request.user.empresa_id)
    preguntas_relevantes = Question.objects.filter(item_kabasis__isnull=False)

    # Inicializa una lista para guardar los resultados
    resultados = []

    # Recorre cada pregunta relevante
    for pregunta in preguntas_relevantes:
        # Obtiene las respuestas para esta pregunta específica
        respuestas_de_la_pregunta = respuestas_relevantes.filter(question_id=pregunta.id)

        # Cuenta el número total de respuestas y el número de respuestas correctas
        total_respuestas = respuestas_de_la_pregunta.count()
        respuestas_correctas = respuestas_de_la_pregunta.filter(option_answer=pregunta.correct_answer).count()

        # Calcula el porcentaje de respuestas correctas si hay respuestas, de lo contrario, el porcentaje es 0
        porcentaje_correctas = (respuestas_correctas / total_respuestas * 100) if total_respuestas > 0 else 0

        # Redondea el porcentaje y lo convierte a entero
        porcentaje_correctas = round(porcentaje_correctas)

        # Agrega el item_kabasis y el porcentaje al arreglo de resultados
        resultados.append((pregunta.item_kabasis, porcentaje_correctas))

    resultados_json = json.dumps(resultados)
    context = {
        'promedio_actitud': promedio_actitud,
        'promedio_conducta': promedio_conducta,
        'promedio_conocimientos': promedio_conocimientos,
        'promedio_compromiso': promedio_compromiso,
        'promedio_contrasena': promedio_contrasena,
        'promedio_correos': promedio_correos,
        'promedio_denuncia': promedio_denuncia,
        'promedio_disuasion': promedio_disuasion,
        'promedio_entrenamiento': promedio_entrenamiento,
        'promedio_hackers': promedio_hackers,
        'promedio_navegar': promedio_navegar,
        'promedio_politicas': promedio_politicas,
        'promedio_riesgos': promedio_riesgos,
        'promedio_seg_computador': promedio_seg_computador,
        'promedio_seg_exterior': promedio_seg_exterior,
        'promedio_sitios_seg': promedio_sitios_seg,
        'promedio_virus': promedio_virus,
        'resultados_json':resultados_json,

        }


    return render(request, 'dashboard/dashboardSurvey.html', context)