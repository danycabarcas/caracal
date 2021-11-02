from flask import Flask, render_template, request,flash, redirect, jsonify, url_for
import os
import yagmail as yagmail
from datetime import datetime
from werkzeug.utils import secure_filename

# SQL
import sqlite3
from sqlite3.dbapi2 import Row

UPLOAD_FOLDER = 'img_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key=os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']

listado_usuarios = []

listado_publicaciones = []

listado_solicitudes = []

# now = datetime.now()
# format = now.strftime("%m/%d/%Y, %H:%M:%S")
# print(format)

sesion_iniciada = False

# ! Objeto que representa a la info del usuario logeado
usuario_activo = {} 


# ! AUX
def get_info_user(username):
    with sqlite3.connect("Redsocial.db") as conn:
        cursor = conn.cursor()

        usuario = cursor.execute(f"SELECT * FROM Users WHERE usuario = '{username}'")

        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
                for row in cursor.fetchall()]
    
        return data[0]

def get_info_user_by_id(id):
    with sqlite3.connect("Redsocial.db") as conn:
        cursor = conn.cursor()

        usuario = cursor.execute(f"SELECT * FROM Users WHERE id = '{id}'")

        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
                for row in cursor.fetchall()]

        return data[0]

def get_listado_usuarios(rol):
    if rol == "user":
        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            usuario = cursor.execute(f"SELECT * FROM Users WHERE rol = 'user'")

            desc = cursor.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))  
                    for row in cursor.fetchall()]

        return data

    elif rol == "admin":
        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            usuario = cursor.execute(f"SELECT * FROM Users WHERE rol != 'sadmin'")

            desc = cursor.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))  
                    for row in cursor.fetchall()]

        return data

    elif rol == "sadmin":
        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            usuario = cursor.execute(f"SELECT * FROM Users")

            desc = cursor.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))  
                    for row in cursor.fetchall()]

        return data

def get_listado_admins():
    with sqlite3.connect("Redsocial.db") as conn:
        cursor = conn.cursor()

        usuario = cursor.execute(f"SELECT * FROM Users WHERE rol != 'user'")

        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
                for row in cursor.fetchall()]

        return data

def get_listado_publicaciones():
    global listado_publicaciones
    with sqlite3.connect("Redsocial.db") as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Publicaciones ORDER BY fecha DESC")

        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
                for row in cursor.fetchall()]
        
        for publicacion in data:
            publicacion["userinfo"] = get_info_user_by_id(publicacion["user_id"])
            publicacion["likes"] = convert(publicacion["likes"])

        return data

def get_publicaciones_usuario(user_id):
    with sqlite3.connect("Redsocial.db") as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM Publicaciones WHERE user_id = '{user_id}' ORDER BY fecha DESC")

        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
                for row in cursor.fetchall()]

        for publicacion in data:
            publicacion["userinfo"] = get_info_user_by_id(publicacion["user_id"])
            publicacion["likes"] = convert(publicacion["likes"])


        return data

def get_mensajes_usuario(user_id):
    with sqlite3.connect("Redsocial.db") as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM Mensajes WHERE de = '{user_id}' OR para= '{user_id}' ORDER BY fecha_envio")

        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
                for row in cursor.fetchall()]

        return data

def get_amigos_usuario(user_id):
    with sqlite3.connect("Redsocial.db") as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM Amigos WHERE id_user_a = '{user_id}' or id_user_b = '{user_id}' ORDER BY fecha_solicitud DESC")

        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
                for row in cursor.fetchall()]

        return data

def get_amigos_activos_usuario(user_id):
    with sqlite3.connect("Redsocial.db") as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM Amigos WHERE (id_user_a = '{user_id}' or id_user_b = '{user_id}') and estado='activo' ")

        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
                for row in cursor.fetchall()]

        return data

def get_solicitudes_usuario(user_id):
    listado_solicitudes = get_amigos_usuario(user_id)

    for solicitud in listado_solicitudes:
        solicitud["id_user_a"] = get_info_user_by_id(solicitud["id_user_a"])
        solicitud["id_user_b"] = get_info_user_by_id(solicitud["id_user_b"])
    
    return listado_solicitudes

