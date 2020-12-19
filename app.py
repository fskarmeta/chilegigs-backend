import datetime
import json
from flask import Flask, render_template, request, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from models import db, Roles, Account, DjProfile, ClientProfile, ObjetosGlobales, Gig
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_raw_jwt
from flask_mail import Mail, Message
from os import access, environ
import config


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object(config.Base)
db.init_app(app)
jwt = JWTManager(app)
mail = Mail(app)
blacklist = set()
Migrate(app, db)
CORS(app)
manager = Manager(app)
manager.add_command("db", MigrateCommand)

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


@app.route('/')
def main():
    return render_template('index.html')

## Recuperar contraseña
@app.route('/recover/password', methods=['PUT'])
def send_password():
    email = request.json.get("email", None)
    if email:
        account = Account.query.filter_by(email=email).first()
        if account:
            expires = datetime.timedelta(hours=3)
            access_token = create_access_token(identity=account.username, expires_delta=expires)
            msg = Message("Recuperar contraseña", recipients=[email])
            msg.html = f"<h1>Hola {account.username}</h1><br><h3>Petición para cambiar contraseña aceptada</h3><br><h4>Pincha <a href='http://localhost:3000/recover/{access_token}'> aquí</a> para generar tu nueva contraseña</h4>"
            mail.send(msg)
            return jsonify({"exito": "Email enviado"}), 200
            # data = {
            #         "token_de_acceso": access_token,
            #     }
        else:
            return jsonify({"msg": "Email no existe en nuestra base de datos"}), 401
    else:
        return jsonify({"msg": "Tienes que ingresar un email"}), 401

############################ OBJETOS GLOBALES #########################################

## recibir objeto globales
@app.route('/objetos', methods=['GET'])
def send():
    objetosglobales = ObjetosGlobales.query.first()
    return jsonify(objetosglobales.serialize()), 201

##actualizar objeto Home
@app.route('/objetos/home', methods=['PUT'])
@jwt_required
def getHome():
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    home = request.get_json()
    print(home)
    if account:
        if account.role_id == 1:
            objetosglobales = ObjetosGlobales.query.first()
            objetosglobales.home = json.dumps(home)
            objetosglobales.update()
            return jsonify({"msg": "objeto home actualizado"}), 201
        else: 
            return jsonify({"msg": "Usuario no tiene permiso para hacer estos cambios"}),400
    else:
        return json({"msg": "No existe tal cuenta de usuario"}), 400


##actualizar objeto Requisitos
@app.route('/objetos/requisitos', methods=['PUT'])
@jwt_required
def getReq():
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    requisitos = request.get_json()
    if account:
        if account.role_id == 1:
            objetosglobales = ObjetosGlobales.query.first()
            objetosglobales.requisitos = json.dumps(requisitos)
            objetosglobales.update()
            return jsonify({"msg": "objeto requisitos actualizado"}), 201
        else: 
            return jsonify({"msg": "Usuario no tiene permiso para hacer estos cambios"}),400
    else:
        return json({"msg": "No existe tal cuenta de usuario"}), 400


############################ CUENTA #################################

