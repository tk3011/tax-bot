from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import bcrypt

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True)
    password_hash = Column(String(200))
    firm_name = Column(String(200))
    agent_code = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Receipt(Base):
    __tablename__ = "receipts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Float)
    vendor = Column(String(200))
    date = Column(String(20))
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    name = Column(String(200))
    email = Column(String(200))
    tfn = Column(String(9))
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

# Create database
engine = create_engine("sqlite:///tax_bot.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_db():
    return Session()
