from database import db 
from models import Juegos 

def insertar_juego(nombre, descripcion, precio):

    juego = Juegos(nombre=nombre, descripcion=descripcion, precio=precio)
    db.session.add(juego)
    db.session.commit()

def obtener_juegos():
    juegos = Juegos.query.all()
    return juegos

def eliminar_juego(id):

    juego = Juegos.query.get(id)
    if juego:

        db.session.delete(juego)
        db.session.commit()

def obtener_juego_por_id(id):

    juego = Juegos.query.get(id)
    return juego

def actualizar_juego(nombre, descripcion, precio, id):

    juego = Juegos.query.get(id)
    if juego:

        juego.nombre = nombre
        juego.descripcion = descripcion
        juego.precio = precio
        db.session.commit()