##Crear cuenta e inicializar perfil
@app.route('/user/register', methods=['POST', 'DELETE'])
def register():
    if request.method == 'POST':
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        email = request.json.get("email", None)
        role = request.json.get("role", None)

        if not username:
            return jsonify({"msg": "Se requiere nombre de usuario"}), 400
        if not password:
            return jsonify({"msg": "Se requiere una contraseña"}), 400
        if not email:
            return jsonify({"msg": "Se requiere un correo electronico"}), 400

        user = Account.query.filter_by(username=username).first()
        if user:
            return jsonify({"msg": "Nombre de usuario ya existe"}), 400


        user_email = Account.query.filter_by(email=email).first()
        if user_email:
            return jsonify({"msg": "Correo electronico ya existe"}), 400

        account = Account()
        account.username = username
        account.email = email
        account.password = generate_password_hash(password)
        account.role_id = role
        account.save()

        if account.role_id == 2:
            dj = DjProfile()
            dj.dj_id = account.id
            dj.username = account.username
            dj.artista = ""
            dj.ciudad = ""
            dj.status = "inactive"
            dj.pais = ""
            dj.imagen = ""
            dj.generos = json.dumps([])
            dj.servicios = json.dumps([])
            dj.tecnica = ""
            dj.requisitos = json.dumps({"equipos":[],"escenario":[],"foodanddrinks":[]})
            dj.save()
        if account.role_id == 3:
            client = ClientProfile()
            client.client_id = account.id
            client.nombre = ""
            client.apellido = ""
            client.rut = ""
            client.nacionalidad = ""
            client.ciudad = ""
            client.pais = ""
            client.imagen = ""
            client.status = "inactive"
            client.save()

        return jsonify(account.serialize()), 201

    if request.method == 'DELETE':
        username = request.json.get("username", None)
        password = request.json.get("password", None)

        if not username:
            return jsonify({"msg": "Nombre de usuario es requerido"}), 400
        if not password:
            return jsonify({"msg": "Password es requerido"}), 400

        account = Account.query.filter_by(username=username).first()
        if account:
            if check_password_hash(account.password, password):
                account.delete()
                return jsonify({"msg": "Cuenta ha sido borrada exitosamente"})
            else:
                return jsonify({"msg": "Clave no coincide con usuario"})
        else:
           return jsonify({"msg": "No existe tal cuenta"}) 

## Borrar cuenta de usuario desde un usuario
@app.route('/user/delete', methods=['DELETE'])
@jwt_required
def deleteAccount():
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    password = request.json.get("password")

    if account.role_id != 1:
        if  check_password_hash(account.password, password):
            if account.role_id == 2:
                profile = DjProfile.query.filter_by(dj_id=account.id).first()
                profile.delete()
                account.delete()
                return jsonify({"success": "Cuenta y perfil han sido borrados exitosamente"}), 201
            if account.role_id == 3:
                profile = ClientProfile.query.filter_by(client_id=account.id).first()
                profile.delete()
                account.delete()
                return jsonify({"success": "Cuenta y perfil han sido borrados exitosamente"}), 201
        else:
            return jsonify({"msg": "Contraseña incorrecta"}), 401
    else:
        return jsonify({"msg": "No se pudo encontrar a este usuario"}), 401


####################### CUENTAS DESDE ADMIN ########################################

## Admin borra cuenta de usuario
@app.route('/admin/accounts/delete/<int:id>', methods=['DELETE'])
@jwt_required
def deleteAccountfromAdmin(id):
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    if account.role_id == 1:
            accountToDelete = Account.query.filter_by(id=id).first()
            if accountToDelete.role_id == 2:
                profileToDelete = DjProfile.query.filter_by(dj_id=id).first()
                profileToDelete.delete()
                accountToDelete.delete()
                return jsonify({"success": "Cuenta y perfil han sido borrados exitosamente"}), 201
            if accountToDelete.role_id == 3:
                profileToDelete = ClientProfile.query.filter_by(client_id=id).first()
                profileToDelete.delete()
                accountToDelete.delete()
                return jsonify({"success": "Cuenta y perfil han sido borrados exitosamente"}), 201
    else:
        return jsonify({"msg": "Usuario no tiene los permisos para ejercer esta acción"}), 401


##Traer todas las cuentas exístentes para el admin
@app.route('/admin/accounts', methods=['GET'])
@jwt_required
def getAllAccounts():
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    if account.role_id == 1:
        accounts = Account.query.all()
        accounts = list(map(lambda account: account.serialize(), accounts))
        return jsonify(accounts), 201
    else:
        return jsonify({"msg": "Solamente el dj puede acceder a esta información"}), 401

##Traer todas las cuentas de CLIENTE exístentes para el admin
@app.route('/admin/accounts/clients', methods=['GET'])
@jwt_required
def getAllClientsAccounts():
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    if account.role_id == 1:
        accounts = Account.query.filter_by(role_id=3).all()
        accounts = list(map(lambda account: account.serialize(), accounts))
        return jsonify(accounts), 201
    else:
        return jsonify({"msg": "Solamente el dj puede acceder a esta información"}), 401

