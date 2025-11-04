"""
Script para migrar dados do SQLite para PostgreSQL
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.database_manager import DatabaseManager
from src.database.postgresql_manager import PostgreSQLManager
from src.database.models import Region, Household, Individual, DeviceUsage, InternetUsage
from src.utils.logger import get_logger

def migrate_sqlite_to_postgresql():
    """Migra todos os dados do SQLite para PostgreSQL em português brasileiro"""
    logger = get_logger(__name__)
    
    print("🚀 Iniciando migração SQLite → PostgreSQL (PT-BR)...")
    
    # Inicializar managers
    sqlite_manager = DatabaseManager()
    postgres_manager = PostgreSQLManager(database='sistema_dac')  # Nome em português
    
    try:
        # 1. Conectar ao SQLite (fonte)
        print("📂 Conectando ao SQLite...")
        sqlite_manager.initialize_database()
        sqlite_session = sqlite_manager.get_session()
        
        # 2. Conectar ao PostgreSQL (destino)
        print("🐘 Conectando ao PostgreSQL...")
        if not postgres_manager.initialize_connection():
            raise Exception("Falha ao conectar com PostgreSQL")
        
        # 3. Criar tabelas no PostgreSQL
        print("📋 Criando estrutura de tabelas no PostgreSQL...")
        postgres_manager.create_tables()
        
        # 4. Migrar dados por tabela
        postgres_session = postgres_manager.get_session()
        
        # Migrar Regiões
        print("🌎 Migrando regiões...")
        regions = sqlite_session.query(Region).all()
        for region in regions:
            new_region = Region(
                code=region.code,
                name=region.name,
                state=region.state,
                macro_region=region.macro_region,
                description=region.description
            )
            postgres_session.merge(new_region)
        postgres_session.commit()
        print(f"   ✅ {len(regions)} regiões migradas")
        
        # Migrar Domicílios
        print("🏠 Migrando domicílios...")
        households = sqlite_session.query(Household).all()
        for household in households:
            new_household = Household(
                id=household.id,
                region_id=household.region_id,
                city=household.city,
                area_type=household.area_type,
                income_range=household.income_range,
                household_size=household.household_size,
                has_internet=household.has_internet
            )
            postgres_session.merge(new_household)
        postgres_session.commit()
        print(f"   ✅ {len(households)} domicílios migrados")
        
        # Migrar Indivíduos
        print("👥 Migrando indivíduos...")
        individuals = sqlite_session.query(Individual).all()
        for individual in individuals:
            new_individual = Individual(
                id=individual.id,
                household_id=individual.household_id,
                age=individual.age,
                gender=individual.gender,
                education_level=individual.education_level,
                has_disability=individual.has_disability,
                employment_status=individual.employment_status
            )
            postgres_session.merge(new_individual)
        postgres_session.commit()
        print(f"   ✅ {len(individuals)} indivíduos migrados")
        
        # Migrar Uso de Dispositivos
        print("📱 Migrando uso de dispositivos...")
        device_usage = sqlite_session.query(DeviceUsage).all()
        for device in device_usage:
            new_device = DeviceUsage(
                id=device.id,
                individual_id=device.individual_id,
                device_type=device.device_type,
                has_device=device.has_device,
                usage_frequency=device.usage_frequency,
                access_location=device.access_location
            )
            postgres_session.merge(new_device)
        postgres_session.commit()
        print(f"   ✅ {len(device_usage)} registros de dispositivos migrados")
        
        # Migrar Uso de Internet
        print("🌐 Migrando uso de internet...")
        internet_usage = sqlite_session.query(InternetUsage).all()
        for internet in internet_usage:
            new_internet = InternetUsage(
                id=internet.id,
                individual_id=internet.individual_id,
                uses_internet=internet.uses_internet,
                access_frequency=internet.access_frequency,
                main_activities=internet.main_activities,
                barriers_to_access=internet.barriers_to_access
            )
            postgres_session.merge(new_internet)
        postgres_session.commit()
        print(f"   ✅ {len(internet_usage)} registros de internet migrados")
        
        # 5. Validar migração
        print("🔍 Validando migração...")
        
        # Contar registros no PostgreSQL
        pg_regions = postgres_session.query(Region).count()
        pg_households = postgres_session.query(Household).count()
        pg_individuals = postgres_session.query(Individual).count()
        pg_devices = postgres_session.query(DeviceUsage).count()
        pg_internet = postgres_session.query(InternetUsage).count()
        
        print(f"""
📊 RESULTADO DA MIGRAÇÃO:
   Regiões:     {len(regions)} → {pg_regions}
   Domicílios:  {len(households)} → {pg_households}
   Indivíduos:  {len(individuals)} → {pg_individuals}
   Dispositivos: {len(device_usage)} → {pg_devices}
   Internet:    {len(internet_usage)} → {pg_internet}
        """)
        
        # Verificar se os totais coincidem
        if (pg_regions == len(regions) and 
            pg_households == len(households) and 
            pg_individuals == len(individuals) and 
            pg_devices == len(device_usage) and 
            pg_internet == len(internet_usage)):
            print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("🎉 Todos os dados foram transferidos corretamente!")
        else:
            print("⚠️  Atenção: Alguns registros podem não ter sido migrados corretamente")
        
        # Testar consulta no PostgreSQL
        print("\n🧪 Testando consulta no PostgreSQL...")
        test_query = postgres_session.query(Individual).join(Household).join(Region).first()
        if test_query:
            print(f"✅ Consulta teste OK: Indivíduo {test_query.id} da região {test_query.household.region.name}")
        
    except Exception as e:
        logger.error(f"Erro durante migração: {e}")
        print(f"❌ Erro: {e}")
        return False
        
    finally:
        # Fechar conexões
        if 'sqlite_session' in locals():
            sqlite_session.close()
        if 'postgres_session' in locals():
            postgres_session.close()
        
        sqlite_manager = None  # SQLite não precisa fechar conexão explicitamente
        postgres_manager.close_connection()
    
    return True

def test_postgresql_connection():
    """Testa apenas a conexão com PostgreSQL em português"""
    print("🧪 Testando conexão PostgreSQL (PT-BR)...")
    
    postgres_manager = PostgreSQLManager(database='sistema_dac')
    
    try:
        if postgres_manager.initialize_connection():
            success, info = postgres_manager.test_connection()
            if success:
                print(f"✅ Conexão OK: {info}")
                return True
            else:
                print(f"❌ Falha no teste: {info}")
                return False
        else:
            print("❌ Falha na inicialização")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    finally:
        postgres_manager.close_connection()

if __name__ == "__main__":
    print("Sistema de Migração DAC - SQLite para PostgreSQL")
    print("=" * 50)
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Testar conexão PostgreSQL")
        print("2. Migrar dados completos")
        print("3. Sair")
        
        choice = input("\nOpção: ").strip()
        
        if choice == "1":
            test_postgresql_connection()
        elif choice == "2":
            if migrate_sqlite_to_postgresql():
                print("\n🎉 Migração finalizada!")
            else:
                print("\n❌ Migração falhou!")
        elif choice == "3":
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida!")
