from app import db, create_app
from app.models.user import User

app = create_app()
with app.app_context():
    nuevo_usuario = User(username='1234')
    nuevo_usuario.set_password('1234')
    db.session.add(nuevo_usuario)
    db.session.commit()
    print("Usuario de prueba creado con éxito")