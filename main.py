import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from turtle import *
import sqlite3


####################################################################################
                         ### CLASE VENTANA ###
#################################################################################### 
         
class Ventana:
    def __init__(self, nombre, ancho, alto):
        self.ventanaPrincipal = tk.Tk()
        self.basePalabras = BDPalabras("palabrasAhorcado")
        self.configurarTamanio(ancho, alto)
        self.configurarNombre(nombre)
        self.correrAplicacion()
        self.ventanaPrincipal.mainloop()
        
    def configurarTamanio(self, ancho, alto):
        ancho_pantalla = self.ventanaPrincipal.winfo_screenwidth() #obtener ancho de pantalla 
        alto_pantalla = self.ventanaPrincipal.winfo_screenheight() #obtener alto de pantalla
        posicion_x = int((ancho_pantalla/2) - (ancho/2)) #con estas cuentas se sacan los puntos donde deberia comenzar la pantalla
        posicion_y = int((alto_pantalla/2) - (alto/2))
        tamanioPosicion = str(ancho) + "x" + str(alto) + "+" + str(posicion_x) + "+" + str(posicion_y)#los primeros 2 son el tamaño, los otros la posicion en la pantalla
        self.ventanaPrincipal.geometry(tamanioPosicion)#geometry aplica el tamaño y la posicion, argumento en string
        self.ventanaPrincipal.resizable(0,0) #deshabilita el boton maximizar
        
    def configurarNombre(self, nombre):
        self.ventanaPrincipal.title(nombre)

    def correrAplicacion(self):
        self.menuPrincipal = PantallaTitulo(unaVentana = self.ventanaPrincipal, basePalabraJuego = self.basePalabras)


####################################################################################
                    ### CLASE ELEMENTO BASE DE DATOS ###
####################################################################################     
    
class ElementoBD:
    def __init__(self):
        self.consulta = None
        self.mensajeExito = None
        self.mensajeError = None
        self.palabra = None     
       
####################################################################################
                         ### BASE DE DATOS ###
####################################################################################
class BDPalabras:
    def __init__(self, nombrebase):
        self.nombreBase = str(nombrebase) + ".db"
        self.crearTabla("tablaPalabras")
        self.insertarPalabraInicial()
        
            
    def ejecutarConsulta(self, consulta: ElementoBD):
        conexionBase=sqlite3.connect(self.nombreBase) #creo/abro la base
        cursorPalabras = conexionBase.cursor()

        if consulta.palabra != None:
            try:
                cursorPalabras.execute(consulta.consulta, consulta.palabra)
                #print(consulta.palabra)
                cursorPalabras.connection.commit()
                return cursorPalabras.fetchall()   
            except sqlite3.OperationalError:
                print(consulta.mensajeError)                    
                conexionBase.close() 
        else:
            try:
                cursorPalabras.execute(consulta.consulta)
                #print(consulta.mensajeExito)
                cursorPalabras.connection.commit()
                return cursorPalabras.fetchall()
                
            except sqlite3.OperationalError:
                print(consulta.mensajeError)                    
                conexionBase.close() 
   
    def crearTabla(self, nombreTabla):
        consultaCrearTabla = ElementoBD()
        consultaCrearTabla.consulta = "CREATE TABLE palabras (codigo integer primary key autoincrement, descripcion text)"
        consultaCrearTabla.mensajeExito = "se creo la tabla " + nombreTabla
        consultaCrearTabla.mensajeError = "La tabla "+nombreTabla+" ya existe"
        
        self.ejecutarConsulta(consultaCrearTabla)

    def existePalabra(self, unaPalabra):
        palabraIngresada = unaPalabra.upper().strip()
        consultaExistePalabra = ElementoBD()
        consultaExistePalabra.consulta = "SELECT * FROM palabras WHERE descripcion=?"
        consultaExistePalabra.mensajeExito = "Si, existe palabra"
        consultaExistePalabra.mensajeError = "Palabra no existe"
        consultaExistePalabra.palabra = (palabraIngresada,)
        return self.ejecutarConsulta(consultaExistePalabra)
        #cursorPalabras.execute("""SELECT * 
         #                              FROM palabras 
          #                             WHERE descripcion=?""", (palabraIngresada,))
        #resultado = cursorPalabras.fetchone()
        
        #return resultado is not None
    
    def agregarPalabra(self, unaPalabra):
        palabraIngresada = unaPalabra.upper().strip()
        consultaAgregarPalabra = ElementoBD()
        consultaAgregarPalabra.consulta = "INSERT INTO palabras (descripcion) VALUES (?)"
        consultaAgregarPalabra.mensajeExito = "Palabra agregada exitosamente: " + palabraIngresada
        consultaAgregarPalabra.mensajeError = "Error al agregar palabra:"
        consultaAgregarPalabra.palabra = (palabraIngresada,)
        
        if self.existePalabra(palabraIngresada):
            mb.showerror("Error", "Palabra ya ingresada")
        else:
            respuesta = self.ejecutarConsulta(consultaAgregarPalabra)

    def contarPalabras(self):
        consultaContarPalabras = ElementoBD()
        consultaContarPalabras.consulta = "SELECT COUNT(*) FROM palabras"
        consultaContarPalabras.mensajeExito = "Se conto la totalidad de palabras"
        consultaContarPalabras.mensajeError = "No se logro contar las palabras"
        cantidad = self.ejecutarConsulta(consultaContarPalabras)[0]
        
        return cantidad


    def insertarPalabraInicial(self):
        if self.contarPalabras()[0] < 1:
            self.agregarPalabra("tuberculo")     
  
    def obtenerPalabrasDeBase(self):
        consultaObtenerPalabras = ElementoBD()
        consultaObtenerPalabras.consulta = "SELECT descripcion FROM palabras"
        consultaObtenerPalabras.mensajeExito = "Se obtuvieron las palabras de la base"
        consultaObtenerPalabras.mensajeError = "No se logro obtener las palabras de la base"
        respuestaConsulta = self.ejecutarConsulta(consultaObtenerPalabras)
        
        if respuestaConsulta:
            listaPalabras = [fila[0] for fila in respuestaConsulta]
            return listaPalabras
        else:
            return []
    
    def borrarPalabra(self, unaPalabra):
        palabraIngresada = unaPalabra.upper().strip()
        consultaBorrarPalabra = ElementoBD()
        consultaBorrarPalabra.consulta = "DELETE FROM palabras WHERE descripcion=?"
        consultaBorrarPalabra.mensajeExito = "Palabra borrada exitosamente: " + palabraIngresada
        consultaBorrarPalabra.mensajeError = "Error al borrar palabra:"
        consultaBorrarPalabra.palabra = (palabraIngresada,)
        
        if not self.existePalabra(palabraIngresada):
            mb.showerror("Error", "La palabra no existe")
        else:
            respuesta = self.ejecutarConsulta(consultaBorrarPalabra)    
    
    def seleccionarPalabraAlAzar(self):
        consultaSeleccionarPalabra = ElementoBD()
        consultaSeleccionarPalabra.consulta = "SELECT descripcion FROM palabras"
        consultaSeleccionarPalabra.mensajeError = "No se pudo seleccionar una palabra al azar"
        consultaSeleccionarPalabra.mensajeExito = "Se selecciono una palabra al azar"
        
        palabras = self.ejecutarConsulta(consultaSeleccionarPalabra)

        if palabras:
            palabraElegida = random.choice(palabras)[0]
            print("Palabra seleccionada al azar:", palabraElegida)
            return palabraElegida
        else:
            print("No hay palabras en la base de datos.")
            return None
