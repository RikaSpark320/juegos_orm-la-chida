from flask import Blueprint, jsonify, request, abort
# Importamos desde el directorio padre (..) los controladores, modelos y db
import controllers
from models import Juegos
from database import db

# Definimos el Blueprint para la API
# Todo lo definido aquí tendrá el prefijo /api
api = Blueprint('api', __name__, url_prefix='/api')


# --- Función Auxiliar ---

def _juego_to_dict(juego: Juegos) -> dict:
    """
    Serializa un objeto 'Juegos' a un diccionario estándar
    para poder convertirlo a JSON.
    """
    return {
        "id": juego.id,
        "nombre": juego.nombre,
        "descripcion": juego.descripcion,
        "precio": float(juego.precio)  # Convertir Decimal a float para JSON
    }


# --- Manejadores de Errores de la API ---
# Nos aseguramos de que los errores de la API devuelvan JSON

@api.errorhandler(400)
def bad_request(error):
    """Manejador para errores 400 (Bad Request)"""
    return jsonify(error=str(error.description)), 400

@api.errorhandler(404)
def not_found(error):
    """Manejador para errores 404 (Not Found)"""
    return jsonify(error=str(error.description)), 404


# --- Endpoints del Recurso JuegoList ---

@api.route('/juegos', methods=['GET'])
def get_juegos():
    """
    [GET] /api/juegos
    Obtiene la lista completa de juegos.
    Respuesta: 200 OK
    """
    juegos_list = controllers.obtener_juegos()
    # Serializamos cada juego en la lista usando la función auxiliar
    juegos_dict_list = [_juego_to_dict(juego) for juego in juegos_list]
    return jsonify(juegos_dict_list), 200


@api.route('/juegos', methods=['POST'])
def create_juego():
    """
    [POST] /api/juegos
    Crea un nuevo juego.
    Respuesta: 201 Created
    """
    data = request.get_json()
    
    # Validación simple del payload
    if not data or 'nombre' not in data or 'descripcion' not in data or 'precio' not in data:
        abort(400, description="Payload inválido. Faltan 'nombre', 'descripcion', o 'precio'.")

    try:
        # Re-implementamos la lógica de 'insertar_juego' del controlador
        # para poder obtener el objeto 'juego' creado (con su ID)
        # y devolverlo en la respuesta.
        juego = Juegos(
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            precio=data['precio']
        )
        db.session.add(juego)
        db.session.commit()
        
        # Devolvemos el objeto recién creado
        return jsonify(_juego_to_dict(juego)), 201  # 201 Created
    
    except Exception as e:
        db.session.rollback()
        abort(400, description=f"Error al crear el juego: {str(e)}")


# --- Endpoints del Recurso JuegoResource ---

@api.route('/juegos/<int:id>', methods=['GET'])
def get_juego_by_id(id):
    """
    [GET] /api/juegos/<id>
    Obtiene un juego específico por su ID.
    Respuesta: 200 OK o 404 Not Found
    """
    juego = controllers.obtener_juego_por_id(id)
    if not juego:
        abort(404, description=f"Juego con id {id} no encontrado.")
    
    return jsonify(_juego_to_dict(juego)), 200


@api.route('/juegos/<int:id>', methods=['PUT'])
def update_juego(id):
    """
    [PUT] /api/juegos/<id>
    Actualiza un juego existente por su ID.
    Respuesta: 200 OK o 404 Not Found
    """
    # Primero, verificamos que el juego exista
    juego_existe = controllers.obtener_juego_por_id(id)
    if not juego_existe:
        abort(404, description=f"Juego con id {id} no encontrado.")
        
    data = request.get_json()
    
    # Validación
    if not data or 'nombre' not in data or 'descripcion' not in data or 'precio' not in data:
        abort(400, description="Payload inválido. Faltan 'nombre', 'descripcion', o 'precio'.")

    try:
        # Usamos el controlador para actualizar
        controllers.actualizar_juego(
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            precio=data['precio'],
            id=id
        )
        
        # Obtenemos el juego ya actualizado para devolverlo
        juego_actualizado = controllers.obtener_juego_por_id(id)
        return jsonify(_juego_to_dict(juego_actualizado)), 200
        
    except Exception as e:
        db.session.rollback()
        abort(400, description=f"Error al actualizar el juego: {str(e)}")


@api.route('/juegos/<int:id>', methods=['DELETE'])
def delete_juego(id):
    """
    [DELETE] /api/juegos/<id>
    Elimina un juego por su ID.
    Respuesta: 204 No Content o 404 Not Found
    """
    # Verificamos que el juego exista
    juego = controllers.obtener_juego_por_id(id)
    if not juego:
        abort(404, description=f"Juego con id {id} no encontrado.")
        
    try:
        # Usamos el controlador para eliminar
        controllers.eliminar_juego(id)
        return '', 204  # 204 No Content
    
    except Exception as e:
        db.session.rollback()
        abort(400, description=f"Error al eliminar el juego: {str(e)}")