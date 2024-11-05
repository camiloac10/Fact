from django.urls import path
from . import views
from .views import (
    ListaSecuencias, Secuencias, EditarSecuencia, EliminarSecuencia,
    CrearFacturador, ListarFacturadores, EditarFacturador, EliminarFacturador,
    LoginFacturador  # Importa la nueva vista aquí
)

app_name = "inventario"

urlpatterns = [
    # Login y Panel
    path('login', views.Login.as_view(), name='login'),
    path('panel', views.Panel.as_view(), name='panel'),
    path('salir', views.Salir.as_view(), name='salir'),
    path('perfil/<str:modo>/<int:p>', views.Perfil.as_view(), name='perfil'),
    path('eliminar/<str:modo>/<int:p>', views.Eliminar.as_view(), name='eliminar'),

    # Productos
    path('listarProductos', views.ListarProductos.as_view(), name='listarProductos'),
    path('agregarProducto', views.AgregarProducto.as_view(), name='agregarProducto'),
    path('importarProductos', views.ImportarProductos.as_view(), name='importarProductos'),
    path('exportarProductos', views.ExportarProductos.as_view(), name='exportarProductos'),
    path('editarProducto/<int:p>', views.EditarProducto.as_view(), name='editarProducto'),

    # Proveedores
    path('listarProveedores', views.ListarProveedores.as_view(), name='listarProveedores'),
    path('agregarProveedor', views.AgregarProveedor.as_view(), name='agregarProveedor'),
    path('importarProveedores', views.ImportarProveedores.as_view(), name='importarProveedores'),
    path('exportarProveedores', views.ExportarProveedores.as_view(), name='exportarProveedores'),
    path('editarProveedor/<int:p>', views.EditarProveedor.as_view(), name='editarProveedor'),

    # Pedidos
    path('agregarPedido', views.AgregarPedido.as_view(), name='agregarPedido'),
    path('listarPedidos', views.ListarPedidos.as_view(), name='listarPedidos'),
    path('detallesPedido', views.DetallesPedido.as_view(), name='detallesPedido'),
    path('verPedido/<int:p>', views.VerPedido.as_view(), name='verPedido'),
    path('validarPedido/<int:p>', views.ValidarPedido.as_view(), name='validarPedido'),
    path('generarPedido/<int:p>', views.GenerarPedido.as_view(), name='generarPedido'),
    path('generarPedidoPDF/<int:p>', views.GenerarPedidoPDF.as_view(), name='generarPedidoPDF'),

    # Clientes
    path('listarClientes', views.ListarClientes.as_view(), name='listarClientes'),
    path('agregarCliente', views.AgregarCliente.as_view(), name='agregarCliente'),
    path('importarClientes', views.ImportarClientes.as_view(), name='importarClientes'),
    path('exportarClientes', views.ExportarClientes.as_view(), name='exportarClientes'),
    path('editarCliente/<int:p>', views.EditarCliente.as_view(), name='editarCliente'),

    # Facturas
    path('emitirFactura', views.EmitirFactura.as_view(), name='emitirFactura'),
    path('detallesDeFactura', views.DetallesFactura.as_view(), name='detallesDeFactura'),
    path('listarFacturas', views.ListarFacturas.as_view(), name='listarFacturas'),
    path('verFactura/<int:p>', views.VerFactura.as_view(), name='verFactura'),
    path('generarFactura/<int:p>', views.GenerarFactura.as_view(), name='generarFactura'),
    path('generarFacturaPDF/<int:p>', views.GenerarFacturaPDF.as_view(), name='generarFacturaPDF'),

    # Usuarios
    path('crearUsuario', views.CrearUsuario.as_view(), name='crearUsuario'),
    path('listarUsuarios', views.ListarUsuarios.as_view(), name='listarUsuarios'),

    # BDD y Configuración
    path('importarBDD', views.ImportarBDD.as_view(), name='importarBDD'),
    path('descargarBDD', views.DescargarBDD.as_view(), name='descargarBDD'),
    path('configuracionGeneral', views.ConfiguracionGeneral.as_view(), name='configuracionGeneral'),
    path('verManualDeUsuario/<str:pagina>/', views.VerManualDeUsuario.as_view(), name='verManualDeUsuario'),

    # Secuencias
    path('secuencias/', Secuencias.as_view(), name='secuencias'),
    path('secuencias/crear/', Secuencias.as_view(), name='crear_secuencia'),
    path('ListaSecuencias/', ListaSecuencias.as_view(), name='lista_secuencias'),
    path('editarSecuencia/<int:id>/', EditarSecuencia.as_view(), name='editar_secuencia'),
    path('eliminarSecuencia/<int:id>/', EliminarSecuencia.as_view(), name='eliminar_secuencia'),

    # Facturadores
    path('facturadores/', ListarFacturadores.as_view(), name='listar_facturadores'),
    path('facturadores/crear/', CrearFacturador.as_view(), name='crear_facturador'),
    path('facturadores/editar/<int:id>/', EditarFacturador.as_view(), name='editar_facturador'),
    path('facturadores/eliminar/<int:id>/', EliminarFacturador.as_view(), name='eliminar_facturador'),

    # Login para facturadores
    path('login_facturador/', LoginFacturador.as_view(), name='login_facturador'),  # Nueva ruta
    #para búsqueda
    path('buscar_cliente/', views.buscar_cliente, name='buscar_cliente'),
    path('buscar_producto/', views.buscar_producto, name='buscar_producto'),
]
