# Generated by Django 2.2.2 on 2019-09-08 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20190906_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='departure_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Horário de saída'),
        ),
        migrations.AlterField(
            model_name='log',
            name='entry_time',
            field=models.DateTimeField(verbose_name='Horário de entrada'),
        ),
    ]
