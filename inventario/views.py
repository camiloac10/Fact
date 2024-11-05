#renderiza las vistas al usuario
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal  # Importar Decimal para manejar las operaciones correctamente
# para redirigir a otras paginas
from django.http import HttpResponseRedirect, HttpResponse, FileResponse, JsonResponse
#el formulario de login
from .forms import *
# clase para crear vistas basadas en sub-clases
from django.views import View
#autentificacion de usuario e inicio de sesion
from django.contrib.auth import authenticate, login, logout
#verifica si el usuario esta logeado
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SecuenciaFormulario  # Asumiendo que existe un formulario llamado SecuenciaFormulario
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Secuencia
from .forms import SecuenciaFormulario
#modelos
from .models import *
#formularios dinamicos
from django.forms import formset_factory
#funciones personalizadas
from .funciones import *
#Mensajes de formulario
from django.contrib import messages
#Ejecuta un comando en la terminal externa
from django.core.management import call_command
#procesa archivos en .json
from django.core import serializers
#permite acceder de manera mas facil a los ficheros
from django.core.files.storage import FileSystemStorage


#Vistas endogenas.


#Interfaz de inicio de sesion----------------------------------------------------#
class Login(View):
    #Si el usuario ya envio el formulario por metodo post
    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = LoginFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            usuario = form.cleaned_data['username']
            clave = form.cleaned_data['password']
            # Se verifica que el usuario y su clave existan
            logeado = authenticate(request, username=usuario, password=clave)
            if logeado is not None:
                login(request, logeado)
                #Si el login es correcto lo redirige al panel del sistema:
                return HttpResponseRedirect('/inventario/panel')
            else:
                #De lo contrario lanzara el mismo formulario
                return render(request, 'inventario/login.html', {'form': form})

    # Si se llega por GET crearemos un formulario en blanco
    def get(self, request):
        if request.user.is_authenticated == True:
            return HttpResponseRedirect('/inventario/panel')

        form = LoginFormulario()
        #Envia al usuario el formulario para que lo llene
        return render(request, 'inventario/login.html', {'form': form})


#Fin de vista---------------------------------------------------------------------#


#Panel de inicio y vista principal------------------------------------------------#
class Panel(LoginRequiredMixin, View):
    #De no estar logeado, el usuario sera redirigido a la pagina de Login
    #Las dos variables son la pagina a redirigir y el campo adicional, respectivamente
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        from datetime import date
        #Recupera los datos del usuario despues del login
        contexto = {'usuario': request.user.username,
                    'id_usuario': request.user.id,
                    'nombre': request.user.first_name,
                    'apellido': request.user.last_name,
                    'correo': request.user.email,
                    'fecha': date.today(),
                    'productosRegistrados': Producto.numeroRegistrados(),
                    'productosVendidos': DetalleFactura.productosVendidos(),
                    'clientesRegistrados': Cliente.numeroRegistrados(),
                    'usuariosRegistrados': Usuario.numeroRegistrados(),
                    'facturasEmitidas': Factura.numeroRegistrados(),
                    'ingresoTotal': Factura.ingresoTotal(),
                    'ultimasVentas': DetalleFactura.ultimasVentas(),
                    'administradores': Usuario.numeroUsuarios('administrador'),
                    'usuarios': Usuario.numeroUsuarios('usuario')

                    }

        return render(request, 'inventario/panel.html', contexto)


#Fin de vista----------------------------------------------------------------------#


#Maneja la salida del usuario------------------------------------------------------#
class Salir(LoginRequiredMixin, View):
    #Sale de la sesion actual
    login_url = 'inventario/login'
    redirect_field_name = None

    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/inventario/login')


#Fin de vista----------------------------------------------------------------------#


#Muestra el perfil del usuario logeado actualmente---------------------------------#
class Perfil(LoginRequiredMixin, View):
    login_url = 'inventario/login'
    redirect_field_name = None

    #se accede al modo adecuado y se valida al usuario actual para ver si puede modificar al otro usuario-
    #-el cual es obtenido por la variable 'p'
    def get(self, request, modo, p):
        if modo == 'editar':
            perf = Usuario.objects.get(id=p)
            editandoSuperAdmin = False

            if p == 1:
                if request.user.nivel != 2:
                    messages.error(request,
                                   'No puede editar el perfil del administrador por no tener los permisos suficientes')
                    return HttpResponseRedirect('/inventario/perfil/ver/%s' % p)
                editandoSuperAdmin = True
            else:
                if request.user.is_superuser != True:
                    messages.error(request, 'No puede cambiar el perfil por no tener los permisos suficientes')
                    return HttpResponseRedirect('/inventario/perfil/ver/%s' % p)

                else:
                    if perf.is_superuser == True:
                        if request.user.nivel == 2:
                            pass

                        elif perf.id != request.user.id:
                            messages.error(request, 'No puedes cambiar el perfil de un usuario de tu mismo nivel')

                            return HttpResponseRedirect('/inventario/perfil/ver/%s' % p)

            if editandoSuperAdmin:
                form = UsuarioFormulario()
                form.fields['level'].disabled = True
            else:
                form = UsuarioFormulario()

            #Me pregunto si habia una manera mas facil de hacer esto, solo necesitaba hacer que el formulario-
            #-apareciera lleno de una vez, pero arrojaba User already exists y no pasaba de form.is_valid()
            form['username'].field.widget.attrs['value'] = perf.username
            form['first_name'].field.widget.attrs['value'] = perf.first_name
            form['last_name'].field.widget.attrs['value'] = perf.last_name
            form['email'].field.widget.attrs['value'] = perf.email
            form['level'].field.widget.attrs['value'] = perf.nivel

            #Envia al usuario el formulario para que lo llene
            contexto = {'form': form, 'modo': request.session.get('perfilProcesado'), 'editar': 'perfil',
                        'nombreUsuario': perf.username}

            contexto = complementarContexto(contexto, request.user)
            return render(request, 'inventario/perfil/perfil.html', contexto)


        elif modo == 'clave':
            perf = Usuario.objects.get(id=p)
            if p == 1:
                if request.user.nivel != 2:
                    messages.error(request,
                                   'No puede cambiar la clave del administrador por no tener los permisos suficientes')
                    return HttpResponseRedirect('/inventario/perfil/ver/%s' % p)
            else:
                if request.user.is_superuser != True:
                    messages.error(request,
                                   'No puede cambiar la clave de este perfil por no tener los permisos suficientes')
                    return HttpResponseRedirect('/inventario/perfil/ver/%s' % p)

                else:
                    if perf.is_superuser == True:
                        if request.user.nivel == 2:
                            pass

                        elif perf.id != request.user.id:
                            messages.error(request, 'No puedes cambiar la clave de un usuario de tu mismo nivel')
                            return HttpResponseRedirect('/inventario/perfil/ver/%s' % p)

            form = ClaveFormulario(request.POST)
            contexto = {'form': form, 'modo': request.session.get('perfilProcesado'),
                        'editar': 'clave', 'nombreUsuario': perf.username}

            contexto = complementarContexto(contexto, request.user)
            return render(request, 'inventario/perfil/perfil.html', contexto)

        elif modo == 'ver':
            perf = Usuario.objects.get(id=p)
            contexto = {'perfil': perf}
            contexto = complementarContexto(contexto, request.user)

            return render(request, 'inventario/perfil/verPerfil.html', contexto)

    def post(self, request, modo, p):
        if modo == 'editar':
            # Crea una instancia del formulario y la llena con los datos:
            form = UsuarioFormulario(request.POST)
            # Revisa si es valido:

            if form.is_valid():
                perf = Usuario.objects.get(id=p)
                # Procesa y asigna los datos con form.cleaned_data como se requiere
                if p != 1:
                    level = form.cleaned_data['level']
                    perf.nivel = level
                    perf.is_superuser = level

                username = form.cleaned_data['username']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']

                perf.username = username
                perf.first_name = first_name
                perf.last_name = last_name
                perf.email = email

                perf.save()

                form = UsuarioFormulario()
                messages.success(request, 'Actualizado exitosamente el perfil de ID %s.' % p)
                request.session['perfilProcesado'] = True
                return HttpResponseRedirect("/inventario/perfil/ver/%s" % perf.id)
            else:
                #De lo contrario lanzara el mismo formulario
                return render(request, 'inventario/perfil/perfil.html', {'form': form})

        elif modo == 'clave':
            form = ClaveFormulario(request.POST)

            if form.is_valid():
                error = 0
                clave_nueva = form.cleaned_data['clave_nueva']
                repetir_clave = form.cleaned_data['repetir_clave']
                #clave = form.cleaned_data['clave']

                #Comentare estas lineas de abajo para deshacerme de la necesidad
                #   de obligar a que el usuario coloque la clave nuevamente
                #correcto = authenticate(username=request.user.username , password=clave)

                #if correcto is not None:
                #if clave_nueva != clave:
                #pass
                #else:
                #error = 1
                #messages.error(request,"La clave nueva no puede ser identica a la actual")

                usuario = Usuario.objects.get(id=p)

                if clave_nueva == repetir_clave:
                    pass
                else:
                    error = 1
                    messages.error(request, "La clave nueva y su repeticion tienen que coincidir")

                #else:
                #error = 1
                #messages.error(request,"La clave de acceso actual que ha insertado es incorrecta")

                if (error == 0):
                    messages.success(request, 'La clave se ha cambiado correctamente!')
                    usuario.set_password(clave_nueva)
                    usuario.save()
                    return HttpResponseRedirect("/inventario/login")

                else:
                    return HttpResponseRedirect("/inventario/perfil/clave/%s" % p)


