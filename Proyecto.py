import oracledb
import time

oracledb.init_oracle_client(lib_dir=r'C:/instantclient_21_10')

connection = oracledb.connect(user='jaime', password='.Inacap2023.', dsn='dbtaller_high')

cursor= connection.cursor()

###########################################################################################################
class User:#Esta clase maneja el inicio de sesión y el log out de los usuarios, de momento el log out no tiene una real funcionalidad pero permite la escalabilidad para dar la función de cambiar de cuentas dentro de la app sin cerrarla
    def LogIn(): #Inicia sesión, cambia la variable CurrentUser que guarda información sensible como la ID del usuario y el tipo de Usuario si es GM o Jugador
        username= str(input("Ingrese nombre de usuario:"))
        password= str(input("Ingrese contraseña:")) #INPUT DATA DEL USUARIO
        CurrentUser= [0, 0]
    
        values= [username, password] #VALORES DEL QUERY
        cursor.execute('SELECT * FROM Usuarios WHERE username= :username AND pword= :password', values)
        result= cursor.fetchone()
    
        if result == None: #VALIDA SI EXISTE EL USUARIO
            print("Usuario o Contraseña incorrecto")
            User.LogIn()
        else:
            cursor.execute('SELECT user_id FROM Usuarios WHERE username= :username AND pword= :password', values)
            CurrentUserID= cursor.fetchone()[0]
            cursor.execute('SELECT user_type FROM Usuarios WHERE username= :username AND pword= :password', values)
            CurrentUserType= cursor.fetchone()[0]
            print("Inicio de sesión exitoso")     
            CurrentUser= [CurrentUserID, CurrentUserType] #Información útil del usuario actual en formato list para lectura global
            return(CurrentUser)
        
    def LogOut():
        CurrentUser= [0, 0]   
        return(CurrentUser) #Establece la información del usuario a valor 0

