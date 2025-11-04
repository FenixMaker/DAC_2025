#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import pandas as pd
import pdfplumber
from pathlib import Path
from typing import List, Dict, Any, Tuple
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.utils.logger import get_logger
except ImportError:
    # Fallback absoluto
    try:
        from ..utils.logger import get_logger
    except ImportError:
        # Último fallback - logger básico
        import logging
        def get_logger(name):
            return logging.getLogger(name)

class PDFProcessor:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.processed_data = {
            'household': [],
            'individual': [],
            'device': [],
            'internet': [],
            'region': []
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrai todo o texto de um PDF com tratamento robusto de erros"""
        text = ""
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(pdf_path):
                self.logger.error(f"Arquivo PDF não encontrado: {pdf_path}")
                return text
            
            # Verificar se o arquivo não está vazio
            if os.path.getsize(pdf_path) == 0:
                self.logger.error(f"Arquivo PDF está vazio: {pdf_path}")
                return text
            
            self.logger.info(f"Extraindo texto de: {pdf_path}")
            
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                self.logger.info(f"PDF possui {total_pages} páginas")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                            self.logger.debug(f"Página {page_num}: {len(page_text)} caracteres extraídos")
                        else:
                            self.logger.warning(f"Página {page_num}: nenhum texto extraído")
                    except Exception as page_error:
                        self.logger.error(f"Erro ao extrair página {page_num}: {page_error}")
                        continue
                        
            # Verificar se foi extraído algum texto
            if not text.strip():
                self.logger.warning(f"Nenhum texto foi extraído de {pdf_path}")
            else:
                self.logger.info(f"Extração concluída: {len(text)} caracteres totais")
                
        except Exception as e:
            self.logger.error(f"Erro ao extrair texto de {pdf_path}: {e}", exc_info=True)
            
        return text
    
    def extract_year_from_filename(self, filename: str) -> int:
        """Extrai o ano do nome do arquivo com fallback seguro"""
        try:
            match = re.search(r'(\d{4})', filename)
            if match:
                year = int(match.group(1))
                # Validar se é um ano razoável (entre 2000 e 2030)
                if 2000 <= year <= 2030:
                    return year
                else:
                    self.logger.warning(f"Ano extraído fora do range esperado: {year}")
                    return 2024
            else:
                self.logger.warning(f"Nenhum ano encontrado no nome do arquivo: {filename}")
                return 2024
        except Exception as e:
            self.logger.error(f"Erro ao extrair ano de {filename}: {e}")
            return 2024
    
    def process_pdf_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Processa todos os PDFs em um diretório
        
        Args:
            directory_path (str): Caminho para o diretório com PDFs
            
        Returns:
            Dict[str, Any]: Dados processados de todos os PDFs
        """
        results = {
            'processed_files': [],
            'failed_files': [],
            'total_data': {
                'household': [],
                'individual': [],
                'device': [],
                'internet': [],
                'region': []
            },
            'summary': {
                'total_files': 0,
                'successful': 0,
                'failed': 0
            }
        }
        
        try:
            directory = Path(directory_path)
            if not directory.exists():
                self.logger.error(f"Diretório não encontrado: {directory_path}")
                return results
            
            # Encontrar todos os arquivos PDF
            pdf_files = list(directory.glob("*.pdf"))
            results['summary']['total_files'] = len(pdf_files)
            
            if not pdf_files:
                self.logger.warning(f"Nenhum arquivo PDF encontrado em: {directory_path}")
                return results
            
            self.logger.info(f"Encontrados {len(pdf_files)} arquivos PDF para processar")
            
            for pdf_file in pdf_files:
                try:
                    self.logger.info(f"Processando: {pdf_file.name}")
                    
                    # Extrair ano do nome do arquivo
                    year = self.extract_year_from_filename(pdf_file.name)
                    
                    # Extrair texto
                    text = self.extract_text_from_pdf(str(pdf_file))
                    
                    if text.strip():
                        # Processar dados estruturados
                        file_data = self.parse_structured_data(text, year)
                        