##Traer todas las cuentas de DJ exístentes para el admin
@app.route('/admin/accounts/djs', methods=['GET'])
@jwt_required
def getAllDjsAccounts():
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    if account.role_id == 1:
        accounts = Account.query.filter_by(role_id=2).all()
        accounts = list(map(lambda account: account.serialize(), accounts))
        return jsonify(accounts), 201
    else:
        return jsonify({"msg": "Solamente el dj puede acceder a esta información"}), 401

##Traer Info general para Admin
@app.route('/admin/accounts/info', methods=['GET'])
@jwt_required
def getInfo():
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    if account.role_id == 1:
        djAmount = Account.query.filter_by(role_id=2).count()
        clientAmount = Account.query.filter_by(role_id=3).count()
        lastTenDjs = Account.query.filter_by(role_id=2).order_by(Account.id.desc()).limit(10)
        lastDjs = list(map(lambda account: account.serialize(), lastTenDjs))
        lastTenClients = Account.query.filter_by(role_id=3).order_by(Account.id.desc()).limit(10)
        lastClients = list(map(lambda account: account.serialize(), lastTenClients))
        # clientsAccountsList = list(map(lambda account: account.serialize(), clientsAccounts))


        data = {
            "djs": djAmount,
            "clients": clientAmount,
            "lastdjs": lastDjs,
            "lastclients": lastClients
        }
        return jsonify(data), 201
    else:
        return jsonify({"msg": "Solamente el dj puede acceder a esta información"}), 401


#################### CONTRASEÑA USUARIO #####################################

## Actualizar contraseña de usuario al recuperar constraseña
@app.route('/user/update/password', methods=['PUT'])
@jwt_required
def updatePassword():
    newpassword = request.json.get("password")
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    if account:
        account.password = generate_password_hash(newpassword)
        account.update()
        return jsonify(account.serialize()), 201
    else:
        return jsonify({"msg": "Tienes que volver a logearte"}), 401

## Actualizar contraseña de usuario desde cuenta
@app.route('/account/update/password', methods=['PUT'])
@jwt_required
def updatePasswordFromAccount():
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    oldpassword = request.json.get("old_password")
    newpassword = request.json.get("new_password")
    if account:
        if  check_password_hash(account.password, oldpassword):
            account.password = generate_password_hash(newpassword)
            account.update()
            return jsonify({"success": "Contraseña ha sido actualizada exitosamente"}), 201
        else:
            return jsonify({"msg": "Clave antigua incorrecta"}), 401
    else:
        return jsonify({"msg": "No se pudo encontrar a este usuario"}), 401

# ## Actualizar Email de cuenta de usuario (validar que no exista ya)
# @app.route('/user/update/email', methods=['PUT'])
# @jwt_required
# def updateEmail():
#     newemail = request.json.get("email")
#     username = get_jwt_identity()
#     account = Account.query.filter_by(username=username).first()
#     email = Account.query.filter_by(email=newemail).first()
#     if account:
#         if email:
#             return jsonify({"msg": "Email ya esta en uso"})
#         else:
#             account.email = newemail
#             account.update()
#             return jsonify(account.serialize())
#     else:
#         return jsonify({"msg": "Tienes que volver a logearte"}), 401


######################### LOGIN #############################

#Chequear token del store
@app.route('/user/autologin', methods=['POST'])
@jwt_required
def autologin():
        username = get_jwt_identity()
        auth_header = request.headers.get('Authorization')
        account = Account.query.filter_by(username=username).first()
        if account:
            client = ClientProfile.query.filter_by(client_id=account.id).first()
            dj = DjProfile.query.filter_by(dj_id=account.id).first()
            if client:
                data = {
                 "cuenta": account.serialize(),
                 "perfil": client.serialize(),
                 "access_token": auth_header 
                }
                return jsonify(data), 200
            if dj:
                data = {
                 "cuenta": account.serialize(),
                 "perfil": dj.serialize(),
                 "access_token": auth_header
                }
                return jsonify(data), 200
            else:
                return jsonify({"msg": "Admin tiene que ingresar manualmente"}), 400
        else:
            return jsonify({"msg": "Usuario no existe o token expiro."}), 401

