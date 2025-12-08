from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text, func, Boolean
from sqlalchemy.orm import relationship
from server.db.connect_db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # You can seed dummy values for dev
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    last_logout = Column(DateTime, nullable=True)

    expenses = relationship(argument="Expense", back_populates="users", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="users", cascade="all, delete-orphan")

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

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    # id, user_id, token_hash, created_at, expires_at, revoked, jti, user_agent, ip_address

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(column="users.id", ondelete="CASCADE"), nullable=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)

    jti = Column(String(64), nullable=True, index=True)

    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(64), nullable=True)

    users = relationship(argument="User", back_populates="refresh_tokens")