def get_politicas_privacidad():
    with sqlite3.connect("Redsocial.db") as conn:
        cursor = conn.cursor()

        usuario = cursor.execute("SELECT * FROM Politicas")

        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
                for row in cursor.fetchall()]

        return data[0]

def convert(string):
    if len(string) > 0:
        li = list(string.split(" "))
        return li
    else:
        return string

# ! PRUEBA - LISTADO DE USUARIOS
@app.route('/listado_usuarios')
def listado():
    return jsonify(listado_usuarios) 

# ! PRUEBA - LISTADO DE PUBLICACIONES
@app.route('/listado_publicaciones')
def listado_p():
    return jsonify(listado_publicaciones) 

# ! REGISTRO Y LOGIN
@app.route('/')#listo
def index():
    return redirect('/login')

@app.route('/registro',methods=["GET","POST"])#listo
def registro_publico():
    global sesion_iniciada
    if request.method == "GET":
        return render_template('registro.html')
    else:
        global listado_usuarios
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")
        rol = "user"
        url_foto_perfil = "img_fotos_perfil/user1.jpg"
        estado = "activo"

        if password != password_confirmation:
            return render_template('registro.html', error = "Las contraseñas no coinciden")

        with sqlite3.connect("Redsocial.db") as conn:
            cur = conn.cursor()

            cur.execute("INSERT INTO Users (rol, nombre, usuario, email, password, url_foto_perfil, estado) VALUES (?,?,?,?,?,?,?)", (rol, nombre, nombre, email, password, url_foto_perfil, estado))

            conn.commit()
        
        for usuario in get_listado_usuarios("user"):
            if usuario["usuario"] != get_info_user(nombre)["usuario"]:
                current_user = get_info_user(nombre)
                with sqlite3.connect("Redsocial.db") as conn:
                    cur = conn.cursor()

                    cur.execute("INSERT INTO Amigos (id_user_a, id_user_b, estado, fecha_solicitud) VALUES (?,?,?,?)", (current_user["id"], usuario["id"], "rechazado", datetime.now()))

                    conn.commit()

        return redirect('/')

@app.route('/login',methods=["GET","POST"])#listo
def login():
    global sesion_iniciada, usuario_activo

    if request.method == "GET":
        return render_template('login.html')
    else:
        credenciales_correctas = False
        email = request.form.get("email")
        password = request.form.get("password")

        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            usuario = cursor.execute(f"SELECT * FROM Users WHERE email = '{email}' AND password= '{password}' AND estado = 'activo'")

            desc = cursor.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))  
                    for row in cursor.fetchall()]
        
        if len(data) > 0:
            usuario = data[0]
            usuario_activo = usuario
            sesion_iniciada = True

            if usuario["rol"] == 'user':
                return redirect('/home')
            elif usuario["rol"] == 'admin':
                return redirect('/home_admin')
            elif usuario["rol"] == 'sadmin':
                return redirect('/home_sadmin')
        else:
            return render_template('login.html', error = "Credenciales incorrectas")

@app.route('/salir',methods=["GET"])#listo
def salir():
    global sesion_iniciada, usuario_activo
    sesion_iniciada = False
    usuario_activo = {}
    return redirect('/')  

@app.route('/recuperar_credenciales',methods=["GET","POST"])#listo
def recuperar_credenciales():
    if request.method == "GET":
        return render_template('forgot-password.html')
    else:
        global listado_usuarios
        email = request.form.get("email")
        password = ''

        for usuario in listado_usuarios:
            if usuario['email'] == email:
                password = usuario['password']

        if password == '':
            return render_template('forgot-password.html', mensaje="Usuario no encontrado")
        else:
            return render_template('forgot-password.html', mensaje="Su contraseña es: " + password)