#login usuario
@app.route('/user/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if not username:
            return jsonify({"msg": "Se requiere un nombre de usuario"}), 400
        if not password:
            return jsonify({"msg": "Se requiere una contraseña"}), 400      
    
        account = Account.query.filter_by(username=username).first()
        if not account:
                return jsonify({"msg": "Clave o usuario incorrecto"}), 401

        if not check_password_hash(account.password, password):
                return jsonify({"msg": "Clave o usuario incorrecto"}), 401

        expires = datetime.timedelta(days=3)
        access_token = create_access_token(identity=account.username, expires_delta=expires)
        data = {
            "token_de_acceso": access_token,
            "cuenta": account.serialize(),
            "expira_en": expires.total_seconds()*1000

        }

        return jsonify(data), 200


## Logout
@app.route('/user/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    print(jti)
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200


############################### PERFILES ######################################

## actualizar perfil de DJ o de Cliente
@app.route('/profile', methods=['PUT'])
@jwt_required
def profile():
    if request.method == 'PUT':
        username = get_jwt_identity()
        account = Account.query.filter_by(username=username).first()
        if not account:
            return jsonify({"msg": "Cuenta no tiene permisos para actualizar un perfil"})
        if account.role_id == 2:
            djprofile = DjProfile.query.filter_by(dj_id=account.id).first()
            if not djprofile:
                return jsonify({"msg": "Cuenta de dj no tiene perfil asociado"})
            else:
                artista = request.json.get("artista", None)
                ciudad = request.json.get("ciudad", None)
                pais = request.json.get("pais", None)
                status = request.json.get("status", None)
                imagen = request.json.get("imagen", None)
                mixcloud = request.json.get("mixcloud")
                soundcloud = request.json.get("soundcloud")
                instagram = request.json.get("instagram")
                generos = request.json.get("generos", None)
                servicios = request.json.get("servicios", None)
                tecnica = request.json.get("tecnica", None)
                agregar_cancion = request.json.get("agregar_cancion")
                url_cancion = request.json.get("url_cancion")
                biografia = request.json.get("biografia")
                viajes = request.json.get("viajes")
                dur_min = request.json.get("dur_min")
                dur_max = request.json.get("dur_max")
                staff = request.json.get("staff")
                arrienda_equipos = request.json.get("arrienda_equipos")
                requisitos = request.json.get("requisitos")
                datos = request.json.get("datos")
                
                


                #campos obligatorios
                if imagen:
                    djprofile.imagen = imagen
                if artista:
                    djprofile.artista = artista
                if ciudad:
                    djprofile.ciudad = ciudad
                if status:
                    djprofile.status = status
                if pais:
                    djprofile.pais = pais
                if generos:
                    djprofile.generos = json.dumps(generos)
                if servicios:
                    djprofile.servicios = json.dumps(servicios)
                if tecnica:
                    djprofile.tecnica = tecnica
                #no obligatorios
                if mixcloud:
                    djprofile.mixcloud = mixcloud
                if soundcloud:
                    djprofile.soundcloud = soundcloud
                if instagram:
                    djprofile.instagram = instagram
                if agregar_cancion or not agregar_cancion:
                    djprofile.agregar_cancion = agregar_cancion
                if url_cancion:
                    djprofile.url_cancion = url_cancion
                if viajes:
                    djprofile.viajes = viajes
                if biografia:
                    djprofile.biografia = biografia
                if dur_min:
                    djprofile.dur_min = dur_min
                if dur_max:
                    djprofile.dur_max = dur_max
                if staff:
                    djprofile.staff = staff
                if arrienda_equipos:
                    djprofile.arrienda_equipos = arrienda_equipos
                if requisitos:
                    djprofile.requisitos = json.dumps(requisitos)
                if datos:
                    djprofile.datos = json.dumps(datos)
                djprofile.update()
                return jsonify(djprofile.serialize()), 201
    
        if account.role_id == 3:
            clientprofile = ClientProfile.query.filter_by(client_id=account.id).first()
            if not clientprofile:
                return jsonify({"msg": "Cuenta no tiene perfil de cliente asociado"})
            else:
                nombre = request.json.get("nombre", None)
                apellido = request.json.get("apellido", None)
                rut = request.json.get("rut", None)
                nacionalidad = request.json.get("nacionalidad", None)
                ciudad = request.json.get("ciudad", None)
                pais = request.json.get("pais", None)
                imagen = request.json.get("imagen", None)
                biografia = request.json.get("biografia")
                status = request.json.get("status")

                if not imagen:
                    return jsonify({"msg": "Se requiere una imagen de perfil"}), 400
                if not nombre:
                    return jsonify({"msg": "Se requiere un nombre"}), 400
                if not apellido:
                    return jsonify({"msg": "Se requiere un apellido"}), 400
                if not nacionalidad:
                    return jsonify({"msg": "Se requiere una nacionalidad"}), 400
                if not rut:
                    return jsonify({"msg": "Se requiere un rut"}), 400
                if not ciudad:
                    return jsonify({"msg": "Se requiere una ciudad"}), 400
                if not pais:
                    return jsonify({"msg": "Se requiere un pais de residencia"}), 400
                if not status:
                    return jsonify({"msg": "Se requiere que se active el status del perfil"}), 400

                clientprofile.nombre = nombre
                clientprofile.apellido = apellido
                clientprofile.rut = rut
                clientprofile.nacionalidad = nacionalidad
                clientprofile.ciudad = ciudad
                clientprofile.pais = pais
                clientprofile.status = status
                clientprofile.imagen = imagen
                if biografia:
                    clientprofile.biografia = biografia
                clientprofile.update()
                return jsonify(clientprofile.serialize()), 201

        else:
            return jsonify({"msg": "Usuario no es un DJ o Cliente"}), 401

## Ruta para recibir un perfil completo de DJ con ID (solo para usuario logeado) (tmb sirve para cliente really)
@app.route('/dj/profile/<int:dj_id>', methods=['GET'])
@jwt_required
def getDjProfile(dj_id):
        username = get_jwt_identity()
        account = Account.query.filter_by(username=username).first()
        if account.role_id == 1 or account.role_id == 2 or account.role_id == 3:
            profile = DjProfile.query.filter_by(dj_id=dj_id).first()
            return jsonify(profile.serialize()), 201
        else:
            return jsonify({"msg": "Porfavor iniciar session o crear cuenta para ver este contenido"}), 400


## Ruta para recibir perfil completo de Dj con username (solo para usuario logead) (tmb sirve para cliente really)
@app.route('/dj/profile/username/<usuario>', methods=['GET'])
@jwt_required
def getDjProfileWithUsername(usuario):
        username = get_jwt_identity()
        account = Account.query.filter_by(username=username).first()
        if account.role_id == 1 or account.role_id == 2 or account.role_id == 3:
            djaccount = Account.query.filter_by(username=usuario).first()
            profile = DjProfile.query.filter_by(dj_id=djaccount.id).first()
            gigs = Gig.query.filter_by(dj_id=djaccount.id).filter_by(estado="Confirmado").all()
            gigs = list(map(lambda gig: gig.gigsReducido(), gigs))

            data = {
                "profile": profile.serialize(),
                "gigs": gigs
            }
            return jsonify(data), 201
        else:
            return jsonify({"msg": "Porfavor iniciar session o crear cuenta para ver este contenido"}), 400


## Ruta para recibir perfil completo de Cliente con ID (solo para usuario logeado)
@app.route('/client/profile/<int:client_id>', methods=['GET'])
@jwt_required
def getClientProfileWithUsername(client_id):
        username = get_jwt_identity()
        account = Account.query.filter_by(username=username).first()
        if account.role_id == 1 or account.role_id == 2 or account.role_id == 3:
            profile = ClientProfile.query.filter_by(client_id=client_id).first()
            return jsonify(profile.serialize()), 201
        else:
            return jsonify({"msg": "Porfavor iniciar session o crear cuenta para ver este contenido"}), 400

## Ruta para recibir perfil completo de Cliente con Username (solo para usuario logeado)
@app.route('/client/profile/username/<usuario>', methods=['GET'])
@jwt_required
def getClientProfile(usuario):
        username = get_jwt_identity()
        account = Account.query.filter_by(username=username).first()
        if account.role_id == 1 or account.role_id == 2 or account.role_id == 3:
            clientaccount = Account.query.filter_by(username=usuario).first()
            profile = ClientProfile.query.filter_by(client_id=clientaccount.id).first()
            return jsonify(profile.serialize()), 201
        else:
            return jsonify({"msg": "Porfavor iniciar session o crear cuenta para ver este contenido"}), 400

## Recibir todas las cartas de perfil dj con status activo
@app.route('/profiles', methods=['GET'])
def profiles():
    profiles = DjProfile.query.filter_by(status="active").all()
    if profiles:
        profiles = list(map(lambda profile: profile.card(), profiles))
        return jsonify(profiles), 200
    else:
        return jsonify({"msg": "No hay perfiles activos"}), 401


########################################## GIGSSSSSSSSSSSSSS ###################################


##Registar Gig (Primer Booking)
@app.route('/gig/register', methods=['POST'])
@jwt_required
def gigRegister():
        username = get_jwt_identity()
        account = Account.query.filter_by(username=username).first()
        if account.role_id == 3:
            client_id = request.json.get("client_id", None)
            dj_id = request.json.get("dj_id", None)
            estado = request.json.get("estado", None)
            username_cliente = request.json.get("username_cliente", None)
            username_dj = request.json.get("username_dj", None)
            dia_evento = request.json.get("dia_evento", None)
            tipo_evento = request.json.get("tipo_evento", None)
            duracion = request.json.get("duracion", None)
            nombre_evento = request.json.get("nombre_evento", None)
            telefono = request.json.get("telefono", None)
            direccion = request.json.get("direccion", None)
            hora_llegada = request.json.get("hora_llegada", None)
            hora_show = request.json.get("hora_show", None)
            transporte = request.json.get("transporte", None)
            oferta = request.json.get("oferta", None)
            link_evento = request.json.get("link_evento")
            privado = request.json.get("privado", None)
            leido_por_dj = request.json.get("leido_por_dj", None)
            leido_por_cliente = request.json.get("leido_por_cliente", None)
            mensaje = request.json.get("mensaje", None)
            artist_name = request.json.get("artist_name")

            gig = Gig()
            gig.client_id = client_id
            gig.dj_id = dj_id
            gig.estado = estado
            gig.username_cliente = username_cliente
            gig.username_dj = username_dj
            gig.duracion = duracion
            gig.dia_evento = dia_evento
            gig.tipo_evento = tipo_evento
            gig.nombre_evento = nombre_evento
            gig.telefono = telefono
            gig.direccion = direccion
            gig.hora_llegada = hora_llegada
            gig.hora_show = hora_show
            gig.transporte = transporte
            gig.oferta = oferta
            gig.link_evento = link_evento
            gig.privado = privado
            gig.leido_por_dj = leido_por_dj
            gig.leido_por_cliente = leido_por_cliente
            gig.mensaje = json.dumps(mensaje)
            gig.artist_name = artist_name
            gig.save()
            return jsonify(gig.serialize()), 201
        else:
            return jsonify({"msg": "Solamente clientes pueden hacer booking"}), 401


## Aactualizar un gig 
@app.route('/gig/update/<int:id>', methods=['PUT'])
@jwt_required
def gigUpdate(id):
        username = get_jwt_identity()
        account = Account.query.filter_by(username=username).first()
        gig = Gig.query.filter_by(id=id).first()
        if account.role_id == 3 or account.role_id == 2:

            estado = request.json.get("estado", None)
            username_cliente = request.json.get("username_cliente", None)
            username_dj = request.json.get("username_dj", None)
            dia_evento = request.json.get("dia_evento", None)
            tipo_evento = request.json.get("tipo_evento", None)
            duracion = request.json.get("duracion", None)
            nombre_evento = request.json.get("nombre_evento", None)
            telefono = request.json.get("telefono", None)
            direccion = request.json.get("direccion", None)
            hora_llegada = request.json.get("hora_llegada", None)
            hora_show = request.json.get("hora_show", None)
            transporte = request.json.get("transporte", None)
            oferta = request.json.get("oferta", None)
            link_evento = request.json.get("link_evento")
            privado = request.json.get("privado", None)
            leido_por_dj = request.json.get("leido_por_dj", None)
            leido_por_cliente = request.json.get("leido_por_cliente", None)
            mensaje = request.json.get("mensaje", None)


            gig.estado = estado
            gig.username_cliente = username_cliente
            gig.username_dj = username_dj
            gig.duracion = duracion
            gig.dia_evento = dia_evento
            gig.tipo_evento = tipo_evento
            gig.nombre_evento = nombre_evento
            gig.telefono = telefono
            gig.direccion = direccion
            gig.hora_llegada = hora_llegada
            gig.hora_show = hora_show
            gig.transporte = transporte
            gig.oferta = oferta
            gig.link_evento = link_evento
            gig.privado = privado
            gig.leido_por_dj = leido_por_dj
            gig.leido_por_cliente = leido_por_cliente
            gig.mensaje = json.dumps(mensaje)
            gig.update()
            return jsonify(gig.serialize()), 201
        else:
            return jsonify({"msg": "No tienes los permisos para hacer estos cambios"}), 401

## Recibir un gig completo 
@app.route('/gig/<int:id>', methods=['GET'])
@jwt_required
def getGig(id):
        username = get_jwt_identity()
        account = Account.query.filter_by(username=username).first()
        if account:
            gig = Gig.query.filter_by(id=id).first()
            if gig.client_id == account.id or gig.dj_id == account.id or account.role_id == 1:
                return jsonify(gig.serialize()), 201
            else:
                return jsonify({"msg": "No tienes permiso para acceder a la información de este gig"}), 201
        else:
            return jsonify({"msg": "No existe tu cuenta en nuestro registro"}), 401

## Recibir todos los gigs asociados al ID de una cuenta
@app.route('/account/gig', methods=['GET'])
@jwt_required
def getGigByAccount():
        username = get_jwt_identity()
        account = Account.query.filter_by(username=username).first()
        if account:
            if account.role_id == 2:
                gigs = Gig.query.filter_by(dj_id=account.id).all()
                gigs = list(map(lambda gig: gig.gigsReducido(), gigs))
                return jsonify(gigs), 201
            if account.role_id == 3:
                gigs = Gig.query.filter_by(client_id=account.id).all()
                gigs = list(map(lambda gig: gig.gigsReducido(), gigs))
                return jsonify(gigs), 200
        else:
            return jsonify({"msg": "Cuenta no existe en nuestros registros"}), 401

## Recibir todos los gigs existentes (solo para admin)
@app.route('/admin/gigs', methods=['GET'])
@jwt_required
def getAllGigs():
        username = get_jwt_identity()
        account = Account.query.filter_by(username=username).first() 
        if account.role_id == 1:
            gigs = Gig.query.all()
            gigs = list(map(lambda gig: gig.serialize(), gigs))
            return jsonify(gigs), 201
        else:
            return jsonify({"msg": "Cuenta no tiene derechos sobre esta información"}), 401    

########## INICIAR ROLES Y OBJETOS GLOBALES AL LEVANTAR SERVER ##################################

@manager.command
def load_globales():
    role = Roles()
    role.name = "admin"
    role.status = True
    role.save()
    role = Roles()
    role.name = "dj"
    role.status = True
    role.save()
    role = Roles()
    role.name = "client"
    role.status = True
    role.save()
    og = ObjetosGlobales()
    og.save()
    print("Objetos globales cargados")
    
if __name__ == '__main__':
    manager.run()