####################################################################################
                         ### CLASE PANTALLA TITULO ###
####################################################################################         
        
class PantallaTitulo(tk.Frame):
    def __init__(self, unaVentana:Ventana, basePalabraJuego: BDPalabras): #con el dos puntos en la variable le digo que tipo de dato es
        super().__init__(unaVentana)
        self.laVentana = unaVentana
        self.BPJuego = basePalabraJuego
        self.config(bg="black")
        self.pack(expand=True, fill="both", ipadx=10, ipady=10)#usamos pack para manejar el tamaño del frame, both le dice q es hacia lo alto y lo ancho
        self.boxTitulo = self.contenedorTitulo()
        self.boxMenu = ContenedorBotonesPantallaTitulo(self, self.BPJuego)
                   
    def contenedorTitulo(self):
        boxTitulo = tk.Canvas(self, background="black",highlightthickness=0, borderwidth=0)#highlightthickness=0, saca los bordes blancos
        self.archivo_titulo = tk.PhotoImage(file="imagenes/nuevo_titulo.png")
        boxTitulo.create_image(5,0, image=self.archivo_titulo, anchor="nw")#vértice superior izquierdo se muestre en la coordenada 0,0. junto con el anchor nw
        boxTitulo.place(relx=0.15, rely=0.17, relwidth=0.70, relheight=0.50)
        
        return boxTitulo

###################################################################################
                ### CLASE CONTENEDOR BOTONES PANTALLA TITULO ###
####################################################################################     
    
class ContenedorBotonesPantallaTitulo:
    def __init__(self, framePrincipal:tk.Frame, basePalabraJuego: BDPalabras):#PantallaTitulo = None
        self.BPJuego = basePalabraJuego
        self.frameMenu = framePrincipal
        self.contenedor= tk.Frame(self.frameMenu)
        self.contenedor.config(background="black")    
        self.contenedor.place(relx=0.4, rely=0.70, relwidth=0.2, relheight=0.25)#relhi015   
        self.cargarBotones()#carga botones a la lista
            
        
    def cargarBotones(self):
        self.jugar = BotonColumna(self.contenedor, "JUGAR", 1, 0.1)
        self.jugar.boton["command"] = self.comandoJugar
        
        self.palabras = BotonColumna(self.contenedor, "PALABRAS", 2, 0.1)
        self.palabras.boton["command"]=self.comandoPalabras
        
        #self.configuracion = BotonColumna(self.contenedor, "CONFIG", 3, 0.1)
        
        self.salir = BotonColumna(self.contenedor, "SALIR", 3, 0.1)
        self.salir.boton["command"] = self.comandoSalir
        
    def comandoSalir(self):
        self.frameMenu.laVentana.destroy()
        
    def comandoJugar(self):
        self.frameMenu.laVentana.menuPrincipal= PantallaModoJuego(self.frameMenu.laVentana, self.BPJuego),
        self.frameMenu.destroy()
        
    def comandoPalabras(self):
        self.ventanaBase = VentanaBasePalabras("Palabras", 400, 400, self.BPJuego)
        
