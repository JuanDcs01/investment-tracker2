from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):

    # Tabla
    __tablename__ = 'users'

    # Atributos (columnas)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Convierte la contraseña a hash
    def set_password(self, password):
        """Genera un hash seguro a partir de la contraseña."""
        self.password_hash = generate_password_hash(password)

    # Verifica la contraseña ingresada
    def check_password(self, password):
        """Verifica si la contraseña ingresada coincide con el hash."""
        return check_password_hash(self.password_hash, password)

    # Representacion del objeto
    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """Convertir el usuario a diccionario."""
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash
        }