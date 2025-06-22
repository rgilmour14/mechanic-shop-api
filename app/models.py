from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List
from datetime import datetime


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)


class Customer(Base):
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(15), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)
    
    tickets: Mapped[List['Ticket']] = db.relationship(back_populates='customer')
    
class Ticket(Base):
    __tablename__ = 'tickets'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(17), nullable=False, unique=True)
    service_date: Mapped[str] = mapped_column(db.String(10), nullable=False)  # Format: MM-DD-YYYY
    service_desc: Mapped[str] = mapped_column(db.String(500), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'), nullable=False)
    
    customer: Mapped["Customer"] = db.relationship(back_populates="tickets")
    mechanic_tickets:  Mapped[List["MechanicServiceTicket"]] = db.relationship(back_populates="ticket")
    ticket_parts: Mapped[List["TicketParts"]] = db.relationship(back_populates="ticket")


class Mechanic(Base):
    __tablename__ = 'mechanics'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(15), nullable=False, unique=True)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)
    
    mechanic_tickets:  Mapped[List["MechanicServiceTicket"]] = db.relationship(back_populates="mechanic")
    
class MechanicServiceTicket(Base):
    __tablename__ = 'mechanic_service_ticket'

    id: Mapped[int] = mapped_column(primary_key=True)
    mechanic_id: Mapped[int] = mapped_column(db.ForeignKey("mechanics.id"), nullable=False)
    ticket_id: Mapped[int] = mapped_column(db.ForeignKey("tickets.id"), nullable=False)
    start_date = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow)

    mechanic: Mapped["Mechanic"] = relationship(back_populates="mechanic_tickets")
    ticket: Mapped["Ticket"] = relationship(back_populates="mechanic_tickets")
    
class Inventory(Base):
    __tablename__ = 'inventory'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    
    ticket_parts: Mapped[List["TicketParts"]] = db.relationship(back_populates="part")
    
class TicketParts(Base):
    __tablename__ = 'ticket_parts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(db.ForeignKey("tickets.id"), nullable=False)
    part_id: Mapped[int] = mapped_column(db.ForeignKey("inventory.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False, default=1)
    
    ticket: Mapped["Ticket"] = relationship(back_populates="ticket_parts")
    part: Mapped["Inventory"] = relationship(back_populates="ticket_parts")

    
