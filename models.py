import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql import expression
db = SQLAlchemy()


class Roles(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    status = db.Column(db.Boolean, default=True)
    accounts = db.relationship("Account", backref="roles")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status
        }


class Account(db.Model):
    __tablename__ = "account"
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, ForeignKey('roles.id'))
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def serialize(self):
        return {
            "id": self.id,
            "role": self.roles.serialize(),
            "username": self.username,
            "email": self.email
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class DjProfile(db.Model):
    __tablename__ = "djprofile"
    id = db.Column(db.Integer, primary_key=True)
    dj_id = db.Column(db.Integer, ForeignKey('account.id'))
    artista = db.Column(db.String(100))
    ciudad = db.Column(db.String(100))
    pais = db.Column(db.String(100))
    mixcloud = db.Column(db.String(100), nullable=True, default="")
    soundcloud = db.Column(db.String(100), nullable=True, default="")
    spotify = db.Column(db.String(100), nullable=True, default="")
    generos = db.Column(db.String(500), default="[]")
    servicios = db.Column(db.String(500), default="[]")
    tecnica = db.Column(db.String(500), default="[]")
    agregar_cancion = db.Column(db.Boolean, server_default=expression.false())
    url_cancion = db.Column(db.String(100), nullable=True, default="")
    biografia = db.Column(db.String(1000), nullable=True, default="")
    dur_min = db.Column(db.String(10), nullable=True, default="")
    dur_max = db.Column(db.String(10), nullable=True, default="")
    staff = db.Column(db.Integer, nullable=True, default=0)
    arrienda_equipos = db.Column(db.String(10), nullable=True, default="No")
    requisitos = db.Column(db.String(1000), nullable=True, default="[]")
    datos = db.Column(db.String(1000), nullable=True, default="[]")
    suma_rating = db.Column(db.Integer, nullable=True, default=0)
    contrataciones = db.Column(db.Integer, nullable=True, default=0)
    feedback = db.Column(db.String(1000), nullable=True, default="[]")
    # cuenta = db.relationship('Account', backref="djprofile", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "dj_id": self.dj_id,
            "artista": self.artista,
            "ciudad": self.ciudad,
            "pais": self.pais,
            "mixcloud": self.mixcloud,
            "soundcloud": self.soundcloud,
            "spotify": self.spotify,
            "generos": json.loads(self.generos),
            "servicios": json.loads(self.servicios),
            "tecnica": json.loads(self.tecnica),
            "agregar_cancion": self.agregar_cancion,
            "url_cancion": self.url_cancion,
            "biografia": self.biografia,
            "dur_min": self.dur_min,
            "dur_max": self.dur_max,
            "staff": self.staff,
            "arrienda_equipos": self.arrienda_equipos,
            "requisitos": self.requisitos,
            "datos": json.loads(self.datos),
            "suma_rating": self.suma_rating,
            "contrataciones": self.contrataciones,
            "feedback": json.loads(self.feedback)
            # "cuenta": self.account.serialize()   
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class ClientProfile(db.Model):
    __tablename__ = "clientprofile"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, ForeignKey('account.id'))
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    rut = db.Column(db.String(100))
    nacionalidad = db.Column(db.String(100))
    ciudad = db.Column(db.String(100))
    pais = db.Column(db.String(100))
    biografia = db.Column(db.String(100), nullable=True, default="")
    suma_rating = db.Column(db.Integer, nullable=True, default=0)
    contrataciones = db.Column(db.Integer, nullable=True, default=0)
    feedback = db.Column(db.String(1000), nullable=True, default="[]")
    # cuenta = db.relationship('Account', backref="clientprofile", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "rut": self.rut,
            "nacionalidad": self.nacionalidad,
            "ciudad": self.ciudad,
            "pais": self.pais,
            "biografia": self.biografia,
            "suma_rating": self.suma_rating,
            "contrataciones": self.contrataciones,
            "feedback": json.loads(self.feedback)
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()