from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()  # Esto define la base de datos

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    mail = db.Column(db.String(120), nullable=False)
    deuda_pesos = db.Column(db.Float, nullable=False)
    deuda_dolares = db.Column(db.Float)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'codigo': self.codigo,
            'mail': self.mail,
            'deuda_pesos': self.deuda_pesos,
            'deuda_dolares': self.deuda_dolares,
            'fecha_actualizacion': self.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S')
        }
