from flask_restful import Resource, Api
from flask import request
from models import db, Proveedor
from app import app

api = Api(app)

class ProveedorResource(Resource):
    def get(self):
        proveedores = Proveedor.query.all()
        return [{'id': p.id, 'nombre': p.nombre, 'contacto': p.contacto, 'telefono': p.telefono, 'direccion': p.direccion} for p in proveedores]

    def post(self):
        data = request.get_json()
        nuevo_proveedor = Proveedor(
            nombre=data['nombre'],
            contacto=data.get('contacto'),
            telefono=data.get('telefono'),
            direccion=data.get('direccion')
        )
        db.session.add(nuevo_proveedor)
        db.session.commit()
        return {'message': 'Proveedor creado exitosamente'}, 201

api.add_resource(ProveedorResource, '/proveedores')


class AlertaStockResource(Resource):
    def get(self):
        productos_bajos = Producto.query.filter(Producto.stock < 5).all()
        return [{'id': p.id, 'nombre': p.nombre, 'stock': p.stock} for p in productos_bajos]

api.add_resource(AlertaStockResource, '/alerta-stock')


class ProductosMasVendidosResource(Resource):
    def get(self):
        productos = Producto.query.order_by(Producto.ventas_totales.desc()).limit(5).all()
        return [{'id': p.id, 'nombre': p.nombre, 'ventas_totales': p.ventas_totales} for p in productos]

api.add_resource(ProductosMasVendidosResource, '/productos-mas-vendidos')