# ! USUARIO FINAL
@app.route('/home',methods=["GET", "POST"])#listo
def dashboard_usuarios():
    if request.method == "GET":
        global sesion_iniciada, usuario_activo, listado_publicaciones

        listado_publicaciones = get_listado_publicaciones()

        listado_amigos = get_amigos_activos_usuario(usuario_activo["id"])

        if sesion_iniciada:
            return render_template('index.html', usuario_activo = usuario_activo, listado_publicaciones = listado_publicaciones, listado_amigos=listado_amigos)
        else:
            return redirect('/')

@app.route('/perfil_edit',methods=["GET","POST"])#listo
def perfil_edit():
    global sesion_iniciada, usuario_activo, listado_usuarios
    if request.method == "GET":
   
        if sesion_iniciada:
            return render_template('perfil-editar.html', usuario_activo = usuario_activo)
        else:
            return redirect('/')
    elif request.method == "POST":
        id_usuario_activo = usuario_activo["id"]
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")

        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            usuario = cursor.execute(f"UPDATE Users SET nombre = '{nombre}', email= '{email}', password= '{password}' WHERE id='{id_usuario_activo}'")
        
        return redirect('/feed/' + usuario_activo['usuario'])

@app.route('/feed/<username>',methods=["GET","POST"])
def perfil(username):
    if request.method == "GET":
        global sesion_iniciada, usuario_activo, listado_usuarios, listado_publicaciones
        
        id_user_activo = usuario_activo["id"]

        # * DETECTAR SI ES EL MISMO PERFIL DEL USUARIO LOGEADO
        perfil_propio = False
        if username == usuario_activo['usuario']:
            perfil_propio = True

        listado_amigos = get_amigos_activos_usuario(get_info_user(username)["id"])

        # estado_solicitud_amistad = {}
        # if not perfil_propio:
        #     listado_solicitudes = get_solicitudes_usuario(get_info_user(username)["id"])

        #     for solicitud in listado_solicitudes:
        #         if solicitud["id_user_a"]["id"] == id_user_activo or solicitud["id_user_b"]["id"] == id_user_activo:
        #             estado_solicitud_amistad = solicitud
        #             break
        
        usuario_encontrado = get_info_user(username)
        
        publicaciones_usuario_encontrado = get_publicaciones_usuario(usuario_encontrado["id"])

        if sesion_iniciada:
            return render_template('feed.html', usuario_activo = usuario_activo, publicaciones_usuario_encontrado=publicaciones_usuario_encontrado, usuario_encontrado=usuario_encontrado, listado_publicaciones = listado_publicaciones, perfil_propio=perfil_propio, listado_amigos=listado_amigos)
        else:
            return redirect('/')

@app.route('/perfil_amigos',methods=["GET", "POST"])#listo
def perfil_amigos():
    global sesion_iniciada, usuario_activo


    return render_template('perfil-amigos.html', usuario_activo=usuario_activo)

@app.route('/subir_publicacion', methods=["GET", "POST"])
def subir_publicacion():
    global sesion_iniciada, usuario_activo, listado_publicaciones

    if request.method == "GET":
        return render_template('subir-imagen.html', usuario_activo=usuario_activo)
    
    if request.method == "POST":
        descripcion = request.form.get("descripcion")
        file = request.files['file']
        file.save("static/img_publicaciones/"+file.filename)

        user_id = usuario_activo["id"]
        fecha = datetime.now()
        img_url = "img_publicaciones/"+file.filename
        likes = ""
        comentarios = ""

        with sqlite3.connect("Redsocial.db") as conn:
            cur = conn.cursor()

            cur.execute("INSERT INTO Publicaciones (descripcion, user_id, fecha, img_url, likes, comentarios) VALUES (?,?,?,?,?,?)", (descripcion, user_id, fecha, img_url, likes, comentarios))

            conn.commit()

        return redirect("/feed/" + usuario_activo['usuario'])

