class Account(db.Model):
    __tablename__ = "account"
    id = db.Column(db.String(100), primary_key=True)
    role_id = db.Column(db.Integer, ForeignKey('roles.id'))
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def serialize(self):
        return {
            "id": self.id,
            "role": self.role.serialize(),
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