                        # Consolidar dados
                        for data_type, data_list in file_data.items():
                            results['total_data'][data_type].extend(data_list)
                        
                        results['processed_files'].append({
                            'filename': pdf_file.name,
                            'year': year,
                            'text_length': len(text),
                            'data_extracted': {k: len(v) for k, v in file_data.items()}
                        })
                        
                        results['summary']['successful'] += 1
                        self.logger.info(f"Processamento concluído: {pdf_file.name}")
                        
                    else:
                        self.logger.warning(f"Nenhum texto extraído de: {pdf_file.name}")
                        results['failed_files'].append({
                            'filename': pdf_file.name,
                            'error': 'Nenhum texto extraído'
                        })
                        results['summary']['failed'] += 1
                        
                except Exception as file_error:
                    self.logger.error(f"Erro ao processar {pdf_file.name}: {file_error}")
                    results['failed_files'].append({
                        'filename': pdf_file.name,
                        'error': str(file_error)
                    })
                    results['summary']['failed'] += 1
            
            # Log do resumo
            self.logger.info(f"Processamento concluído: {results['summary']['successful']} sucessos, {results['summary']['failed']} falhas")
            
        except Exception as e:
            self.logger.error(f"Erro no processamento do diretório: {e}", exc_info=True)
            
        return results
    
    def parse_structured_data(self, text: str, year: int) -> Dict[str, List[Dict]]:
        """Extrai dados estruturados do texto baseado em padrões identificados"""
        data = {
            'household': [],
            'individual': [],
            'device': [],
            'internet': [],
            'region': []
        }
        
        lines = text.split('\n')
        
        # Processa linha por linha procurando por padrões de dados
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Procura por linhas com dados percentuais e contexto
            numbers = re.findall(r'\b(\d{1,3})(?:%|\b)', line)
            if len(numbers) >= 2:
                context = self._get_context(lines, i)
                
                # Classifica o tipo de dado baseado no contexto
                data_type = self._classify_data_type(context + " " + line)
                
                if data_type != 'unknown':
                    # Extrai dados específicos baseado no tipo
                    extracted = self._extract_specific_data(line, context, data_type, year)
                    if extracted:
                        data[data_type].extend(extracted)
        
        return data
    
    def _get_context(self, lines: List[str], current_index: int, context_range: int = 3) -> str:
        """Obtém o contexto das linhas anteriores"""
        start = max(0, current_index - context_range)
        context_lines = []
        
        for i in range(start, current_index):
            line = lines[i].strip()
            if line and not re.match(r'^\d+\s*$', line):  # Ignora linhas só com números
                context_lines.append(line)
        
        return ' '.join(context_lines[-2:])  # Últimas 2 linhas relevantes
    
    def _classify_data_type(self, text: str) -> str:
        """Classifica o tipo de dados baseado no contexto"""
        text_lower = text.lower()
        
        # Palavras-chave expandidas baseadas na análise dos PDFs
        keywords = {
            'household': [
                'domicílio', 'domicílios', 'casa', 'residência', 'lar',
                'urbana', 'rural', 'área urbana', 'área rural'
            ],
            'individual': [
                'indivíduo', 'indivíduos', 'pessoa', 'pessoas', 'usuário', 'usuários',
                'população', 'anos ou mais', 'faixa etária', 'idade'
            ],
            'device': [
                'computador', 'celular', 'smartphone', 'tablet', 'dispositivo',
                'equipamento', 'aparelho', 'tecnologia'
            ],
            'internet': [
                'internet', 'conexão', 'acesso', 'banda larga', 'wi-fi', 'wifi',
                'rede', 'online', 'navegação'
            ],
            'region': [
                'norte', 'nordeste', 'sudeste', 'sul', 'centro-oeste',
                'região', 'estado', 'brasil', 'nacional'
            ]
        }
        
        # Sistema de pontuação para classificação
        scores = {category: 0 for category in keywords.keys()}
        
        for category, words in keywords.items():
            for word in words:
                if word in text_lower:
                    scores[category] += 1
        
        # Retorna a categoria com maior pontuação
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return 'unknown'
    
