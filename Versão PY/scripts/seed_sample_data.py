# -*- coding: utf-8 -*-
"""
Script para popular o banco de dados com dados de demonstração para testes de consulta.
Execute pelo terminal: python scripts/seed_sample_data.py
"""

from pathlib import Path
import random

import sys
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.database.database_manager import DatabaseManager
from src.database.models import Region, Household, Individual, DeviceUsage, InternetUsage


def seed():
    db = DatabaseManager()
    db.initialize_database()
    session = db.get_session()

    try:
        # Evitar duplicidade: se já houver indivíduos, não semear novamente
        existing = session.query(Individual).count()
        if existing > 0:
            print(f"Banco já possui {existing} indivíduos. Nada a fazer.")
            return

        # Garantir algumas regiões nomeadas
        regions = {
            'Sudeste': ('SE', 'Geral', 'Sudeste'),
            'Nordeste': ('NE', 'Geral', 'Nordeste'),
        }
        region_objs = {}
        for name, (code, state, macro) in regions.items():
            r = session.query(Region).filter_by(name=name).first()
            if not r:
                r = Region(code=code, name=name, state=state, macro_region=macro, description=f'Região {name}')
                session.add(r)
                session.flush()
            region_objs[name] = r

        # Criar domicílios e indivíduos
        people_specs = [
            {"region": 'Sudeste', "city": 'São Paulo', "income": 'R$ 2k-5k', "gender": 'Masculino', "age": 28, "internet": True},
            {"region": 'Sudeste', "city": 'Rio de Janeiro', "income": 'R$ 1k-2k', "gender": 'Feminino', "age": 35, "internet": True},
            {"region": 'Nordeste', "city": 'Recife', "income": 'R$ 1k-2k', "gender": 'feminino', "age": 42, "internet": False},
            {"region": 'Nordeste', "city": 'Fortaleza', "income": 'R$ 2k-5k', "gender": 'masculino', "age": 19, "internet": True},
        ]

        for spec in people_specs:
            region = region_objs[spec['region']]
            hh = Household(
                region_id=region.id,
                city=spec['city'],
                area_type='urbana',
                income_range=spec['income'],
                household_size=random.randint(1, 5),
                has_internet=spec['internet'],
            )
            session.add(hh)
            session.flush()

            ind = Individual(
                household_id=hh.id,
                age=spec['age'],
                gender=spec['gender'],
                education_level=random.choice(['Fundamental', 'Médio', 'Superior']),
                has_disability=random.choice([False, False, True]),
            )
            session.add(ind)
            session.flush()

            # Dispositivos
            for device_type in ['computer', 'tablet', 'mobile']:
                has_device = random.choice([True, False])
                du = DeviceUsage(
                    individual_id=ind.id,
                    device_type=device_type,
                    has_device=has_device,
                    usage_frequency=('daily' if has_device else 'never'),
                    access_location=random.choice(['home', 'work', 'school']) if has_device else None,
                )
                session.add(du)

            # Internet
            iu = InternetUsage(
                individual_id=ind.id,
                uses_internet=spec['internet'],
                access_frequency=('daily' if spec['internet'] else 'never'),
                main_activities=('general' if spec['internet'] else None),
            )
            session.add(iu)

        session.commit()
        print("Dados de demonstração inseridos com sucesso.")

    except Exception as e:
        session.rollback()
        print(f"Erro ao semear dados: {e}")
    finally:
        session.close()


if __name__ == '__main__':
    seed()
