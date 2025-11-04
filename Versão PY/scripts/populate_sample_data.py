# -*- coding: utf-8 -*-
"""
Script para popular o banco de dados com dados de amostra
"""
import sys
from pathlib import Path

# Garantir que o diretório raiz esteja no sys.path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.database_manager import DatabaseManager
from src.database.models import Region, Household, Individual, DeviceUsage, InternetUsage


def populate_sample_data():
    """Popula o banco com dados de amostra"""
    db = DatabaseManager()
    
    try:
        # Inicializar banco
        if db.engine is None or db.Session is None:
            db.initialize_database()
        
        session = db.get_session()
        
        # Verificar se já existem dados suficientes
        existing_individuals = session.query(Individual).count()
        if existing_individuals > 10:
            print(f"Banco já possui {existing_individuals} indivíduos. Pulando população.")
            return
        
        # Obter regiões existentes
        regions = session.query(Region).all()
        if not regions:
            print("ERRO: Nenhuma região encontrada no banco. Execute a inicialização primeiro.")
            return
        
        print(f"Encontradas {len(regions)} regiões no banco.")
        
        # Criar domicílios de amostra
        households_data = []
        for i, region in enumerate(regions[:3]):  # Usar as 3 primeiras regiões
            for j in range(3):  # 3 domicílios por região
                household = Household(
                    region_id=region.id,
                    city=f"Cidade {region.name} {j+1}",
                    area_type='urbana' if j % 2 == 0 else 'rural',
                    income_range=['Até 1 SM', '1-3 SM', '3-5 SM', 'Acima de 5 SM'][j % 4],
                    household_size=2 + j,
                    has_internet=(j % 2 == 0)
                )
                session.add(household)
                households_data.append(household)
        
        session.commit()
        print(f"Criados {len(households_data)} domicílios de amostra.")
        
        # Criar indivíduos de amostra
        individuals_data = []
        genders = ['masculino', 'feminino']
        education_levels = ['Fundamental', 'Médio', 'Superior', 'Pós-graduação']
        
        for i, household in enumerate(households_data):
            for j in range(2):  # 2 indivíduos por domicílio
                individual = Individual(
                    household_id=household.id,
                    age=20 + (i * 5) + (j * 10),
                    gender=genders[j % 2],
                    education_level=education_levels[i % 4],
                    has_disability=(i % 5 == 0),  # 20% com deficiência
                    employment_status='empregado' if j == 0 else 'desempregado'
                )
                session.add(individual)
                individuals_data.append(individual)
        
        session.commit()
        print(f"Criados {len(individuals_data)} indivíduos de amostra.")
        
        # Criar registros de uso de dispositivos
        device_types = ['Celular', 'Computador', 'Tablet', 'Smart TV']
        frequencies = ['Diária', 'Semanal', 'Mensal', 'Raramente']
        
        device_count = 0
        for i, individual in enumerate(individuals_data):
            # Cada indivíduo tem 2-3 dispositivos
            for j in range(2 + (i % 2)):
                device = DeviceUsage(
                    individual_id=individual.id,
                    device_type=device_types[j % len(device_types)],
                    has_device=True,
                    usage_frequency=frequencies[i % len(frequencies)],
                    access_location='Casa' if i % 2 == 0 else 'Trabalho'
                )
                session.add(device)
                device_count += 1
        
        session.commit()
        print(f"Criados {device_count} registros de uso de dispositivos.")
        
        # Criar registros de uso de internet
        internet_count = 0
        for i, individual in enumerate(individuals_data):
            internet = InternetUsage(
                individual_id=individual.id,
                uses_internet=(i % 3 != 0),  # 66% usam internet
                access_frequency=frequencies[i % len(frequencies)] if i % 3 != 0 else 'Nunca',
                main_activities='Redes sociais, E-mail, Pesquisa' if i % 3 != 0 else 'N/A',
                barriers_to_access='Nenhuma' if i % 3 != 0 else 'Sem acesso'
            )
            session.add(internet)
            internet_count += 1
        
        session.commit()
        print(f"Criados {internet_count} registros de uso de internet.")
        
        # Exibir estatísticas finais
        stats = db.get_database_stats(use_cache=False)
        print("\n=== Estatísticas do Banco ===")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n✓ Dados de amostra inseridos com sucesso!")
        return 0
        
    except Exception as e:
        print(f"ERRO ao popular banco: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        try:
            session.close()
            db.close()
        except:
            pass


if __name__ == '__main__':
    raise SystemExit(populate_sample_data())