    def _extract_specific_data(self, line: str, context: str, data_type: str, year: int) -> List[Dict]:
        """Extrai dados específicos baseado no tipo identificado"""
        extracted_data = []
        
        # Extrai números da linha
        numbers = re.findall(r'\b(\d{1,3})(?:%|\b)', line)
        if not numbers:
            return extracted_data
        
        # Identifica categorias/regiões no contexto
        categories = self._identify_categories(context + " " + line, data_type)
        
        if data_type == 'household':
            extracted_data.extend(self._extract_household_data(numbers, categories, year))
        elif data_type == 'individual':
            extracted_data.extend(self._extract_individual_data(numbers, categories, year))
        elif data_type == 'device':
            extracted_data.extend(self._extract_device_data(numbers, categories, year))
        elif data_type == 'internet':
            extracted_data.extend(self._extract_internet_data(numbers, categories, year))
        elif data_type == 'region':
            extracted_data.extend(self._extract_region_data(numbers, categories, year))
        
        return extracted_data
    
    def _identify_categories(self, text: str, data_type: str) -> List[str]:
        """Identifica categorias específicas no texto"""
        text_lower = text.lower()
        categories = []
        
        # Categorias comuns
        common_categories = {
            'urbana': ['urbana', 'área urbana'],
            'rural': ['rural', 'área rural'],
            'total': ['total', 'brasil', 'nacional'],
            'norte': ['norte'],
            'nordeste': ['nordeste'],
            'sudeste': ['sudeste'],
            'sul': ['sul'],
            'centro-oeste': ['centro-oeste', 'centro oeste']
        }
        
        # Categorias específicas por tipo
        if data_type == 'individual':
            age_categories = {
                '10-15': ['10 a 15', '10-15'],
                '16-24': ['16 a 24', '16-24'],
                '25-34': ['25 a 34', '25-34'],
                '35-44': ['35 a 44', '35-44'],
                '45-59': ['45 a 59', '45-59'],
                '60+': ['60 ou mais', '60+', 'acima de 60']
            }
            common_categories.update(age_categories)
        
        # Procura por categorias no texto
        for category, keywords in common_categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    categories.append(category)
                    break
        
        return categories if categories else ['geral']
    
    def _extract_household_data(self, numbers: List[str], categories: List[str], year: int) -> List[Dict]:
        """Extrai dados de domicílios"""
        data = []
        for i, number in enumerate(numbers):
            category = categories[i] if i < len(categories) else categories[0] if categories else 'geral'
            data.append({
                'year': year,
                'category': category,
                'has_internet': None,
                'has_computer': None,
                'income_class': None,
                'location_type': category if category in ['urbana', 'rural'] else None,
                'percentage': int(number),
                'region': category if category in ['norte', 'nordeste', 'sudeste', 'sul', 'centro-oeste'] else None
            })
        return data
    
    def _extract_individual_data(self, numbers: List[str], categories: List[str], year: int) -> List[Dict]:
        """Extrai dados de indivíduos"""
        data = []
        for i, number in enumerate(numbers):
            category = categories[i] if i < len(categories) else categories[0] if categories else 'geral'
            data.append({
                'year': year,
                'age_group': category if any(c in category for c in ['10', '16', '25', '35', '45', '60']) else None,
                'uses_internet': None,
                'has_smartphone': None,
                'education_level': None,
                'income_class': None,
                'percentage': int(number),
                'region': category if category in ['norte', 'nordeste', 'sudeste', 'sul', 'centro-oeste'] else None
            })
        return data
    
    def _extract_device_data(self, numbers: List[str], categories: List[str], year: int) -> List[Dict]:
        """Extrai dados de dispositivos"""
        data = []
        for i, number in enumerate(numbers):
            category = categories[i] if i < len(categories) else categories[0] if categories else 'geral'
            data.append({
                'year': year,
                'device_type': 'computer',  # Assumindo computador por padrão
                'ownership_percentage': int(number),
                'region': category if category in ['norte', 'nordeste', 'sudeste', 'sul', 'centro-oeste'] else None,
                'location_type': category if category in ['urbana', 'rural'] else None
            })
        return data
    
