import datetime
from decimal import Decimal
from django import forms
from .models import Producto, Cliente, Proveedor, Usuario, Opciones, Secuencia, Facturador
from django.forms import ModelChoiceField
from django.core.exceptions import ValidationError

class MisProductos(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.descripcion

class MisPrecios(ModelChoiceField):
    def label_from_instance(self,obj):
        return "%s" % obj.precio

class MisDisponibles(ModelChoiceField):
    def label_from_instance(self,obj):
        return "%s" % obj.disponible

class LoginFormulario(forms.Form):
    username = forms.CharField(label="Tu nombre de usuario",
            widget=forms.TextInput(attrs={
            'placeholder': 'Cédula o RUC',
            'class': 'form-control underlined',
            'type': 'text',
            'id': 'user',
            'maxlength': '13',
            'pattern': '[0-9]*',
            'inputmode': 'numeric'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.isdigit():
            raise ValidationError('El nombre de usuario solo debe contener números.')
        return username
    password = forms.CharField(label="Contraseña",widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña',
        'class': 'form-control underlined', 'type':'password','id':'password'}))


class ProductoFormulario(forms.ModelForm):
    precio = forms.DecimalField(
        min_value=0,
        label='Precio',
        widget=forms.NumberInput(attrs={'placeholder': 'Precio del producto', 'id': 'precio', 'class': 'form-control'}),
    )

    precio2 = forms.DecimalField(
        min_value=0,
        label='Precio 2',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Precio 2 (opcional)', 'id': 'precio2', 'class': 'form-control'}),
    )

    class Meta:
        model = Producto
        fields = ['codigo', 'codigo_barras', 'descripcion', 'precio', 'precio2', 'categoria', 'disponible', 'iva', 'costo_actual']
        labels = {
            'descripcion': 'Nombre',
            'disponible': 'Disponible',
            'iva': 'I.V.A:',
            'costo_actual': 'Costo actual:',
        }
        widgets = {
            'codigo': forms.TextInput(attrs={'placeholder': 'Código del producto', 'id': 'codigo', 'class': 'form-control'}),
            'codigo_barras': forms.TextInput(attrs={'placeholder': 'Código de barras del producto', 'id': 'codigo_barras', 'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'placeholder': 'Nombre del producto', 'id': 'descripcion', 'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control', 'id': 'categoria'}),
            'disponible': forms.NumberInput(attrs={'placeholder': 'Cantidad disponible', 'id': 'disponible', 'class': 'form-control'}),
            'iva': forms.Select(attrs={'class': 'form-control', 'id': 'iva'}),
            'costo_actual': forms.TextInput(attrs={'placeholder': 'Costo actual', 'id': 'costo_actual', 'class': 'form-control'}),
        }

    # Campos de solo lectura para mostrar el precio con IVA calculado
    precio_iva1 = forms.DecimalField(
        label='Precio IVA 1:',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'id': 'precio_iva1'}),
    )

    precio_iva2 = forms.DecimalField(
        label='Precio IVA 2:',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'id': 'precio_iva2'}),
    )

    def __init__(self, *args, **kwargs):
        super(ProductoFormulario, self).__init__(*args, **kwargs)
        if self.instance.pk:
            # El formulario se utiliza para editar un producto existente
            self.calcular_precios_con_iva(self.instance.precio, self.instance.precio2, self.instance.iva)
        else:
            # El formulario es nuevo
            self.fields['precio_iva1'].initial = 0
            self.fields['precio_iva2'].initial = 0

    def calcular_precios_con_iva(self, precio, precio2, iva):
        iva_percent = Decimal(dict(Producto.tiposIVA).get(iva).replace('%', '')) / 100
        self.fields['precio_iva1'].initial = precio * (Decimal('1.00') + iva_percent)
        if precio2:
            self.fields['precio_iva2'].initial = precio2 * (Decimal('1.00') + iva_percent)
        else:
            self.fields['precio_iva2'].initial = 0