####################################################################################
                         ### CLASE BOTON COLUMNA###
####################################################################################         

class BotonColumna:
    def __init__(self, frameContenedor:ContenedorBotonesPantallaTitulo, nombre, fila, posrely):
        self.fila=fila 
        self.posy= posrely#0.1#20
        if fila != 1:
            self.posy=self.posy+0.2 * (fila-1)#20+(24+5)*(fila-1) #boton mide 24 de alto
        self.posx=0.26#40 
        self.boton = ttk.Button(frameContenedor, text=nombre)
        self.boton.place(relx=self.posx, rely=self.posy)
        self.boton["command"]=None
        
####################################################################################
                         ### CLASE BOTON FILA###
####################################################################################         

class BotonFila:
    def __init__(self, frameContenedor:ContenedorBotonesPantallaTitulo, nombre, fila, posrely, columna, posrelx, distanciaFila):
        self.fila=fila #4
        self.posy= posrely#0.1#20
        if fila != 1:
            self.posy=self.posy+distanciaFila * (fila-1)#20+(24+5)*(fila-1) #boton mide 24 de alto0.2
        self.posx=posrelx#0.05#40 
        if columna !=1:
            self.posx = self.posx+0.25 * (columna - 1)
        self.boton = ttk.Button(frameContenedor, text=nombre)
        self.boton.place(relx=self.posx, rely=self.posy)
        self.boton["command"]=None
        
####################################################################################
                         ### CLASE BOTON GENERAL###
####################################################################################         

class Boton:
    def __init__(self, frameContenedor:ContenedorBotonesPantallaTitulo, nombre, fila, columna, posinicialy, posinicialx, distanciaColumna, distanciaFila):
        #self.fila=fila #4
        self.nombre = nombre
        self.posx=posinicialx#0.05#40 
        self.posy= posinicialy#0.1#20
        
        if fila != 1:
            self.posy=self.posy+distanciaFila * (fila-1)#20+(24+5)*(fila-1) #boton mide 24 de alto0.2
        
        if columna !=1:
            self.posx = self.posx+distanciaColumna * (columna - 1)#0.48
        self.boton = ttk.Button(frameContenedor, text=nombre)
        self.boton.place(relx=self.posx, rely=self.posy)
        self.boton["command"]=None
        
####################################################################################
                    ### CLASE PANTALLA MODO JUEGO ###
####################################################################################        
class PantallaModoJuego(tk.Frame):
    def __init__(self, unaVentana:Ventana, basePalabraJuego: BDPalabras): #= None
        super().__init__(unaVentana)
        self.BPJuego = basePalabraJuego
        self.laVentana = unaVentana
        self.config(bg="black")
        self.pack(expand=True, fill="both", ipadx=10, ipady=10)#usamos pack para manejar el tamaño del frame, both le dice q es hacia lo alto y lo ancho
        self.boxMenu = ContenedorBotonesModoJuego(self, self.BPJuego)
      
        """
        place(relx=0.15, rely=0.17, relwidth=0.70, relheight=0.50)
            rel -> posiciones relativas respecto del padre. van de 0 a 1. Ej: 0.15 quiere decir 15% del ancho del padre
        """
            ####################################################################################
                                ### CLASE CONTENEDOR BOTONES MODO JUEGO ###
            ####################################################################################        