#FUNCIONES DE JUGADOR
class Jugador:
    #Clase jugador con todos los metodos que son esenciales al jugador, funciona para generar la vista única jugador y para reunir todo lo relacionado al jugador en un sitio
    def select_raza(): #subfunción para crear personaje, proceso de selección de raza, la volví función porque es una rutina que se repite constante y ahorra código
        cursor.execute("SELECT raza_id, nombre_raza FROM Raza")
        for row in cursor.fetchall():
            print(row)
        print("Indica el id de la raza que quieres")
        idRaza= [int(input("Elige la raza:"))]
        cursor.execute("SELECT raza_id FROM Raza WHERE raza_id= :idRaza", idRaza)
        razaAuth= cursor.fetchone()
        if razaAuth != None:#todas las variables Auth se refieren a algun tipo de Authentication y son principalmente para saber si es que cierto elemento existe en la base de datos
            cursor.execute("SELECT nombre_raza FROM Raza WHERE raza_id= :idRaza", idRaza)
            return(idRaza)
        else:#En caso de que la raza elegida no esté en la base de datos
            print("ID de raza incorrecta, intenta nuevamente")
            Jugador.select_raza()  
        
    #Bloque de Modificar equipo a un personaje
    def add_equipoaPJ(idPersonaje):#Agrega un equipo a el personaje entregado
        cursor.execute("SELECT equipo_id, nombre_equipo FROM Equipos")
        for row in cursor.fetchall():
            print(row)
        print("Indica el id del equipo que quieres agregar")
        idEquipo= [int(input("Elige el equipo para tu personaje:"))]
        cursor.execute("SELECT equipo_id FROM Equipos WHERE equipo_id= :idEquipo", idEquipo)#Busca el equipo de acuerdo a la id entregada
        EquipoAuth= cursor.fetchone()
        if EquipoAuth != None:#Authentication de si la id entregada existe en la bd
            cursor.execute("SELECT nombre_equipo FROM Equipos WHERE equipo_id= :idEquipo", idEquipo)            
            values= [idPersonaje, idEquipo[0]]#Variable que contiene las variables en forma de tupla que recibe cursor.execute
            cursor.execute("INSERT INTO Equipamiento VALUES (:idPersonaje, :idEquipo)", values)#Inserta el equipo en la tabla de equipamientos que guarda los equipos de cada jugador
            connection.commit()
            print("Agregado correctamente")
        else:
            print("ID de equipo incorrecto, intenta nuevamente")
            Jugador.add_equipoaPJ()
        
    def del_equipoaPJ(IDPersonaje):#Borra un equipo de un personaje especifico
        idPersonaje= [IDPersonaje]
        cursor.execute("SELECT Equipamiento.equipo_id, Equipos.nombre_equipo FROM Equipamiento JOIN Equipos ON Equipos.equipo_id = Equipamiento.equipo_id WHERE Equipamiento.personaje_id = :idPersonaje", idPersonaje)
        for row in cursor.fetchall():
            print(row)
        print("Indica el id del equipo que quieres eliminar")
        idEquipo= int(input("Elige el equipo de tu personaje:"))
        cursor.execute("SELECT equipo_id FROM Equipamiento WHERE equipo_id= :idEquipo", idEquipo)
        EquipoAuth= cursor.fetchone()
        if EquipoAuth != None:
            cursor.execute("DELETE FROM Equipamiento WHERE equipo_id= :idEquipo", idEquipo)
            connection.commit()
            print("Eliminado correctamente")
        else:
            print("ID de equipo incorrecto, intenta nuevamente")
            Jugador.del_equipoaPJ()

    #Bloque de Modificar poder a un personaje
    def add_poderaPJ(IDPersonaje):#Agrega un poder a un personaje especifico
        idPersonaje= [IDPersonaje]
        cursor.execute("SELECT poder_id, nombre FROM Poder")
        for row in cursor.fetchall():
            print(row)
        print("Indica el id del poder que quieres agregar")
        idPoder= [int(input("Elige el poder para tu personaje:"))]
        cursor.execute("SELECT poder_id FROM Poder WHERE poder_id= :idPoder", idPoder)
        PoderAuth= cursor.fetchone()
        cursor.execute("SELECT raza_id FROM Personaje WHERE personaje_id= :idPersonaje", idPersonaje)
        razaPersonaje= cursor.fetchone()[0]
        cursor.execute("SELECT raza_id FROM Poder WHERE poder_id = :idPoder", idPoder)
        razaPoder= cursor.fetchone()[0]
        if PoderAuth != None and razaPersonaje == razaPoder:
            cursor.execute("SELECT nombre FROM Poder WHERE poder_id= :idPoder", idPoder)
            values= [idPoder[0], idPersonaje[0]]
            cursor.execute("INSERT INTO Poderes_Personaje VALUES (:idPoder, :idPersonaje)", values)
            connection.commit()
            print("Agregado correctamente")
        elif PoderAuth != None and razaPersonaje != razaPoder:
            print("El poder elegido no es de la raza de tu personaje, intenta nuevamente")
            Jugador.add_poderaPJ()
        else:
            print("ID de poder incorrecto, intenta nuevamente")
            Jugador.add_poderaPJ()
        
    def del_poderaPJ(IDPersonaje):#Elimina un poder de un personaje especifico
        idPersonaje= [IDPersonaje]
        cursor.execute("SELECT Poderes_Personaje.poder_id, Poder.nombre FROM Poderes_Personaje JOIN Poder ON Poder.poder_id = Poderes_Personaje.poder_id WHERE Poderes_Personaje.personaje_id = :idPersonaje", idPersonaje)
        for row in cursor.fetchall():
            print(row)
        print("Indica el id del poder que quieres eliminar")
        idPoder= [int(input("Elige el poder de tu personaje:"))]
        cursor.execute("SELECT poder_id FROM Poderes_Personaje WHERE poder_id= :idPoder", idPoder)
        PoderAuth= cursor.fetchone()
        if PoderAuth != None:
            cursor.execute("DELETE FROM Poderes_Personaje WHERE poder_id= :idPoder", idPoder)
            connection.commit()
            print("Eliminado correctamente")
        else:
            print("ID de poder incorrecto, intenta nuevamente")
            Jugador.del_poderaPJ()
 
    #Bloque de Modificar habilidad a un personaje
    def add_habaPJ(IDPersonaje):#Agrega una habilidad a un personaje especifico
        idPersonaje= [IDPersonaje]
        cursor.execute("SELECT habilidad_id, nombre FROM Habilidad")
        for row in cursor.fetchall():
            print(row)
        print("Indica el id de la habilidad que quieres agregar")
        idHabilidad= [int(input("Elige la habilidad para tu personaje:"))]
        cursor.execute("SELECT habilidad_id FROM Habilidad WHERE habilidad_id= :idHabilidad", idHabilidad)
        HabAuth= cursor.fetchone()
        cursor.execute("SELECT raza_id FROM Habilidad WHERE habilidad_id = :idHabilidad", idHabilidad)
        razaHab= cursor.fetchone()[0]
        cursor.execute("SELECT raza_id FROM Personaje WHERE personaje_id= :idPersonaje", idPersonaje)
        razaPersonaje= cursor.fetchone()[0]
        if HabAuth != None and razaPersonaje == razaHab:
            cursor.execute("SELECT nombre FROM Habilidad WHERE habilidad_id= :idHabilidad", idHabilidad)
            values= [idHabilidad[0], idPersonaje[0]]
            cursor.execute("INSERT INTO Habilidades_Personaje VALUES (:idHabilidad, :idPersonaje)", values)
            connection.commit()
            print("Agregado correctamente")
        elif HabAuth != None and razaPersonaje != razaHab:
            print("La habilidad elegida no es de la raza de tu personaje, intenta nuevamente")
            Jugador.add_habaPJ()
        else:
            print("ID de habilidad incorrecto, intenta nuevamente")
            Jugador.add_habaPJ()

    def del_habaPJ(IDPersonaje):#Elimina una habilidad de un personaje especifico
        idPersonaje= [IDPersonaje]
        cursor.execute("SELECT Habilidades_Personaje.habilidad_id, Habilidad.nombre FROM Habilidades_Personaje JOIN Habilidad ON Habilidad.habilidad_id = Habilidades_Personaje.habilidad_id WHERE Habilidades_Personaje.personaje_id = :idPersonaje", idPersonaje)
        for row in cursor.fetchall():
            print(row)
        print("Indica el id de la habilidad que quieres eliminar")
        idHabilidad= [int(input("Elige la habilidad de tu personaje:"))]
        cursor.execute("SELECT habilidad_id FROM Habilidades_Personaje WHERE habilidad_id= :idHabilidad", idHabilidad)
        HabAuth= cursor.fetchone()
        if HabAuth != None:
            cursor.execute("DELETE FROM Habilidades_Personaje WHERE habilidad_id= :idHabilidad", idHabilidad)
            connection.commit()
            print("Eliminado correctamente")
        else:
            print("ID de habilidad incorrecto, intenta nuevamente")
            Jugador.del_habaPJ()
            
    #Bloque de creación de personaje
    def select_starterGear(idPersonaje): #subfuncion para crear personaje, proceso de elección de setup inicial
        #2 habilidades, 1 poder, 1 equipo
        Jugador.add_equipoaPJ(idPersonaje) #1equipo   
        Jugador.add_poderaPJ(idPersonaje) #1poder
        Jugador.add_habaPJ(idPersonaje)#2habilidades
        Jugador.add_habaPJ(idPersonaje)
    
    def crear_personaje():#Todos los pjs inician en lvl 1, ingresar setup inicial. Con esta funcion se genera un formulario para crear un personaje
        idJugador= CurrentUser[0]
        cursor.execute("SELECT COUNT( personaje_id ) FROM Personaje")
        idPersonaje= int(cursor.fetchone()[0]) + 1
        #La ID de personaje se compone de la cantidad de personajes en la lista asi con cada creación 
        #se produce un auto incremento asegurando ID numericas unicas infinitas
        namePersonaje= str(input("Ingrese el nombre del personaje:")) 
        nivel= 1
        status= 1
        idRaza= Jugador.select_raza()[0]
        values= [idPersonaje, namePersonaje, nivel, idJugador, idRaza, status]
        cursor.execute("INSERT INTO Personaje VALUES (:idPersonaje, :namePersonaje, :nivel, :idJugador, :idRaza, :status)", values)
        connection.commit()
        Jugador.select_starterGear(idPersonaje)#Se usa la rutina descrita anteriormente para reducir código y reutilizarla de ser necesario

    #Bloque de visualización de personajes de un jugador        
    def ver_personajesJG(IDJugador):#Muestra los pjs asociados a la ID del Jugador, el ID se consigue con el ID de usuario (son practicamente lo mismo solo que una tabla tiene los datos del tipo de usuario) 
        idJugador= [IDJugador]    
        print("Tus personajes son: \n")
        cursor.execute("SELECT nombre_personaje, nivel FROM Personaje WHERE jugador_id= :idJugador", idJugador)
        for row in cursor.fetchall():
            print(row)
            
    def ver_detallePJ(IDPersonaje):#Ve todo el detalle de un personaje en especifico, equipo, poderes, habilidades, nivel, raza, todo
        idPersonaje= [IDPersonaje]
        print("La información de tu personaje es:")
        cursor.execute("SELECT Personaje.nombre_personaje, Personaje.nivel, Raza.nombre_raza, Estado.nombre_estado FROM Personaje RIGHT JOIN Raza ON Personaje.raza_id= Raza.raza_id RIGHT JOIN Estado ON Personaje.estado_id= Estado.estado_id WHERE Personaje.personaje_id = :idPersonaje", idPersonaje)
        print(cursor.fetchone())
        print("Equipamiento")
        cursor.execute("SELECT Equipos.nombre_equipo FROM Equipamiento JOIN Equipos ON Equipos.equipo_id = Equipamiento.equipo_id WHERE Equipamiento.personaje_id= :idPersonaje", idPersonaje)
        for row in cursor.fetchall():
            print(row)
        print("Poderes")
        cursor.execute("SELECT Poder.nombre FROM Poderes_Personaje JOIN Poder ON Poder.poder_id= Poderes_Personaje.poder_id WHERE Poderes_Personaje.personaje_id= :idPersonaje", idPersonaje)
        for row in cursor.fetchall():
            print(row)
        print("Habilidades")
        cursor.execute("SELECT Habilidad.nombre FROM Habilidades_Personaje JOIN Habilidad ON Habilidades_Personaje.habilidad_id= Habilidad.habilidad_id WHERE Habilidades_Personaje.personaje_id= :idPersonaje", idPersonaje)
        for row in cursor.fetchall():
            print(row)
                       
