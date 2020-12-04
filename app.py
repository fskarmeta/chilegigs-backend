import datetime
import json
from flask import Flask, render_template, request, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from models import db, Roles, Account, DjProfile, ClientProfile, ObjetosGlobales
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_raw_jwt
from os import access, environ
import config


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object(config.Base)
db.init_app(app)
jwt = JWTManager(app)
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


## Crear y borrar Cuenta, en la tabla de roles en su workbench generar 3 tipos de cuenta
## Id queda vacío, nombre (una cliente, otra dj, otra admin), en status insertar un 1
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

## Actualizar nombre de cuenta de usuario (esto no va)
@app.route('/user/update/username', methods=['PUT'])
@jwt_required
def updateUsername():
    newusername = request.json.get("username")
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    if account:
        account.username = newusername
        account.update()
        return jsonify(account.serialize())
    else:
        return jsonify({"msg": "Tienes que volver a logearte"}), 401

## Actualizar contraseña de usuario
@app.route('/user/update/password', methods=['PUT'])
@jwt_required
def updatePassword():
    newpassword = request.json.get("password")
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    if account:
        account.password = generate_password_hash(newpassword)
        account.update()
        return jsonify(account.serialize())
    else:
        return jsonify({"msg": "Tienes que volver a logearte"}), 401

## Actualizar Email de cuenta de usuario (validar que no exista ya)
@app.route('/user/update/email', methods=['PUT'])
@jwt_required
def updateEmail():
    newemail = request.json.get("email")
    username = get_jwt_identity()
    account = Account.query.filter_by(username=username).first()
    email = Account.query.filter_by(email=newemail).first()
    if account:
        if email:
            return jsonify({"msg": "Email ya esta en uso"})
        else:
            account.email = newemail
            account.update()
            return jsonify(account.serialize())
    else:
        return jsonify({"msg": "Tienes que volver a logearte"}), 401


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

## crear Perfl DJ 
@app.route('/profile', methods=['POST'])
@jwt_required
def profile():
    if request.method == 'POST':
        username = get_jwt_identity()
        account = Account.query.filter_by(username=username).first()
        if account.role_id == 2:
            djprofile = DjProfile.query.filter_by(dj_id=account.role_id).first()
            if djprofile:
                return jsonify({"msg": "Dj ya tiene un perfil"})
            else:
                artista = request.json.get("artista", None)
                ciudad = request.json.get("ciudad", None)
                pais = request.json.get("pais", None)
                mixcloud = request.json.get("mixcloud")
                soundcloud = request.json.get("soundcloud")
                spotify = request.json.get("spotify")
                generos = request.json.get("generos", None)
                servicios = request.json.get("servicios", None)
                tecnica = request.json.get("tecnica", None)
                agregar_cancion = request.json.get("agregar_cancion")
                url_cancion = request.json.get("url_cancion")
                biografia = request.json.get("artista")
                dur_min = request.json.get("dur_min")
                dur_max = request.json.get("dur_max")
                staff = request.json.get("staff")
                arrienda_equipos = request.json.get("arrienda_equipos")
                requisitos = request.json.get("requisitos")
                datos = request.json.get("datos")
                

                if not artista:
                    return jsonify({"msg": "Se requiere nombre de artista"}), 400
                if not ciudad:
                    return jsonify({"msg": "Se requiere que incluyas una ciudad de origen"}), 400
                if not pais:
                    return jsonify({"msg": "Se requiere que incluyas un pais de origen"}), 400
                if not servicios:
                    return jsonify({"msg": "Se requiere que incluyas como minimo un genero"}), 400
                if not servicios:
                    return jsonify({"msg": "Se requiere que incluyas como minimo un servicio"}), 400
                if not tecnica:
                    return jsonify({"msg": "Se requiere que especifiques una técnica"}), 400

                dj = DjProfile()
                dj.dj_id = account.id
                dj.artista = artista
                dj.ciudad = ciudad
                dj.pais = pais
                dj.mixcloud = mixcloud
                dj.soundcloud = soundcloud
                dj.spotify = spotify
                dj.generos = json.dumps(generos)
                dj.servicios = json.dumps(servicios)
                dj.tecnica = json.dumps(tecnica)
                dj.agregar_cancion = agregar_cancion
                dj.url_cancion = url_cancion
                dj.biografia = biografia
                dj.dur_min = dur_max
                dj.dur_max = dur_max
                dj.staff = staff
                dj.arrienda_equipos = arrienda_equipos
                dj.requisitos = requisitos
                dj.datos = datos
                dj.save()
                return jsonify(dj.serialize()), 201
    
        if account.role_id == 3:
            clientprofile = ClientProfile.query.filter_by(client_id=account.role_id).first()
            if clientprofile:
                return jsonify({"msg": "Cliente ya tiene un perfil"})
            else:
                nombre = request.json.get("nombre", None)
                apellido = request.json.get("apellido", None)
                rut = request.json.get("rut", None)
                nacionalidad = request.json.get("nacionalidad", None)
                ciudad = request.json.get("ciudad", None)
                pais = request.json.get("pais", None)
                biografia = request.json.get("biografia")

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


                client = ClientProfile()
                client.client_id = account.id
                client.nombre = nombre
                client.apellido = apellido
                client.rut = rut
                client.nacionalidad = nacionalidad
                client.ciudad = ciudad
                client.pais = pais
                client.biografia = biografia
                client.save()
                return jsonify(client.serialize()), 201

        else:
            return jsonify({"msg": "Usuario no es un DJ o Cliente"})



## Ruta para recibir un perfil completo de DJ (solo para usuario logeado)
@app.route('/profile/<int:dj_id>', methods=['GET'])
@jwt_required
def getprofile(dj_id):
        username = get_jwt_identity()
        account = Account.query.filter_by(username=username).first()
        if account.role_id == 1 or account.role_id == 2 or account.role_id == 3:
            profile = DjProfile.query.filter_by(dj_id=dj_id).first()
            return jsonify(profile.serialize()), 201
        else:
            return jsonify({"msg": "Porfavor iniciar session o crear cuenta para ver este contenido"}), 400

## Recibir todas las cartas de perfil
@app.route('/profiles', methods=['GET'])
def profiles():
    profiles = DjProfile.query.all()
    profiles = list(map(lambda profile: profile.card(), profiles))
    return jsonify(profiles), 200

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