class ContenedorBotonesModoJuego:          
    def __init__(self, framePrincipal:PantallaModoJuego, basePalabraJuego: BDPalabras): #=None 
        self.frameModoJuego = framePrincipal
        self.contenedor= tk.Frame(self.frameModoJuego)
        self.BPJuego = basePalabraJuego
        self.contenedor.config(background="grey")    
        self.contenedor.place(relx=0.4, rely=0.35, relwidth=0.2, relheight=0.25)#relhi015   
        self.cargarBotones()#carga botones a la lista
        
    def cargarBotones(self):
        self.aleatorio = BotonColumna(self.contenedor, "ALEATORIO", 1, 0.2)
        self.aleatorio.boton["command"] = self.comandoAleatorio
        
        self.ingresar = BotonColumna(self.contenedor, "INGRESAR", 2, 0.2)
        self.ingresar.boton["command"] = self.comandoIngresar
        
        self.volver = BotonColumna(self.contenedor, "VOLVER", 3, 0.2)
        self.volver.boton["command"] = self.comandoVolver
        
    def comandoVolver(self):
        self.frameModoJuego.laVentana.menuPrincipal = PantallaTitulo(unaVentana = self.frameModoJuego.laVentana, basePalabraJuego = self.BPJuego)
        self.frameModoJuego.destroy()

    def comandoIngresar(self):
        self.frameModoJuego.laVentana.menuPrincipal = PantallaIngresarPalabra(unaVentana = self.frameModoJuego.laVentana, basePalabraJuego = self.BPJuego)
        self.frameModoJuego.destroy()
        
    def comandoAleatorio(self):
         
        palabra = self.BPJuego.seleccionarPalabraAlAzar()
        
        #print(palabra)
        
        if self.validarPalabra(palabra):
            self.frameModoJuego.laVentana.menuPrincipal = PantallaJuego(palabra, unaVentana = self.frameModoJuego.laVentana, basePalabraJuego = self.BPJuego)
            self.frameModoJuego.destroy()
        else:
            #tirar mensaje error
            mb.showerror("Error", "La palabra ingresada tiene caracteres invalidos")
        
    def validarPalabra(self, unaPalabra):
        return unaPalabra.isalpha()
####################################################################################
                    ### CLASE PANTALLA INGRESAR PALABRA ###
####################################################################################        
class PantallaIngresarPalabra(tk.Frame):
    def __init__(self, unaVentana:Ventana, basePalabraJuego: BDPalabras): #= None
        super().__init__(unaVentana)
        self.laVentana = unaVentana
        self.BPJuego = basePalabraJuego
        self.config(bg="black")
        self.pack(expand=True, fill="both", ipadx=10, ipady=10)#usamos pack para manejar el tamaño del frame, both le dice q es hacia lo alto y lo ancho
        self.boxMenu = ContenedorIngresaPalabra(self, self.BPJuego)

            ####################################################################################
                                ### CLASE CONTENEDOR INGRESA PALABRA ###
            #################################################################################### 

class ContenedorIngresaPalabra:
    def __init__(self, framePrincipal:PantallaTitulo, basePalabraJuego: BDPalabras): #= None
        self.frameIngresarPalabra = framePrincipal
        self.contenedor= tk.Frame(self.frameIngresarPalabra)
        self.BPJuego = basePalabraJuego
        self.contenedor.config(background="grey")    
        self.contenedor.place(relx=0.3, rely=0.35, relwidth=0.40, relheight=0.30)
        self.ingresoPalabra()
        
        self.botonesIngresoPalabra()
        
    def ingresoPalabra(self):
        self.titulo = tk.Label(self.contenedor, text="INGRESE PALABRA:")
        self.titulo.place(relx=0.05, rely=0.10, relwidth=0.60, relheight=0.20)
        self.titulo.config(bg="red", fg="black", font=("Showcard Gothic", 15))
        
        self.dato = tk.StringVar()
        self.ingreso = ttk.Entry(self.contenedor,textvariable=self.dato, width=1)
        self.ingreso.place(relx=0.05, rely=0.35, relwidth=0.50, relheight=0.15)
        self.dato.trace_add('write', lambda *args: self.dato.set(self.dato.get().upper())) #El dato que se ingresa es en mayuscula
        
        
        
    def botonesIngresoPalabra(self):
        self.volver = BotonFila(self.contenedor, "VOLVER", 4, 0.2,1, 0.05, 0.2)
        self.volver.boton["command"] = self.comandoVolver
        
        self.comenzar = BotonFila(self.contenedor, "COMENZAR", 4, 0.2,2, 0.05,0.2)
        self.comenzar.boton["command"] = self.comandoComenzar
        
    def comandoVolver(self):
        self.frameIngresarPalabra.laVentana.menuPrincipal = PantallaModoJuego(unaVentana = self.frameIngresarPalabra.laVentana, basePalabraJuego = self.BPJuego)
        self.frameIngresarPalabra.destroy()
    
    def comandoComenzar(self):
        palabra = str(self.dato.get())
        
        self.BPJuego.agregarPalabra(palabra)
        
        #print(self.validarPalabra(palabra))
        
        if self.validarPalabra(palabra):
            self.frameIngresarPalabra.laVentana.menuPrincipal = PantallaJuego(palabra, unaVentana = self.frameIngresarPalabra.laVentana, basePalabraJuego = self.BPJuego)
            self.frameIngresarPalabra.destroy()
        else:
            #tirar mensaje error
            mb.showerror("Error", "La palabra ingresada tiene caracteres invalidos")
    
    def validarPalabra(self, unaPalabra):
        return unaPalabra.isalpha()
    
    
        
####################################################################################
                    ### CLASE PANTALLA INGRESAR PALABRA ###
