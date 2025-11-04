# -*- coding: utf-8 -*-
"""
Modelos de dados SQLAlchemy para o sistema DAC
Baseado na arquitetura técnica documentada
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Region(Base):
    """Modelo para regiões geográficas"""
    __tablename__ = 'regions'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    state = Column(String(50), nullable=False, index=True)
    macro_region = Column(String(20), nullable=False, index=True)
    description = Column(String(200))  # Campo usado no database_manager
    
    # Relacionamentos
    households = relationship("Household", back_populates="region")
    
    def __repr__(self):
        return f"<Region(code='{self.code}', name='{self.name}')>"

class Household(Base):
    """Modelo para domicílios"""
    __tablename__ = 'households'
    
    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    area_type = Column(String(20), nullable=False, index=True)  # urbana/rural
    income_range = Column(String(50), index=True)
    household_size = Column(Integer, default=1, index=True)  # Campo usado no database_manager
    has_internet = Column(Boolean, default=False, index=True)  # Acesso à internet no domicílio
    
    # Relacionamentos
    region = relationship("Region", back_populates="households")
    individuals = relationship("Individual", back_populates="household")
    
    # Índices compostos para consultas comuns
    __table_args__ = (
        Index('idx_household_region_area', 'region_id', 'area_type'),
        Index('idx_household_city_income', 'city', 'income_range'),
        Index('idx_household_internet_area', 'has_internet', 'area_type'),
    )
    
    def __repr__(self):
        return f"<Household(id={self.id}, city='{self.city}', area_type='{self.area_type}')>"

class Individual(Base):
    """Modelo para indivíduos"""
    __tablename__ = 'individuals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey('households.id'), nullable=False, index=True)
    age = Column(Integer, nullable=True, index=True)
    gender = Column(String(10), nullable=True, index=True)  # 'masculino', 'feminino', 'outro'
    education_level = Column(String(50), nullable=True, index=True)
    has_disability = Column(Boolean, default=False, index=True)
    employment_status = Column(String(30), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relacionamentos
    household = relationship("Household", back_populates="individuals")
    device_usage = relationship("DeviceUsage", back_populates="individual")
    internet_usage = relationship("InternetUsage", back_populates="individual")
    
    # Índices compostos para consultas comuns
    __table_args__ = (
        Index('idx_individual_age_gender', 'age', 'gender'),
        Index('idx_individual_disability_age', 'has_disability', 'age'),
        Index('idx_individual_household_gender', 'household_id', 'gender'),
    )
    
    def __repr__(self):
        return f"<Individual(id={self.id}, age={self.age}, has_disability={self.has_disability})>"

class DeviceUsage(Base):
    """Modelo para uso de dispositivos"""
    __tablename__ = 'device_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    individual_id = Column(Integer, ForeignKey('individuals.id'), nullable=False, index=True)
    device_type = Column(String(30), nullable=False, index=True)
    has_device = Column(Boolean, default=False, index=True)  # Corrigido para has_device
    usage_frequency = Column(String(20), nullable=True, index=True)
    access_location = Column(String(30), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relacionamentos
    individual = relationship("Individual", back_populates="device_usage")
    
    # Índices compostos para consultas comuns
    __table_args__ = (
        Index('idx_device_type_access', 'device_type', 'has_device'),
        Index('idx_device_individual_type', 'individual_id', 'device_type'),
        Index('idx_device_access_frequency', 'has_device', 'usage_frequency'),
    )
    
    def __repr__(self):
        return f"<DeviceUsage(id={self.id}, device_type='{self.device_type}', has_device={self.has_device})>"

class InternetUsage(Base):
    """Modelo para uso da internet"""
    __tablename__ = 'internet_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    individual_id = Column(Integer, ForeignKey('individuals.id'), nullable=False, index=True)
    uses_internet = Column(Boolean, default=False, index=True)  # Corrigido para uses_internet
    access_frequency = Column(String(30), nullable=True, index=True)  # Corrigido para access_frequency
    main_activities = Column(Text, nullable=True)  # Corrigido para main_activities
    barriers_to_access = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relacionamentos
    individual = relationship("Individual", back_populates="internet_usage")
    
    # Índices compostos para consultas comuns
    __table_args__ = (
        Index('idx_internet_access_frequency', 'uses_internet', 'access_frequency'),
        Index('idx_internet_individual_access', 'individual_id', 'uses_internet'),
    )
    
    def __repr__(self):
        return f"<InternetUsage(id={self.id}, uses_internet={self.uses_internet})>"