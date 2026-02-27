from app import db, create_app
from app.models.user import User

app = create_app()
with app.app_context():
    nuevo_usuario = User(username='JuanDcs375')
    nuevo_usuario.set_password('Black375z@')
    db.session.add(nuevo_usuario)
    db.session.commit()
    print("Usuario de prueba creado con éxito")