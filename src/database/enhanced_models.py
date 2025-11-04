# -*- coding: utf-8 -*-
"""
Modelos de dados SQLAlchemy expandidos para o sistema DAC
Incorpora novos campos para dados extraídos de imagens OCR
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey, Index, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Region(Base):
    """Modelo expandido para regiões geográficas"""
    __tablename__ = 'regions'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    state = Column(String(50), nullable=False, index=True)
    macro_region = Column(String(20), nullable=False, index=True)
    description = Column(String(200))
    
    # Novos campos expandidos
    population = Column(Integer, nullable=True)
    area_km2 = Column(Float, nullable=True)
    urban_population_percentage = Column(Float, nullable=True)
    rural_population_percentage = Column(Float, nullable=True)
    economic_indicators = Column(JSON, nullable=True)  # Indicadores econômicos
    
    # Relacionamentos
    households = relationship("Household", back_populates="region")
    extracted_data = relationship("ExtractedData", back_populates="region")
    
    def __repr__(self):
        return f"<Region(code='{self.code}', name='{self.name}')>"

class Household(Base):
    """Modelo expandido para domicílios"""
    __tablename__ = 'households'
    
    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    area_type = Column(String(20), nullable=False, index=True)  # urbana/rural
    income_range = Column(String(50), index=True)
    household_size = Column(Integer, default=1, index=True)
    has_internet = Column(Boolean, default=False, index=True)
    
    # Novos campos expandidos
    income_value_min = Column(Float, nullable=True)  # Valor mínimo da faixa de renda
    income_value_max = Column(Float, nullable=True)  # Valor máximo da faixa de renda
    housing_type = Column(String(50), nullable=True)  # Tipo de moradia
    housing_ownership = Column(String(30), nullable=True)  # Própria, alugada, etc.
    basic_services = Column(JSON, nullable=True)  # Água, luz, esgoto, etc.
    internet_type = Column(String(50), nullable=True)  # Banda larga, móvel, etc.
    internet_speed = Column(String(30), nullable=True)  # Velocidade da internet
    digital_devices_count = Column(Integer, default=0)  # Quantidade de dispositivos
    monthly_internet_cost = Column(Float, nullable=True)  # Custo mensal da internet
    internet_barriers = Column(Text, nullable=True)  # Barreiras de acesso
    
    # Metadados de extração
    data_source = Column(String(50), default='image_ocr')  # Fonte dos dados
    extraction_confidence = Column(Float, nullable=True)  # Confiança da extração
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    region = relationship("Region", back_populates="households")
    individuals = relationship("Individual", back_populates="household")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_household_region_area', 'region_id', 'area_type'),
        Index('idx_household_city_income', 'city', 'income_range'),
        Index('idx_household_internet_area', 'has_internet', 'area_type'),
        Index('idx_household_income_values', 'income_value_min', 'income_value_max'),
        Index('idx_household_devices_internet', 'digital_devices_count', 'has_internet'),
    )
    
    def __repr__(self):
        return f"<Household(id={self.id}, city='{self.city}', area_type='{self.area_type}')>"

class Individual(Base):
    """Modelo expandido para indivíduos"""
    __tablename__ = 'individuals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    household_id = Column(Integer, ForeignKey('households.id'), nullable=False, index=True)
    age = Column(Integer, nullable=True, index=True)
    gender = Column(String(10), nullable=True, index=True)
    education_level = Column(String(50), nullable=True, index=True)
    has_disability = Column(Boolean, default=False, index=True)
    employment_status = Column(String(30), nullable=True, index=True)
    
    # Novos campos expandidos
    age_range = Column(String(20), nullable=True, index=True)  # Faixa etária padronizada
    education_years = Column(Integer, nullable=True)  # Anos de estudo
    occupation = Column(String(100), nullable=True)  # Ocupação específica
    monthly_income = Column(Float, nullable=True)  # Renda individual
    disability_type = Column(String(50), nullable=True)  # Tipo de deficiência
    disability_severity = Column(String(20), nullable=True)  # Severidade da deficiência
    digital_literacy_level = Column(String(30), nullable=True)  # Nível de alfabetização digital
    internet_usage_frequency = Column(String(30), nullable=True)  # Frequência de uso
    main_internet_activities = Column(Text, nullable=True)  # Principais atividades online
    digital_skills = Column(JSON, nullable=True)  # Habilidades digitais específicas
    barriers_to_internet = Column(Text, nullable=True)  # Barreiras específicas
    
    # Metadados de extração
    data_source = Column(String(50), default='image_ocr')
    extraction_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    household = relationship("Household", back_populates="individuals")
    device_usage = relationship("DeviceUsage", back_populates="individual")
    internet_usage = relationship("InternetUsage", back_populates="individual")
    accessibility_needs = relationship("AccessibilityNeed", back_populates="individual")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_individual_age_gender', 'age', 'gender'),
        Index('idx_individual_disability_age', 'has_disability', 'age'),
        Index('idx_individual_household_gender', 'household_id', 'gender'),
        Index('idx_individual_education_employment', 'education_level', 'employment_status'),
        Index('idx_individual_digital_literacy', 'digital_literacy_level', 'internet_usage_frequency'),
        Index('idx_individual_age_range', 'age_range'),
    )
    
    def __repr__(self):
        return f"<Individual(id={self.id}, age={self.age}, has_disability={self.has_disability})>"

class DeviceUsage(Base):
    """Modelo expandido para uso de dispositivos"""
    __tablename__ = 'device_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    individual_id = Column(Integer, ForeignKey('individuals.id'), nullable=False, index=True)
    device_type = Column(String(30), nullable=False, index=True)
    has_device = Column(Boolean, default=False, index=True)
    usage_frequency = Column(String(20), nullable=True, index=True)
    access_location = Column(String(30), nullable=True, index=True)
    
    # Novos campos expandidos
    device_brand = Column(String(50), nullable=True)  # Marca do dispositivo
    device_model = Column(String(100), nullable=True)  # Modelo específico
    device_age_years = Column(Integer, nullable=True)  # Idade do dispositivo
    device_condition = Column(String(20), nullable=True)  # Estado do dispositivo
    acquisition_method = Column(String(30), nullable=True)  # Como adquiriu
    sharing_with_others = Column(Boolean, default=False)  # Compartilha com outros
    main_usage_purposes = Column(Text, nullable=True)  # Principais usos
    technical_issues = Column(Text, nullable=True)  # Problemas técnicos
    replacement_needs = Column(Boolean, default=False)  # Precisa substituir
    cost_barrier = Column(Boolean, default=False)  # Barreira de custo
    
    # Metadados de extração
    data_source = Column(String(50), default='image_ocr')
    extraction_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    individual = relationship("Individual", back_populates="device_usage")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_device_type_access', 'device_type', 'has_device'),
        Index('idx_device_individual_type', 'individual_id', 'device_type'),
        Index('idx_device_access_frequency', 'has_device', 'usage_frequency'),
        Index('idx_device_sharing_condition', 'sharing_with_others', 'device_condition'),
        Index('idx_device_barriers', 'cost_barrier', 'replacement_needs'),
    )
    
    def __repr__(self):
        return f"<DeviceUsage(id={self.id}, device_type='{self.device_type}', has_device={self.has_device})>"

class InternetUsage(Base):
    """Modelo expandido para uso de internet"""
    __tablename__ = 'internet_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    individual_id = Column(Integer, ForeignKey('individuals.id'), nullable=False, index=True)
    uses_internet = Column(Boolean, default=False, index=True)
    access_frequency = Column(String(30), nullable=True, index=True)
    main_activities = Column(Text, nullable=True)
    barriers_to_access = Column(Text, nullable=True)
    
    # Novos campos expandidos
    first_access_age = Column(Integer, nullable=True)  # Idade do primeiro acesso
    years_using_internet = Column(Integer, nullable=True)  # Anos de uso
    daily_usage_hours = Column(Float, nullable=True)  # Horas diárias de uso
    preferred_access_device = Column(String(30), nullable=True)  # Dispositivo preferido
    internet_skills_level = Column(String(20), nullable=True)  # Nível de habilidades
    online_services_used = Column(JSON, nullable=True)  # Serviços online utilizados
    social_media_usage = Column(JSON, nullable=True)  # Uso de redes sociais
    ecommerce_usage = Column(Boolean, default=False)  # Usa e-commerce
    online_banking = Column(Boolean, default=False)  # Usa banco online
    online_education = Column(Boolean, default=False)  # Usa educação online
    telehealth_usage = Column(Boolean, default=False)  # Usa telemedicina
    government_services_online = Column(Boolean, default=False)  # Serviços gov. online
    privacy_concerns = Column(Text, nullable=True)  # Preocupações com privacidade
    security_knowledge = Column(String(20), nullable=True)  # Conhecimento de segurança
    
    # Barreiras específicas
    cost_barrier = Column(Boolean, default=False)  # Barreira de custo
    infrastructure_barrier = Column(Boolean, default=False)  # Barreira de infraestrutura
    skills_barrier = Column(Boolean, default=False)  # Barreira de habilidades
    accessibility_barrier = Column(Boolean, default=False)  # Barreira de acessibilidade
    content_barrier = Column(Boolean, default=False)  # Barreira de conteúdo relevante
    
    # Metadados de extração
    data_source = Column(String(50), default='image_ocr')
    extraction_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    individual = relationship("Individual", back_populates="internet_usage")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_internet_access_frequency', 'uses_internet', 'access_frequency'),
        Index('idx_internet_individual_access', 'individual_id', 'uses_internet'),
        Index('idx_internet_skills_usage', 'internet_skills_level', 'daily_usage_hours'),
        Index('idx_internet_services', 'ecommerce_usage', 'online_banking', 'online_education'),
        Index('idx_internet_barriers', 'cost_barrier', 'infrastructure_barrier', 'skills_barrier'),
    )
    
    def __repr__(self):
        return f"<InternetUsage(id={self.id}, uses_internet={self.uses_internet})>"

class AccessibilityNeed(Base):
    """Novo modelo para necessidades de acessibilidade"""
    __tablename__ = 'accessibility_needs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    individual_id = Column(Integer, ForeignKey('individuals.id'), nullable=False, index=True)
    
    # Tipos de necessidades
    visual_impairment = Column(Boolean, default=False, index=True)
    hearing_impairment = Column(Boolean, default=False, index=True)
    motor_impairment = Column(Boolean, default=False, index=True)
    cognitive_impairment = Column(Boolean, default=False, index=True)
    multiple_impairments = Column(Boolean, default=False, index=True)
    
    # Severidade e detalhes
    impairment_severity = Column(String(20), nullable=True)  # Leve, moderada, severa
    assistive_technology_used = Column(JSON, nullable=True)  # Tecnologias assistivas
    accessibility_features_needed = Column(JSON, nullable=True)  # Recursos necessários
    digital_accessibility_barriers = Column(Text, nullable=True)  # Barreiras digitais
    support_person_needed = Column(Boolean, default=False)  # Precisa de ajuda
    
    # Adaptações utilizadas
    screen_reader = Column(Boolean, default=False)
    voice_recognition = Column(Boolean, default=False)
    large_text = Column(Boolean, default=False)
    high_contrast = Column(Boolean, default=False)
    keyboard_navigation = Column(Boolean, default=False)
    alternative_input_devices = Column(Boolean, default=False)
    
    # Metadados
    data_source = Column(String(50), default='image_ocr')
    extraction_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    individual = relationship("Individual", back_populates="accessibility_needs")
    
    # Índices
    __table_args__ = (
        Index('idx_accessibility_visual', 'visual_impairment'),
        Index('idx_accessibility_hearing', 'hearing_impairment'),
        Index('idx_accessibility_motor', 'motor_impairment'),
        Index('idx_accessibility_cognitive', 'cognitive_impairment'),
        Index('idx_accessibility_multiple', 'multiple_impairments'),
        Index('idx_accessibility_severity', 'impairment_severity'),
    )
    
    def __repr__(self):
        return f"<AccessibilityNeed(id={self.id}, individual_id={self.individual_id})>"

class ExtractedData(Base):
    """Novo modelo para dados brutos extraídos das imagens"""
    __tablename__ = 'extracted_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Informações da fonte
    source_file = Column(String(255), nullable=False, index=True)
    source_year = Column(Integer, nullable=False, index=True)
    page_number = Column(Integer, nullable=True)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=True, index=True)
    
    # Dados extraídos
    category = Column(String(50), nullable=False, index=True)  # household, individual, etc.
    subcategory = Column(String(50), nullable=True, index=True)
    extracted_text = Column(Text, nullable=False)
    structured_data = Column(JSON, nullable=True)  # Dados estruturados
    
    # Valores numéricos
    numeric_value = Column(Float, nullable=True, index=True)
    percentage_value = Column(Float, nullable=True, index=True)
    unit = Column(String(20), nullable=True)  # count, percentage, etc.
    
    # Contexto e qualidade
    context_text = Column(Text, nullable=True)  # Texto ao redor
    extraction_confidence = Column(Float, nullable=True, index=True)
    validation_status = Column(String(20), default='pending', index=True)  # pending, validated, rejected
    validation_notes = Column(Text, nullable=True)
    
    # Metadados
    extraction_method = Column(String(50), default='ocr')
    processing_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    region = relationship("Region", back_populates="extracted_data")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_extracted_source_year', 'source_file', 'source_year'),
        Index('idx_extracted_category_year', 'category', 'source_year'),
        Index('idx_extracted_confidence_status', 'extraction_confidence', 'validation_status'),
        Index('idx_extracted_numeric_values', 'numeric_value', 'percentage_value'),
    )
    
    def __repr__(self):
        return f"<ExtractedData(id={self.id}, category='{self.category}', year={self.source_year})>"

class DataQualityMetric(Base):
    """Novo modelo para métricas de qualidade dos dados"""
    __tablename__ = 'data_quality_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identificação
    source_file = Column(String(255), nullable=False, index=True)
    source_year = Column(Integer, nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    
    # Métricas de qualidade
    total_records_extracted = Column(Integer, default=0)
    valid_records = Column(Integer, default=0)
    invalid_records = Column(Integer, default=0)
    duplicate_records = Column(Integer, default=0)
    missing_values_count = Column(Integer, default=0)
    
    # Confiança da extração
    average_confidence = Column(Float, nullable=True)
    min_confidence = Column(Float, nullable=True)
    max_confidence = Column(Float, nullable=True)
    
    # Estatísticas de validação
    manually_validated = Column(Integer, default=0)
    auto_validated = Column(Integer, default=0)
    rejected_records = Column(Integer, default=0)
    
    # Problemas identificados
    ocr_errors_detected = Column(Integer, default=0)
    format_inconsistencies = Column(Integer, default=0)
    outliers_detected = Column(Integer, default=0)
    
    # Metadados
    calculation_timestamp = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Índices
    __table_args__ = (
        Index('idx_quality_source_year', 'source_file', 'source_year'),
        Index('idx_quality_category_year', 'category', 'source_year'),
        Index('idx_quality_confidence', 'average_confidence'),
    )
    
    def __repr__(self):
        return f"<DataQualityMetric(id={self.id}, category='{self.category}', year={self.source_year})>"

class ProcessingLog(Base):
    """Novo modelo para logs de processamento"""
    __tablename__ = 'processing_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Informações do processamento
    process_type = Column(String(50), nullable=False, index=True)  # ocr, validation, migration
    source_file = Column(String(255), nullable=True, index=True)
    status = Column(String(20), nullable=False, index=True)  # started, completed, failed
    
    # Detalhes do processamento
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Resultados
    records_processed = Column(Integer, default=0)
    records_successful = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Mensagens e erros
    success_message = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    warnings = Column(JSON, nullable=True)
    
    # Configurações utilizadas
    processing_config = Column(JSON, nullable=True)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Índices
    __table_args__ = (
        Index('idx_processing_type_status', 'process_type', 'status'),
        Index('idx_processing_start_time', 'start_time'),
        Index('idx_processing_source', 'source_file'),
    )
    
    def __repr__(self):
        return f"<ProcessingLog(id={self.id}, process_type='{self.process_type}', status='{self.status}')>"

# Função para criar todas as tabelas
def create_all_tables(engine):
    """Cria todas as tabelas no banco de dados"""
    Base.metadata.create_all(engine)

# Função para obter todos os modelos
def get_all_models():
    """Retorna todos os modelos definidos"""
    return {
        'Region': Region,
        'Household': Household,
        'Individual': Individual,
        'DeviceUsage': DeviceUsage,
        'InternetUsage': InternetUsage,
        'AccessibilityNeed': AccessibilityNeed,
        'ExtractedData': ExtractedData,
        'DataQualityMetric': DataQualityMetric,
        'ProcessingLog': ProcessingLog
    }