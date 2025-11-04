# -*- coding: utf-8 -*-
"""
Modelos de dados específicos para o projeto DAC
Classes Python para representação orientada a objetos dos dados da pesquisa TIC Domicílios
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Domicilio(Base):
    """
    Classe para representar domicílios da pesquisa TIC Domicílios
    Corresponde à tabela TB_DOMICILIO no banco de dados
    """
    __tablename__ = 'TB_DOMICILIO'
    
    # Atributos conforme especificação
    id_domicilio = Column(Integer, primary_key=True, autoincrement=True)
    regiao = Column(String(50), nullable=False, index=True)  # Ex: "Nordeste", "Sul"
    area = Column(String(20), nullable=False, index=True)    # Ex: "Urbana", "Rural"
    renda_familiar = Column(String(50), nullable=False, index=True)  # Ex: "Até 1 salário mínimo"
    possui_internet = Column(Boolean, default=False, nullable=False)
    tipo_conexao = Column(String(50), nullable=True)  # Ex: "Banda larga fixa", "Móvel 3G/4G"
    possui_computador = Column(Boolean, default=False, nullable=False)
    
    # Relacionamento com moradores
    moradores = relationship("Morador", back_populates="domicilio")
    
    # Índices para otimização
    __table_args__ = (
        Index('idx_domicilio_regiao', 'regiao'),
        Index('idx_domicilio_area_renda', 'area', 'renda_familiar'),
        Index('idx_domicilio_internet', 'possui_internet'),
    )
    
    def __repr__(self):
        return f"<Domicilio(id={self.id_domicilio}, regiao='{self.regiao}', area='{self.area}')>"
    
    def __init__(self, regiao, area, renda_familiar, possui_internet=False, tipo_conexao=None, possui_computador=False):
        self.regiao = regiao
        self.area = area
        self.renda_familiar = renda_familiar
        self.possui_internet = possui_internet
        self.tipo_conexao = tipo_conexao
        self.possui_computador = possui_computador

class Morador(Base):
    """
    Classe para representar moradores dos domicílios
    Corresponde à tabela TB_MORADOR no banco de dados
    """
    __tablename__ = 'TB_MORADOR'
    
    # Atributos conforme especificação
    id_morador = Column(Integer, primary_key=True, autoincrement=True)
    id_domicilio_fk = Column(Integer, ForeignKey('TB_DOMICILIO.id_domicilio'), nullable=False, index=True)
    faixa_etaria = Column(String(30), nullable=False, index=True)  # Ex: "60 anos ou mais"
    escolaridade = Column(String(50), nullable=False, index=True)  # Ex: "Ensino médio completo"
    possui_deficiencia = Column(Boolean, default=False, nullable=False)
    habilidades_digitais = Column(String(20), nullable=True, index=True)  # Ex: "Básica", "Avançada"
    
    # Relacionamento com domicílio
    domicilio = relationship("Domicilio", back_populates="moradores")
    
    # Índices para otimização
    __table_args__ = (
        Index('idx_morador_faixa_etaria', 'faixa_etaria'),
        Index('idx_morador_deficiencia', 'possui_deficiencia'),
        Index('idx_morador_domicilio_idade', 'id_domicilio_fk', 'faixa_etaria'),
        Index('idx_morador_escolaridade', 'escolaridade'),
    )
    
    def __repr__(self):
        return f"<Morador(id={self.id_morador}, faixa_etaria='{self.faixa_etaria}', possui_deficiencia={self.possui_deficiencia})>"
    
    def __init__(self, id_domicilio_fk, faixa_etaria, escolaridade, possui_deficiencia=False, habilidades_digitais=None):
        self.id_domicilio_fk = id_domicilio_fk
        self.faixa_etaria = faixa_etaria
        self.escolaridade = escolaridade
        self.possui_deficiencia = possui_deficiencia
        self.habilidades_digitais = habilidades_digitais

# Métodos auxiliares para análise de vulnerabilidade digital
class AnaliseVulnerabilidade:
    """
    Classe auxiliar para análise de vulnerabilidade digital
    """
    
    @staticmethod
    def identificar_vulneraveis(session):
        """
        Identifica moradores em situação de vulnerabilidade digital
        Critérios: idosos (60+) + baixa renda (até 1 salário mínimo)
        """
        from sqlalchemy.orm import sessionmaker
        
        vulneraveis = session.query(Morador, Domicilio).join(
            Domicilio, Morador.id_domicilio_fk == Domicilio.id_domicilio
        ).filter(
            Morador.faixa_etaria == '60 anos ou mais',
            Domicilio.renda_familiar == 'Até 1 salário mínimo'
        ).all()
        
        return vulneraveis
    
    @staticmethod
    def estatisticas_acesso_internet(session):
        """
        Calcula estatísticas de acesso à internet por região
        """
        from sqlalchemy import func
        
        stats = session.query(
            Domicilio.regiao,
            func.count(Domicilio.id_domicilio).label('total_domicilios'),
            func.sum(func.cast(Domicilio.possui_internet, Integer)).label('com_internet')
        ).group_by(Domicilio.regiao).all()
        
        return stats