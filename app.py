from flask import Flask, jsonify, request
app = Flask(__name__)

productos = [
    {"id": 1, "nombre": "Laptop", "precio": 1200, "stock": 5},
    {"id": 2, "nombre": "Mouse", "precio": 25, "stock": 0},
    {"id": 3, "nombre": "Teclado", "precio": 80, "stock": 12}
]

@app.route('/productos', methods=['GET'])
def get_productos():
    return jsonify(productos), 200

@app.route('/productos/<int:id>', methods=['GET'])
def get_producto(id):
    for producto in productos:
        if producto['id'] == id:
            return jsonify(producto), 200
    return jsonify({"error": "Producto no encontrado"}), 404


@app.route('/productos', methods=['POST'])
def crear_producto():
    datos= request.get_json()

    if not datos.get('nombre'):
        return jsonify({"error": "El nombre es obligatorio"}), 400
    
    if not datos.get('precio') or datos['precio'] <= 0:
        return jsonify({"error": "El precio es invalido"}), 400
    
    nuevo_id= max(p['id'] for p in productos)+1

    nuevo_producto= {
        "id": nuevo_id,
        "nombre": datos['nombre'],
        "precio": datos['precio'],
        "stock": datos.get('stock',0)
    }

    productos.append(nuevo_producto)
    return jsonify(nuevo_producto), 201

@app.route('/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):

    datos= request.get_json()
    for producto in productos:
        if producto['id'] == id:
            producto['nombre'] = datos.get('nombre', producto['nombre'])
            producto['precio'] = datos.get('precio', producto['precio'])
            producto['stock'] = datos.get ('stock', producto['stock'])

            

            return jsonify(producto), 200
        
    return jsonify({"error": "No existe el producto con ese id"}), 404


@app.route('/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    for producto in productos:
        if producto['id']==id:
            productos.remove(producto)

            return jsonify({"exito": "Producto eliminado exitosamente"}), 200
        
    return jsonify({"error": "El id ingresado no existe en la lista de productos"}), 404


if __name__ == '__main__':
    app.run(debug=True)