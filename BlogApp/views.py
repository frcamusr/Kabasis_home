from django.shortcuts import render

from BlogApp.models import Post, Categoria



# Create your views here.



def blog(request):
    posts=Post.objects.all()
    categoria = Categoria.objects.all()
    return render(request, "BlogApp/blog.html", {"posts":posts, "categorias": categoria})


def categoria(request, categoria_id):
    categoria = Categoria.objects.get(id=categoria_id)
    posts = Post.objects.filter(categorias=categoria)
    return render(request, "BlogApp/categoria.html", {'categorias': categoria, "posts":posts})