@app.route('/like_publicacion',methods=["POST"])#listo
def like_publicacion():
    global sesion_iniciada, usuario_activo

    if sesion_iniciada == False:
        return redirect('/feed/'+usuario_activo['usuario'])
    else:
        id_publicacion = request.form.get("id_publicacion")
        id_user = usuario_activo["id"]

        publicacion_likes = ""
        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM Publicaciones WHERE id='{id_publicacion}'")

            desc = cursor.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))  
                for row in cursor.fetchall()]
            
            publicacion_likes += data[0]["likes"]

        if publicacion_likes == "":
            nuevos_likes = str(id_user)
        else:
            if str(id_user) in convert(publicacion_likes):
                nuevos_likes = publicacion_likes.replace(str(id_user), "")
            else:
                nuevos_likes = publicacion_likes + " " + str(id_user)

        nuevos_likes = nuevos_likes.strip()
        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            cursor.execute(f"UPDATE Publicaciones SET likes = '{nuevos_likes}' WHERE id='{id_publicacion}'")

        return redirect("/home")
        # return redirect('/feed/'+usuario_activo['usuario'])

@app.route('/mensajes',methods=["GET"])#listo
def chat():
    global usuario_activo, listado_usuarios

    listado_amigos = get_amigos_activos_usuario(usuario_activo["id"])

    user_id = usuario_activo["id"]
    listado_mensajes_usuario = get_mensajes_usuario(user_id)

    listado_remitentes_id = []
    for mensaje in listado_mensajes_usuario:
        if mensaje["de"] != user_id:
            if mensaje["de"] not in listado_remitentes_id:
                listado_remitentes_id.append(mensaje["de"])
        if mensaje["para"] != user_id:
            if mensaje["para"] not in listado_remitentes_id:
                listado_remitentes_id.append(mensaje["para"])
    
    listado_remitentes = []
    for id in listado_remitentes_id:
        listado_remitentes.append(get_info_user_by_id(id))

    # return jsonify(listado_remitentes)

    return render_template('chat.html', usuario_activo=usuario_activo, listado_mensajes_usuario=listado_mensajes_usuario, listado_remitentes=listado_remitentes, listado_amigos=listado_amigos)  

@app.route('/buscar_usuario_mensaje', methods=["GET", "POST"])
def buscar_usuario():
    global usuario_activo

    if request.method == "GET":
        return render_template('chat-buscar-usuario.html', usuario_activo=usuario_activo)
    
    elif request.method == "POST":
        id_user_activo = usuario_activo["id"]
        username = request.form.get("username")

        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            usuario = cursor.execute(f"SELECT * FROM Users WHERE usuario LIKE '%{username}%' AND rol='user' AND id!='{id_user_activo}'")

            desc = cursor.description
            column_names = [col[0] for col in desc]
            data = [dict(zip(column_names, row))  
                    for row in cursor.fetchall()]

            return render_template('chat-buscar-usuario.html', usuario_activo=usuario_activo, listado_usuarios=data)

@app.route('/enviar_mensaje',methods=["POST"])
def enviar_mensaje():
    global usuario_activo

    id_remitente = request.form.get("id_remitente")
    id_destinatario = request.form.get("id_destinatario")
    mensaje = request.form.get("mensaje")
    fecha_envio = datetime.now()

    with sqlite3.connect("Redsocial.db") as conn:
        cur = conn.cursor()

        cur.execute("INSERT INTO Mensajes (de, para, mensaje, fecha_envio) VALUES (?,?,?,?)", (int(id_remitente), int(id_destinatario), mensaje, fecha_envio))

        conn.commit()

    return redirect("/mensajes") 

@app.route('/comentarios',methods=["GET"])#listo
def comentarios():
    return render_template('comentarios.html')  

@app.route('/solicitud_amigos',methods=["GET"])#listo
def solicitudamigos():
    global sesion_iniciada, usuario_activo

    if request.method == "GET":

        listado_amigos = get_amigos_activos_usuario(usuario_activo["id"])
        listado_solicitudes = get_amigos_usuario(usuario_activo["id"])

        for solicitud in listado_solicitudes:
            solicitud["id_user_a"] = get_info_user_by_id(solicitud["id_user_a"])
            solicitud["id_user_b"] = get_info_user_by_id(solicitud["id_user_b"])

        return render_template('solicitud-amigos.html',usuario_activo=usuario_activo, listado_solicitudes=listado_solicitudes, listado_amigos=listado_amigos)   

