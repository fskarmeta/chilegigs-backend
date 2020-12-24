import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql import expression, func
db = SQLAlchemy()




requisitosArray = {"equipos":[{"label":"Controladores","options":[{"value":"Ableton Push 3","label":"Ableton Push 3","group":"Controladores"},{"value":"Akai AMX - Mixing Surface","label":"Akai AMX - Mixing Surface","group":"Controladores"}]},{"label":"Mixer","options":[{"value":"10 entradas","label":"10 entradas","group":"Mixer"},{"value":"8 entradas","label":"8 entradas","group":"Mixer"}]}],"escenario":[{"label":"Mesas Ancho x Largo","options":[{"value":"Mesa 1x1 m^2","label":"Mesa 1x1 m^2","group":"Mesas Ancho x Largo"},{"value":"Mesa 1x2 m^2","label":"Mesa 1x2 m^2","group":"Mesas Ancho x Largo"},{"value":"Mesa 1x5 m^2","label":"Mesa 1x5 m^2","group":"Mesas Ancho x Largo"},{"value":"Mesa 1.5x1 m^2","label":"Mesa 1.5x1 m^2","group":"Mesas Ancho x Largo"},{"value":"Mesa 1.5x2 m^2","label":"Mesa 1.5x2 m^2","group":"Mesas Ancho x Largo"},{"value":"Mesa 1.5x3 m^2","label":"Mesa 1.5x3 m^2","group":"Mesas Ancho x Largo"}]},{"label":"Iluminación","options":[{"value":"Panel Led","label":"Panel Led","group":"Iluminación"},{"value":"Data Show","label":"Data Show","group":"Iluminación"}]}],"foodanddrinks":[{"label":"Bebestibles","options":[{"value":"Botella de Agua sin gas","label":"Botella de Agua sin gas","group":"Bebestible"},{"value":"Botella de Agua con gas","label":"Botella de Agua con gas","group":"Bebestibles"},{"value":"Coca Cola Light","label":"Coca Cola Light","group":"Bebestibles"},{"value":"Tequila","label":"Tequila","group":"Bebestibles"}]},{"label":"Snacks","options":[{"value":"Snacks Vegetarianos","label":"Snacks Vegetarianos","group":"Snacks"},{"value":"Snacks Veganos","label":"Snacks Veganos","group":"Snacks"}]}]}
homeArray = {"header":{"image":"https://res.cloudinary.com/chilegigs/image/upload/v1607467204/home/imagen10_lbjxpa.jpg","cita":""},"subheader":{"image":"./img/home/subheader.jpg","color":"white","title":"Creemos en el poder de la música","box1":{"title":"+8.000","text":"Personas felices con nuestro DJ's"},"box2":{"title":"+300 eventos","text":"Promovemos a los mejores Dj's de Chile"}},"citas":[{"imagen":"https://res.cloudinary.com/chilegigs/image/upload/v1607467268/citas/profile1_zioyrs.jpg","nombre":"Dj Lucifer","cita":"Amo la musica tanto como esta página"},{"imagen":"https://res.cloudinary.com/chilegigs/image/upload/v1607655370/citas/ognbzmmb1kysqytjlpks.jpg","nombre":"Dj Crap","cita":"Chilegigs es lo mejor que la ha pasado a nuestra industria"},{"imagen":"https://res.cloudinary.com/chilegigs/image/upload/v1607655411/citas/ui0j1ykp1bz7pgt3bvey.jpg","nombre":"Dj Tekila","cita":"El mejor sitio para dar a conocer mi talento"}]}

