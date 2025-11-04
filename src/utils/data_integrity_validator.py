# -*- coding: utf-8 -*-
"""
Módulo de validação de integridade de dados após importação
"""

from typing import Dict, List, Tuple, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from ..database.models import Household, Individual, DeviceUsage, InternetUsage, Region
from ..utils.logger import get_logger
from datetime import datetime
import json

class DataIntegrityValidator:
    """Validador de integridade de dados do sistema DAC"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.validation_results = []
    
    def validate_all_data(self, session: Session) -> Dict[str, Any]:
        """Executa todas as validações de integridade
        
        Args:
            session: Sessão do SQLAlchemy
            
        Returns:
            Dict com resultados das validações
        """
        self.validation_results = []
        
        validation_report = {
            'timestamp': datetime.now().isoformat(),
            'validations': {},
            'summary': {
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            },
            'critical_issues': [],
            'recommendations': []
        }
        
        # Lista de validações a executar
        validations = [
            ('referential_integrity', self._validate_referential_integrity),
            ('data_consistency', self._validate_data_consistency),
            ('duplicate_records', self._validate_duplicate_records),
            ('data_completeness', self._validate_data_completeness),
            ('data_ranges', self._validate_data_ranges),
            ('orphaned_records', self._validate_orphaned_records),
            ('statistical_anomalies', self._validate_statistical_anomalies)
        ]
        
        for validation_name, validation_func in validations:
            try:
                self.logger.info(f"Executando validação: {validation_name}")
                result = validation_func(session)
                validation_report['validations'][validation_name] = result
                validation_report['summary']['total_checks'] += 1
                
                if result['status'] == 'passed':
                    validation_report['summary']['passed'] += 1
                elif result['status'] == 'failed':
                    validation_report['summary']['failed'] += 1
                    if result.get('critical', False):
                        validation_report['critical_issues'].extend(result.get('issues', []))
                elif result['status'] == 'warning':
                    validation_report['summary']['warnings'] += 1
                
                # Adicionar recomendações
                if 'recommendations' in result:
                    validation_report['recommendations'].extend(result['recommendations'])
                
            except Exception as e:
                self.logger.error(f"Erro na validação {validation_name}: {e}")
                validation_report['validations'][validation_name] = {
                    'status': 'error',
                    'message': f"Erro na execução: {str(e)}"
                }
        
        # Calcular score geral
        total = validation_report['summary']['total_checks']
        passed = validation_report['summary']['passed']
        validation_report['summary']['integrity_score'] = (passed / total * 100) if total > 0 else 0
        
        self.logger.info(f"Validação de integridade concluída. Score: {validation_report['summary']['integrity_score']:.1f}%")
        return validation_report
    
    def _validate_referential_integrity(self, session: Session) -> Dict[str, Any]:
        """Valida integridade referencial entre tabelas"""
        issues = []
        
        try:
            # Verificar se todos os individuals têm household válido
            orphaned_individuals = session.query(Individual).filter(
                ~Individual.household_id.in_(
                    session.query(Household.id)
                )
            ).count()
            
            if orphaned_individuals > 0:
                issues.append(f"{orphaned_individuals} indivíduos sem domicílio válido")
            
            # Verificar se todos os households têm região válida
            households_without_region = session.query(Household).filter(
                ~Household.region_id.in_(
                    session.query(Region.id)
                )
            ).count()
            
            if households_without_region > 0:
                issues.append(f"{households_without_region} domicílios sem região válida")
            
            # Verificar device_usage com individual_id inválido
            orphaned_devices = session.query(DeviceUsage).filter(
                ~DeviceUsage.individual_id.in_(
                    session.query(Individual.id)
                )
            ).count()
            
            if orphaned_devices > 0:
                issues.append(f"{orphaned_devices} registros de dispositivos sem indivíduo válido")
            
            # Verificar internet_usage com individual_id inválido
            orphaned_internet = session.query(InternetUsage).filter(
                ~InternetUsage.individual_id.in_(
                    session.query(Individual.id)
                )
            ).count()
            
            if orphaned_internet > 0:
                issues.append(f"{orphaned_internet} registros de internet sem indivíduo válido")
            
            status = 'failed' if issues else 'passed'
            
            return {
                'status': status,
                'issues': issues,
                'critical': len(issues) > 0,
                'message': 'Integridade referencial validada',
                'recommendations': [
                    'Corrigir referências órfãs antes de continuar',
                    'Implementar constraints de chave estrangeira'
                ] if issues else []
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erro na validação de integridade referencial: {str(e)}"
            }
    
    def _validate_data_consistency(self, session: Session) -> Dict[str, Any]:
        """Valida consistência dos dados"""
        issues = []
        
        try:
            # Verificar consistência de idades
            invalid_ages = session.query(Individual).filter(
                (Individual.age < 0) | (Individual.age > 120)
            ).count()
            
            if invalid_ages > 0:
                issues.append(f"{invalid_ages} indivíduos com idade inválida")
            
            # Verificar tamanho de domicílio vs número de indivíduos
            household_size_inconsistencies = session.execute(text("""
                SELECT h.id, h.household_size, COUNT(i.id) as actual_size
                FROM households h
                LEFT JOIN individuals i ON h.id = i.household_id
                GROUP BY h.id, h.household_size
                HAVING h.household_size != COUNT(i.id)
            """)).fetchall()
            
            if household_size_inconsistencies:
                issues.append(f"{len(household_size_inconsistencies)} domicílios com tamanho inconsistente")
            
            # Verificar valores de gênero padronizados
            invalid_genders = session.query(Individual).filter(
                ~Individual.gender.in_(['masculino', 'feminino', 'outro', 'não informado'])
            ).count()
            
            if invalid_genders > 0:
                issues.append(f"{invalid_genders} indivíduos com gênero não padronizado")
            
            status = 'warning' if issues else 'passed'
            
            return {
                'status': status,
                'issues': issues,
                'message': 'Consistência de dados validada',
                'recommendations': [
                    'Padronizar valores de gênero',
                    'Verificar e corrigir idades inválidas',
                    'Sincronizar tamanho de domicílio com número real de membros'
                ] if issues else []
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erro na validação de consistência: {str(e)}"
            }
    
    def _validate_duplicate_records(self, session: Session) -> Dict[str, Any]:
        """Valida registros duplicados"""
        issues = []
        
        try:
            # Verificar domicílios duplicados por household_id
            duplicate_households = session.execute(text("""
                SELECT household_id, COUNT(*) as count
                FROM households
                WHERE household_id IS NOT NULL AND household_id != ''
                GROUP BY household_id
                HAVING COUNT(*) > 1
            """)).fetchall()
            
            if duplicate_households:
                total_duplicates = sum(row[1] - 1 for row in duplicate_households)
                issues.append(f"{total_duplicates} domicílios duplicados encontrados")
            
            # Verificar indivíduos duplicados por individual_id
            duplicate_individuals = session.execute(text("""
                SELECT individual_id, COUNT(*) as count
                FROM individuals
                WHERE individual_id IS NOT NULL AND individual_id != ''
                GROUP BY individual_id
                HAVING COUNT(*) > 1
            """)).fetchall()
            
            if duplicate_individuals:
                total_duplicates = sum(row[1] - 1 for row in duplicate_individuals)
                issues.append(f"{total_duplicates} indivíduos duplicados encontrados")
            
            # Verificar regiões duplicadas por nome
            duplicate_regions = session.execute(text("""
                SELECT name, COUNT(*) as count
                FROM regions
                GROUP BY name
                HAVING COUNT(*) > 1
            """)).fetchall()
            
            if duplicate_regions:
                total_duplicates = sum(row[1] - 1 for row in duplicate_regions)
                issues.append(f"{total_duplicates} regiões duplicadas encontradas")
            
            status = 'warning' if issues else 'passed'
            
            return {
                'status': status,
                'issues': issues,
                'message': 'Verificação de duplicatas concluída',
                'recommendations': [
                    'Remover registros duplicados',
                    'Implementar constraints UNIQUE nos campos apropriados'
                ] if issues else []
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erro na validação de duplicatas: {str(e)}"
            }
    
    def _validate_data_completeness(self, session: Session) -> Dict[str, Any]:
        """Valida completude dos dados"""
        issues = []
        warnings = []
        
        try:
            # Verificar campos obrigatórios em branco
            empty_household_ids = session.query(Household).filter(
                (Household.household_id.is_(None)) | (Household.household_id == '')
            ).count()
            
            if empty_household_ids > 0:
                issues.append(f"{empty_household_ids} domicílios sem ID")
            
            empty_individual_ids = session.query(Individual).filter(
                (Individual.individual_id.is_(None)) | (Individual.individual_id == '')
            ).count()
            
            if empty_individual_ids > 0:
                issues.append(f"{empty_individual_ids} indivíduos sem ID")
            
            # Verificar campos opcionais com muitos valores em branco
            total_individuals = session.query(Individual).count()
            
            if total_individuals > 0:
                missing_education = session.query(Individual).filter(
                    (Individual.education_level.is_(None)) | 
                    (Individual.education_level == '') |
                    (Individual.education_level == 'Não informado')
                ).count()
                
                if missing_education / total_individuals > 0.5:
                    warnings.append(f"{missing_education}/{total_individuals} indivíduos sem nível educacional")
                
                missing_employment = session.query(Individual).filter(
                    (Individual.employment_status.is_(None)) | 
                    (Individual.employment_status == '') |
                    (Individual.employment_status == 'Não informado')
                ).count()
                
                if missing_employment / total_individuals > 0.5:
                    warnings.append(f"{missing_employment}/{total_individuals} indivíduos sem status de emprego")
            
            status = 'failed' if issues else ('warning' if warnings else 'passed')
            all_issues = issues + warnings
            
            return {
                'status': status,
                'issues': all_issues,
                'critical': len(issues) > 0,
                'message': 'Completude de dados validada',
                'recommendations': [
                    'Preencher campos obrigatórios em branco',
                    'Melhorar coleta de dados opcionais'
                ] if all_issues else []
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erro na validação de completude: {str(e)}"
            }
    
    def _validate_data_ranges(self, session: Session) -> Dict[str, Any]:
        """Valida se os dados estão dentro de faixas esperadas"""
        issues = []
        
        try:
            # Verificar faixas de idade
            age_stats = session.query(
                func.min(Individual.age),
                func.max(Individual.age),
                func.avg(Individual.age)
            ).first()
            
            if age_stats[0] is not None:
                min_age, max_age, avg_age = age_stats
                
                if min_age < 0:
                    issues.append(f"Idade mínima inválida: {min_age}")
                if max_age > 120:
                    issues.append(f"Idade máxima suspeita: {max_age}")
                if avg_age < 10 or avg_age > 80:
                    issues.append(f"Idade média suspeita: {avg_age:.1f}")
            
            # Verificar tamanhos de domicílio
            household_size_stats = session.query(
                func.min(Household.household_size),
                func.max(Household.household_size),
                func.avg(Household.household_size)
            ).first()
            
            if household_size_stats[0] is not None:
                min_size, max_size, avg_size = household_size_stats
                
                if min_size < 1:
                    issues.append(f"Tamanho mínimo de domicílio inválido: {min_size}")
                if max_size > 20:
                    issues.append(f"Tamanho máximo de domicílio suspeito: {max_size}")
            
            status = 'warning' if issues else 'passed'
            
            return {
                'status': status,
                'issues': issues,
                'message': 'Faixas de dados validadas',
                'statistics': {
                    'age_range': f"{age_stats[0]}-{age_stats[1]}" if age_stats[0] is not None else 'N/A',
                    'avg_age': f"{age_stats[2]:.1f}" if age_stats[2] is not None else 'N/A',
                    'household_size_range': f"{household_size_stats[0]}-{household_size_stats[1]}" if household_size_stats[0] is not None else 'N/A'
                },
                'recommendations': [
                    'Verificar dados fora das faixas esperadas',
                    'Implementar validação de entrada mais rigorosa'
                ] if issues else []
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erro na validação de faixas: {str(e)}"
            }
    
    def _validate_orphaned_records(self, session: Session) -> Dict[str, Any]:
        """Valida registros órfãos que podem ser removidos"""
        issues = []
        
        try:
            # Verificar regiões sem domicílios
            unused_regions = session.query(Region).filter(
                ~Region.id.in_(
                    session.query(Household.region_id).filter(Household.region_id.isnot(None))
                )
            ).count()
            
            if unused_regions > 0:
                issues.append(f"{unused_regions} regiões não utilizadas")
            
            # Verificar domicílios sem indivíduos
            empty_households = session.query(Household).filter(
                ~Household.id.in_(
                    session.query(Individual.household_id).filter(Individual.household_id.isnot(None))
                )
            ).count()
            
            if empty_households > 0:
                issues.append(f"{empty_households} domicílios vazios")
            
            status = 'warning' if issues else 'passed'
            
            return {
                'status': status,
                'issues': issues,
                'message': 'Registros órfãos identificados',
                'recommendations': [
                    'Considerar remoção de registros órfãos',
                    'Verificar se registros órfãos são intencionais'
                ] if issues else []
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erro na validação de órfãos: {str(e)}"
            }
    
    def _validate_statistical_anomalies(self, session: Session) -> Dict[str, Any]:
        """Identifica anomalias estatísticas nos dados"""
        issues = []
        
        try:
            # Verificar distribuição de gênero
            gender_distribution = session.execute(text("""
                SELECT gender, COUNT(*) as count
                FROM individuals
                GROUP BY gender
            """)).fetchall()
            
            if gender_distribution:
                total = sum(row[1] for row in gender_distribution)
                for gender, count in gender_distribution:
                    percentage = (count / total) * 100
                    if percentage > 80:  # Mais de 80% de um gênero
                        issues.append(f"Distribuição de gênero suspeita: {gender} = {percentage:.1f}%")
            
            # Verificar distribuição etária
            age_groups = session.execute(text("""
                SELECT 
                    CASE 
                        WHEN age < 18 THEN 'Menor'
                        WHEN age BETWEEN 18 AND 65 THEN 'Adulto'
                        ELSE 'Idoso'
                    END as age_group,
                    COUNT(*) as count
                FROM individuals
                WHERE age IS NOT NULL
                GROUP BY age_group
            """)).fetchall()
            
            if age_groups:
                total = sum(row[1] for row in age_groups)
                for age_group, count in age_groups:
                    percentage = (count / total) * 100
                    if (age_group == 'Menor' and percentage > 50) or \
                       (age_group == 'Idoso' and percentage > 40):
                        issues.append(f"Distribuição etária suspeita: {age_group} = {percentage:.1f}%")
            
            status = 'warning' if issues else 'passed'
            
            return {
                'status': status,
                'issues': issues,
                'message': 'Anomalias estatísticas verificadas',
                'statistics': {
                    'gender_distribution': dict(gender_distribution) if gender_distribution else {},
                    'age_groups': dict(age_groups) if age_groups else {}
                },
                'recommendations': [
                    'Verificar se distribuições anômalas são esperadas',
                    'Revisar processo de coleta de dados'
                ] if issues else []
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erro na validação estatística: {str(e)}"
            }
    
    def generate_integrity_report(self, validation_results: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Gera relatório detalhado de integridade
        
        Args:
            validation_results: Resultados das validações
            output_path: Caminho para salvar o relatório
            
        Returns:
            Conteúdo do relatório em texto
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("RELATÓRIO DE INTEGRIDADE DE DADOS - SISTEMA DAC")
        report_lines.append("=" * 60)
        report_lines.append(f"Data/Hora: {validation_results['timestamp']}")
        report_lines.append("")
        
        # Resumo
        summary = validation_results['summary']
        report_lines.append("RESUMO EXECUTIVO:")
        report_lines.append("-" * 20)
        report_lines.append(f"Score de Integridade: {summary['integrity_score']:.1f}%")
        report_lines.append(f"Total de Verificações: {summary['total_checks']}")
        report_lines.append(f"Aprovadas: {summary['passed']}")
        report_lines.append(f"Falharam: {summary['failed']}")
        report_lines.append(f"Avisos: {summary['warnings']}")
        report_lines.append("")
        
        # Problemas críticos
        if validation_results['critical_issues']:
            report_lines.append("PROBLEMAS CRÍTICOS:")
            report_lines.append("-" * 20)
            for issue in validation_results['critical_issues']:
                report_lines.append(f"• {issue}")
            report_lines.append("")
        
        # Detalhes das validações
        report_lines.append("DETALHES DAS VALIDAÇÕES:")
        report_lines.append("-" * 30)
        
        for validation_name, result in validation_results['validations'].items():
            report_lines.append(f"\n{validation_name.upper().replace('_', ' ')}:")
            report_lines.append(f"Status: {result['status'].upper()}")
            report_lines.append(f"Mensagem: {result.get('message', 'N/A')}")
            
            if 'issues' in result and result['issues']:
                report_lines.append("Problemas encontrados:")
                for issue in result['issues']:
                    report_lines.append(f"  • {issue}")
            
            if 'statistics' in result:
                report_lines.append("Estatísticas:")
                for key, value in result['statistics'].items():
                    report_lines.append(f"  {key}: {value}")
        
        # Recomendações
        if validation_results['recommendations']:
            report_lines.append("\nRECOMENDAÇÕES:")
            report_lines.append("-" * 15)
            for i, recommendation in enumerate(validation_results['recommendations'], 1):
                report_lines.append(f"{i}. {recommendation}")
        
        report_lines.append("\n" + "=" * 60)
        
        report_content = "\n".join(report_lines)
        
        # Salvar arquivo se especificado
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                self.logger.info(f"Relatório de integridade salvo em: {output_path}")
            except Exception as e:
                self.logger.error(f"Erro ao salvar relatório: {e}")
        
        return report_content


# Instância global do validador
integrity_validator = DataIntegrityValidator()