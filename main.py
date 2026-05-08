from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import LoginManager, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
from api.routes import api as api_blueprint 
import controllers 
from database import db 
from models import Juegos, User 
from auth import auth as auth_blueprint 
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'esta-es-una-llave-muy-secreta'

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:hola123@localhost/juegos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/errors.log', maxBytes=10240, backupCount=10)
    
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    file_handler.setLevel(logging.ERROR)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.ERROR)
    app.logger.info('Arranque de la aplicación')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(api_blueprint)

@app.route("/agregar_juego")
@login_required 
def formulario_agregar_juego():
    return render_template("agregar_juego.html")

@app.route("/guardar_juego", methods=["POST"])
@login_required 
def guardar_juego():
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    controllers.insertar_juego(nombre, descripcion, precio)
    flash("Juego guardado correctamente")
    return redirect(url_for('juegos')) 

@app.route("/")
@app.route("/juegos")
@login_required 
def juegos():
    juegos = controllers.obtener_juegos()
    return render_template("juegos.html", juegos=juegos)

@app.route("/eliminar_juego", methods=["POST"])
@login_required 
def eliminar_juego():
    controllers.eliminar_juego(request.form["id"])
    flash("Juego eliminado correctamente")
    return redirect(url_for('juegos'))

@app.route("/formulario_editar_juego/<int:id>")
@login_required 
def editar_juego(id):
    if id <= 0:
        abort(400, description="El ID del juego debe ser un número positivo.")
    
    juego = controllers.obtener_juego_por_id(id)
    
    if not juego:
        abort(404)
        
    return render_template("editar_juego.html", juego=juego)

@app.route("/actualizar_juego", methods=["POST"])
@login_required 
def actualizar_juego():
    id = request.form["id"]
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    controllers.actualizar_juego(nombre, descripcion, precio, id)
    flash("Juego actualizado correctamente")
    return redirect(url_for('juegos'))

@app.route("/test_500")
@login_required
def test_500():
    x = 1 / 0
    return "Nunca llegarás aquí"

@app.errorhandler(400)
def bad_request_error(error):
    return render_template("400.html", error=error), 400

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html", error=error), 404

@app.errorhandler(405)
def method_not_allowed_error(error):
    return render_template("405.html", error=error), 405

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error(f"Error interno del servidor: {error}", exc_info=True)
    return render_template("500.html", error=error), 500

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """
    Manejador genérico para excepciones HTTP.
    Si la ruta empieza con /api/, devuelve JSON.
    De lo contrario, devuelve la página de error HTML estándar.
    """
    if request.path.startswith('/api/'):
        response = e.get_response()
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }).data
        response.content_type = "application/json"
        return response
    
    if e.code == 400:
        return bad_request_error(e)
    if e.code == 404:
        return not_found_error(e)
    if e.code == 405:
        return method_not_allowed_error(e)
    if e.code == 500:
        return internal_server_error(e)
    
    return e

@app.errorhandler(Exception)
def handle_generic_exception(e):
    """
    Manejador para excepciones no-HTTP (errores de código).
    Siempre registra el error y muestra la página 500.
    """
    if isinstance(e, HTTPException):
        return handle_http_exception(e)

    app.logger.error(f"Excepción no controlada: {e}", exc_info=True)
    return render_template("500.html", error=e), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="127.0.0.1", port=8000, debug=True)