#FUNCIONES DEL GM
class GM:#Clase GM que contiene todo lo relacionado a ese perfil y permite inicializar la vista GM con sus métodos correspondientes
    def select_raza(): #subfunción para crear seleccionar raza, rutina para simplificar código más adelante
            cursor.execute("SELECT raza_id, nombre_raza FROM Raza")
            for row in cursor.fetchall():
                print(row)
            print("Indica el id de la raza que quieres")
            idRaza= [int(input("Elige la raza:"))]
            cursor.execute("SELECT raza_id FROM Raza WHERE raza_id= :idRaza", idRaza)
            razaAuth= cursor.fetchone()
            if razaAuth != None:
                cursor.execute("SELECT nombre_raza FROM Raza WHERE raza_id= :idRaza", idRaza)
                return(idRaza)
            else:
                print("ID de raza incorrecta, intenta nuevamente")
                GM.select_raza()
                        
    def crear_raza():#metodo para crear una raza y añadirla a la base de datos
        try:#try/except para confirmar que no se generó ningún error
            print("para crear una nueva habilidad ingrese:")
            nombre= input("Nombre de la Raza: ")        
            cursor.execute("SELECT COUNT(raza_id) FROM Raza")
            idRaza= int(cursor.fetchone()[0]) + 1       
            values= [idRaza, nombre]
            cursor.execute("INSERT INTO Raza VALUES (:idRaza, :nombre)", values)
            connection.commit()#siempre el commit en todos los DML para escribir en la base de datos
            print("Creado correctamente")
        except:
            print("Un error ha ocurrido")
                    
    def ver_todosPJ():#Permite al GM ver todos los personajes creados y un resumen de la información relevante de ellos
        print("Los personajes en la partida son:")
        cursor.execute("SELECT Personaje.nombre_personaje, Personaje.nivel, Jugador.nombre_usuario, Raza.nombre_raza, Estado.nombre_estado FROM Personaje LEFT JOIN Jugador ON Jugador.jugador_id= Personaje.jugador_id RIGHT JOIN Raza ON Raza.raza_id= Personaje.raza_id RIGHT JOIN Estado ON Estado.estado_id= Personaje.estado_id")
        for row in cursor.fetchall():
            print(row)
    
    #BLOQUE CRUD PODER    
    def crear_poder():#Permite crear un poder en la bd
        try:
            print("para crear un nuevo poder ingrese:")
            nombre= input("Nombre del Poder: ")
            descrip= input("Breve descripción: ")
            cursor.execute("SELECT COUNT( poder_id ) FROM Poder")
            idPoder= int(cursor.fetchone()[0]) + 1
            raza= GM.select_raza()[0]
            values= [idPoder, nombre, descrip, raza]
            cursor.execute("INSERT INTO Poder VALUES (:idPoder, :nombre, :descrip, :raza)", values)
            connection.commit()
            print("Creado correctamente")
        except:
            print("Un error ha ocurrido")
    
    def edit_poder():#permite modificar un poder
        cursor.execute("SELECT poder_id, nombre FROM Poder")
        for row in cursor.fetchall():
            print(row)
        idpoder= int(input("¿Que poder deseas editar?: "))
        print("(1) Nombre del poder.\n(2) Descripción del poder.\n(3) Raza a la que pertenece.")
        opcion= int(input("¿Que sección deseas editar del poder?: "))
        if opcion ==1:
            try:
                name= input("Ingresa el nuevo nombre del poder:")
                values= [name, idpoder]
                cursor.execute("UPDATE Poder SET nombre= :name WHERE poder_id= :idpoder", values)
                connection.commit()
                print("Nombre cambiado con éxito")
            except:
                print("Ha ocurrido un error")
        elif opcion ==2:
            try:
                descrip= input("Ingrese la nueva descripción del poder:")
                values= [descrip, idpoder]
                cursor.execute("UPDATE Poder SET descripcion= :descrip WHERE poder_id= :idpoder", values)
                connection.commit()
                print("Descripción cambiada con éxito")
            except:
                print("Ha ocurrido un error")
        elif opcion ==3:
            try:
                idraza= GM.select_raza()[0]
                values= [idraza, idpoder]
                cursor.execute("UPDATE Poder SET raza_id= :idraza WHERE poder_id= :idpoder", values)
                connection.commit()
                print("Raza cambiada con éxito")
            except:
                print("Ha ocurrido un error")
        else:
            print("Opción no es correcta")            