####################################################################################        
class PantallaJuego(tk.Frame):
    def __init__(self, palabra, unaVentana:Ventana, basePalabraJuego: BDPalabras): #= None
        super().__init__(unaVentana)
        self.palabraIngresada = palabra 
        self.laVentana = unaVentana
        self.BPJuego = basePalabraJuego
        self.config(bg="black")
        self.pack(expand=True, fill="both", ipadx=10, ipady=10)#usamos pack para manejar el tamaño del frame, both le dice q es hacia lo alto y lo ancho
        self.boxBotones = ContenedorBotonesJuego(self, self.BPJuego)
        self.boxLetras = ContenedorLetras(self, self.BPJuego)
        self.boxPalabra = ContenedorPalabra(self)
        self.boxMuerto = ContenedorHorca(self)#ContenedorMuerto(self)
        #self.boxTiempo = ContenedorReloj(self)

    
        
                    ####################################################################################
                                    ### CLASE CONTENEDOR BOTONES JUEGO ###
                    ####################################################################################          
class ContenedorBotonesJuego:          
    def __init__(self, framePrincipal:PantallaJuego, basePalabraJuego: BDPalabras): #= None
        self.framePantallaJuego = framePrincipal
        self.contenedor= tk.Frame(self.framePantallaJuego)
        self.BPJuego = basePalabraJuego
        self.contenedor.config(background="black")    
        self.contenedor.place(relx=0.07, rely=0.90, relwidth=0.3, relheight=0.05)#relhi015   
        self.cargarBotones()#carga botones a la lista
        
    def cargarBotones(self):
        self.ingresar = BotonFila(self.contenedor, "VOLVER", 1, 0.05,1, 0.05,0.2)
        self.ingresar.boton["command"] = self.comandoVolver
        
        self.volver = BotonFila(self.contenedor, "RENDIRSE", 1, 0.05,3, 0.05,0.2)
        self.volver.boton["command"] = self.comandoRendirse
        
    def comandoVolver(self):
        self.framePantallaJuego.laVentana.menuPrincipal = PantallaIngresarPalabra(unaVentana = self.framePantallaJuego.laVentana, basePalabraJuego = self.BPJuego)
        self.framePantallaJuego.destroy()

    def comandoRendirse(self):
        self.framePantallaJuego.laVentana.menuPrincipal = PantallaTitulo(unaVentana = self.framePantallaJuego.laVentana, basePalabraJuego = self.BPJuego)
        self.framePantallaJuego.destroy()
        
                    ####################################################################################
                                            ### CLASE CONTENEDOR LETRAS ###
                    ####################################################################################        