class ObjetosGlobales(db.Model):
    __tablename__ = "objetosglobales"
    id = db.Column(db.Integer, primary_key=True)
    requisitos = db.Column(db.Text())
    home = db.Column(db.Text())

    def serialize(self):
        return {
            "requisitos": json.loads(self.requisitos),
            "home": json.loads(self.home)
        }

    def save(self):
        self.requisitos = json.dumps(requisitosArray) 
        self.home = json.dumps(homeArray)
        db.session.add(self)
        db.session.commit()    

    def update(self):
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
    username = db.Column(db.String(100))
    pais = db.Column(db.String(100))
    imagen = db.Column(db.String(300))
    status = db.Column(db.String(50), nullable=True, default="inactive")
    mixcloud = db.Column(db.String(100), nullable=True, default="")
    soundcloud = db.Column(db.String(100), nullable=True, default="")
    instagram = db.Column(db.String(100), nullable=True, default="")
    generos = db.Column(db.String(500), default="[]")
    servicios = db.Column(db.String(500), default="[]")
    tecnica = db.Column(db.String(500), default="")
    agregar_cancion = db.Column(db.Boolean, server_default=expression.false())
    url_cancion = db.Column(db.String(100), nullable=True, default="")
    biografia = db.Column(db.String(1000), nullable=True, default="")
    dur_min = db.Column(db.String(100), nullable=True, default="")
    dur_max = db.Column(db.String(100), nullable=True, default="")
    viajes = db.Column(db.String(100), nullable=True, default="")
    staff = db.Column(db.Integer, nullable=True, default=0)
    arrienda_equipos = db.Column(db.String(100), nullable=True, default="No")
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
            "imagen": self.imagen,
            "mixcloud": self.mixcloud,
            "soundcloud": self.soundcloud,
            "instagram": self.instagram,
            "generos": json.loads(self.generos),
            "servicios": json.loads(self.servicios),
            "tecnica": self.tecnica,
            "agregar_cancion": self.agregar_cancion,
            "url_cancion": self.url_cancion,
            "biografia": self.biografia,
            "dur_min": self.dur_min,
            "dur_max": self.dur_max,
            "viajes": self.viajes,
            "staff": self.staff,
            "arrienda_equipos": self.arrienda_equipos,
            "requisitos": json.loads(self.requisitos),
            "datos": json.loads(self.datos),
            "suma_rating": self.suma_rating,
            "contrataciones": self.contrataciones,
            "feedback": json.loads(self.feedback),
            "djaccount": self.djaccount.serialize(), 
            "status": self.status, 
            "username": self.username
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
            "instagram": self.instagram,
            "suma_rating": self.suma_rating,
            "contrataciones": self.contrataciones,
            "generos": json.loads(self.generos),
            "servicios": json.loads(self.servicios),
            "tecnica": self.tecnica,
            "status": self.status,
            "imagen": self.imagen,
            "username": self.username,
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
    status = db.Column(db.String(50), nullable=True, default="inactive")
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    imagen = db.Column(db.String(300))
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
            "imagen": self.imagen,
            "nacionalidad": self.nacionalidad,
            "ciudad": self.ciudad,
            "pais": self.pais,
            "biografia": self.biografia,
            "suma_rating": self.suma_rating,
            "contrataciones": self.contrataciones,
            "feedback": json.loads(self.feedback),
            "clientaccount": self.clientaccount.serialize(),
            "status": self.status
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


## GIG

