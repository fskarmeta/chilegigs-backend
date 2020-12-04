import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql import expression, func
db = SQLAlchemy()




requisitosArray = {"equipos":[{"label":"Controladores","options":[{"value":"Ableton Push 3","label":"Ableton Push 3","group":"Controladores"},{"value":"Akai AMX - Mixing Surface","label":"Akai AMX - Mixing Surface","group":"Controladores"}]},{"label":"Mixer","options":[{"value":"10 entradas","label":"10 entradas","group":"Mixer"},{"value":"8 entradas","label":"8 entradas","group":"Mixer"}]}],"escenario":[{"label":"Mesas Ancho x Largo","options":[{"value":"Mesa 1x1 m^2","label":"Mesa 1x1 m^2","group":"Mesas Ancho x Largo"},{"value":"Mesa 1x2 m^2","label":"Mesa 1x2 m^2","group":"Mesas Ancho x Largo"},{"value":"Mesa 1x5 m^2","label":"Mesa 1x5 m^2","group":"Mesas Ancho x Largo"},{"value":"Mesa 1.5x1 m^2","label":"Mesa 1.5x1 m^2","group":"Mesas Ancho x Largo"},{"value":"Mesa 1.5x2 m^2","label":"Mesa 1.5x2 m^2","group":"Mesas Ancho x Largo"},{"value":"Mesa 1.5x3 m^2","label":"Mesa 1.5x3 m^2","group":"Mesas Ancho x Largo"}]},{"label":"Iluminación","options":[{"value":"Panel Led","label":"Panel Led","group":"Iluminación"},{"value":"Data Show","label":"Data Show","group":"Iluminación"}]}],"foodanddrinks":[{"label":"Bebestibles","options":[{"value":"Botella de Agua sin gas","label":"Botella de Agua sin gas","group":"Bebestible"},{"value":"Botella de Agua con gas","label":"Botella de Agua con gas","group":"Bebestibles"},{"value":"Coca Cola Light","label":"Coca Cola Light","group":"Bebestibles"},{"value":"Tequila","label":"Tequila","group":"Bebestibles"}]},{"label":"Snacks","options":[{"value":"Snacks Vegetarianos","label":"Snacks Vegetarianos","group":"Snacks"},{"value":"Snacks Veganos","label":"Snacks Veganos","group":"Snacks"}]}]}
homeArray = {"header":{"image":"./img/home/header.jpg","cita":"hola buenos días"},"subheader":{"image":"./img/home/subheader.jpg","color":"black","title":"Chile gigs, el mejor lugar para Dj's","box1":{"title":"+8.000","text":"personas felices con nuestro producto"},"box2":{"title":"+300 eventos","text":"Promovemos a los mejores Dj's de Chile"}},"citas":[{"imagen":"./img/home/citas/dj1.jpg","nombre":"Dj Lucifer","cita":"Amo la musica tanto como esta página"},{"imagen":"./img/home/citas/dj2.jpg","nombre":"Dj Crap","cita":"Chilegigs es lo mejor que la ha pasado a nuestra industria"}]}

class ObjetosGlobales(db.Model):
    __tablename__ = "objetoglobales"
    id = db.Column(db.Integer, primary_key=True)
    requisitos = db.Column(db.Text())
    home = db.Column(db.Text())

    def save(self):
        self.requisitos = json.dumps(requisitosArray) 
        self.home = json.dumps(homeArray)
        db.session.add(self)
        db.session.commit()    
    

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
    def save(self):
        db.session.add(self)
        db.session.commit()

class Account(db.Model):
    __tablename__ = "account"
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, ForeignKey('roles.id'))
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    time_created = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)

    client_profile = db.relationship('ClientProfile', backref="clientaccount", lazy=True)
    dj_profile = db.relationship('DjProfile', backref="djaccount", lazy=True)
  

    def serialize(self):
        return {
            "id": self.id,
            "role": self.roles.serialize(),
            "username": self.username,
            "email": self.email,
            "time_created": self.time_created
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
    dj_id = db.Column(db.Integer, ForeignKey('account.id', ondelete="CASCADE"))
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
            "feedback": json.loads(self.feedback),
            "djaccount": self.djaccount.serialize()   
        }
    
    def card(self):
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
            "tecnica": json.loads(self.tecnica)
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
    client_id = db.Column(db.Integer, ForeignKey('account.id', ondelete="CASCADE"))
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
            "feedback": json.loads(self.feedback),
            "clientaccount": self.clientaccount.serialize()
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