class ContenedorLetras:
    def __init__(self, framePrincipal:PantallaJuego, basePalabraJuego: BDPalabras): # = None
        self.error = 0
        self.frameJuego = framePrincipal
        self.contenedor= tk.Frame(self.frameJuego)
        self.BPJuego = basePalabraJuego
        self.contenedor.config(background="grey")    
        self.contenedor.place(relx=0.65, rely=0.08, relwidth=0.30, relheight=0.85)
        self.cargarBotones()    
        
    def cargarBotones(self):
                        
        self.A = Boton(self.contenedor, "A", 1, 1, 0.03, 0.1, 0.48, 0.03)
        self.A.boton["command"] = lambda:self.comandoLetra(self.A)
             
        self.B = Boton(self.contenedor, "B", 1, 2, 0.03, 0.10, 0.48, 0.07)
        self.B.boton["command"] = lambda:self.comandoLetra(self.B)
        
        self.C = Boton(self.contenedor, "C", 2, 1, 0.03, 0.10, 0.48, 0.07)
        self.C.boton["command"] = lambda:self.comandoLetra(self.C)
                
        self.D = Boton(self.contenedor, "D", 2, 2, 0.03, 0.10, 0.48, 0.07)
        self.D.boton["command"] = lambda:self.comandoLetra(self.D)
        
        self.E = Boton(self.contenedor, "E", 3, 1, 0.03, 0.10, 0.48, 0.07)
        self.E.boton["command"] = lambda:self.comandoLetra(self.E)
                
        self.F = Boton(self.contenedor, "F", 3, 2, 0.03, 0.10, 0.48, 0.07)
        self.F.boton["command"] = lambda:self.comandoLetra(self.F)
        
        self.G = Boton(self.contenedor, "G", 4, 1, 0.03, 0.10, 0.48, 0.07)
        self.G.boton["command"] = lambda:self.comandoLetra(self.G)
                
        self.H = Boton(self.contenedor, "H", 4, 2, 0.03, 0.10, 0.48, 0.07)
        self.H.boton["command"] = lambda:self.comandoLetra(self.H)
        
        self.I = Boton(self.contenedor, "I", 5, 1, 0.03, 0.1, 0.48, 0.07)
        self.I.boton["command"] = lambda:self.comandoLetra(self.I)        
        
        self.J = Boton(self.contenedor, "J", 5, 2, 0.03, 0.10, 0.48, 0.07)
        self.J.boton["command"] = lambda:self.comandoLetra(self.J)
        
        self.K = Boton(self.contenedor, "K", 6, 1, 0.03, 0.10, 0.48, 0.07)
        self.K.boton["command"] = lambda:self.comandoLetra(self.K)
                
        self.L = Boton(self.contenedor, "L", 6, 2, 0.03, 0.10, 0.48, 0.07)
        self.L.boton["command"] = lambda:self.comandoLetra(self.L)
        
        self.M = Boton(self.contenedor, "M", 7, 1, 0.03, 0.10, 0.48, 0.07)
        self.M.boton["command"] = lambda:self.comandoLetra(self.M)
                
        self.N = Boton(self.contenedor, "N", 7, 2, 0.03, 0.10, 0.48, 0.07)
        self.N.boton["command"] = lambda:self.comandoLetra(self.N)
        
        self.Ñ = Boton(self.contenedor, "Ñ", 8, 1, 0.03, 0.10, 0.48, 0.07)
        self.Ñ.boton["command"] = lambda:self.comandoLetra(self.Ñ)
                
        self.O = Boton(self.contenedor, "O", 8, 2, 0.03, 0.10, 0.48, 0.07)
        self.O.boton["command"] = lambda:self.comandoLetra(self.O)
        
        self.P = Boton(self.contenedor, "p", 9, 1, 0.03, 0.10, 0.48, 0.07)
        self.P.boton["command"] = lambda:self.comandoLetra(self.P)
        
        self.Q = Boton(self.contenedor, "Q", 9, 2, 0.03, 0.10, 0.48, 0.07)
        self.Q.boton["command"] = lambda:self.comandoLetra(self.Q)
                
        self.R = Boton(self.contenedor, "R", 10, 1, 0.03, 0.10, 0.48, 0.07)
        self.R.boton["command"] = lambda:self.comandoLetra(self.R)
        
        self.S = Boton(self.contenedor, "S", 10, 2, 0.03, 0.10, 0.48, 0.07)
        self.S.boton["command"] = lambda:self.comandoLetra(self.S)
                
        self.T = Boton(self.contenedor, "T", 11, 1, 0.03, 0.10, 0.48, 0.07)
        self.T.boton["command"] = lambda:self.comandoLetra(self.T)
        
        self.U = Boton(self.contenedor, "U", 11, 2, 0.03, 0.1, 0.48, 0.07)
        self.U.boton["command"] = lambda:self.comandoLetra(self.U)        
        
        self.V = Boton(self.contenedor, "V", 12, 1, 0.03, 0.10, 0.48, 0.07)
        self.V.boton["command"] = lambda:self.comandoLetra(self.V)
        
        self.W = Boton(self.contenedor, "W", 12, 2, 0.03, 0.10, 0.48, 0.07)
        self.W.boton["command"] = lambda:self.comandoLetra(self.W)        
        
        self.X = Boton(self.contenedor, "X", 13, 1, 0.03, 0.10, 0.48, 0.07)
        self.X.boton["command"] = lambda:self.comandoLetra(self.X)
        
        self.Y = Boton(self.contenedor, "Y", 13, 2, 0.03, 0.10, 0.48, 0.07)
        self.Y.boton["command"] = lambda:self.comandoLetra(self.Y)        
        
        self.Z = Boton(self.contenedor, "Z", 14, 1, 0.03, 0.10, 0.48, 0.07)
        self.Z.boton["command"] = lambda:self.comandoLetra(self.Z)
        
    def letraEstaEnPalabra(self, letra):
        respuesta = False
        for i in range (len(self.frameJuego.palabraIngresada)):
            if self.frameJuego.palabraIngresada[i] == letra:
                #print("esta en palabra")
                respuesta = True
                break
            
        return respuesta
    
    def seDescubrio(self):
        respuesta = False
        letras = 0
        for i in range (len(self.frameJuego.boxPalabra.palabraADescubrir)):
            if self.frameJuego.boxPalabra.palabraADescubrir[i] == "_":
                respuesta = False
            else:
                letras = letras+1
                #print(letras)
                if letras == len(self.frameJuego.boxPalabra.palabraADescubrir):
                    respuesta = True
        return respuesta
    
    #def deshabilitarBotones(self):
    
    def comandoLetra(self, boton:Boton):
        if self.letraEstaEnPalabra(boton.nombre):
            boton.boton.config(state="disable")
            self.frameJuego.boxPalabra.actualizarPalabra(boton.nombre)
            if self.seDescubrio():
                self.mensajeGanador()
                #destruir pantalla y volver a la inicial
                self.frameJuego.laVentana.menuPrincipal = PantallaTitulo(unaVentana = self.frameJuego.laVentana, basePalabraJuego = self.BPJuego)
                self.frameJuego.destroy()
        else:
            #print(self.error)
            self.error = self.error+1
            #print (self.error)
            boton.boton.config(state="disable")
            if self.error!=6 and self.error<7:
                self.frameJuego.boxMuerto.mostrarHorca(self.error)
            if self.error==6:
                self.frameJuego.boxMuerto.mostrarHorca(self.error)
                self.mensajePerdisteUno()            
                self.mensajePerdisteDos()
                #destruir pantalla y volver a la inicial
                self.frameJuego.laVentana.menuPrincipal = PantallaTitulo(unaVentana = self.frameJuego.laVentana, basePalabraJuego = self.BPJuego)
                self.frameJuego.destroy()
    
    def mensajePerdisteUno(self):
        mb.showerror("GAME OVER", "Perdiste la partida, jajajaja")
        
    def mensajePerdisteDos(self):
        mb.showinfo("GAME OVER", f"La palabra era: {self.frameJuego.palabraIngresada}")#frameJuego.boxPalabra.palabraADescubrir
        
    def mensajeGanador(self):
        mb.showinfo("YOU WIN", "Has ganado la partida")
                    ####################################################################################
                                        ### CLASE CONTENEDOR PALABRA###
                    ####################################################################################