class ImportarProductosFormulario(forms.Form):
    importar = forms.FileField(
        max_length = 100000000000,
        label = 'Escoger archivo',
        widget = forms.ClearableFileInput(
        attrs={'id':'importar','class':'form-control'}),
        )

class ImportarClientesFormulario(forms.Form):
    importar = forms.FileField(
        max_length = 100000000000,
        label = 'Escoger archivo',
        widget = forms.ClearableFileInput(
        attrs={'id':'importar','class':'form-control'}),
        )

class ExportarProductosFormulario(forms.Form):
    desde = forms.DateField(
        label = 'Desde',
        widget = forms.DateInput(format=('%d-%m-%Y'),
        attrs={'id':'desde','class':'form-control','type':'date'}),
        )

    hasta = forms.DateField(
        label = 'Hasta',
        widget = forms.DateInput(format=('%d-%m-%Y'),
        attrs={'id':'hasta','class':'form-control','type':'date'}),
        )

class ExportarClientesFormulario(forms.Form):
    desde = forms.DateField(
        label = 'Desde',
        widget = forms.DateInput(format=('%d-%m-%Y'),
        attrs={'id':'desde','class':'form-control','type':'date'}),
        )

    hasta = forms.DateField(
        label = 'Hasta',
        widget = forms.DateInput(format=('%d-%m-%Y'),
        attrs={'id':'hasta','class':'form-control','type':'date'}),
        )
class ClienteFormulario(forms.ModelForm):
    tipoC = [('1', 'Cédula'), ('2', 'Ruc'), ('3', 'Pasaporte')]
    tipoV = [('1', 'Local'), ('2', 'Exportación')]
    tipoR = [('1', 'General'), ('2', 'Rimpe - Emprendedores'), ('3', 'Rimpe - Negocios Populares')]
    tipoCL = [('1', 'Persona Natural'), ('2', 'Sociedad')]

    tipoCedula = forms.ChoiceField(
        label="Tipo de cedula",
        choices=tipoC,
        widget=forms.Select(attrs={'placeholder': 'Tipo de cedula', 'id': 'tipoCedula', 'class': 'form-control'})
    )
    tipoVenta = forms.ChoiceField(
        label="Tipo de venta",
        choices=tipoV,
        widget=forms.Select(attrs={'placeholder': 'Tipo de venta', 'id': 'tipoVenta', 'class': 'form-control'})
    )
    tipoRegimen = forms.ChoiceField(
        label="Tipo de regimen",
        choices=tipoR,
        widget=forms.Select(attrs={'placeholder': 'Tipo de regimen', 'id': 'tipoRegimen', 'class': 'form-control'})
    )
    tipoCliente = forms.ChoiceField(
        label="Tipo de cliente",
        choices=tipoCL,
        widget=forms.Select(attrs={'placeholder': 'Tipo de cliente', 'id': 'tipoCliente', 'class': 'form-control'})
    )

    class Meta:
        model = Cliente
        fields = ['tipoCedula', 'cedula', 'nombre', 'apellido', 'direccion', 'telefono', 'correo', 'observaciones', 'convencional', 'tipoVenta', 'tipoRegimen', 'tipoCliente']
        labels = {
            'cedula': 'Cedula del cliente',
            'nombre': 'Razón Social',
            'apellido': 'Nombre Comercial',
            'direccion': 'Dirección',
            'telefono': 'Numero telefonico del cliente',
            'correo': 'Correo electronico del cliente',
            'observaciones': 'Observaciones del cliente',
            'convencional': 'Convencional del cliente',
            'tipoVenta': 'Tipo de venta',
            'tipoRegimen': 'Tipo de Régimen',
            'tipoCliente': 'Tipo de cliente'
        }
        widgets = {
            'cedula': forms.TextInput(attrs={
                'placeholder': 'Inserte la cedula de identidad del cliente',
                'id': 'cedula',
                'class': 'form-control'
            }),
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Inserte la razón social',
                'id': 'nombre',
                'class': 'form-control'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'apellido',
                'placeholder': 'Inserte el nombre comercial'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'direccion',
                'placeholder': 'Direccion del cliente'
            }),
            'telefono': forms.TextInput(attrs={
                'id': 'telefono',
                'class': 'form-control',
                'placeholder': 'El telefono del cliente'
            }),
            'correo': forms.TextInput(attrs={
                'placeholder': 'Correo del cliente',
                'id': 'correo',
                'class': 'form-control'
            }),
            'convencional': forms.TextInput(attrs={
                'placeholder': 'Convencional del cliente',
                'id': 'convencional',
                'class': 'form-control'
            }),
            'observaciones': forms.TextInput(attrs={
                'placeholder': 'Observaciones del cliente',
                'id': 'observaciones',
                'class': 'form-control'
            }),
        }

