# Generated by Django 2.2.24 on 2024-06-21 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0014_auto_20200609_1526'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detallefactura',
            name='sub_total',
        ),
        migrations.RemoveField(
            model_name='detallefactura',
            name='total',
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='base_imponible',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='codigo_auxiliar',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='codigo_impuesto',
            field=models.CharField(default=1, max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='codigo_porcentaje',
            field=models.CharField(default=1, max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='codigo_principal',
            field=models.CharField(default=1, max_length=25),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='descripcion',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='descuento',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='det_adicional_nombre0',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='det_adicional_nombre1',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='det_adicional_valor0',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='det_adicional_valor1',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='precio_sin_subsidio',
            field=models.DecimalField(decimal_places=6, default=1, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='precio_total_sin_impuesto',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='precio_unitario',
            field=models.DecimalField(decimal_places=6, default=1, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='tarifa',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='unidad_medida',
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='valor_devolucion_iva',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='detallefactura',
            name='valor_impuesto',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='agente_retencion',
            field=models.CharField(default=1, max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='clave_acceso',
            field=models.CharField(default=1, max_length=49),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='cod_doc',
            field=models.CharField(default=1, max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='contribuyente_especial',
            field=models.CharField(default=1, max_length=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='contribuyente_rimpe',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='dir_establecimiento',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='dir_matriz',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='direccion_comprador',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='estab',
            field=models.CharField(default=1, max_length=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='fecha_emision',
            field=models.DateField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='identificacion_comprador',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='importe_total',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='moneda',
            field=models.CharField(default=1, max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='nombre_comercial',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='factura',
            name='obligado_contabilidad',
            field=models.CharField(default=1, max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='pto_emi',
            field=models.CharField(default=1, max_length=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='razon_social',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='razon_social_comprador',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='ruc',
            field=models.CharField(default=1, max_length=13),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='secuencial',
            field=models.CharField(default=1, max_length=9),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='tipo_identificacion_comprador',
            field=models.CharField(default=1, max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='factura',
            name='total_descuento',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='factura',
            name='total_sin_impuestos',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='detallefactura',
            name='cantidad',
            field=models.DecimalField(decimal_places=6, max_digits=20),
        ),
    ]
