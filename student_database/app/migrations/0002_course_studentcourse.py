# Generated by Django 5.0.3 on 2024-03-29 08:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_name', models.CharField(max_length=100)),
                ('course_code', models.CharField(max_length=10, unique=True)),
                ('dept', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='StudentCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance', models.FloatField(default=0)),
                ('course_marks', models.FloatField(default=0)),
                ('course_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.course')),
                ('regno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.details')),
            ],
        ),
    ]