@app.route('/responder_solicitud_amistad',methods=["POST"])#listo
def responder_solicitud_amigos():
    global sesion_iniciada, usuario_activo

    id_usuario_activo = usuario_activo["id"]
    id_solicitud = request.form.get("id_solicitud")
    respuesta = request.form.get("respuesta_solicitud")
    id_usuario_b = request.form.get("id_usuario_b")

    with sqlite3.connect("Redsocial.db") as conn:
        cursor = conn.cursor()

        usuario = cursor.execute(f"UPDATE Amigos SET estado = '{respuesta}' WHERE id='{id_solicitud}'")
    
    if respuesta == "pendiente":
        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            cursor.execute(f"UPDATE Amigos SET id_user_a = '{id_usuario_activo}', id_user_b= '{id_usuario_b}' WHERE id='{id_solicitud}'")
        
    return redirect("/solicitud_amigos")  

@app.route('/politicas_privacidad',methods=["GET"])#listo
def politicas_privacidad():
    politicas = get_politicas_privacidad()["texto"]
    # return jsonify(politicas)
    return render_template('politicas_privacidad.html', politicas_texto=politicas)

# ! ADMIN
@app.route('/home_admin',methods=["GET"])#listo
def home_admin():
    global usuario_activo, listado_publicaciones

    listado_publicaciones = get_listado_publicaciones()

    return render_template('admin/home_admin.html', usuario_activo=usuario_activo, listado_publicaciones=listado_publicaciones)

@app.route('/lista_usuarios_admin',methods=["GET", "POST"])#listo
def lista_usuarios_admin():
    global usuario_activo, listado_usuarios

    listado_usuarios = get_listado_usuarios("admin")

    return render_template('admin/lista_usuarios_admin.html', usuario_activo=usuario_activo, listado_usuarios=listado_usuarios)

@app.route('/usuario_edit_admin/<username>',methods=["GET","POST"])#listo
def editar_usuario_admin(username):
    global usuario_activo, sesion_iniciada

    if not sesion_iniciada or usuario_activo['rol'] == "user":
        return redirect('/')
    
    if request.method == "GET":
        usuario_editar = get_info_user(username)

        return render_template('admin/editar-usuario-admin.html', usuario_activo=usuario_activo, usuario_editar=usuario_editar)   
    elif request.method == "POST":
        estado = request.form.get("estado")
        id_user = get_info_user(username)["id"]

        rol = request.form.get("rol")

        if rol == "user":
            with sqlite3.connect("Redsocial.db") as conn:
                cursor = conn.cursor()

                usuario = cursor.execute(f"UPDATE Users SET estado= '{estado}' WHERE id='{id_user}'")
        
        elif rol == "admin":
            nombre = request.form.get("nombre")
            password = request.form.get("password")
            with sqlite3.connect("Redsocial.db") as conn:
                cursor = conn.cursor()

                usuario = cursor.execute(f"UPDATE Users SET nombre='{nombre}', password='{password}' WHERE id='{id_user}'")

        
        
        return redirect('/lista_usuarios_admin')

# ! ADMIN - SUPERADMIN
@app.route('/usuario_eliminar/<username>',methods=["POST"])#listo
def eliminar_usuario(username):
    global usuario_activo, listado_usuarios, sesion_iniciada

    if not sesion_iniciada or usuario_activo['rol'] == "user":
        return redirect('/')

    if request.method == "POST":
        user_id = get_info_user(username)["id"]
        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            usuario = cursor.execute(f"DELETE FROM Users WHERE id='{user_id}'")


        if usuario_activo['rol'] == "admin":
            return redirect('/lista_usuarios_admin')
        if usuario_activo['rol'] == "sadmin":
            return redirect('/lista_usuarios')

@app.route('/eliminar_publicacion/<id>', methods=["POST"])
def eliminar_publicacion(id):
    global usuario_activo, sesion_iniciada

    if not sesion_iniciada or usuario_activo['rol'] == "user":
        return redirect('/')

    if request.method == "POST":
        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            usuario = cursor.execute(f"DELETE FROM Publicaciones WHERE id='{id}'")

        if usuario_activo["rol"] == "admin":
            return redirect('/home_admin')
        if usuario_activo["rol"] == "sadmin":
            return redirect('/home_sadmin')
            
