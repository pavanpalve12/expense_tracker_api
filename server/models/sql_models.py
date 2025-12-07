from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from server.db.connect_db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # You can seed dummy values for dev
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    expenses = relationship(argument="Expense", back_populates="users", cascade="all, delete-orphan")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    amount =  Column(Numeric(precision=10, scale=2), nullable=False)
    description = Column(type_=Text, nullable=True)
    date = Column(Date, nullable=False, index=True)

    created_at = Column(type_=DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(type_=DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(type_=DateTime, nullable=True)

    users = relationship(argument="User", back_populates="expenses")