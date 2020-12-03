import datetime
import json
from flask import Flask, render_template, request, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from models import db, Roles, Account
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from os import access, environ
import config


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object(config.Base)
db.init_app(app)
jwt = JWTManager(app)
Migrate(app, db)
CORS(app)
manager = Manager(app)
manager.add_command("db", MigrateCommand)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/user/register', methods=['POST'])
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

        return jsonify(Account.serialize()), 201


if __name__ == '__main__':
    manager.run()