# ! SUPERADMIN
@app.route('/dashboard_sadmin',methods=["GET"])#listo
def dashboard_sadmin():
    global usuario_activo, lista_usuarios

    listado_admins = get_listado_admins()

    return render_template('sadmin/dashboard_sadmin.html', usuario_activo=usuario_activo, listado_admins=listado_admins)

@app.route('/home_sadmin',methods=["GET"])#listo
def home_sadmin():
    global usuario_activo, listado_publicaciones

    listado_publicaciones = get_listado_publicaciones()

    return render_template('sadmin/home_sadmin.html', usuario_activo=usuario_activo, listado_publicaciones=listado_publicaciones)

@app.route('/lista_usuarios',methods=["GET", "POST"])#listo
def lista_usuarios():
    global usuario_activo, listado_usuarios

    listado_usuarios = get_listado_usuarios(usuario_activo["rol"])

    return render_template('sadmin/lista_usuarios_sadmin.html', usuario_activo=usuario_activo, listado_usuarios=listado_usuarios)

@app.route('/usuario_edit/<username>',methods=["GET","POST"])#listo
def editar_usuario(username):
    global usuario_activo, listado_usuarios, sesion_iniciada

    if not sesion_iniciada or usuario_activo['rol'] == "user":
        return redirect('/')
    
    if request.method == "GET":
        usuario_editar = get_info_user(username)
        return render_template('sadmin/editar-usuario-sadmin.html', usuario_activo=usuario_activo, usuario_editar=usuario_editar)   

    elif request.method == "POST":
        nombre = request.form.get("nombre")
        rol = request.form.get("rol")
        estado = request.form.get("estado")
        password = request.form.get("password")

        id_usuario = get_info_user(username)["id"]

        # return jsonify({"nombre":nombre, "rol":rol, "estado":estado, "password":password, "id_usuario":id_usuario})

        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            usuario = cursor.execute(f"UPDATE Users SET nombre = '{nombre}', rol= '{rol}', password= '{password}',estado= '{estado}'  WHERE id='{id_usuario}'")
        
        return redirect('/lista_usuarios')

@app.route('/politicas_edit',methods=["GET","POST"])#listo
def editar_politicas():
    global usuario_activo

    if request.method == "GET":
        politicas = get_politicas_privacidad()["texto"]

        return render_template('sadmin/politicasprivacidad_edit.html', usuario_activo=usuario_activo, politicas_privacidad=politicas)    
    if request.method == "POST":
        politicas = request.form.get("politicas")

        with sqlite3.connect("Redsocial.db") as conn:
            cursor = conn.cursor()

            usuario = cursor.execute(f"UPDATE Politicas SET texto='{politicas}' WHERE id='1'")

        return redirect('/politicas_edit')

@app.route('/nuevo_usuario',methods=["GET", "POST"])#listo
def nuevo_usuario():
    global usuario_activo, listado_usuarios, sesion_iniciada

    if not sesion_iniciada or usuario_activo['rol'] != "sadmin":
        return redirect('/')
    
    if request.method == "GET":
        return render_template('sadmin/crear-usuario-sadmin.html', usuario_activo=usuario_activo)
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        rol = request.form.get("rol")

        url_foto_perfil = "img_fotos_perfil/user4.jpg"
        estado = "activo"

        with sqlite3.connect("Redsocial.db") as conn:
            cur = conn.cursor()

            cur.execute("INSERT INTO Users (rol, nombre, usuario, email, password, url_foto_perfil, estado) VALUES (?,?,?,?,?,?,?)", (rol, nombre, nombre, email, password, url_foto_perfil, estado))

            conn.commit()

        listado_usuarios.append(nuevo_usuario)

        return redirect('/dashboard_sadmin')




# ! SIN CLASIFICAR
@app.route('/confirmacion_registro',methods=["GET","POST"])#listo
def confirmacion_registro():
    return render_template('registro-confirmacion.html')     

if __name__ =="__main__":
    app.run(debug=True)
    