class EmitirFacturaFormulario(forms.Form):
    def __init__(self, *args, **kwargs):
        elecciones = kwargs.pop('cedulas', None)  # Opciones para los clientes
        productos = kwargs.pop('productos', None)  # Opciones para los productos
        super(EmitirFacturaFormulario, self).__init__(*args, **kwargs)

        # Cliente a facturar
        if elecciones:
            self.fields["cliente"] = forms.CharField(
                label="Cliente a facturar", max_length=50,
                widget=forms.Select(
                    choices=elecciones,
                    attrs={
                        'placeholder': 'La cédula del cliente a facturar',
                        'id': 'cliente', 'class': 'form-control'
                    }
                )
            )

        # Productos disponibles
        if productos:
            self.fields["producto"] = forms.ChoiceField(
                label="Producto",
                choices=[(p.id, p.descripcion) for p in productos],
                widget=forms.Select(attrs={'class': 'form-control'})
            )

    productos = forms.IntegerField(
        label="Número de productos",
        widget=forms.NumberInput(
            attrs={'placeholder': 'Número de productos a facturar', 'id': 'productos', 'class': 'form-control'}
        )
    )

    fecha_emision = forms.DateField(
        label="Fecha de emisión",
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    fecha_vencimiento = forms.DateField(
        label="Fecha de vencimiento",
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    serie = forms.CharField(
        label="Serie",
        max_length=3,
        initial='001',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Serie de la factura'})
    )

    secuencia = forms.CharField(
        label="Secuencia",
        max_length=9,
        initial='000000000',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Secuencia de la factura'})
    )

    concepto = forms.CharField(
        label="Concepto",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Concepto de la factura'})
    )

    identificacion_cliente = forms.CharField(
        label="C.I./RUC",
        max_length=13,
        initial='9999999999999',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'C.I. o RUC del cliente'})
    )

    nombre_cliente = forms.CharField(
        label="Nombre del cliente",
        max_length=100,
        initial='CONSUMIDOR FINAL',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'})
    )

    codigo_producto = forms.CharField(
        label="Código del producto",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código del producto (opcional)'})
    )
class DetallesFacturaFormulario(forms.Form):
    productos = Producto.productosRegistrados()

    descripcion = MisProductos(queryset=productos,widget=forms.Select(attrs={'placeholder': 'El producto a debitar','class':'form-control select-group','onchange':'establecerOperaciones(this)'}))

    vista_precio = MisPrecios(required=False,queryset=productos,label="Precio del producto",widget=forms.Select(attrs={'placeholder': 'El precio del producto','class':'form-control','disabled':'true'}))

    cantidad = forms.IntegerField(label="Cantidad a facturar",min_value=0,widget=forms.NumberInput(attrs={'placeholder': 'Introduzca la cantidad del producto','class':'form-control','value':'0','onchange':'calculoPrecio(this);calculoDisponible(this)', 'max':'0'}))

    cantidad_disponibles = forms.IntegerField(required=False,label="Stock disponible",min_value=0,widget=forms.NumberInput(attrs={'placeholder': 'Introduzca la cantidad del producto','class':'form-control','value':'0', 'max':'0', 'disabled':'true'}))

    selec_disponibles = MisDisponibles(queryset=productos,required=False,widget=forms.Select(attrs={'placeholder': 'El producto a debitar','class':'form-control','disabled':'true','hidden':'true'}))

    subtotal = forms.DecimalField(required=False,label="Sub-total",min_value=0,widget=forms.NumberInput(attrs={'placeholder': 'Monto sub-total','class':'form-control','disabled':'true','value':'0'}))

    valor_subtotal = forms.DecimalField(min_value=0,widget=forms.NumberInput(attrs={'placeholder': 'Monto sub-total','class':'form-control','hidden':'true','value':'0'}))


