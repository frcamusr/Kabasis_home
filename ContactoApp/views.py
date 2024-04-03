from django.shortcuts import render, redirect

from .forms import FormularioContacto

from django.core.mail import EmailMessage

from django.contrib import messages

# Create your views here.


def contacto(request):

    formulario_contacto = FormularioContacto()

    if request.method == "POST":
        formulario_contacto = FormularioContacto(data=request.POST)
        if formulario_contacto.is_valid():
            nombre=request.POST.get("nombre")
            email=request.POST.get("email")
            contenido=request.POST.get("contenido")

            email = EmailMessage("Mensaje desde App Django",
            "El usuaurio con nombre {} con la dirección {} escribe lo siguiente: \n\n {}".format(nombre, email, contenido),
            "", ["oscargp.94@gmail.com"], reply_to=[email])

            try:
                email.send()
                messages.success(request, 'Correo enviado correctamente.')
                return redirect("/contacto/?valido")
            
            except:
                return redirect("/contacto/?novalido")

    return render(request, "ContactoApp/contacto.html", {'miformulario':formulario_contacto})