#BLOQUE CRUD HABILIDADES
    def crear_habilidad():#permite crear una habilidad en la bd
        try:
            print("para crear una nueva habilidad ingrese:")
            nombre= input("Nombre de la habilidad: ")
            descrip= input("Breve descripción: ")
            cursor.execute("SELECT COUNT( habilidad_id ) FROM Habilidad")
            idHabilidad= int(cursor.fetchone()[0]) + 1
            raza= GM.select_raza()[0]
            values= [idHabilidad, nombre, descrip, raza]
            cursor.execute("INSERT INTO Habilidad VALUES (:idHabilidad, :nombre, :descrip, :raza)", values)
            connection.commit()
            print("Creado correctamente")
        except:
            print("Un error ha ocurrido")
            
    def edit_habilidad():#permite modificar una habilidad de la bd
        cursor.execute("SELECT habilidad_id, nombre FROM Habilidad")
        for row in cursor.fetchall():
            print(row)
        idhab= int(input("¿Que habilidad deseas editar?: "))
        print("(1) Nombre de la habilidad.\n(2) Descripción de la habilidad.\n(3) Raza a la que pertenece.")
        opcion= int(input("¿Que sección deseas editar de la habilidad?: "))
        if opcion ==1:
            try:
                name= input("Ingresa el nuevo nombre de la habilidad:")
                values= [name, idhab]
                cursor.execute("UPDATE Habilidad SET nombre= :name WHERE habilidad_id= :idhab", values)
                connection.commit()
                print("Nombre cambiado con éxito")
            except:
                print("Ha ocurrido un error")
        elif opcion ==2:
            try:
                descrip= input("Ingrese la nueva descripción de la habilidad:")
                values= [descrip, idhab]
                cursor.execute("UPDATE Habilidad SET descripcion= :descrip WHERE habilidad_id= :idhab", values)
                connection.commit()
                print("Descripción cambiada con éxito")
            except:
                print("Ha ocurrido un error")
        elif opcion ==3:
            try:
                idraza= GM.select_raza()[0]
                values= [idraza, idhab]
                cursor.execute("UPDATE Habilidad SET raza_id= :idraza WHERE habilidad_id= :idhab", values)
                connection.commit()
                print("Raza cambiada con éxito")
            except:
                print("Ha ocurrido un error")
        else:
            print("Opción no es correcta")