    def _extract_internet_data(self, numbers: List[str], categories: List[str], year: int) -> List[Dict]:
        """Extrai dados de internet"""
        data = []
        for i, number in enumerate(numbers):
            category = categories[i] if i < len(categories) else categories[0] if categories else 'geral'
            data.append({
                'year': year,
                'usage_type': 'general',
                'percentage': int(number),
                'region': category if category in ['norte', 'nordeste', 'sudeste', 'sul', 'centro-oeste'] else None,
                'location_type': category if category in ['urbana', 'rural'] else None,
                'access_type': None
            })
        return data
    
    def _extract_region_data(self, numbers: List[str], categories: List[str], year: int) -> List[Dict]:
        """Extrai dados regionais"""
        data = []
        for i, number in enumerate(numbers):
            category = categories[i] if i < len(categories) else categories[0] if categories else 'geral'
            if category in ['norte', 'nordeste', 'sudeste', 'sul', 'centro-oeste']:
                data.append({
                    'year': year,
                    'region_name': category,
                    'internet_penetration': int(number),
                    'computer_ownership': None,
                    'smartphone_usage': None
                })
        return data
    
    def process_pdf(self, pdf_path: str) -> Dict[str, List[Dict]]:
        """Processa um único PDF e extrai dados estruturados"""
        self.logger.info(f"Processando PDF: {pdf_path}")
        
        # Extrai texto completo
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            self.logger.warning(f"Não foi possível extrair texto de {pdf_path}")
            return {}
        
        # Extrai ano do nome do arquivo
        year = self.extract_year_from_filename(os.path.basename(pdf_path))
        
        # Processa dados estruturados
        data = self.parse_structured_data(text, year)
        
        # Log dos resultados
        for data_type, records in data.items():
            if records:
                self.logger.info(f"Extraídos {len(records)} registros de {data_type} do PDF {year}")
        
        return data
    
    def process_all_pdfs(self, pdf_directory: str) -> Dict[str, List[Dict]]:
        """Processa todos os PDFs em um diretório"""
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            self.logger.error(f"Diretório não encontrado: {pdf_directory}")
            return {}
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        self.logger.info(f"Encontrados {len(pdf_files)} arquivos PDF")
        
        all_data = {
            'household': [],
            'individual': [],
            'device': [],
            'internet': [],
            'region': []
        }
        
        for pdf_file in pdf_files:
            try:
                pdf_data = self.process_pdf(str(pdf_file))
                
                # Combina os dados
                for data_type, records in pdf_data.items():
                    all_data[data_type].extend(records)
                    
            except Exception as e:
                self.logger.error(f"Erro ao processar {pdf_file}: {e}")
        
        # Log do resumo final
        total_records = sum(len(records) for records in all_data.values())
        self.logger.info(f"Processamento concluído. Total de registros extraídos: {total_records}")
        
        for data_type, records in all_data.items():
            if records:
                self.logger.info(f"  {data_type}: {len(records)} registros")
        
        self.processed_data = all_data
        return all_data
    
    def export_to_csv(self, output_directory: str):
        """Exporta os dados processados para arquivos CSV"""
        output_dir = Path(output_directory)
        output_dir.mkdir(exist_ok=True)
        
        for data_type, records in self.processed_data.items():
            if records:
                df = pd.DataFrame(records)
                csv_path = output_dir / f"{data_type}_data.csv"
                df.to_csv(csv_path, index=False, encoding='utf-8')
                self.logger.info(f"Dados de {data_type} exportados para {csv_path}")
    
    def get_processed_data(self) -> Dict[str, List[Dict]]:
        """Retorna os dados processados"""
        return self.processed_data
    
    def get_available_pdfs(self, pdf_directory: str = "Dados") -> List[str]:
        """Retorna lista de PDFs disponíveis no diretório"""
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            self.logger.warning(f"Diretório não encontrado: {pdf_directory}")
            return []
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        return [str(pdf_file) for pdf_file in pdf_files]