class ContenedorPalabra:          
    def __init__(self, framePrincipal:PantallaJuego = None):
        self.framePantallaJuego = framePrincipal
        self.contenedor= tk.Label(self.framePantallaJuego)#, text="INGRESE PALABRA")
        self.contenedor.place(relx=0.2, rely=0.80, relwidth=0.3, relheight=0.05)#relhi015   
        self.contenedor.config(bg="red", fg="white", font=("Showcard Gothic", 15))    
        self.palabraIngresada = self.framePantallaJuego.palabraIngresada
        self.palabraADescubrir = self.estadoInicial()
        self.actualizarBox()
        
    def estadoInicial(self):
        laPalabra = []
        for i in range (len(self.framePantallaJuego.palabraIngresada)):
            laPalabra.append("_")
        return laPalabra            
        
        
    def actualizarBox(self):
        self.contenedor.config(text=self.palabraADescubrir)
        
    def actualizarPalabra(self, letra):
        for i in range (len(self.palabraIngresada)):
            if self.palabraIngresada[i] == letra:
                self.palabraADescubrir[i] = letra
                self.actualizarBox()
        return self.palabraADescubrir
    
    
                    ####################################################################################
                                    ### CLASE CONTENEDOR BOTONES JUEGO ###
                    ####################################################################################    
class ContenedorHorca:
    def __init__(self, framePrincipal:PantallaJuego = None):
        self.framePantallaJuego = framePrincipal
        self.boxHorca = tk.Canvas(self.framePantallaJuego, background="blue",highlightthickness=0, borderwidth=0)#highlightthickness=0, saca los bordes blancos
        #self.archivo_titulo = tk.PhotoImage(file="imagenes/horca.png")
        #self.boxHorca.create_image(5,0, image=self.archivo_titulo, anchor="nw")#vértice superior izquierdo se muestre en la coordenada 0,0. junto con el anchor nw
        self.boxHorca.place(relx=0.2, rely=0.2, relwidth=0.30, relheight=0.55)#relx=0.1, rely=0.1, relwidth=0.45, relheight=0.70)#relwidth=0.70, relheight=0.50)
        
        self.imagenes = self.crearImagenesMuerto()
        self.muerto = self.mostrarHorca(0)
    
    
    def mostrarHorca(self, numero: int):
        imagen = self.imagenes[numero]
        self.boxHorca.create_image(0,0, image=imagen, anchor="nw")#vértice superior izquierdo se muestre en la coordenada 0,0. junto con el anchor nw
    
    def crearImagenesMuerto(self):
        self.archivo_horca = tk.PhotoImage(file="imagenes/horca.png")
        self.archivo_error_1 = tk.PhotoImage(file="imagenes/error_1.png")
        self.archivo_error_2 = tk.PhotoImage(file="imagenes/error_2.png")
        self.archivo_error_3 = tk.PhotoImage(file="imagenes/error_3.png")
        self.archivo_error_4 = tk.PhotoImage(file="imagenes/error_4.png")
        self.archivo_error_5 = tk.PhotoImage(file="imagenes/error_5.png")
        self.archivo_error_6 = tk.PhotoImage(file="imagenes/error_6.png")

        listaImagenes = [self.archivo_horca, 
                              self.archivo_error_1,
                              self.archivo_error_2, 
                              self.archivo_error_3,
                              self.archivo_error_4,
                              self.archivo_error_5,
                              self.archivo_error_6]
        
        return listaImagenes

        
####################################################################################
                ### CLASE VENTANA SECUNDARIA BASE DE DATOS ###