#BLOQUE CRUD EQUIPO        
    def crear_equipo():#permite crear un equipo nuevo en la bd
        try:
            print("para crear un nuevo equipo ingrese:")
            nombre= input("Nombre del equipo: ")
            descrip= input("Breve descripción: ")
            cursor.execute("SELECT COUNT( equipo_id ) FROM Equipos")
            idEquipo= int(cursor.fetchone()[0]) + 1
            values= [idEquipo, nombre, descrip]
            cursor.execute("INSERT INTO Equipos VALUES (:idEquipo, :nombre, :descrip)", values)
            connection.commit()
            print("Creado correctamente")
        except:
            print("Un error ha ocurrido")
        
    def edit_equipo():#permite modificar equipos en la bd
        cursor.execute("SELECT equipo_id, nombre_equipo FROM Equipos")
        for row in cursor.fetchall():
            print(row)
        idequipo= int(input("¿Que equipo deseas editar?: "))
        print("(1) Nombre del equipo.\n(2) Descripción del equipo.")
        opcion= int(input("¿Que sección deseas editar del equipo?: "))
        if opcion ==1:
            try:
                name= input("Ingresa el nuevo nombre del poder:")
                values= [name, idequipo]
                cursor.execute("UPDATE Equipos SET nombre_equipo= :name WHERE equipo_id= :idequipo", values)
                connection.commit()
                print("Nombre cambiado con éxito")
            except:
                print("Ha ocurrido un error")
        elif opcion ==2:
            try:
                descrip= input("Ingrese la nueva descripción del equipo:")
                values= [descrip, idequipo]
                cursor.execute("UPDATE Equipos SET descripcion= :descrip WHERE equipo_id= :idequipo", values)
                connection.commit()
                print("Descripción cambiada con éxito")
            except:
                print("Ha ocurrido un error")    
        else:
            print("Opción no es correcta") 

