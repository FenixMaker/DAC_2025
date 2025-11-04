#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador de Imagens OCR para extração de dados de pesquisas
Substitui o processamento de PDF por análise direta de imagens JPG
"""

import os
import re
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import sys
from datetime import datetime
import json

# OCR Libraries
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    
    # Configurar caminho do Tesseract no Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except ImportError:
    print("ERRO: Bibliotecas OCR não encontradas. Execute: pip install pytesseract pillow opencv-python")
    sys.exit(1)

# Adicionar o diretório raiz ao path para imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.utils.logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

class ImageProcessor:
    """
    Processador avançado de imagens para extração de dados de pesquisas
    Utiliza OCR e processamento de imagem para extrair informações estruturadas
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.processed_data = {
            'household': [],
            'individual': [],
            'device': [],
            'internet': [],
            'region': [],
            'demographics': [],
            'socioeconomic': [],
            'accessibility': []
        }
        
        # Configurações OCR otimizadas
        self.ocr_config = {
            'lang': 'eng',  # Inglês (por enquanto)
            'oem': 3,       # OCR Engine Mode
            'psm': 6,       # Page Segmentation Mode
            'config': '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöùúûüý .,;:!?()[]{}"\'-/%'
        }
        
        # Padrões de dados para extração
        self.data_patterns = {
            'percentages': r'(\d{1,3}[,.]?\d*)\s*%',
            'numbers': r'\b(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)\b',
            'age_ranges': r'(\d{1,2})\s*(?:a|à|-)\s*(\d{1,2})\s*anos?',
            'income_ranges': r'(\d+(?:[.,]\d+)?)\s*(?:a|à|-)\s*(\d+(?:[.,]\d+)?)\s*(?:salários?|SM|reais?|R\$)',
            'regions': r'(Norte|Nordeste|Centro-Oeste|Sudeste|Sul|Rural|Urbana?)',
            'devices': r'(computador|celular|smartphone|tablet|notebook|desktop|internet|wi-?fi|banda larga)',
            'education': r'(fundamental|médio|superior|analfabeto|pós-graduação|mestrado|doutorado)',
            'disabilities': r'(deficiência|deficiente|visual|auditiva|motora|intelectual|múltipla)'
        }
        
        # Mapeamentos de categorias
        self.category_mappings = {
            'income_ranges': {
                'até 1': 'Até 1 SM',
                '1 a 2': '1 a 2 SM', 
                '2 a 3': '2 a 3 SM',
                '3 a 5': '3 a 5 SM',
                'mais de 5': 'Mais de 5 SM',
                'não informado': 'Não informado'
            },
            'age_ranges': {
                '10-15': '10 a 15 anos',
                '16-24': '16 a 24 anos',
                '25-34': '25 a 34 anos', 
                '35-44': '35 a 44 anos',
                '45-59': '45 a 59 anos',
                '60+': '60 anos ou mais'
            },
            'devices': {
                'computador': 'Computador',
                'celular': 'Celular',
                'smartphone': 'Smartphone',
                'tablet': 'Tablet',
                'notebook': 'Notebook'
            }
        }
    
    def preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Pré-processa imagem para melhorar qualidade do OCR
        """
        try:
            # Carregar imagem
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Não foi possível carregar a imagem: {image_path}")
                return None
            
            # Converter para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Aplicar filtros para melhorar qualidade
            # 1. Redução de ruído
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # 2. Ajuste de contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # 3. Binarização adaptativa
            binary = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 4. Morfologia para limpar texto
            kernel = np.ones((1,1), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Erro no pré-processamento da imagem {image_path}: {e}")
            return None
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extrai texto de uma imagem usando OCR otimizado
        """
        try:
            # Pré-processar imagem
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                return ""
            
            # Converter para PIL Image
            pil_image = Image.fromarray(processed_image)
            
            # Aplicar melhorias adicionais
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(2.0)
            
            # Executar OCR
            text = pytesseract.image_to_string(
                pil_image, 
                lang=self.ocr_config['lang'],
                config=self.ocr_config['config']
            )
            
            # Limpar texto extraído
            cleaned_text = self._clean_extracted_text(text)
            
            self.logger.info(f"Texto extraído de {os.path.basename(image_path)}: {len(cleaned_text)} caracteres")
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"Erro na extração de texto da imagem {image_path}: {e}")
            return ""
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Limpa e normaliza texto extraído do OCR
        """
        if not text:
            return ""
        
        # Remover caracteres especiais desnecessários
        text = re.sub(r'[^\w\s.,;:!?()\[\]{}"\'-/%àáâãäåçèéêëìíîïñòóôõöùúûüý]', ' ', text)
        
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text)
        
        # Corrigir erros comuns de OCR
        corrections = {
            'O': '0',  # O maiúsculo por zero
            'l': '1',  # l minúsculo por um
            'S': '5',  # S por cinco em contextos numéricos
        }
        
        for wrong, correct in corrections.items():
            # Aplicar correções apenas em contextos numéricos
            text = re.sub(f'(?<=\\d){wrong}(?=\\d)', correct, text)
            text = re.sub(f'(?<=\\d){wrong}(?=\\s)', correct, text)
            text = re.sub(f'(?<=\\s){wrong}(?=\\d)', correct, text)
        
        return text.strip()
    
    def extract_year_from_path(self, image_path: str) -> int:
        """
        Extrai ano do caminho da imagem
        """
        try:
            path_parts = Path(image_path).parts
            for part in path_parts:
                if part.isdigit() and len(part) == 4 and part.startswith('20'):
                    return int(part)
            
            # Fallback: extrair do nome do arquivo
            filename = os.path.basename(image_path)
            year_match = re.search(r'(20\d{2})', filename)
            if year_match:
                return int(year_match.group(1))
            
            self.logger.warning(f"Não foi possível extrair ano de {image_path}")
            return datetime.now().year
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair ano de {image_path}: {e}")
            return datetime.now().year
    
    def process_image_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Processa todas as imagens JPG em um diretório específico
        """
        try:
            year_dir = Path(directory_path)
            if not year_dir.exists():
                raise FileNotFoundError(f"Diretório não encontrado: {directory_path}")
            
            # Extrair ano do nome do diretório
            year = int(year_dir.name) if year_dir.name.isdigit() else datetime.now().year
            self.logger.info(f"Processando imagens do diretório {year_dir}")
            
            # Processar o diretório
            results = self._process_year_directory(year_dir, year)
            
            self.logger.info(f"Processamento concluído: {results['processed_count']} imagens processadas")
            return results
            
        except Exception as e:
            error_msg = f"Erro no processamento do diretório {directory_path}: {e}"
            self.logger.error(error_msg)
            return {
                'processed_count': 0,
                'failed_count': 0,
                'extracted_texts': [],
                'structured_data': {
                    'household': [],
                    'individual': [],
                    'device': [],
                    'internet': [],
                    'region': [],
                    'demographics': [],
                    'socioeconomic': [],
                    'accessibility': []
                },
                'errors': [error_msg]
            }
    
    def _process_year_directory(self, year_dir: Path, year: int) -> Dict[str, Any]:
        """
        Processa todas as imagens de um ano específico
        """
        year_data = {
            'processed_count': 0,
            'failed_count': 0,
            'extracted_texts': [],
            'structured_data': {
                'household': [],
                'individual': [],
                'device': [],
                'internet': [],
                'region': [],
                'demographics': [],
                'socioeconomic': [],
                'accessibility': []
            }
        }
        
        # Processar cada imagem JPG
        image_files = sorted(year_dir.glob('*.jpg'))
        self.logger.info(f"Encontradas {len(image_files)} imagens para o ano {year}")
        print(f"DEBUG: Encontradas {len(image_files)} imagens em {year_dir}")
        
        for image_path in image_files:
            print(f"DEBUG: Processando {image_path.name}...")
            try:
                # Extrair texto da imagem
                extracted_text = self.extract_text_from_image(str(image_path))
                
                if extracted_text:
                    year_data['extracted_texts'].append({
                        'file': image_path.name,
                        'text': extracted_text,
                        'length': len(extracted_text)
                    })
                    
                    # Processar dados estruturados
                    structured = self._parse_structured_data(extracted_text, year)
                    
                    # Consolidar dados estruturados
                    for category, data_list in structured.items():
                        year_data['structured_data'][category].extend(data_list)
                    
                    year_data['processed_count'] += 1
                    self.logger.debug(f"Processada: {image_path.name}")
                else:
                    year_data['failed_count'] += 1
                    self.logger.warning(f"Falha na extração: {image_path.name}")
                    
            except Exception as e:
                year_data['failed_count'] += 1
                self.logger.error(f"Erro ao processar {image_path.name}: {e}")
        
        return year_data
    
    def _parse_structured_data(self, text: str, year: int) -> Dict[str, List[Dict]]:
        """
        Analisa texto extraído e converte em dados estruturados
        """
        structured_data = {
            'household': [],
            'individual': [],
            'device': [],
            'internet': [],
            'region': [],
            'demographics': [],
            'socioeconomic': [],
            'accessibility': []
        }
        
        try:
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Obter contexto (linhas adjacentes)
                context = self._get_context(lines, i, 2)
                
                # Classificar tipo de dados
                data_type = self._classify_data_type(line, context)
                
                # Extrair dados específicos
                if data_type != 'unknown':
                    extracted_items = self._extract_specific_data(line, context, data_type, year)
                    structured_data[data_type].extend(extracted_items)
            
            return structured_data
            
        except Exception as e:
            self.logger.error(f"Erro na análise de dados estruturados: {e}")
            return structured_data
    
    def _get_context(self, lines: List[str], current_index: int, context_range: int = 2) -> str:
        """
        Obtém contexto ao redor de uma linha específica
        """
        start = max(0, current_index - context_range)
        end = min(len(lines), current_index + context_range + 1)
        return ' '.join(lines[start:end]).strip()
    
    def _classify_data_type(self, line: str, context: str) -> str:
        """
        Classifica o tipo de dados baseado no conteúdo da linha e contexto
        """
        line_lower = line.lower()
        context_lower = context.lower()
        
        # Palavras-chave para classificação
        keywords = {
            'household': ['domicílio', 'residência', 'casa', 'lar', 'moradia', 'habitação'],
            'individual': ['pessoa', 'indivíduo', 'morador', 'habitante', 'cidadão'],
            'device': ['computador', 'celular', 'smartphone', 'tablet', 'notebook', 'dispositivo'],
            'internet': ['internet', 'conexão', 'acesso', 'banda larga', 'wi-fi', 'rede'],
            'region': ['região', 'estado', 'cidade', 'município', 'urbano', 'rural'],
            'demographics': ['idade', 'sexo', 'gênero', 'anos', 'masculino', 'feminino'],
            'socioeconomic': ['renda', 'salário', 'educação', 'escolaridade', 'trabalho', 'emprego'],
            'accessibility': ['deficiência', 'deficiente', 'acessibilidade', 'limitação', 'dificuldade']
        }
        
        # Verificar correspondências
        for data_type, type_keywords in keywords.items():
            for keyword in type_keywords:
                if keyword in line_lower or keyword in context_lower:
                    return data_type
        
        return 'unknown'
    
    def _extract_specific_data(self, line: str, context: str, data_type: str, year: int) -> List[Dict]:
        """
        Extrai dados específicos baseado no tipo identificado
        """
        extracted_data = []
        
        try:
            # Extrair números e percentuais
            numbers = re.findall(self.data_patterns['numbers'], line)
            percentages = re.findall(self.data_patterns['percentages'], line)
            
            # Identificar categorias relevantes
            categories = self._identify_categories(context, data_type)
            
            # Processar baseado no tipo de dados
            if data_type == 'household':
                extracted_data.extend(self._extract_household_data(numbers, categories, year, line, context))
            elif data_type == 'individual':
                extracted_data.extend(self._extract_individual_data(numbers, categories, year, line, context))
            elif data_type == 'device':
                extracted_data.extend(self._extract_device_data(numbers, categories, year, line, context))
            elif data_type == 'internet':
                extracted_data.extend(self._extract_internet_data(numbers, categories, year, line, context))
            elif data_type == 'region':
                extracted_data.extend(self._extract_region_data(numbers, categories, year, line, context))
            elif data_type == 'demographics':
                extracted_data.extend(self._extract_demographics_data(numbers, categories, year, line, context))
            elif data_type == 'socioeconomic':
                extracted_data.extend(self._extract_socioeconomic_data(numbers, categories, year, line, context))
            elif data_type == 'accessibility':
                extracted_data.extend(self._extract_accessibility_data(numbers, categories, year, line, context))
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Erro na extração de dados específicos: {e}")
            return []
    
    def _identify_categories(self, context: str, data_type: str) -> List[str]:
        """
        Identifica categorias relevantes no contexto
        """
        categories = []
        context_lower = context.lower()
        
        category_patterns = {
            'household': ['urbano', 'rural', 'renda', 'tamanho', 'tipo'],
            'individual': ['idade', 'sexo', 'educação', 'trabalho', 'deficiência'],
            'device': ['computador', 'celular', 'smartphone', 'tablet', 'notebook'],
            'internet': ['acesso', 'uso', 'frequência', 'atividade', 'barreira'],
            'region': ['norte', 'nordeste', 'centro-oeste', 'sudeste', 'sul'],
            'demographics': ['masculino', 'feminino', 'jovem', 'adulto', 'idoso'],
            'socioeconomic': ['fundamental', 'médio', 'superior', 'empregado', 'desempregado'],
            'accessibility': ['visual', 'auditiva', 'motora', 'intelectual', 'múltipla']
        }
        
        if data_type in category_patterns:
            for pattern in category_patterns[data_type]:
                if pattern in context_lower:
                    categories.append(pattern)
        
        return categories
    
    def _extract_household_data(self, numbers: List[str], categories: List[str], year: int, line: str, context: str) -> List[Dict]:
        """
        Extrai dados específicos de domicílios
        """
        data = []
        
        for i, number in enumerate(numbers):
            try:
                value = float(number.replace(',', '.'))
                
                # Determinar categoria baseada no contexto
                category = 'geral'
                if 'urbano' in context.lower():
                    category = 'urbano'
                elif 'rural' in context.lower():
                    category = 'rural'
                elif any(income in context.lower() for income in ['renda', 'salário', 'sm']):
                    category = 'renda'
                
                data.append({
                    'year': year,
                    'category': category,
                    'value': value,
                    'unit': 'percentage' if '%' in line else 'count',
                    'source_line': line.strip(),
                    'context': context.strip()[:200],
                    'extracted_at': datetime.now().isoformat()
                })
                
            except ValueError:
                continue
        
        return data
    
    def _extract_individual_data(self, numbers: List[str], categories: List[str], year: int, line: str, context: str) -> List[Dict]:
        """
        Extrai dados específicos de indivíduos
        """
        data = []
        
        # Extrair faixas etárias
        age_ranges = re.findall(self.data_patterns['age_ranges'], line + ' ' + context)
        
        for i, number in enumerate(numbers):
            try:
                value = float(number.replace(',', '.'))
                
                # Determinar categoria
                category = 'geral'
                if age_ranges:
                    category = f"{age_ranges[0][0]}-{age_ranges[0][1]} anos"
                elif 'masculino' in context.lower():
                    category = 'masculino'
                elif 'feminino' in context.lower():
                    category = 'feminino'
                elif any(edu in context.lower() for edu in ['fundamental', 'médio', 'superior']):
                    category = 'educação'
                
                data.append({
                    'year': year,
                    'category': category,
                    'value': value,
                    'unit': 'percentage' if '%' in line else 'count',
                    'source_line': line.strip(),
                    'context': context.strip()[:200],
                    'extracted_at': datetime.now().isoformat()
                })
                
            except ValueError:
                continue
        
        return data
    
    def _extract_device_data(self, numbers: List[str], categories: List[str], year: int, line: str, context: str) -> List[Dict]:
        """
        Extrai dados específicos de dispositivos
        """
        data = []
        
        # Identificar tipos de dispositivos
        device_types = []
        for device in self.data_patterns['devices']:
            if re.search(device, context.lower()):
                device_types.append(device)
        
        for i, number in enumerate(numbers):
            try:
                value = float(number.replace(',', '.'))
                
                # Usar tipo de dispositivo se identificado
                category = device_types[0] if device_types else 'dispositivo'
                
                data.append({
                    'year': year,
                    'category': category,
                    'device_type': category,
                    'value': value,
                    'unit': 'percentage' if '%' in line else 'count',
                    'source_line': line.strip(),
                    'context': context.strip()[:200],
                    'extracted_at': datetime.now().isoformat()
                })
                
            except ValueError:
                continue
        
        return data
    
    def _extract_internet_data(self, numbers: List[str], categories: List[str], year: int, line: str, context: str) -> List[Dict]:
        """
        Extrai dados específicos de uso de internet
        """
        data = []
        
        for i, number in enumerate(numbers):
            try:
                value = float(number.replace(',', '.'))
                
                # Determinar categoria de uso
                category = 'acesso'
                if 'frequência' in context.lower():
                    category = 'frequência'
                elif 'atividade' in context.lower():
                    category = 'atividade'
                elif 'barreira' in context.lower():
                    category = 'barreira'
                
                data.append({
                    'year': year,
                    'category': category,
                    'value': value,
                    'unit': 'percentage' if '%' in line else 'count',
                    'source_line': line.strip(),
                    'context': context.strip()[:200],
                    'extracted_at': datetime.now().isoformat()
                })
                
            except ValueError:
                continue
        
        return data
    
    def _extract_region_data(self, numbers: List[str], categories: List[str], year: int, line: str, context: str) -> List[Dict]:
        """
        Extrai dados específicos de regiões
        """
        data = []
        
        # Identificar regiões
        regions = re.findall(self.data_patterns['regions'], context, re.IGNORECASE)
        
        for i, number in enumerate(numbers):
            try:
                value = float(number.replace(',', '.'))
                
                # Usar região se identificada
                category = regions[0].lower() if regions else 'geral'
                
                data.append({
                    'year': year,
                    'category': category,
                    'region': category,
                    'value': value,
                    'unit': 'percentage' if '%' in line else 'count',
                    'source_line': line.strip(),
                    'context': context.strip()[:200],
                    'extracted_at': datetime.now().isoformat()
                })
                
            except ValueError:
                continue
        
        return data
    
    def _extract_demographics_data(self, numbers: List[str], categories: List[str], year: int, line: str, context: str) -> List[Dict]:
        """
        Extrai dados demográficos específicos
        """
        data = []
        
        for i, number in enumerate(numbers):
            try:
                value = float(number.replace(',', '.'))
                
                # Determinar categoria demográfica
                category = 'geral'
                if 'idade' in context.lower():
                    category = 'idade'
                elif 'sexo' in context.lower() or 'gênero' in context.lower():
                    category = 'gênero'
                
                data.append({
                    'year': year,
                    'category': category,
                    'value': value,
                    'unit': 'percentage' if '%' in line else 'count',
                    'source_line': line.strip(),
                    'context': context.strip()[:200],
                    'extracted_at': datetime.now().isoformat()
                })
                
            except ValueError:
                continue
        
        return data
    
    def _extract_socioeconomic_data(self, numbers: List[str], categories: List[str], year: int, line: str, context: str) -> List[Dict]:
        """
        Extrai dados socioeconômicos específicos
        """
        data = []
        
        # Identificar faixas de renda
        income_ranges = re.findall(self.data_patterns['income_ranges'], context)
        
        for i, number in enumerate(numbers):
            try:
                value = float(number.replace(',', '.'))
                
                # Determinar categoria socioeconômica
                category = 'geral'
                if income_ranges:
                    category = f"renda_{income_ranges[0][0]}-{income_ranges[0][1]}"
                elif any(edu in context.lower() for edu in ['fundamental', 'médio', 'superior']):
                    category = 'educação'
                elif 'trabalho' in context.lower() or 'emprego' in context.lower():
                    category = 'emprego'
                
                data.append({
                    'year': year,
                    'category': category,
                    'value': value,
                    'unit': 'percentage' if '%' in line else 'count',
                    'source_line': line.strip(),
                    'context': context.strip()[:200],
                    'extracted_at': datetime.now().isoformat()
                })
                
            except ValueError:
                continue
        
        return data
    
    def _extract_accessibility_data(self, numbers: List[str], categories: List[str], year: int, line: str, context: str) -> List[Dict]:
        """
        Extrai dados específicos de acessibilidade
        """
        data = []
        
        # Identificar tipos de deficiência
        disability_types = re.findall(self.data_patterns['disabilities'], context, re.IGNORECASE)
        
        for i, number in enumerate(numbers):
            try:
                value = float(number.replace(',', '.'))
                
                # Usar tipo de deficiência se identificado
                category = disability_types[0].lower() if disability_types else 'deficiência'
                
                data.append({
                    'year': year,
                    'category': category,
                    'disability_type': category,
                    'value': value,
                    'unit': 'percentage' if '%' in line else 'count',
                    'source_line': line.strip(),
                    'context': context.strip()[:200],
                    'extracted_at': datetime.now().isoformat()
                })
                
            except ValueError:
                continue
        
        return data
    
    def process_all_images(self, images_directory: str = "Dados") -> Dict[str, Any]:
        """
        Processa todas as imagens do diretório principal
        """
        try:
            self.logger.info(f"Iniciando processamento completo de imagens em {images_directory}")
            
            base_dir = Path(images_directory)
            if not base_dir.exists():
                raise FileNotFoundError(f"Diretório não encontrado: {images_directory}")
            
            # Inicializar contadores
            total_processed = 0
            total_failed = 0
            years_processed = set()
            all_errors = []
            extracted_data = {}
            
            # Processar cada subdiretório de ano
            year_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.isdigit()]
            
            for year_dir in sorted(year_dirs):
                year = int(year_dir.name)
                self.logger.info(f"Processando ano {year}")
                
                # Processar diretório do ano
                year_results = self._process_year_directory(year_dir, year)
                
                # Consolidar resultados
                total_processed += year_results['processed_count']
                total_failed += year_results['failed_count']
                years_processed.add(year)
                
                # Armazenar dados extraídos por ano
                extracted_data[year] = year_results
                
                # Consolidar dados processados globalmente
                for category, data_list in year_results['structured_data'].items():
                    self.processed_data[category].extend(data_list)
            
            # Estatísticas finais
            total_records = sum(len(data_list) for data_list in self.processed_data.values())
            
            self.logger.info(f"Processamento concluído: {total_records} registros extraídos de {len(years_processed)} anos")
            
            return {
                'success': True,
                'processed_images': total_processed,
                'failed_images': total_failed,
                'years_processed': sorted(list(years_processed)),
                'total_records': total_records,
                'records_by_category': {k: len(v) for k, v in self.processed_data.items()},
                'extracted_data': extracted_data,
                'errors': all_errors,
                'summary': f"{total_records} registros extraídos de {total_processed} imagens em {len(years_processed)} anos"
            }
            
        except Exception as e:
            error_msg = f"Erro no processamento completo: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'processed_images': 0,
                'failed_images': 0,
                'summary': f"Erro: {error_msg}"
            }
    
    def export_to_csv(self, output_directory: str):
        """
        Exporta dados processados para arquivos CSV
        """
        try:
            output_path = Path(output_directory)
            output_path.mkdir(exist_ok=True)
            
            for category, data_list in self.processed_data.items():
                if data_list:
                    df = pd.DataFrame(data_list)
                    csv_path = output_path / f"{category}_data.csv"
                    df.to_csv(csv_path, index=False, encoding='utf-8')
                    self.logger.info(f"Exportado {category}: {len(data_list)} registros -> {csv_path}")
            
            self.logger.info(f"Exportação concluída em {output_directory}")
            
        except Exception as e:
            self.logger.error(f"Erro na exportação: {e}")
    
    def get_processed_data(self) -> Dict[str, List[Dict]]:
        """
        Retorna dados processados
        """
        return self.processed_data.copy()
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do processamento
        """
        stats = {
            'total_records': sum(len(data_list) for data_list in self.processed_data.values()),
            'records_by_category': {k: len(v) for k, v in self.processed_data.items()},
            'categories_with_data': [k for k, v in self.processed_data.items() if v],
            'empty_categories': [k for k, v in self.processed_data.items() if not v]
        }
        
        return stats

if __name__ == "__main__":
    # Teste básico
    processor = ImageProcessor()
    results = processor.process_all_images("f:\\Sites\\DAC\\Dados")
    print(f"Processamento concluído: {results}")