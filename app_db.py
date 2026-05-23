# API REST de productos - Elias Silvera
from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('productos.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/productos', methods=['GET'])
def get_productos():
    conn = get_db()
    productos = conn.execute('SELECT * FROM productos').fetchall()
    conn.close()
    return jsonify([dict(p) for p in productos]), 200

@app.route('/productos/<int:id>', methods=['GET'])
def get_producto(id):
    conn = get_db()
    producto = conn.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
    conn.close()
    if producto is None:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(dict(producto)), 200

@app.route('/productos', methods=['POST'])
def crear_producto():
    datos = request.get_json()
    if not datos.get('nombre'):
        return jsonify({"error": "El nombre es obligatorio"}), 400
    if not datos.get('precio') or datos['precio'] < 0:
        return jsonify({"error": "El precio es inválido"}), 400
    conn = get_db()
    cursor = conn.execute(
        'INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)',
        (datos['nombre'], datos['precio'], datos.get('stock', 0))
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": nuevo_id, "nombre": datos['nombre'], "precio": datos['precio'], "stock": datos.get('stock', 0)}), 201

@app.route('/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):
    conn = get_db()
    producto = conn.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
    if producto is None:
        conn.close()
        return jsonify({"error": "Producto no encontrado"}), 404
    datos = request.get_json()
    conn.execute(
        'UPDATE productos SET nombre = ?, precio = ?, stock = ? WHERE id = ?',
        (
            datos.get('nombre', producto['nombre']),
            datos.get('precio', producto['precio']),
            datos.get('stock', producto['stock']),
            id
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"id": id, "nombre": datos.get('nombre', producto['nombre']), "precio": datos.get('precio', producto['precio']), "stock": datos.get('stock', producto['stock'])}), 200

@app.route('/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    conn = get_db()
    producto = conn.execute('SELECT * FROM productos WHERE id = ?', (id,)).fetchone()
    if producto is None:
        conn.close()
        return jsonify({"error": "Producto no encontrado"}), 404
    conn.execute('DELETE FROM productos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"exito": "Producto eliminado"}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)