####################################################################################   
class VentanaBasePalabras:
    def __init__(self, nombre, ancho, alto, basePalabraJuego: BDPalabras):
        self.ventanaBase = tk.Toplevel()#ventana secundaria, si se cierra la principal, esta tambien lo haratk.Tk()
        self.BPJuego = basePalabraJuego
        self.configurarTamanio(ancho, alto)
        self.configurarNombre(nombre)
        self.ventanaBase.grab_set() #Mantiene el foco de la ventana hasta que se cierre y devuelve la interacción con la ventana principal el root en este caso.
        self.ventanaBase.focus_set() #Mantiene el foco cuando se abre la ventana.
        self.modificarBasePalabras()
        

    def configurarTamanio(self, ancho, alto):
        ancho_pantalla = self.ventanaBase.winfo_screenwidth() #obtener ancho de pantalla 
        alto_pantalla = self.ventanaBase.winfo_screenheight() #obtener alto de pantalla
        posicion_x = int((ancho_pantalla/2) - (ancho/2)) #con estas cuentas se sacan los puntos donde deberia comenzar la pantalla
        posicion_y = int((alto_pantalla/2) - (alto/2))
        tamanioPosicion = str(ancho) + "x" + str(alto) + "+" + str(posicion_x) + "+" + str(posicion_y)#los primeros 2 son el tamaño, los otros la posicion en la pantalla
        self.ventanaBase.geometry(tamanioPosicion)#geometry aplica el tamaño y la posicion, argumento en string
        self.ventanaBase.resizable(0,0) #deshabilita el boton maximizar
        
    def configurarNombre(self, nombre):
        self.ventanaBase.title(nombre) 

    def modificarBasePalabras(self):
        self.menuPalabras = PantallaBasePalabras(ventanaVisorBase = self.ventanaBase, basePalabrasJuego=self.BPJuego)

####################################################################################
                ### CLASE FRAME PANTALLA BASE PALABRAS ###
####################################################################################   

class PantallaBasePalabras(tk.Frame):
    def __init__(self, ventanaVisorBase: VentanaBasePalabras, basePalabrasJuego: BDPalabras):
        super().__init__(ventanaVisorBase)
        self.BDJuego = basePalabrasJuego
        self.ventanaBaseDatos = ventanaVisorBase
        self.config(bg="grey")
        self.pack(expand=True, fill="both", ipadx=10, ipady=10)#usamos pack para manejar el tamaño del frame, both le dice q es hacia lo alto y lo ancho. sin esto no tiene efecto el fondo
        self.contenedorElementos = self.frameElementos()
               
        self.salir = Boton(self.ventanaBaseDatos, "SALIR", 1, 1, 0.90, 0.76, 0.48, 0.03)
        self.salir.boton["command"] = self.comandoSalir
        
        
        self.elementos()
        self.actualizarListadoPalabras()
        
    def comandoSalir(self):
        self.ventanaBaseDatos.destroy()
    
    def frameElementos(self):
        contenedor = tk.Frame(self.ventanaBaseDatos)
        contenedor.config()
        contenedor.place(relx=0.05, rely=0.05, relwidth=0.90, relheight=0.80)
        return contenedor
    
    def elementos(self):
       
        self.titulo = ttk.Label(self.ventanaBaseDatos, text="Ingresar palabra:")
        self.titulo.place(relx=0.13, rely=0.07, relwidth=0.33, relheight=0.08)
        self.titulo.config(background="white", font=("verdana", 11) )
        
        self.entrada = ttk.Entry(self.ventanaBaseDatos)
        self.entrada.place(relx=0.47, rely=0.09, relwidth=0.35, relheight=0.05)
        
        self.agregar = Boton(self.ventanaBaseDatos, "AGREGAR", 1, 1, 0.17, 0.40, 0.48, 0.03)
        self.agregar.boton["command"] = self.comandoAgregar
        
        
        self.palabraSeleccionada = tk.StringVar()
        self.listado = tk.Listbox(self.contenedorElementos, listvariable=self.palabraSeleccionada)
        self.listado.place(relx=0.25, rely=0.25, relwidth=0.50, relheight=0.60)
        
        self.borrar = Boton(self.ventanaBaseDatos, "BORRAR", 1, 1, 0.76, 0.40, 0.48, 0.03)
        self.borrar.boton["command"] = self.comandoBorrar
    
    def actualizarListadoPalabras(self): # Obtener las palabras de la base de datos y agregarlas al Listbox
        palabras = self.BDJuego.obtenerPalabrasDeBase()
        self.listado.delete(0, tk.END)  # Limpiar el Listbox
        for palabra in palabras:
            self.listado.insert(tk.END, palabra)
        
    def comandoAgregar(self):
        palabra = self.entrada.get()
        print(palabra)
        self.BDJuego.agregarPalabra(palabra)
        self.actualizarListadoPalabras()
        self.entrada.delete("0", "end")

    def comandoBorrar(self):
        indiceSeleccionado = self.listado.curselection()

        if indiceSeleccionado:
            palabraSeleccionada = self.listado.get(indiceSeleccionado[0])
            print("Palabra seleccionada:", palabraSeleccionada)
            self.BDJuego.borrarPalabra(palabraSeleccionada)
            self.actualizarListadoPalabras()
        else:
            print("No se ha seleccionado ninguna palabra.")
        
####################################################################################
                    ### INICIALIZACION DE APLICACION ###
#################################################################################### 

ahorcado = Ventana("Ahorcado", 800, 600)        