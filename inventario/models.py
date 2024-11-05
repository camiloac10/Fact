from decimal import Decimal

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# MODELOS

# --------------------------------USUARIO------------------------------------------------
class Usuario(AbstractUser):
    # id
    username = models.CharField(max_length=80, unique=True)
    password = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=60)
    nivel = models.IntegerField(null=True)

    @classmethod
    def numeroRegistrados(self):
        return int(self.objects.all().count())

    @classmethod
    def numeroUsuarios(self, tipo):
        if tipo == 'administrador':
            return int(self.objects.filter(is_superuser=True).count())
        elif tipo == 'usuario':
            return int(self.objects.filter(is_superuser=False).count())


class Opciones(models.Model):
    identificacion = models.CharField(max_length=20, unique=True, default='1234567890')
    razon_social = models.CharField(max_length=200, default='Empresa Predeterminada')
    nombre_comercial = models.CharField(max_length=200, default='Comercial X')
    direccion = models.TextField(max_length=200, default='Calle Falsa 123')
    correo = models.EmailField(max_length=100, default='correo@empresa.com')
    telefono = models.CharField(max_length=20, default='123456789')
    obligado = models.CharField(max_length=200, choices=[('1', 'SI'), ('2', 'NO')], default='1')
    tipo_regimen = models.CharField(max_length=20, choices=[('1', 'General'), ('2', 'RIMPE - EMPRENDEDORES')],
                                    default='1')
    valor_iva = models.IntegerField(unique=True, default=12)
    nombre_negocio = models.CharField(max_length=25, null=True, default='Mi negocio')
    mensaje_factura = models.TextField(null=True, default='Gracias por su compra')
    moneda = models.CharField(max_length=20, null=True, blank=True, default='USD')  # Nuevo campo


# ---------------------------------------------------------------------------------------