class EmitirPedidoFormulario(forms.Form):
    def __init__(self, *args, **kwargs):
       elecciones = kwargs.pop('cedulas')
       super(EmitirPedidoFormulario, self).__init__(*args, **kwargs)

       if(elecciones):
            self.fields["proveedor"] = forms.CharField(label="Proveedor",max_length=50,
            widget=forms.Select(choices=elecciones,attrs={'placeholder': 'La cedula del proveedor que vende el producto',
            'id':'proveedor','class':'form-control'}))

    productos = forms.IntegerField(label="Numero de productos",widget=forms.NumberInput(attrs={'placeholder': 'Numero de productos a comprar',
        'id':'productos','class':'form-control'}))


class DetallesPedidoFormulario(forms.Form):
    productos = Producto.productosRegistrados()
    precios = Producto.preciosProductos()

    descripcion = MisProductos(queryset=productos,widget=forms.Select(attrs={'placeholder': 'El producto a debitar','class':'form-control','onchange':'establecerPrecio(this)'}))

    vista_precio = MisPrecios(required=False,queryset=productos,label="Precio del producto",widget=forms.Select(attrs={'placeholder': 'El precio del producto','class':'form-control','disabled':'true'}))

    cantidad = forms.IntegerField(label="Cantidad",min_value=0,widget=forms.NumberInput(attrs={'placeholder': 'Introduzca la cantidad del producto','class':'form-control','value':'0','onchange':'calculoPrecio(this)'}))

    subtotal = forms.DecimalField(required=False,label="Sub-total",min_value=0,widget=forms.NumberInput(attrs={'placeholder': 'Monto sub-total','class':'form-control','disabled':'true','value':'0'}))

    valor_subtotal = forms.DecimalField(min_value=0,widget=forms.NumberInput(attrs={'placeholder': 'Monto sub-total','class':'form-control','hidden':'true','value':'0'}))




class ProveedorFormulario(forms.ModelForm):
    tipoC =  [ ('1','V'),('2','E') ]

    telefono2 = forms.CharField(
        required = False,
        label = 'Segundo numero telefonico( Opcional )',
        widget = forms.TextInput(
        attrs={'placeholder': 'Inserte el telefono alternativo del proveedor',
        'id':'telefono2','class':'form-control'}),
        )

    correo2 = forms.CharField(
        required=False,
        label = 'Segundo correo electronico( Opcional )',
        widget = forms.TextInput(
        attrs={'placeholder': 'Inserte el correo alternativo del proveedor',
        'id':'correo2','class':'form-control'}),
        )

    tipoCedula = forms.CharField(
        label="Tipo de cedula",
        max_length=2,
        widget=forms.Select(choices=tipoC,attrs={'placeholder': 'Tipo de cedula',
        'id':'tipoCedula','class':'form-control'}
        )
        )


    class Meta:
        model = Cliente
        fields = ['tipoCedula','cedula','nombre','apellido','direccion','telefono','correo','telefono2','correo2']
        labels = {
        'cedula': 'Cedula del proveedor',
        'nombre': 'Nombre del proveedor',
        'apellido': 'Apellido del proveedor',
        'direccion': 'Direccion del proveedor',
        'telefono': 'Numero telefonico del proveedor',
        'correo': 'Correo electronico del proveedor',
        'telefono2': 'Segundo numero telefonico',
        'correo2': 'Segundo correo electronico'
        }
        widgets = {
        'cedula': forms.TextInput(attrs={'placeholder': 'Inserte la cedula de identidad del proveedor',
        'id':'cedula','class':'form-control'} ),
        'nombre': forms.TextInput(attrs={'placeholder': 'Inserte el primer o primeros nombres del proveedor',
        'id':'nombre','class':'form-control'}),
        'apellido': forms.TextInput(attrs={'class':'form-control','id':'apellido','placeholder':'El apellido del proveedor'}),
        'direccion': forms.TextInput(attrs={'class':'form-control','id':'direccion','placeholder':'Direccion del proveedor'}),
        'nacimiento':forms.DateInput(format=('%d-%m-%Y'),attrs={'id':'hasta','class':'form-control','type':'date'} ),
        'telefono':forms.TextInput(attrs={'id':'telefono','class':'form-control',
        'placeholder':'El telefono del proveedor'} ),
        'correo':forms.TextInput(attrs={'placeholder': 'Correo del proveedor',
        'id':'correo','class':'form-control'} )
        }