#----------------------------------------------------------------------------------#   


#Elimina usuarios, productos, clientes o proveedores----------------------------
class Eliminar(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, modo, p):

        if modo == 'producto':
            prod = Producto.objects.get(id=p)
            prod.delete()
            messages.success(request, 'Producto de ID %s borrado exitosamente.' % p)
            return HttpResponseRedirect("/inventario/listarProductos")

        elif modo == 'cliente':
            cliente = Cliente.objects.get(id=p)
            cliente.delete()
            messages.success(request, 'Cliente de ID %s borrado exitosamente.' % p)
            return HttpResponseRedirect("/inventario/listarClientes")


        elif modo == 'proveedor':
            proveedor = Proveedor.objects.get(id=p)
            proveedor.delete()
            messages.success(request, 'Proveedor de ID %s borrado exitosamente.' % p)
            return HttpResponseRedirect("/inventario/listarProveedores")

        elif modo == 'usuario':
            if request.user.is_superuser == False:
                messages.error(request, 'No tienes permisos suficientes para borrar usuarios')
                return HttpResponseRedirect('/inventario/listarUsuarios')

            elif p == 1:
                messages.error(request, 'No puedes eliminar al super-administrador.')
                return HttpResponseRedirect('/inventario/listarUsuarios')

            elif request.user.id == p:
                messages.error(request, 'No puedes eliminar tu propio usuario.')
                return HttpResponseRedirect('/inventario/listarUsuarios')

            else:
                usuario = Usuario.objects.get(id=p)
                usuario.delete()
                messages.success(request, 'Usuario de ID %s borrado exitosamente.' % p)
                return HttpResponseRedirect("/inventario/listarUsuarios")

            #Fin de vista-------------------------------------------------------------------


