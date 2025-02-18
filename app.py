from flask import Flask, request, jsonify
from models import db, Proveedor
import requests
from datetime import datetime
import os
import csv  # Asegúrate de importar el módulo csv

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///proveedores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def get_dolar_oficial():
    try:
        response = requests.get('https://dolarapi.com/v1/dolares/oficial')
        data = response.json()
        return data['venta']  # Usamos el valor de venta del dólar oficial
    except Exception as e:
        print(f"Error al obtener cotización del dólar: {e}")
        return None

def actualizar_csv():
    proveedores = Proveedor.query.all()  # Obtiene todos los proveedores existentes
    with open('proveedores_actualizados.csv', mode='w', newline='') as file:  # Cambia a modo 'w' para sobrescribir
        writer = csv.writer(file)
        writer.writerow(['ID', 'Nombre', 'Código', 'Mail', 'Deuda Pesos', 'Deuda Dólares', 'Fecha Actualización'])  # Escribe encabezados
        for proveedor in proveedores:
            writer.writerow([proveedor.id, proveedor.nombre, proveedor.codigo, proveedor.mail, proveedor.deuda_pesos, proveedor.deuda_dolares, proveedor.fecha_actualizacion])

@app.route('/proveedores', methods=['GET'])
def get_proveedores():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    proveedores = Proveedor.query.paginate(page=page, per_page=per_page)
    return jsonify({
        'proveedores': [p.to_dict() for p in proveedores.items],
        'total': proveedores.total,
        'pages': proveedores.pages,
        'current_page': proveedores.page
    })

@app.route('/proveedores/<int:id>', methods=['GET'])
def get_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    return jsonify(proveedor.to_dict())

@app.route('/proveedores', methods=['POST'])
def create_proveedor():
    data = request.get_json()
    
    # Validar datos requeridos
    required_fields = ['nombre', 'codigo', 'mail', 'deuda_pesos']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es requerido'}), 400
    
    # Obtener cotización del dólar
    dolar_valor = get_dolar_oficial()
    if dolar_valor is None:
        return jsonify({'error': 'No se pudo obtener la cotización del dólar'}), 500
    
    # Calcular deuda en dólares
    deuda_dolares = float(data['deuda_pesos']) / dolar_valor
    
    nuevo_proveedor = Proveedor(
        nombre=data['nombre'],
        codigo=data['codigo'],
        mail=data['mail'],
        deuda_pesos=data['deuda_pesos'],
        deuda_dolares=deuda_dolares,
        fecha_actualizacion=datetime.utcnow()
    )
    
    try:
        db.session.add(nuevo_proveedor)
        db.session.commit()
        actualizar_csv()  # Llama a la función para actualizar el CSV
        return jsonify(nuevo_proveedor.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/proveedores/<int:id>', methods=['PUT'])
def update_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    data = request.get_json()
    
    if 'deuda_pesos' in data:
        dolar_valor = get_dolar_oficial()
        if dolar_valor is None:
            return jsonify({'error': 'No se pudo obtener la cotización del dólar'}), 500
        data['deuda_dolares'] = float(data['deuda_pesos']) / dolar_valor
        data['fecha_actualizacion'] = datetime.utcnow()
    
    for key, value in data.items():
        if hasattr(proveedor, key):
            setattr(proveedor, key, value)
    
    try:
        db.session.commit()
        actualizar_csv()  # Llama a la función para actualizar el CSV
        return jsonify(proveedor.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/proveedores/<int:id>', methods=['DELETE'])
def delete_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    try:
        db.session.delete(proveedor)
        db.session.commit()
        actualizar_csv()  # Llama a la función para actualizar el CSV
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/proveedores/search', methods=['GET'])
def search_proveedores():
    nombre = request.args.get('nombre')
    codigo = request.args.get('codigo')
    
    query = Proveedor.query
    if nombre:
        query = query.filter(Proveedor.nombre.ilike(f'%{nombre}%'))
    if codigo:
        query = query.filter(Proveedor.codigo.ilike(f'%{codigo}%'))
    
    proveedores = query.all()
    return jsonify([p.to_dict() for p in proveedores])

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

