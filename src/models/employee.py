from src import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)  # システムで使う番号
    password = db.Column(db.String(25))
    name = db.Column(db.String(255), nullable=False, unique=True)  # 社員名
    dates = relationship("EmployeeDate", back_populates="employee")

class EmployeeDate(db.Model):
    __tablename__ = 'employee_date'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    employee = relationship("Employee", back_populates="dates")
    day = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    shift = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)  # 作成日時
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)  # 更新日時