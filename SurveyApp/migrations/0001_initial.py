# Generated by Django 4.2.6 on 2023-10-24 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OpcionMultiple',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.CharField(max_length=255)),
                ('es_correcta', models.BooleanField(default=False)),
                ('puntaje', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Pregunta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField()),
                ('tipo_pregunta', models.CharField(choices=[('TEX', 'Pregunta de texto'), ('OPC', 'Pregunta de opciones múltiples')], default='TEX', max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='RespuestaUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto_respuesta', models.TextField(blank=True, null=True)),
                ('opcion_elegida', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SurveyApp.opcionmultiple')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SurveyApp.pregunta')),
            ],
        ),
        migrations.AddField(
            model_name='opcionmultiple',
            name='pregunta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SurveyApp.pregunta'),
        ),
    ]