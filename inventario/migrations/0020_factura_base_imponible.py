# Generated by Django 2.2.24 on 2024-10-15 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0019_auto_20241014_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='factura',
            name='base_imponible',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
    ]