#Muestra una lista de 10 productos por pagina----------------------------------------#
class ListarProductos(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        from django.db import models

        #Lista de productos de la BDD
        productos = Producto.objects.all()

        contexto = {'tabla': productos}

        contexto = complementarContexto(contexto, request.user)

        return render(request, 'inventario/producto/listarProductos.html', contexto)


#Fin de vista-------------------------------------------------------------------------#


#Maneja y visualiza un formulario--------------------------------------------------#
class AgregarProducto(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        form = ProductoFormulario(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            codigo_barras = form.cleaned_data['codigo_barras']
            descripcion = form.cleaned_data['descripcion']
            precio = form.cleaned_data['precio']
            precio2 = form.cleaned_data.get('precio2', None)
            categoria = form.cleaned_data['categoria']
            disponible = form.cleaned_data['disponible']
            iva = form.cleaned_data['iva']
            costo_actual = form.cleaned_data['costo_actual']

            iva_percent = Decimal(dict(Producto.tiposIVA).get(iva).replace('%', '')) / 100

            precio_iva1 = precio * (Decimal('1.00') + iva_percent)
            precio_iva2 = precio2 * (Decimal('1.00') + iva_percent) if precio2 else None

            prod = Producto(
                codigo=codigo,
                codigo_barras=codigo_barras,
                descripcion=descripcion,
                precio=precio,
                precio2=precio2,
                categoria=categoria,
                disponible=disponible,
                iva=iva,
                costo_actual=costo_actual,
                precio_iva1=precio_iva1,
                precio_iva2=precio_iva2
            )
            prod.save()

            form = ProductoFormulario()
            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % prod.id)
            request.session['productoProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarProducto")
        else:
            return render(request, 'inventario/producto/agregarProducto.html', {'form': form})

    def get(self, request):
        form = ProductoFormulario()
        contexto = {'form': form, 'modo': request.session.get('productoProcesado')}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/producto/agregarProducto.html', contexto)

        #FIN DEL CONTEXTO-----------------------------#


#Formulario simple que procesa un script para importar los productos-----------------#
class ImportarProductos(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        form = ImportarProductosFormulario(request.POST)
        if form.is_valid():
            request.session['productosImportados'] = True
            return HttpResponseRedirect("/inventario/importarProductos")

    def get(self, request):
        form = ImportarProductosFormulario()

        if request.session.get('productosImportados') == True:
            importado = request.session.get('productoImportados')
            contexto = {'form': form, 'productosImportados': importado}
            request.session['productosImportados'] = False

        else:
            contexto = {'form': form}
            contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/producto/importarProductos.html', contexto)

    #Fin de vista-------------------------------------------------------------------------#


#Formulario simple que crea un archivo y respalda los productos-----------------------#
class ExportarProductos(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        form = ExportarProductosFormulario(request.POST)
        if form.is_valid():
            request.session['productosExportados'] = True

            #Se obtienen las entradas de producto en formato JSON
            data = serializers.serialize("json", Producto.objects.all())
            fs = FileSystemStorage('inventario/tmp/')

            #Se utiliza la variable fs para acceder a la carpeta con mas facilidad
            with fs.open("productos.json", "w") as out:
                out.write(data)
                out.close()

            with fs.open("productos.json", "r") as out:
                response = HttpResponse(out.read(), content_type="application/force-download")
                response['Content-Disposition'] = 'attachment; filename="productos.json"'
                out.close()
                #------------------------------------------------------------
            return response

    def get(self, request):
        form = ExportarProductosFormulario()

        if request.session.get('productosExportados') == True:
            exportado = request.session.get('productoExportados')
            contexto = {'form': form, 'productosExportados': exportado}
            request.session['productosExportados'] = False

        else:
            contexto = {'form': form}
            contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/producto/exportarProductos.html', contexto)


#Fin de vista-------------------------------------------------------------------------#


#Muestra el formulario de un producto especifico para editarlo----------------------------------#
class EditarProducto(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request, p):
        # Crea una instancia del formulario y la llena con los datos:
        form = ProductoFormulario(request.POST)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            descripcion = form.cleaned_data['descripcion']
            precio = form.cleaned_data['precio']
            categoria = form.cleaned_data['categoria']
            tiene_iva = form.cleaned_data['tiene_iva']

            prod = Producto.objects.get(id=p)
            prod.descripcion = descripcion
            prod.precio = precio
            prod.categoria = categoria
            prod.tiene_iva = tiene_iva
            prod.save()
            form = ProductoFormulario(instance=prod)
            messages.success(request, 'Actualizado exitosamente el producto de ID %s.' % p)
            request.session['productoProcesado'] = 'editado'
            return HttpResponseRedirect("/inventario/editarProducto/%s" % prod.id)
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/producto/agregarProducto.html', {'form': form})

    def get(self, request, p):
        prod = Producto.objects.get(id=p)
        form = ProductoFormulario(instance=prod)
        #Envia al usuario el formulario para que lo llene
        contexto = {'form': form, 'modo': request.session.get('productoProcesado'), 'editar': True}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/producto/agregarProducto.html', contexto)


#Fin de vista------------------------------------------------------------------------------------#

# Búsqueda de Clientes
def buscar_cliente(request):
    query = request.GET.get('q', '')
    clientes = Cliente.objects.filter(cedula__icontains=query)[:5]
    resultados = [{'id': cliente.id, 'nombre': f"{cliente.cedula} - {cliente.nombre}"} for cliente in clientes]
    return JsonResponse(resultados, safe=False)

# Búsqueda de Productos
def buscar_producto(request):
    query = request.GET.get('q', '')
    productos = Producto.objects.filter(codigo__icontains=query)[:5]
    resultados = [{'id': producto.id, 'nombre': f"{producto.codigo} - {producto.descripcion}"} for producto in productos]
    return JsonResponse(resultados, safe=False)
#Crea una lista de los clientes, 10 por pagina----------------------------------------#
class ListarClientes(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        from django.db import models
        #Saca una lista de todos los clientes de la BDD
        clientes = Cliente.objects.all()
        contexto = {'tabla': clientes}
        contexto = complementarContexto(contexto, request.user)

        return render(request, 'inventario/cliente/listarClientes.html', contexto)
    #Fin de vista--------------------------------------------------------------------------#


#Crea y procesa un formulario para agregar a un cliente---------------------------------#
class AgregarCliente(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = ClienteFormulario(request.POST)
        # Revisa si es valido:

        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere

            cedula = form.cleaned_data['cedula']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            direccion = form.cleaned_data['direccion']
            telefono = form.cleaned_data['telefono']
            correo = form.cleaned_data['correo']
            observaciones = form.cleaned_data['observaciones']
            convencional = form.cleaned_data['convencional']
            tipoVenta = form.cleaned_data['tipoVenta']
            tipoRegimen = form.cleaned_data['tipoRegimen']
            tipoCliente = form.cleaned_data['tipoCliente']
            tipoCedula = form.cleaned_data['tipoCedula']

            cliente = Cliente(cedula=cedula, nombre=nombre, apellido=apellido,
                              direccion=direccion, telefono=telefono,
                              correo=correo, observaciones=observaciones, convencional=convencional,
                              tipoVenta=tipoVenta,
                              tipoRegimen=tipoRegimen, tipoCliente=tipoCliente, tipoCedula=tipoCedula)

            cliente.save()
            form = ClienteFormulario()
            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % cliente.id)
            request.session['clienteProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarCliente")
        else:

            #De lo contrario lanzara el mismo formulario
            messages.error(request, 'Error al agregar el cliente, ya existe o se encuentra en la base de datos')

            return render(request, 'inventario/cliente/agregarCliente.html', {'form': form})

    def get(self, request):
        form = ClienteFormulario()
        #Envia al usuario el formulario para que lo llene
        contexto = {'form': form, 'modo': request.session.get('clienteProcesado')}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/cliente/agregarCliente.html', contexto)


#Fin de vista-----------------------------------------------------------------------------#


#Formulario simple que procesa un script para importar los clientes-----------------#
class ImportarClientes(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        form = ImportarClientesFormulario(request.POST)
        if form.is_valid():
            request.session['clientesImportados'] = True
            return HttpResponseRedirect("/inventario/importarClientes")

    def get(self, request):
        form = ImportarClientesFormulario()

        if request.session.get('clientesImportados') == True:
            importado = request.session.get('clientesImportados')
            contexto = {'form': form, 'clientesImportados': importado}
            request.session['clientesImportados'] = False

        else:
            contexto = {'form': form}
            contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/cliente/importarClientes.html', contexto)


#Fin de vista-------------------------------------------------------------------------#


#Formulario simple que crea un archivo y respalda los clientes-----------------------#
class ExportarClientes(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        form = ExportarClientesFormulario(request.POST)
        if form.is_valid():
            request.session['clientesExportados'] = True

            #Se obtienen las entradas de producto en formato JSON
            data = serializers.serialize("json", Cliente.objects.all())
            fs = FileSystemStorage('inventario/tmp/')

            #Se utiliza la variable fs para acceder a la carpeta con mas facilidad
            with fs.open("clientes.json", "w") as out:
                out.write(data)
                out.close()

            with fs.open("clientes.json", "r") as out:
                response = HttpResponse(out.read(), content_type="application/force-download")
                response['Content-Disposition'] = 'attachment; filename="clientes.json"'
                out.close()
                #------------------------------------------------------------
            return response

    def get(self, request):
        form = ExportarClientesFormulario()

        if request.session.get('clientesExportados') == True:
            exportado = request.session.get('clientesExportados')
            contexto = {'form': form, 'clientesExportados': exportado}
            request.session['clientesExportados'] = False

        else:
            contexto = {'form': form}
            contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/cliente/exportarClientes.html', contexto)


#Fin de vista-------------------------------------------------------------------------#


#Muestra el mismo formulario del cliente pero con los datos a editar----------------------#
class EditarCliente(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request, p):
        # Crea una instancia del formulario y la llena con los datos:
        cliente = Cliente.objects.get(id=p)
        form = ClienteFormulario(request.POST, instance=cliente)
        # Revisa si es valido:

        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            cedula = form.cleaned_data['cedula']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            direccion = form.cleaned_data['direccion']
            nacimiento = form.cleaned_data['nacimiento']
            telefono = form.cleaned_data['telefono']
            correo = form.cleaned_data['correo']
            telefono2 = form.cleaned_data['telefono2']
            correo2 = form.cleaned_data['correo2']

            cliente.cedula = cedula
            cliente.nombre = nombre
            cliente.apellido = apellido
            cliente.direccion = direccion
            cliente.nacimiento = nacimiento
            cliente.telefono = telefono
            cliente.correo = correo
            cliente.telefono2 = telefono2
            cliente.correo2 = correo2
            cliente.save()
            form = ClienteFormulario(instance=cliente)

            messages.success(request, 'Actualizado exitosamente el cliente de ID %s.' % p)
            request.session['clienteProcesado'] = 'editado'
            return HttpResponseRedirect("/inventario/editarCliente/%s" % cliente.id)
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/cliente/agregarCliente.html', {'form': form})

    def get(self, request, p):
        cliente = Cliente.objects.get(id=p)
        form = ClienteFormulario(instance=cliente)
        #Envia al usuario el formulario para que lo llene
        contexto = {'form': form, 'modo': request.session.get('clienteProcesado'), 'editar': True}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/cliente/agregarCliente.html', contexto)
    #Fin de vista--------------------------------------------------------------------------------#


#Emite la primera parte de la factura------------------------------#
class EmitirFactura(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos enviados
        cedulas = Cliente.cedulasRegistradas()
        productos = Producto.objects.all()  # Obtenemos la lista de productos disponibles
        form = EmitirFacturaFormulario(request.POST, cedulas=cedulas, productos=productos)

        # Verifica si el formulario es válido
        if form.is_valid():
            # Recupera los datos del formulario
            id_cliente = form.cleaned_data['cliente']
            id_producto = form.cleaned_data['producto']
            numero_productos = form.cleaned_data['productos']
            codigo_producto = form.cleaned_data['codigo_producto']

            # Obtiene el producto y calcula el precio con o sin IVA
            producto = obtenerProducto(id_producto)
            precio_unitario = producto.precio

            # Guarda los datos relevantes en la sesión para usarlos más adelante
            request.session['form_details'] = {
                'id_cliente': id_cliente,
                'id_producto': id_producto,
                'cantidad': numero_productos,
                'codigo_producto': codigo_producto,
            }

            # Redirige a la página de detalles de la factura
            return HttpResponseRedirect("detallesDeFactura")
        else:
            # Si el formulario no es válido, lo muestra de nuevo con errores
            return render(request, 'inventario/factura/emitirFactura.html', {'form': form})

    def get(self, request):
        # Obtiene las opciones de clientes y productos
        cedulas = Cliente.cedulasRegistradas()
        productos = Producto.objects.all()

        # Inicializa el formulario con las opciones
        form = EmitirFacturaFormulario(cedulas=cedulas, productos=productos)

        # Prepara el contexto con los datos del usuario
        contexto = {'form': form}
        contexto = complementarContexto(contexto, request.user)

        # Renderiza el formulario
        return render(request, 'inventario/factura/emitirFactura.html', contexto)


#Fin de vista---------------------------------------------------------------------------------#


#Muestra y procesa los detalles de cada producto de la factura--------------------------------#
class DetallesFactura(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        # Recupera los datos de la sesión correctamente
        form_details = request.session.get('form_details', {})

        # Verifica si 'form_details' contiene los datos esperados
        if not isinstance(form_details, dict) or 'cantidad' not in form_details:
            messages.error(request, 'Los datos de la factura son inválidos o están incompletos.')
            return redirect('inventario:emitirFactura')

        # Crea un formset basado en la cantidad de productos
        cantidad = form_details.get('cantidad', 1)  # Asegura que sea un número válido
        FacturaFormulario = formset_factory(DetallesFacturaFormulario, extra=cantidad)
        formset = FacturaFormulario(initial=[form_details])

        # Prepara el contexto y lo complementa
        contexto = {'formset': formset}
        contexto = complementarContexto(contexto, request.user)

        # Renderiza la plantilla de detalles de la factura
        return render(request, 'inventario/factura/detallesFactura.html', contexto)

    def post(self, request):
        # Recupera los datos de la sesión
        form_details = request.session.get('form_details', {})

        # Crea un formset con los datos enviados por el usuario
        cantidad = form_details.get('cantidad', 1)
        FacturaFormulario = formset_factory(DetallesFacturaFormulario, extra=cantidad)
        formset = FacturaFormulario(request.POST)

        if formset.is_valid():
            sub_monto = 0
            detalles = []

            # Procesa cada formulario en el formset
            for form in formset:
                producto = form.cleaned_data['descripcion']
                cantidad = form.cleaned_data['cantidad']
                subtotal = form.cleaned_data['valor_subtotal']

                sub_monto += subtotal  # Suma correctamente los subtotales
                detalles.append((producto, cantidad, subtotal))

            # Crea la factura
            cliente = get_object_or_404(Cliente, cedula=request.session.get('id_client'))
            factura = Factura(cliente=cliente, fecha=date.today(), sub_monto=sub_monto, monto_general=sub_monto)
            factura.save()

            # Guarda los detalles de la factura
            for producto, cantidad, subtotal in detalles:
                objeto_producto = obtenerProducto(producto.id)
                detalle = DetalleFactura(
                    id_factura=factura,
                    id_producto=objeto_producto,
                    cantidad=cantidad,
                    sub_total=subtotal,
                    total=subtotal
                )
                objeto_producto.disponible -= cantidad
                objeto_producto.save()
                detalle.save()

            # Muestra un mensaje de éxito y redirige
            messages.success(request, f'Factura de ID {factura.id} insertada exitosamente.')
            return HttpResponseRedirect("/inventario/emitirFactura")

        # Si hay errores, vuelve a mostrar el formulario con errores
        contexto = {'formset': formset}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/factura/detallesFactura.html', contexto)
        #Fin de vista-----------------------------------------------------------------------------------#


#Muestra y procesa los detalles de cada producto de la factura--------------------------------#
class ListarFacturas(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        #Lista de productos de la BDD
        facturas = Factura.objects.all()
        #Crea el paginador

        contexto = {'tabla': facturas}
        contexto = complementarContexto(contexto, request.user)

        return render(request, 'inventario/factura/listarFacturas.html', contexto)

    #Fin de vista---------------------------------------------------------------------------------------#


#Muestra los detalles individuales de una factura------------------------------------------------#
class VerFactura(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        factura = Factura.objects.get(id=p)
        detalles = DetalleFactura.objects.filter(id_factura_id=p)
        contexto = {'factura': factura, 'detalles': detalles}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/factura/verFactura.html', contexto)


#Fin de vista--------------------------------------------------------------------------------------#


#Genera la factura en CSV--------------------------------------------------------------------------#
class GenerarFactura(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        import csv

        factura = Factura.objects.get(id=p)
        detalles = DetalleFactura.objects.filter(id_factura_id=p)

        nombre_factura = "factura_%s.csv" % (factura.id)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_factura
        writer = csv.writer(response)

        writer.writerow(['Producto', 'Cantidad', 'Sub-total', 'Total',
                         'Porcentaje IVA utilizado: %s' % (factura.iva.valor_iva)])

        for producto in detalles:
            writer.writerow([producto.id_producto.descripcion, producto.cantidad, producto.sub_total, producto.total])

        writer.writerow(['Total general:', '', '', factura.monto_general])

        return response

        #Fin de vista--------------------------------------------------------------------------------------#


#Genera la factura en PDF--------------------------------------------------------------------------#
class GenerarFacturaPDF(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        import io
        from reportlab.pdfgen import canvas
        import datetime

        factura = Factura.objects.get(id=p)
        general = Opciones.objects.get(id=1)
        detalles = DetalleFactura.objects.filter(id_factura_id=p)

        data = {
            'fecha': factura.fecha,
            'monto_general': factura.monto_general,
            'nombre_cliente': factura.cliente.nombre + " " + factura.cliente.apellido,
            'cedula_cliente': factura.cliente.cedula,
            'id_reporte': factura.id,
            'iva': factura.iva.valor_iva,
            'detalles': detalles,
            'modo': 'factura',
            'general': general
        }

        nombre_factura = "factura_%s.pdf" % (factura.id)

        pdf = render_to_pdf('inventario/PDF/prueba.html', data)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_factura

        return response

        #Fin de vista--------------------------------------------------------------------------------------#


#Crea una lista de los clientes, 10 por pagina----------------------------------------#
class ListarProveedores(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        from django.db import models
        #Saca una lista de todos los clientes de la BDD
        proveedores = Proveedor.objects.all()
        contexto = {'tabla': proveedores}
        contexto = complementarContexto(contexto, request.user)

        return render(request, 'inventario/proveedor/listarProveedores.html', contexto)
    #Fin de vista--------------------------------------------------------------------------#


#Crea y procesa un formulario para agregar a un proveedor---------------------------------#
class AgregarProveedor(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = ProveedorFormulario(request.POST)
        # Revisa si es valido:

        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere

            cedula = form.cleaned_data['cedula']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            direccion = form.cleaned_data['direccion']
            nacimiento = form.cleaned_data['nacimiento']
            telefono = form.cleaned_data['telefono']
            correo = form.cleaned_data['correo']
            telefono2 = form.cleaned_data['telefono2']
            correo2 = form.cleaned_data['correo2']

            proveedor = Proveedor(cedula=cedula, nombre=nombre, apellido=apellido,
                                  direccion=direccion, nacimiento=nacimiento, telefono=telefono,
                                  correo=correo, telefono2=telefono2, correo2=correo2)
            proveedor.save()
            form = ProveedorFormulario()

            messages.success(request, 'Ingresado exitosamente bajo la ID %s.' % proveedor.id)
            request.session['proveedorProcesado'] = 'agregado'
            return HttpResponseRedirect("/inventario/agregarProveedor")
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/proveedor/agregarProveedor.html', {'form': form})

    def get(self, request):
        form = ProveedorFormulario()
        #Envia al usuario el formulario para que lo llene
        contexto = {'form': form, 'modo': request.session.get('proveedorProcesado')}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/proveedor/agregarProveedor.html', contexto)


#Fin de vista-----------------------------------------------------------------------------#

#Formulario simple que procesa un script para importar los proveedores-----------------#
class ImportarProveedores(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        form = ImportarClientesFormulario(request.POST)
        if form.is_valid():
            request.session['clientesImportados'] = True
            return HttpResponseRedirect("/inventario/importarClientes")

    def get(self, request):
        form = ImportarClientesFormulario()

        if request.session.get('clientesImportados') == True:
            importado = request.session.get('clientesImportados')
            contexto = {'form': form, 'clientesImportados': importado}
            request.session['clientesImportados'] = False

        else:
            contexto = {'form': form}
            contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/importarClientes.html', contexto)


#Fin de vista-------------------------------------------------------------------------#


#Formulario simple que crea un archivo y respalda los proveedores-----------------------#
class ExportarProveedores(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request):
        form = ExportarClientesFormulario(request.POST)
        if form.is_valid():
            request.session['clientesExportados'] = True

            #Se obtienen las entradas de producto en formato JSON
            data = serializers.serialize("json", Cliente.objects.all())
            fs = FileSystemStorage('inventario/tmp/')

            #Se utiliza la variable fs para acceder a la carpeta con mas facilidad
            with fs.open("clientes.json", "w") as out:
                out.write(data)
                out.close()

            with fs.open("clientes.json", "r") as out:
                response = HttpResponse(out.read(), content_type="application/force-download")
                response['Content-Disposition'] = 'attachment; filename="clientes.json"'
                out.close()
                #------------------------------------------------------------
            return response

    def get(self, request):
        form = ExportarClientesFormulario()

        if request.session.get('clientesExportados') == True:
            exportado = request.session.get('clientesExportados')
            contexto = {'form': form, 'clientesExportados': exportado}
            request.session['clientesExportados'] = False

        else:
            contexto = {'form': form}
            contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/exportarClientes.html', contexto)


#Fin de vista-------------------------------------------------------------------------#


#Muestra el mismo formulario del cliente pero con los datos a editar----------------------#
class EditarProveedor(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def post(self, request, p):
        # Crea una instancia del formulario y la llena con los datos:
        proveedor = Proveedor.objects.get(id=p)
        form = ProveedorFormulario(request.POST, instance=proveedor)
        # Revisa si es valido:

        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            cedula = form.cleaned_data['cedula']
            nombre = form.cleaned_data['nombre']
            apellido = form.cleaned_data['apellido']
            direccion = form.cleaned_data['direccion']
            nacimiento = form.cleaned_data['nacimiento']
            telefono = form.cleaned_data['telefono']
            correo = form.cleaned_data['correo']
            telefono2 = form.cleaned_data['telefono2']
            correo2 = form.cleaned_data['correo2']

            proveedor.cedula = cedula
            proveedor.nombre = nombre
            proveedor.apellido = apellido
            proveedor.direccion = direccion
            proveedor.nacimiento = nacimiento
            proveedor.telefono = telefono
            proveedor.correo = correo
            proveedor.telefono2 = telefono2
            proveedor.correo2 = correo2
            proveedor.save()
            form = ProveedorFormulario(instance=proveedor)

            messages.success(request, 'Actualizado exitosamente el proveedor de ID %s.' % p)
            request.session['proveedorProcesado'] = 'editado'
            return HttpResponseRedirect("/inventario/editarProveedor/%s" % proveedor.id)
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/proveedor/agregarProveedor.html', {'form': form})

    def get(self, request, p):
        proveedor = Proveedor.objects.get(id=p)
        form = ProveedorFormulario(instance=proveedor)
        #Envia al usuario el formulario para que lo llene
        contexto = {'form': form, 'modo': request.session.get('proveedorProcesado'), 'editar': True}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/proveedor/agregarProveedor.html', contexto)
    #Fin de vista--------------------------------------------------------------------------------#


#Agrega un pedido-----------------------------------------------------------------------------------#      
class AgregarPedido(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        cedulas = Proveedor.cedulasRegistradas()
        form = EmitirPedidoFormulario(cedulas=cedulas)
        contexto = {'form': form}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/pedido/emitirPedido.html', contexto)

    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        cedulas = Proveedor.cedulasRegistradas()
        form = EmitirPedidoFormulario(request.POST, cedulas=cedulas)
        # Revisa si es valido:
        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            request.session['form_details'] = form.cleaned_data['productos']
            request.session['id_proveedor'] = form.cleaned_data['proveedor']
            return HttpResponseRedirect("detallesPedido")
        else:
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/pedido/emitirPedido.html', {'form': form})


#--------------------------------------------------------------------------------------------------#


#Lista todos los pedidos---------------------------------------------------------------------------#
class ListarPedidos(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        from django.db import models
        #Saca una lista de todos los clientes de la BDD
        pedidos = Pedido.objects.all()
        contexto = {'tabla': pedidos}
        contexto = complementarContexto(contexto, request.user)

        return render(request, 'inventario/pedido/listarPedidos.html', contexto)

    #------------------------------------------------------------------------------------------------#


#Muestra y procesa los detalles de cada producto de la factura--------------------------------#
class DetallesPedido(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        cedula = request.session.get('id_proveedor')
        productos = request.session.get('form_details')
        PedidoFormulario = formset_factory(DetallesPedidoFormulario, extra=productos)
        formset = PedidoFormulario()
        contexto = {'formset': formset}
        contexto = complementarContexto(contexto, request.user)

        return render(request, 'inventario/pedido/detallesPedido.html', contexto)

    def post(self, request):
        cedula = request.session.get('id_proveedor')
        productos = request.session.get('form_details')

        PedidoFormulario = formset_factory(DetallesPedidoFormulario, extra=productos)

        inicial = {
            'descripcion': '',
            'cantidad': 0,
            'subtotal': 0,
        }

        data = {
            'form-TOTAL_FORMS': productos,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': '',
        }

        formset = PedidoFormulario(request.POST, data)

        if formset.is_valid():

            id_producto = []
            cantidad = []
            subtotal = []
            total_general = []
            sub_monto = 0
            monto_general = 0

            for form in formset:
                desc = form.cleaned_data['descripcion'].descripcion
                cant = form.cleaned_data['cantidad']
                sub = form.cleaned_data['valor_subtotal']

                id_producto.append(
                    obtenerIdProducto(desc))  #esta funcion, a estas alturas, es innecesaria porque ya tienes la id
                cantidad.append(cant)
                subtotal.append(sub)

                #Ingresa la factura
            #--Saca el sub-monto
            for index in subtotal:
                sub_monto += index

            #--Saca el monto general
            for index, element in enumerate(subtotal):
                if productoTieneIva(id_producto[index]):
                    nuevoPrecio = sacarIva(element)
                    monto_general += nuevoPrecio
                    total_general.append(nuevoPrecio)
                else:
                    monto_general += element
                    total_general.append(element)

            from datetime import date

            proveedor = Proveedor.objects.get(cedula=cedula)
            iva = ivaActual('objeto')
            presente = False
            pedido = Pedido(proveedor=proveedor, fecha=date.today(), sub_monto=sub_monto, monto_general=monto_general,
                            iva=iva,
                            presente=presente)

            pedido.save()
            id_pedido = pedido

            for indice, elemento in enumerate(id_producto):
                objetoProducto = obtenerProducto(elemento)
                cantidadDetalle = cantidad[indice]
                subDetalle = subtotal[indice]
                totalDetalle = total_general[indice]

                detallePedido = DetallePedido(id_pedido=id_pedido, id_producto=objetoProducto, cantidad=cantidadDetalle
                                              , sub_total=subDetalle, total=totalDetalle)
                detallePedido.save()

            messages.success(request, 'Pedido de ID %s insertado exitosamente.' % id_pedido.id)
            return HttpResponseRedirect("/inventario/agregarPedido")

        #Fin de vista-----------------------------------------------------------------------------------#


#Muestra los detalles individuales de un pedido------------------------------------------------#
class VerPedido(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        pedido = Pedido.objects.get(id=p)
        detalles = DetallePedido.objects.filter(id_pedido_id=p)
        recibido = Pedido.recibido(p)
        contexto = {'pedido': pedido, 'detalles': detalles, 'recibido': recibido}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/pedido/verPedido.html', contexto)


#Fin de vista--------------------------------------------------------------------------------------#

#Valida un pedido ya insertado------------------------------------------------#
class ValidarPedido(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        pedido = Pedido.objects.get(id=p)
        detalles = DetallePedido.objects.filter(id_pedido_id=p)

        #Agrega los productos del pedido
        for elemento in detalles:
            elemento.id_producto.disponible += elemento.cantidad
            elemento.id_producto.save()

        pedido.presente = True
        pedido.save()
        messages.success(request, 'Pedido de ID %s verificado exitosamente.' % pedido.id)
        return HttpResponseRedirect("/inventario/verPedido/%s" % p)
    #Fin de vista--------------------------------------------------------------------------------------#


#Genera el pedido en CSV--------------------------------------------------------------------------#
class GenerarPedido(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        import csv

        pedido = Pedido.objects.get(id=p)
        detalles = DetallePedido.objects.filter(id_pedido_id=p)

        nombre_pedido = "pedido_%s.csv" % (pedido.id)

        response = HttpResponse(content_type='text/csv')

        response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_pedido
        writer = csv.writer(response)

        writer.writerow(['Producto', 'Cantidad', 'Sub-total', 'Total',
                         'Porcentaje IVA utilizado: %s' % (pedido.iva.valor_iva)])

        for producto in detalles:
            writer.writerow([producto.id_producto.descripcion, producto.cantidad, producto.sub_total, producto.total])

        writer.writerow(['Total general:', '', '', pedido.monto_general])

        return response

        #Fin de vista--------------------------------------------------------------------------------------#


#Genera el pedido en PDF--------------------------------------------------------------------------#
class GenerarPedidoPDF(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, p):
        pedido = Pedido.objects.get(id=p)
        general = Opciones.objects.get(id=1)
        detalles = DetallePedido.objects.filter(id_pedido_id=p)

        data = {
            'fecha': pedido.fecha,
            'monto_general': pedido.monto_general,
            'nombre_proveedor': pedido.proveedor.nombre + " " + pedido.proveedor.apellido,
            'cedula_proveedor': pedido.proveedor.cedula,
            'id_reporte': pedido.id,
            'iva': pedido.iva.valor_iva,
            'detalles': detalles,
            'modo': 'pedido',
            'general': general
        }

        nombre_pedido = "pedido_%s.pdf" % (pedido.id)

        pdf = render_to_pdf('inventario/PDF/prueba.html', data)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % nombre_pedido

        return response
        #Fin de vista--------------------------------------------------------------------------------------#


#Crea un nuevo usuario--------------------------------------------------------------#
class CrearUsuario(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        if request.user.is_superuser:
            form = NuevoUsuarioFormulario()
            #Envia al usuario el formulario para que lo llene
            contexto = {'form': form, 'modo': request.session.get('usuarioCreado')}
            contexto = complementarContexto(contexto, request.user)
            return render(request, 'inventario/usuario/crearUsuario.html', contexto)
        else:
            messages.error(request, 'No tiene los permisos para crear un usuario nuevo')
            return HttpResponseRedirect('/inventario/panel')

    def post(self, request):
        form = NuevoUsuarioFormulario(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            rep_password = form.cleaned_data['rep_password']
            level = form.cleaned_data['level']

            error = 0

            if password == rep_password:
                pass

            else:
                error = 1
                messages.error(request, 'La clave y su repeticion tienen que coincidir')

            if usuarioExiste(Usuario, 'username', username) is False:
                pass

            else:
                error = 1
                messages.error(request, "El nombre de usuario '%s' ya existe. eliga otro!" % username)

            if usuarioExiste(Usuario, 'email', email) is False:
                pass

            else:
                error = 1
                messages.error(request, "El correo '%s' ya existe. eliga otro!" % email)

            if (error == 0):
                if level == '0':
                    nuevoUsuario = Usuario.objects.create_user(username=username, password=password, email=email)
                    nivel = 0
                elif level == '1':
                    nuevoUsuario = Usuario.objects.create_superuser(username=username, password=password, email=email)
                    nivel = 1

                nuevoUsuario.first_name = first_name
                nuevoUsuario.last_name = last_name
                nuevoUsuario.nivel = nivel
                nuevoUsuario.save()

                messages.success(request, 'Usuario creado exitosamente')
                return HttpResponseRedirect('/inventario/crearUsuario')

            else:
                return HttpResponseRedirect('/inventario/crearUsuario')


#Fin de vista----------------------------------------------------------------------


#Lista todos los usuarios actuales--------------------------------------------------------------#
class ListarUsuarios(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        usuarios = Usuario.objects.all()
        #Envia al usuario el formulario para que lo llene
        contexto = {'tabla': usuarios}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/usuario/listarUsuarios.html', contexto)

    def post(self, request):
        pass

    #Fin de vista----------------------------------------------------------------------


#Importa toda la base de datos, primero crea una copia de la actual mientras se procesa la nueva--#
class ImportarBDD(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        if request.user.is_superuser == False:
            messages.error(request, 'Solo los administradores pueden importar una nueva base de datos')
            return HttpResponseRedirect('/inventario/panel')

        form = ImportarBDDFormulario()
        contexto = {'form': form}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/BDD/importar.html', contexto)

    def post(self, request):
        form = ImportarBDDFormulario(request.POST, request.FILES)

        if form.is_valid():
            ruta = 'inventario/archivos/BDD/inventario_respaldo.xml'
            manejarArchivo(request.FILES['archivo'], ruta)

            try:
                call_command('loaddata', ruta, verbosity=0)
                messages.success(request, 'Base de datos subida exitosamente')
                return HttpResponseRedirect('/inventario/importarBDD')
            except Exception:
                messages.error(request, 'El archivo esta corrupto')
                return HttpResponseRedirect('/inventario/importarBDD')


#Fin de vista--------------------------------------------------------------------------------


#Descarga toda la base de datos en un archivo---------------------------------------------#
class DescargarBDD(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        #Se obtiene la carpeta donde se va a guardar y despues se crea el respaldo ahi
        fs = FileSystemStorage('inventario/archivos/tmp/')
        with fs.open('inventario_respaldo.xml', 'w') as output:
            call_command('dumpdata', 'inventario', indent=4, stdout=output, format='xml',
                         exclude=['contenttypes', 'auth.permission'])

            output.close()

        #Lo de abajo es para descargarlo
        with fs.open('inventario_respaldo.xml', 'r') as output:
            response = HttpResponse(output.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'attachment; filename="inventario_respaldo.xml"'

            #Cierra el archivo
            output.close()

            #Borra el archivo
            ruta = 'inventario/archivos/tmp/inventario_respaldo.xml'
            call_command('erasefile', ruta)

            #Regresa el archivo a descargar
            return response


#Fin de vista--------------------------------------------------------------------------------


#Configuracion general de varios elementos--------------------------------------------------#
class ConfiguracionGeneral(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        conf = Opciones.objects.get(id=1)
        form = OpcionesFormulario()

        #Envia al usuario el formulario para que lo llene
        form['identificacion'].field.widget.attrs['value'] = conf.identificacion
        form['razon_social'].field.widget.attrs['value'] = conf.razon_social
        form['nombre_comercial'].field.widget.attrs['value'] = conf.nombre_comercial
        form['direccion'].field.widget.attrs['value'] = conf.direccion
        form['correo'].field.widget.attrs['value'] = conf.correo
        form['telefono'].field.widget.attrs['value'] = conf.telefono
        form.fields['obligado'].initial = conf.obligado
        form.fields['tipo_regimen'].initial = conf.tipo_regimen
        form['moneda'].field.widget.attrs['value'] = conf.moneda
        form['valor_iva'].field.widget.attrs['value'] = conf.valor_iva
        form['mensaje_factura'].field.widget.attrs['value'] = conf.mensaje_factura
        form['nombre_negocio'].field.widget.attrs['value'] = conf.nombre_negocio

        contexto = {'form': form}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/opciones/configuracion.html', contexto)

    def post(self, request):
        # Crea una instancia del formulario y la llena con los datos:
        form = OpcionesFormulario(request.POST, request.FILES)
        # Revisa si es valido:

        if form.is_valid():
            # Procesa y asigna los datos con form.cleaned_data como se requiere
            identificacion = form.cleaned_data['identificacion']
            razon_social = form.cleaned_data['razon_social']
            nombre_comercial = form.cleaned_data['nombre_comercial']
            direccion = form.cleaned_data['direccion']
            correo = form.cleaned_data['correo']
            telefono = form.cleaned_data['telefono']
            obligado = form.cleaned_data['obligado']
            tipo_regimen = form.cleaned_data['tipo_regimen']
            moneda = form.cleaned_data['moneda']
            valor_iva = form.cleaned_data['valor_iva']
            mensaje_factura = form.cleaned_data['mensaje_factura']
            nombre_negocio = form.cleaned_data['nombre_negocio']
            imagen = request.FILES.get('imagen', False)

            #Si se subio un logo se sobreescribira en la carpeta ubicada
            #--en la siguiente ruta
            if imagen:
                manejarArchivo(imagen, 'inventario/static/inventario/assets/logo/logo2.png')

            conf = Opciones.objects.get(id=1)
            conf.identificacion = identificacion
            conf.razon_social = razon_social
            conf.nombre_comercial = nombre_comercial
            conf.direccion = direccion
            conf.correo = correo
            conf.telefono = telefono
            conf.obligado = obligado
            conf.tipo_regimen = tipo_regimen
            conf.moneda = moneda
            conf.valor_iva = valor_iva
            conf.mensaje_factura = mensaje_factura
            conf.nombre_negocio = nombre_negocio
            conf.save()

            messages.success(request, 'Configuracion actualizada exitosamente!')
            return HttpResponseRedirect("/inventario/configuracionGeneral")
        else:
            form = OpcionesFormulario(instance=conf)
            #De lo contrario lanzara el mismo formulario
            return render(request, 'inventario/opciones/configuracion.html', {'form': form})


#Fin de vista--------------------------------------------------------------------------------


#Accede a los modulos del manual de usuario---------------------------------------------#
class VerManualDeUsuario(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, pagina):
        if pagina == 'inicio':
            return render(request, 'inventario/manual/index.html')

        if pagina == 'producto':
            return render(request, 'inventario/manual/producto.html')

        if pagina == 'proveedor':
            return render(request, 'inventario/manual/proveedor.html')

        if pagina == 'pedido':
            return render(request, 'inventario/manual/pedido.html')

        if pagina == 'clientes':
            return render(request, 'inventario/manual/clientes.html')

        if pagina == 'factura':
            return render(request, 'inventario/manual/factura.html')

        if pagina == 'usuarios':
            return render(request, 'inventario/manual/usuarios.html')

        if pagina == 'opciones':
            return render(request, 'inventario/manual/opciones.html')


#Fin de vista--------------------------------------------------------------------------------

class Secuencias(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        secuencias = Secuencia.objects.all()
        form = SecuenciaFormulario()  # Formulario vacío para crear una nueva secuencia
        contexto = {'form': form, 'secuencias': secuencias}
        contexto = complementarContexto(contexto, request.user)  # Añade información adicional al contexto
        return render(request, 'inventario/opciones/secuencias.html', contexto)

    def post(self, request):
        secuencia_id = request.POST.get('id', None)  # Recuperar el ID del formulario (puede ser None)
        form = SecuenciaFormulario(request.POST)

        if form.is_valid():
            try:
                # Si se proporciona un ID, intenta buscar la secuencia para actualizar
                if secuencia_id and Secuencia.objects.filter(id=secuencia_id).exists():
                    secuencia = Secuencia.objects.get(id=secuencia_id)
                    for field, value in form.cleaned_data.items():
                        setattr(secuencia, field, value)
                    secuencia.save()
                    messages.success(request, f'Secuencia actualizada exitosamente con ID {secuencia.id}!')
                else:
                    # Si no hay ID, o el ID no existe, crear una nueva secuencia
                    nueva_secuencia = form.save()
                    messages.success(request, f'Nueva secuencia creada exitosamente con ID {nueva_secuencia.id}!')

                return redirect('inventario:secuencias')

            except Exception as e:
                messages.error(request, f'Error al actualizar o crear la secuencia: {e}')

        else:
            messages.error(request, 'Error en los datos del formulario.')

        # Recargar las secuencias si hay errores
        secuencias = Secuencia.objects.all()
        contexto = {'form': form, 'secuencias': secuencias}
        contexto = complementarContexto(contexto, request.user)
        return render(request, 'inventario/opciones/secuencias.html', contexto)


class ListaSecuencias(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request):
        # Recuperar todas las secuencias de la base de datos
        secuencias = Secuencia.objects.all()
        contexto = {'secuencias': secuencias}
        contexto = complementarContexto(contexto, request.user)  # Añade información al contexto si es necesario
        return render(request, 'inventario/opciones/lista_secuencias.html', contexto)


class EliminarSecuencia(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, id):
        secuencia = get_object_or_404(Secuencia, id=id)
        secuencia.delete()
        messages.success(request, f'Secuencia con ID {id} eliminada exitosamente.')
        return redirect('inventario:lista_secuencias')


class EditarSecuencia(LoginRequiredMixin, View):
    login_url = '/inventario/login'
    redirect_field_name = None

    def get(self, request, *args, **kwargs):
        # Extraemos el 'id' desde los argumentos de la URL
        secuencia_id = kwargs.get('id')
        # Obtenemos la secuencia o lanzamos 404 si no existe
        secuencia = get_object_or_404(Secuencia, id=secuencia_id)
        # Inicializamos el formulario con la instancia de la secuencia
        form = SecuenciaFormulario(instance=secuencia)
        # Renderizamos la plantilla con el formulario
        return render(request, 'inventario/opciones/editar_secuencia.html', {'form': form, 'secuencia': secuencia})

    def post(self, request, *args, **kwargs):
        # Extraemos el 'id' desde los argumentos de la URL
        secuencia_id = kwargs.get('id')
        # Obtenemos la secuencia o lanzamos 404 si no existe
        secuencia = get_object_or_404(Secuencia, id=secuencia_id)
        # Vinculamos los datos enviados con la instancia existente
        form = SecuenciaFormulario(request.POST, instance=secuencia)

        if form.is_valid():
            # Guardamos los cambios si el formulario es válido
            form.save()
            messages.success(request, 'Secuencia actualizada correctamente.')
            return redirect('inventario:lista_secuencias')  # Redirige a la lista de secuencias
        else:
            # Mostramos un mensaje de error si el formulario no es válido
            messages.error(request, 'Error al actualizar la secuencia.')
            return render(request, 'inventario/opciones/editar_secuencia.html', {'form': form, 'secuencia': secuencia})

class CrearFacturador(View):
    def get(self, request):
        form = FacturadorForm()
        # Cambiamos la ruta a la plantilla correcta
        return render(request, 'inventario/opciones/facturador_form.html', {'form': form})

    def post(self, request):
        form = FacturadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facturador creado exitosamente.')
            return redirect('inventario:listar_facturadores')
        else:
            messages.error(request, 'Por favor, corrija los errores.')
            return render(request, 'inventario/opciones/facturador_form.html', {'form': form})

# Listar Facturadores
class ListarFacturadores(View):
    def get(self, request):
        facturadores = Facturador.objects.all()
        # Asegúrate de que la plantilla esté en la ruta correcta
        return render(request, 'inventario/opciones/facturador_list.html', {'facturadores': facturadores})

# Editar Facturador
class EditarFacturador(View):
    def get(self, request, id):
        # Recupera el facturador o lanza 404 si no existe
        facturador = get_object_or_404(Facturador, id=id)
        # Crea el formulario con los datos existentes
        form = FacturadorForm(instance=facturador)
        return render(request, 'inventario/opciones/editar_facturador.html', {
            'form': form,
            'facturador': facturador
        })

    def post(self, request, id):
        # Recupera el facturador o lanza 404 si no existe
        facturador = get_object_or_404(Facturador, id=id)

        # Copia los datos del formulario para evitar problemas con el checkbox
        data = request.POST.copy()
        # Si el checkbox no se envía, se considera como False
        data['activo'] = data.get('activo') == 'True'

        # Crea el formulario con los datos enviados y el facturador a editar
        form = FacturadorForm(data, instance=facturador)

        if form.is_valid():
            # Guarda los cambios si el formulario es válido
            form.save()
            messages.success(request, 'Facturador actualizado exitosamente.')
            return redirect('inventario:listar_facturadores')
        else:
            # Muestra los errores en la consola para depuración
            print(form.errors)
            messages.error(request, 'Revise los datos proporcionados. Hay errores en el formulario.')
            # Reenvía el formulario con los errores al usuario
            return render(request, 'inventario/opciones/editar_facturador.html', {
                'form': form,
                'facturador': facturador
            })

# Eliminar Facturador
class EliminarFacturador(View):
    def get(self, request, id):
        facturador = get_object_or_404(Facturador, id=id)
        facturador.delete()
        messages.success(request, 'Facturador eliminado exitosamente.')
        return redirect('inventario:listar_facturadores')

class LoginFacturador(View):
    def post(self, request):
        password = request.POST.get('password')
        # Filtra por la contraseña. Asegúrate que las contraseñas estén almacenadas encriptadas.
        facturador = Facturador.objects.filter(password=password).first()

        if facturador:
            request.session['facturador_id'] = facturador.id  # Guarda la sesión del facturador
            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': False,
                'error': 'El facturador no existe. Verifique la contraseña.'
            })