# -------------------------------PRODUCTO------------------------------------------------
class Producto(models.Model):
    decisiones = [('1', 'Unidad'), ('2', 'Kilo'), ('3', 'Litro'), ('4', 'Otros')]
    tiposIVA = [('0', '0%'), ('1', '13%'), ('2', '12%'), ('3', '14%'), ('4', '15%'), ('5', '5%'), ('6', 'No Objeto'),
                ('7', 'Exento de IVA'), ('8', '8%')]

    codigo = models.CharField(max_length=20)
    codigo_barras = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=40)
    precio = models.DecimalField(max_digits=9, decimal_places=2)
    precio2 = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    disponible = models.IntegerField(null=True)
    categoria = models.CharField(max_length=20, choices=decisiones)
    iva = models.CharField(max_length=10, choices=tiposIVA)
    costo_actual = models.DecimalField(max_digits=9, decimal_places=2)

    # Campos calculados para el precio con IVA
    precio_iva1 = models.DecimalField(max_digits=9, decimal_places=2, editable=False, default=0)
    precio_iva2 = models.DecimalField(max_digits=9, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        # Convertimos el tipo de IVA a porcentaje decimal
        iva_percent = Decimal(dict(self.tiposIVA).get(self.iva).replace('%', '')) / 100
        # Calculamos los precios con IVA
        self.precio_iva1 = self.precio * (Decimal('1.00') + iva_percent)
        if self.precio2:
            self.precio_iva2 = self.precio2 * (Decimal('1.00') + iva_percent)
        super(Producto, self).save(*args, **kwargs)

    @classmethod
    def numeroRegistrados(self):
        return int(self.objects.all().count())

    @classmethod
    def productosRegistrados(self):
        objetos = self.objects.all().order_by('descripcion')
        return objetos

    @classmethod
    def preciosProductos(self):
        objetos = self.objects.all().order_by('id')
        arreglo = []
        etiqueta = True
        extra = 1

        for indice, objeto in enumerate(objetos):
            arreglo.append([])
            if etiqueta:
                arreglo[indice].append(0)
                arreglo[indice].append("------")
                etiqueta = False
                arreglo.append([])

            arreglo[indice + extra].append(objeto.id)
            precio_producto = objeto.precio
            arreglo[indice + extra].append("%d" % (precio_producto))

        return arreglo

    @classmethod
    def productosDisponibles(self):
        objetos = self.objects.all().order_by('id')
        arreglo = []
        etiqueta = True
        extra = 1

        for indice, objeto in enumerate(objetos):
            arreglo.append([])
            if etiqueta:
                arreglo[indice].append(0)
                arreglo[indice].append("------")
                etiqueta = False
                arreglo.append([])

            arreglo[indice + extra].append(objeto.id)
            productos_disponibles = objeto.disponible
            arreglo[indice + extra].append("%d" % (productos_disponibles))

        return arreglo
    # ---------------------------------------------------------------------------------------


# ------------------------------------------CLIENTE--------------------------------------
class Cliente(models.Model):
    tipoCedula = models.CharField(max_length=2, choices=[
        ('1', 'Cédula'),
        ('2', 'Ruc'),
        ('3', 'Pasaporte'),
    ])
    cedula = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    correo = models.CharField(max_length=100)
    observaciones = models.CharField(max_length=300, blank=True, null=True)
    convencional = models.CharField(max_length=100, blank=True, null=True)
    tipoVenta = models.CharField(max_length=2, choices=[
        ('1', 'Local'),
        ('2', 'Exportación'),
    ])
    tipoRegimen = models.CharField(max_length=3, choices=[
        ('1', 'General'),
        ('2', 'Rimpe - Emprendedores'),
        ('3', 'Rimpe - Negocios Populares'),
    ])
    tipoCliente = models.CharField(max_length=2, choices=[
        ('1', 'Persona Natural'),
        ('2', 'Sociedad'),
    ])

    @classmethod
    def numeroRegistrados(self):
        return int(self.objects.all().count())

    @classmethod
    def cedulasRegistradas(self):
        objetos = self.objects.all().order_by('nombre')
        arreglo = []
        for indice, objeto in enumerate(objetos):
            arreglo.append([])
            arreglo[indice].append(objeto.cedula)
            nombre_cliente = objeto.nombre + " " + objeto.apellido
            arreglo[indice].append("%s. C.I: %s" % (nombre_cliente, self.formatearCedula(objeto.cedula)))

        return arreglo

    @staticmethod
    def formatearCedula(cedula):
        return format(int(cedula), ',d')
    # -----------------------------------------------------------------------------------------


# -------------------------------------FACTURA---------------------------------------------
from django.db import models
import datetime

from django.db import models
import datetime


class Factura(models.Model):
    # Relación con el cliente usando su cédula o RUC
    cliente = models.ForeignKey('Cliente', to_field='cedula', on_delete=models.CASCADE)

    # Fechas de emisión y vencimiento
    fecha_emision = models.DateField(default=datetime.date.today)
    fecha_vencimiento = models.DateField(default=datetime.date.today)

    # Serie y secuencia
    serie = models.CharField(max_length=6, default='001001')  # Formato 001001
    secuencia = models.CharField(max_length=9, default='000000001')  # Longitud de 9 dígitos

    # Concepto y datos del cliente
    concepto = models.CharField(max_length=255, blank=True, null=True)
    identificacion_cliente = models.CharField(max_length=13, default='9999999999999')  # RUC o cédula
    nombre_cliente = models.CharField(max_length=100, default='CONSUMIDOR FINAL')

    # Montos
    sub_monto = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    base_imponible = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    monto_general = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    # IVA relacionado con opciones de impuesto
    iva = models.ForeignKey('Opciones', to_field='valor_iva', on_delete=models.CASCADE, null=True, blank=True)

    # Código de producto
    codigo_producto = models.CharField(max_length=50, blank=True, null=True)

    # Clave de acceso para la facturación electrónica
    clave_acceso = models.CharField(max_length=49, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.clave_acceso:
            self.clave_acceso = self.generar_clave_acceso()
        super().save(*args, **kwargs)

    def generar_clave_acceso(self):
        # Lógica para generar los 49 dígitos de la clave de acceso según el esquema SRI
        return '1234567890123456789012345678901234567890123456789'  # Placeholder

    def __str__(self):
        return f'Factura {self.serie}-{self.secuencia}'

    # Métodos para obtener información agregada
    @classmethod
    def numeroRegistrados(cls):
        return cls.objects.count()

    @classmethod
    def ingresoTotal(cls):
        return cls.objects.aggregate(total=models.Sum('monto_general'))['total'] or 0

    def __str__(self):
        return f'Factura {self.serie}-{self.secuencia} para {self.cliente}'


# -----------------------------------------------------------------------------------------


# -------------------------------------DETALLES DE FACTURA---------------------------------
class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    sub_total = models.DecimalField(max_digits=20, decimal_places=2)
    total = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return f'Detalle de Factura {self.factura.id}: {self.producto.nombre}'

    @classmethod
    def productosVendidos(self):
        vendidos = self.objects.all()
        totalVendidos = 0
        for producto in vendidos:
            totalVendidos += producto.cantidad

        return totalVendidos

    @classmethod
    def ultimasVentas(self):
        objetos = self.objects.all().order_by('-id')[:10]

        return objetos


# ---------------------------------------------------------------------------------------


# ------------------------------------------PROVEEDOR-----------------------------------
class Proveedor(models.Model):
    # id
    cedula = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=40)
    direccion = models.CharField(max_length=200)
    nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    telefono2 = models.CharField(max_length=20, null=True)
    correo = models.CharField(max_length=100)
    correo2 = models.CharField(max_length=100, null=True)

    @classmethod
    def cedulasRegistradas(self):
        objetos = self.objects.all().order_by('nombre')
        arreglo = []
        for indice, objeto in enumerate(objetos):
            arreglo.append([])
            arreglo[indice].append(objeto.cedula)
            nombre_cliente = objeto.nombre + " " + objeto.apellido
            arreglo[indice].append("%s. C.I: %s" % (nombre_cliente, self.formatearCedula(objeto.cedula)))

        return arreglo

    @staticmethod
    def formatearCedula(cedula):
        return format(int(cedula), ',d')
    # ---------------------------------------------------------------------------------------


# ----------------------------------------PEDIDO-----------------------------------------
class Pedido(models.Model):
    # id
    proveedor = models.ForeignKey(Proveedor, to_field='cedula', on_delete=models.CASCADE)
    fecha = models.DateField()
    sub_monto = models.DecimalField(max_digits=20, decimal_places=2)
    monto_general = models.DecimalField(max_digits=20, decimal_places=2)
    iva = models.ForeignKey(Opciones, to_field='valor_iva', on_delete=models.CASCADE)
    presente = models.BooleanField(null=True)

    @classmethod
    def recibido(self, pedido):
        return self.objects.get(id=pedido).presente


# ---------------------------------------------------------------------------------------


# -------------------------------------DETALLES DE PEDIDO-------------------------------
class DetallePedido(models.Model):
    # id
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    sub_total = models.DecimalField(max_digits=20, decimal_places=2)
    total = models.DecimalField(max_digits=20, decimal_places=2)


# ---------------------------------------------------------------------------------------


# ------------------------------------NOTIFICACIONES------------------------------------
class Notificaciones(models.Model):
    # id
    autor = models.ForeignKey(Usuario, to_field='username', on_delete=models.CASCADE)
    mensaje = models.TextField()


# ---------------------------------------------------------------------------------------

# ------------------------------------SECUENCIAS------------------------------------
class Secuencia(models.Model):
    id = models.AutoField(
        primary_key=True,  # Declaramos que este es el campo de clave primaria
        verbose_name="ID"
    )

    descripcion = models.CharField(
        max_length=100,
        verbose_name="Descripción"
    )  # Descripción del documento (e.g., Facturas Electrónicas)

    tipo_documento = models.CharField(
        max_length=2,
        verbose_name="Tipo de Documento"
    )  # Tipo de documento (e.g., 01, 03)

    secuencial = models.IntegerField(
        verbose_name="Número Secuencial"
    )  # Número secuencial inicial

    establecimiento = models.CharField(
        max_length=3,
        verbose_name="Establecimiento"
    )  # Código del establecimiento (e.g., 001)

    punto_emision = models.CharField(
        max_length=3,
        verbose_name="Punto de Emisión"
    )  # Código del punto de emisión (e.g., 901)

    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )  # Si la secuencia está activa

    iva = models.BooleanField(
        default=True,
        verbose_name="IVA"
    )  # Si aplica IVA

    fiscal = models.BooleanField(
        default=True,
        verbose_name="Fiscal"
    )  # Si es un documento fiscal

    documento_electronico = models.BooleanField(
        default=True,
        verbose_name="Documento Electrónico"
    )  # Si es un documento electrónico

    class Meta:
        verbose_name = "Secuencia"
        verbose_name_plural = "Secuencias"
        db_table = 'inventario_secuencias'  # Nombre de la tabla en la base de datos
        unique_together = ('tipo_documento', 'establecimiento', 'punto_emision')

    def __str__(self):
        return f"{self.descripcion} - {self.tipo_documento} (Establecimiento: {self.establecimiento}, Punto de Emisión: {self.punto_emision})"


class FacturadorManager(BaseUserManager):
    def create_facturador(self, nombres, telefono, correo, password=None, **extra_fields):
        """Crea y guarda un nuevo facturador"""
        if not correo:
            raise ValueError('El correo es obligatorio')
        correo = self.normalize_email(correo)
        facturador = self.model(nombres=nombres, telefono=telefono, correo=correo, **extra_fields)
        facturador.set_password(password)
        facturador.save(using=self._db)
        return facturador


class Facturador(AbstractBaseUser):
    nombres = models.CharField(max_length=255, verbose_name='Nombres')
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name='Teléfono')
    correo = models.EmailField(unique=True, verbose_name='Correo')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    descuento_permitido = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name='Descuento Permitido'
    )

    objects = FacturadorManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombres', 'telefono']

    class Meta:
        verbose_name = 'Facturador'
        verbose_name_plural = 'Facturadores'

    def __str__(self):
        return f'{self.nombres} - {self.correo}'