#BLOQUE CREAR ESTADO
    def crear_estado():#permite crear estados nuevos en la bd
        try:
            print("para crear un nuevo estado ingrese:")
            nombre= input("Nombre del estado: ")
            descrip= input("Breve descripción: ")
            cursor.execute("SELECT COUNT( estado_id ) FROM Estado")
            idEstado= int(cursor.fetchone()[0]) + 1
            values= [idEstado, nombre, descrip]
            cursor.execute("INSERT INTO Estado VALUES (:idEstado, :nombre, :descrip)", values)
            connection.commit()
            print("Creado correctamente")
        except:
            print("Un error ha ocurrido")

#MAIN SCRIPT
CurrentUser= [0, 0]#la información del usuario inicializada en 0

CurrentUser= User.LogIn()#se inicia mediante primero el inicio de sesión

if CurrentUser[1] == 'PLAYER':#evalua el tipo de usuario actualmente logeado para elegir su vista, si es jugador abre la vista de jugador
    while True:
        print("(1) Ver personajes.\n(2) Ver detalle de  un personaje.\n(3) Crear personajes.\n(4) Agregar habilidad a personaje.\n(5) Quitar habilidad a personaje.\n(6) Agregar poder a personaje.\n(7) Quitar poder a personaje.\n(8) Agregar equipo a personaje.\n(9) Quitar equipo a personaje.\n(10) Salir.")
        opcion= int(input("¿Que te gustaría hacer?: "))
        if opcion ==1:#si desea ver los personajes
            Jugador.ver_personajesJG(CurrentUser[0])
            time.sleep(3)
            print("\n")
        elif opcion ==2:#si desea ver los detalles de un personaje en especifico
            idPersonaje= int(input("Indica el id del personaje que quieres ver: "))
            Jugador.ver_detallePJ(idPersonaje)
            time.sleep(3)
            print("\n")
        elif opcion ==3:#si desea crear un personaje nuevo
            Jugador.crear_personaje()
            time.sleep(3)
            print("\n")
        elif opcion ==4:#si desea añadir una habilidad a un personaje
            idPersonaje= int(input("Indica el id del personaje que quieres agregar una habilidad: "))
            Jugador.add_habaPJ(idPersonaje)
            time.sleep(3)
            print("\n")
        elif opcion ==5:#si desea eliminar una habilidad de un personaje
            idPersonaje= int(input("Indica el id del personaje que quieres quitar una habilidad: "))
            Jugador.del_habaPJ(idPersonaje)
            time.sleep(3)
            print("\n")
        elif opcion ==6:#si desea añadir un poder a un personaje
            idPersonaje= int(input("Indica el id del personaje que quieres agregar un poder: "))
            Jugador.add_poderaPJ(idPersonaje)
            time.sleep(3)
            print("\n")
        elif opcion ==7:#si desea eliminar un poder de un personaje
            idPersonaje= int(input("Indica el id del personaje que quieres quitar un poder: "))
            Jugador.del_poderaPJ(idPersonaje)
            time.sleep(3)
            print("\n")
        elif opcion ==8:#si desea añadir un equipo a un personaje
            idPersonaje= int(input("Indica el id del personaje que quieres agregar un equipo: "))
            Jugador.add_equipoaPJ(idPersonaje)  
            time.sleep(3)
            print("\n")
        elif opcion ==9:#si desea eliminar un equipo de un personaje
            idPersonaje= int(input("Indica el id del personaje que quieres quitar un equipo: "))
            Jugador.del_equipoaPJ(idPersonaje)
            time.sleep(3)
            print("\n")
        elif opcion ==10:#si desea salir del programa
            print("El programa se cerrará automáticamente en 5 segundos.")
            time.sleep(5)#siempre con tiempo de congelado en el programa para permitir la lectura antes del cierre
            break
        else:#si la elección no corresponde a alguna de las alternativas dadas
            print("Elige una opción válida")
            time.sleep(3)
            print("\n") 
    
