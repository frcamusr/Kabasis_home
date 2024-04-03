from django.shortcuts import render

# Create your views here.

from ServiciosApp.models import Servicio
from django.contrib.auth.decorators import login_required, permission_required


def servicios(request):

    servicios=Servicio.objects.all()
    return render(request, "ServiciosApp/servicios.html", {"servicios" : servicios})