class UsuarioFormulario(forms.Form):
    niveles =  [ ('1','Administrador'),('0','Usuario') ]

    username = forms.CharField(
        label = "Nombre de usuario",
        max_length=50,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte un nombre de usuario',
        'id':'username','class':'form-control','value':''} ),
        )

    first_name = forms.CharField(
        label = 'Nombre',
        max_length =100,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte un nombre',
        'id':'first_name','class':'form-control','value':''}),
        )

    last_name = forms.CharField(
        label = 'Apellido',
        max_length = 100,
        widget = forms.TextInput(attrs={'class':'form-control','id':'last_name','placeholder':'Inserte un apellido','value':''}),
        )

    email = forms.CharField(
        label = 'Correo electronico',
        max_length=100,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte un correo valido',
        'id':'email','class':'form-control','type':'email','value':''} )
        )

    level =  forms.CharField(
        required=False,
        label="Nivel de acceso",
        max_length=2,
        widget=forms.Select(choices=niveles,attrs={'placeholder': 'El nivel de acceso',
        'id':'level','class':'form-control','value':''}
        )
        )

class NuevoUsuarioFormulario(forms.Form):
    niveles =  [ ('1','Administrador'),('0','Usuario') ]

    username = forms.CharField(
        label = "Nombre de usuario",
        max_length=50,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte un nombre de usuario',
        'id':'username','class':'form-control','value':''} ),
        )

    first_name = forms.CharField(
        label = 'Nombre',
        max_length =100,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte un nombre',
        'id':'first_name','class':'form-control','value':''}),
        )

    last_name = forms.CharField(
        label = 'Apellido',
        max_length = 100,
        widget = forms.TextInput(attrs={'class':'form-control','id':'last_name','placeholder':'Inserte un apellido','value':''}),
        )

    email = forms.CharField(
        label = 'Correo electronico',
        max_length=100,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte un correo valido',
        'id':'email','class':'form-control','type':'email','value':''} )
        )

    password = forms.CharField(
        label = 'Clave',
        max_length=100,
        widget = forms.TextInput(attrs={'placeholder': 'Inserte una clave',
        'id':'password','class':'form-control','type':'password','value':''} )
        )

    rep_password = forms.CharField(
        label = 'Repetir clave',
        max_length=100,
        widget = forms.TextInput(attrs={'placeholder': 'Repita la clave de arriba',
        'id':'rep_password','class':'form-control','type':'password','value':''} )
        )

    level =  forms.CharField(
        label="Nivel de acceso",
        max_length=2,
        widget=forms.Select(choices=niveles,attrs={'placeholder': 'El nivel de acceso',
        'id':'level','class':'form-control','value':''}
        )
        )


class ClaveFormulario(forms.Form):
    #clave = forms.CharField(
        #label = 'Ingrese su clave actual',
        #max_length=50,
        #widget = forms.TextInput(
        #attrs={'placeholder': 'Inserte la clave actual para verificar su identidad',
        #'id':'clave','class':'form-control', 'type': 'password'}),
        #)

    clave_nueva = forms.CharField(
        label = 'Ingrese la clave nueva',
        max_length=50,
        widget = forms.TextInput(
        attrs={'placeholder': 'Inserte la clave nueva de acceso',
        'id':'clave_nueva','class':'form-control', 'type': 'password'}),
        )

    repetir_clave = forms.CharField(
        label="Repita la clave nueva",
        max_length=50,
        widget = forms.TextInput(
        attrs={'placeholder': 'Vuelva a insertar la clave nueva',
        'id':'repetir_clave','class':'form-control', 'type': 'password'}),
        )