elif CurrentUser[1] == 'GM':#evalua si el usuario activo es un GM para abrir la vista GM
    while True:#El ciclo permite mantener la aplicación corriendo
        print("(1) Ver personajes.\n(2) Crear raza nueva.\n(3) Crear Poder nuevo.\n(4) Editar un Poder.\n(5) Crear Habilidad nueva.\n(6) Editar una Habilidad.\n(7) Crear Equipo nuevo.\n(8) Editar un equipo.\n(9) Crear Estado nuevo.\n(10) Salir.")
        opcion= int(input("¿Que te gustaría hacer?: "))
        if opcion ==1:
            GM.ver_todosPJ()
            time.sleep(3)
            print("\n")
        elif opcion ==2:
            GM.crear_raza()
            time.sleep(3)
            print("\n")
        elif opcion ==3:
            GM.crear_poder()
            time.sleep(3)
            print("\n")
        elif opcion ==4:
            GM.edit_poder()
            time.sleep(3)
            print("\n")
        elif opcion ==5:
            GM.crear_habilidad()
            time.sleep(3)
            print("\n")
        elif opcion ==6:
            GM.edit_habilidad()
            time.sleep(3)
            print("\n")
        elif opcion ==7:
            GM.crear_equipo()
            time.sleep(3)
            print("\n")
        elif opcion ==8:
           GM.edit_equipo()
           time.sleep(3)
           print("\n")     
        elif opcion ==9:
            GM.crear_estado()
            time.sleep(3)
            print("\n")
        elif opcion ==10:
            print("El programa se cerrará automáticamente en 5 segundos.")
            time.sleep(5)
            break
        else:
            print("Elige una opción válida")
            print("\n")        

else:
    print("Usuario no válido.")
    print("El programa se cerrará automáticamente en 5 segundos.")
    time.sleep(5)

                
cursor.close()#cierra el cursor para recuperar los recursos de la base de datos