class Gig(db.Model):
    __tablename__ = "gig"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, ForeignKey('account.id', ondelete="CASCADE"))
    dj_id = db.Column(db.Integer, ForeignKey('account.id', ondelete="CASCADE"))
    estado = db.Column(db.String(100))
    username_cliente = db.Column(db.String(100))
    username_dj = db.Column(db.String(100))
    dia_evento = db.Column(db.String(100))
    tipo_evento = db.Column(db.String(100))
    nombre_evento = db.Column(db.String(100))
    telefono = db.Column(db.String(100))
    direccion = db.Column(db.String(100))
    duracion = db.Column(db.String(100))
    hora_llegada = db.Column(db.String(100))
    hora_show = db.Column(db.String(100))
    transporte = db.Column(db.String(100))
    oferta = db.Column(db.String(100))
    artist_name = db.Column(db.String(100), default="")
    link_evento = db.Column(db.String(100), nullable=True, default="")
    privado = db.Column(db.Boolean, server_default=expression.false())
    leido_por_dj = db.Column(db.Boolean, server_default=expression.false())
    leido_por_cliente = db.Column(db.Boolean, server_default=expression.false())
    mensaje = db.Column(db.String(10000))
    time_created = db.Column(db.DateTime, nullable=False,
    default=datetime.utcnow)
    feedback_client = db.Column(db.Boolean, server_default=expression.false())
    feedback_dj = db.Column(db.Boolean, server_default=expression.false())

    def serialize(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "dj_id": self.dj_id,
            "estado": self.estado,
            "username_cliente": self.username_cliente,
            "username_dj": self.username_dj,
            "dia_evento": self.dia_evento,
            "tipo_evento": self.tipo_evento,
            "nombre_evento": self.nombre_evento,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "hora_llegada": self.hora_llegada,
            "hora_show": self.hora_show,
            "transporte": self.transporte,
            "oferta": self.oferta,
            "link_evento": self.link_evento,
            "privado": self.privado,
            "duracion": self.duracion,
            "leido_por_dj": self.leido_por_dj,
            "leido_por_cliente": self.leido_por_cliente,
            "mensaje": json.loads(self.mensaje),
            "time_created": self.time_created,
            "artist_name": self.artist_name
        }

    def gigsReducido(self):
        return {
            "id": self.id,
            "dj_id": self.dj_id,
            "username_cliente": self.username_cliente,
            "username_dj": self.username_dj,
            "dia_evento": self.dia_evento,
            "hora_llegada": self.hora_llegada,
            "nombre_evento": self.nombre_evento,
            "hora_show": self.hora_show,
            "link_evento": self.link_evento,
            "privado": self.privado,
            "leido_por_cliente": self.leido_por_cliente,
            "leido_por_dj": self.leido_por_dj,
            "estado": self.estado,
            "artist_name": self.artist_name,
            "feedback_client": self.feedback_client,
            "feedback_dj": self.feedback_dj
        }


    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)
    gig_id = db.Column(db.Integer)
    client_id = db.Column(db.Integer)
    dj_id = db.Column(db.Integer)
    client_username = db.Column(db.String(100))
    dj_username = db.Column(db.String(100))
    dia_evento = db.Column(db.String(100))
    nombre_evento = db.Column(db.String(100))
    by_dj_commentary = db.Column(db.String(1000))
    by_client_commentary = db.Column(db.String(1000))
    by_dj_rating = db.Column(db.Integer)
    by_client_rating = db.Column(db.Integer)
    rated_by_dj = db.Column(db.Boolean, server_default=expression.false())
    rated_by_client = db.Column(db.Boolean, server_default=expression.false())

    def serialize(self):
        return {
            "id": self.id,
            "gig_id": self.gig_id,
            "client_id": self.client_id,
            "dj_id": self.dj_id,
            "client_username": self.client_username,
            "dj_username": self.dj_username,
            "dia_evento": self.dia_evento,
            "nombre_evento": self.nombre_evento,
            "by_dj_commentary": self.by_dj_commentary,
            "by_client_commentary": self.by_client_commentary,
            "by_dj_rating": self.by_dj_rating,
            "by_client_rating": self.by_client_rating,
            "rated_by_dj": self.rated_by_dj,
            "rated_by_client": self.rated_by_client
        }
    
    def serializeForDj(self):
        return {
            "id": self.id,
            "client_username": self.client_username,
            "dia_evento": self.dia_evento,
            "nombre_evento": self.nombre_evento,
            "by_client_commentary": self.by_client_commentary,
            "by_client_rating": self.by_client_rating
        }

    def serializeForClient(self):
        return {
            "id": self.id,
            "dj_username": self.dj_username,
            "dia_evento": self.dia_evento,
            "nombre_evento": self.nombre_evento,
            "by_dj_commentary": self.by_dj_commentary,
            "by_dj_rating": self.by_dj_rating
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