class ImportarBDDFormulario(forms.Form):
    archivo = forms.FileField(
        widget=forms.FileInput(
            attrs={'placeholder': 'Archivo de la base de datos',
            'id':'customFile','class':'custom-file-input'})
        )

class OpcionesFormulario(forms.Form):
    regimen = [('1', 'General'), ('2', 'RIMPE - EMPRENDEDORES'), ('3', 'RIMPE - NEGOCIOS POPULARES')]
    obligacion = [('1', 'SI'), ('2', 'NO')]
    identificacion = forms.CharField(
        label='Identificación',
        max_length=20,
        widget=forms.TextInput(
            attrs={
                   'id': 'identificacion', 'class': 'form-control'}),
    )
    razon_social = forms.CharField(
        label='Razón social',
        max_length=200,
        widget=forms.TextInput(
            attrs={
                   'id': 'razon_social', 'class': 'form-control'}),
    )
    nombre_comercial = forms.CharField(
        label='Nombre Comercial',
        max_length=200,
        widget=forms.TextInput(
            attrs={
                   'id': 'razon_social', 'class': 'form-control'}),
    )

    direccion = forms.CharField(
        label='Dirección',
        max_length=200,
        widget=forms.TextInput(
            attrs={
                   'id': 'direccion', 'class': 'form-control'}),
    )
    correo = forms.CharField(
        label='Correo electrónico',
        max_length=100,
        widget=forms.TextInput(
            attrs={'id': 'correo', 'class': 'form-control'}),
    )
    telefono = forms.CharField(
        label='Telefono',
        max_length=100,
        widget=forms.TextInput(
            attrs={'id': 'telefono', 'class': 'form-control'}),
    )
    obligado = forms.CharField(
        label="Obligación",
        max_length=2,
        widget=forms.Select(choices=obligacion, attrs={'placeholder': 'Obligado o no',
        'id': 'obligado', 'class': 'form-control'}
                            )
    )
    tipo_regimen = forms.CharField(
        label="Régimen",
        max_length=2,
        widget=forms.Select(choices=regimen, attrs={'placeholder': 'Régimen de la empresa',
        'id': 'tipo_regimen', 'class': 'form-control'}
                            )
    )
    moneda = forms.CharField(
        label = 'Moneda a emplear en el sistema',
        max_length=20,
        widget = forms.TextInput(
        attrs={'placeholder': 'Inserte la abreviatura de la moneda que quiere usar (Ejemplo: $)',
        'id':'moneda','class':'form-control'}),
        )

    valor_iva = forms.DecimalField(
        label="Valor del IVA",
        min_value=0,widget=forms.NumberInput(
            attrs={'placeholder': 'Introduzca el IVA actual',
            'class':'form-control','id':'valor_iva'}))

    mensaje_factura = forms.CharField(
        label = 'Mensaje personal que va en las facturas',
        max_length=50,
        widget = forms.TextInput(
        attrs={'placeholder': 'Inserte el mensaje personal que ira en el pie de la factura',
        'id':'mensaje_factura','class':'form-control'}),
        )

    nombre_negocio = forms.CharField(
        label = 'Nombre actual del negocio',
        max_length=50,
        widget = forms.TextInput(
        attrs={'class':'form-control','id':'nombre_negocio',
            'placeholder':'Coloque el nombre actual del negocio'}),
        )

    imagen = forms.FileField(required=False,widget = forms.FileInput(
        attrs={'class':'custom-file-input','id':'customFile'}))

from django import forms
from .models import Secuencia

from django import forms
from .models import Secuencia

class SecuenciaFormulario(forms.ModelForm):
    id = forms.IntegerField(
        required=False,  # Esto permite que sea opcional al crear nuevas secuencias
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'ID de la Secuencia',
                'id': 'id',
                'class': 'form-control'
            }
        ),
        label='ID'
    )

    class Meta:
        model = Secuencia
        fields = [
            'id',  # Incluir el campo de ID aquí
            'descripcion',
            'tipo_documento',
            'secuencial',
            'establecimiento',
            'punto_emision',
            'activo',
            'iva',
            'fiscal',
            'documento_electronico'
        ]
        labels = {
            'descripcion': 'Descripción',
            'tipo_documento': 'Tipo de Documento',
            'secuencial': 'Secuencial',
            'establecimiento': 'Establecimiento',
            'punto_emision': 'Punto de Emisión',
            'activo': 'Activo',
            'iva': 'IVA',
            'fiscal': 'Fiscal',
            'documento_electronico': 'Documento Electrónico'
        }
        widgets = {
            'descripcion': forms.TextInput(
                attrs={
                    'placeholder': 'Descripción del documento',
                    'id': 'descripcion',
                    'class': 'form-control'
                }
            ),
            'tipo_documento': forms.Select(
                choices=[
                    ('01', 'Factura'),
                    ('03', 'Liquidación de Compra'),
                    ('04', 'Nota de Crédito'),
                    ('05', 'Nota de Débito'),
                    ('06', 'Guía de Remisión'),
                    ('07', 'Retención')
                ],
                attrs={
                    'id': 'tipo_documento',
                    'class': 'form-control'
                }
            ),
            'secuencial': forms.NumberInput(
                attrs={
                    'placeholder': 'Número secuencial',
                    'id': 'secuencial',
                    'class': 'form-control'
                }
            ),
            'establecimiento': forms.TextInput(
                attrs={
                    'placeholder': 'Código del establecimiento',
                    'id': 'establecimiento',
                    'class': 'form-control'
                }
            ),
            'punto_emision': forms.TextInput(
                attrs={
                    'placeholder': 'Código del punto de emisión',
                    'id': 'punto_emision',
                    'class': 'form-control'
                }
            ),
            'activo': forms.CheckboxInput(
                attrs={
                    'id': 'activo',
                    'class': 'form-check-input'
                }
            ),
            'iva': forms.CheckboxInput(
                attrs={
                    'id': 'iva',
                    'class': 'form-check-input'
                }
            ),
            'fiscal': forms.CheckboxInput(
                attrs={
                    'id': 'fiscal',
                    'class': 'form-check-input'
                }
            ),
            'documento_electronico': forms.CheckboxInput(
                attrs={
                    'id': 'documento_electronico',
                    'class': 'form-check-input'
                }
            ),
        }

class FacturadorForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la contraseña'
        }),
        label='Contraseña',
        min_length=8,
        required=False,  # No obligatorio al editar
        error_messages={
            'min_length': 'La contraseña debe tener al menos 8 caracteres.',
        }
    )
    verificar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Verifique la contraseña'
        }),
        label='Verificar Contraseña',
        required=False  # No obligatorio al editar
    )
    nombres = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el nombre completo'
        }),
        label='Nombres',
        max_length=255,
        error_messages={
            'required': 'El campo nombres es obligatorio.',
        }
    )
    telefono = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el teléfono'
        }),
        label='Teléfono',
        max_length=15,
        required=False
    )
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el correo electrónico'
        }),
        label='Correo',
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Ingrese un correo válido.',
        }
    )
    descuento_permitido = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el descuento permitido'
        }),
        label='Descuento Permitido',
        max_digits=5,
        decimal_places=2
    )
    activo = forms.BooleanField(
        required=False,
        initial=True,
        label='Activo',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    class Meta:
        model = Facturador
        fields = [
            'nombres',
            'telefono',
            'correo',
            'descuento_permitido',
            'activo',
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        verificar_password = cleaned_data.get("verificar_password")

        # Si se proporciona una contraseña, validar que coincidan
        if password or verificar_password:
            if password != verificar_password:
                raise forms.ValidationError("Las contraseñas no coinciden. Inténtelo de nuevo.")

        return cleaned_data

