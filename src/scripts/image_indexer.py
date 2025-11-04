#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para indexar e processar imagens das pastas de dados (2021-2024)
Extrai metadados das imagens e armazena no banco de dados
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from PIL import Image, ExifTags
import hashlib
import json
from typing import Dict, List, Optional, Tuple

# Adicionar o diretório src ao path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, project_root)

from database.database_manager import DatabaseManager
from database.enhanced_models import ExtractedData, ProcessingLog, DataQualityMetric
from modules.image_processor import ImageProcessor
from sqlalchemy import text

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_indexing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImageIndexer:
    """Classe para indexar e processar imagens das pastas de dados"""
    
    def __init__(self, base_path: str = "d:\\Sites\\DAC\\Dados"):
        self.base_path = Path(base_path)
        self.db_manager = DatabaseManager()
        self.image_processor = ImageProcessor()
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
        
        # Inicializar banco de dados
        self.db_manager.initialize_database()
        
    def get_image_metadata(self, image_path: Path) -> Dict:
        """Extrai metadados de uma imagem"""
        metadata = {
            'file_path': str(image_path),
            'file_name': image_path.name,
            'file_size': image_path.stat().st_size,
            'created_date': datetime.fromtimestamp(image_path.stat().st_ctime).isoformat(),
            'modified_date': datetime.fromtimestamp(image_path.stat().st_mtime).isoformat(),
            'file_hash': self._calculate_file_hash(image_path)
        }
        
        try:
            with Image.open(image_path) as img:
                metadata.update({
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                })
                
                # Extrair dados EXIF se disponíveis
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = {}
                    for tag_id, value in img._getexif().items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)
                    metadata['exif_data'] = exif_data
                    
        except Exception as e:
            logger.warning(f"Erro ao extrair metadados da imagem {image_path}: {e}")
            metadata['error'] = str(e)
            
        return metadata
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcula hash MD5 do arquivo"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Erro ao calcular hash do arquivo {file_path}: {e}")
            return ""
    
    def extract_year_from_path(self, image_path: Path) -> int:
        """Extrai o ano da estrutura de pastas"""
        parts = image_path.parts
        for part in parts:
            if part.isdigit() and len(part) == 4 and 2020 <= int(part) <= 2030:
                return int(part)
        
        # Tentar extrair do nome do arquivo
        filename = image_path.stem
        if filename.startswith('2021') or filename.startswith('2022') or \
           filename.startswith('2023') or filename.startswith('2024'):
            return int(filename[:4])
            
        return 2021  # Default
    
    def process_image_directory(self, year: int) -> Tuple[int, int, List[str]]:
        """Processa todas as imagens de um diretório específico"""
        year_path = self.base_path / str(year)
        
        if not year_path.exists():
            logger.warning(f"Diretório {year_path} não encontrado")
            return 0, 0, [f"Diretório {year_path} não encontrado"]
        
        logger.info(f"Processando imagens do ano {year} em {year_path}")
        
        processed_count = 0
        error_count = 0
        errors = []
        
        # Buscar todas as imagens no diretório
        image_files = []
        for ext in self.supported_formats:
            image_files.extend(year_path.glob(f"*{ext}"))
            image_files.extend(year_path.glob(f"*{ext.upper()}"))
        
        logger.info(f"Encontradas {len(image_files)} imagens para processar")
        
        session = self.db_manager.get_session()
        
        try:
            for image_path in image_files:
                try:
                    # Verificar se já foi processada
                    existing = session.query(ExtractedData).filter(
                        ExtractedData.source_file == str(image_path)
                    ).first()
                    
                    if existing:
                        logger.debug(f"Imagem {image_path.name} já processada, pulando...")
                        continue
                    
                    # Extrair metadados
                    metadata = self.get_image_metadata(image_path)
                    
                    # Processar com OCR se disponível
                    ocr_text = ""
                    confidence = 0.0
                    
                    try:
                        # Usar o ImageProcessor existente para OCR
                        ocr_result = self.image_processor.extract_text_from_image(str(image_path))
                        if ocr_result:
                            ocr_text = ocr_result.get('text', '')
                            confidence = ocr_result.get('confidence', 0.0)
                    except Exception as ocr_error:
                        logger.warning(f"Erro no OCR para {image_path.name}: {ocr_error}")
                    
                    # Criar registro na tabela extracted_data
                    extracted_data = ExtractedData(
                        source_file=str(image_path),
                        source_year=year,
                        page_number=self._extract_page_number(image_path.name),
                        category='image_metadata',
                        subcategory='file_info',
                        extracted_text=ocr_text,
                        structured_data=metadata,
                        extraction_confidence=confidence,
                        validation_status='pending',
                        extraction_method='metadata_ocr',
                        processing_timestamp=datetime.utcnow()
                    )
                    
                    session.add(extracted_data)
                    processed_count += 1
                    
                    if processed_count % 10 == 0:
                        session.commit()
                        logger.info(f"Processadas {processed_count} imagens...")
                        
                except Exception as e:
                    error_count += 1
                    error_msg = f"Erro ao processar {image_path.name}: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    continue
            
            # Commit final
            session.commit()
            logger.info(f"Processamento do ano {year} concluído: {processed_count} sucessos, {error_count} erros")
            
        except Exception as e:
            session.rollback()
            error_msg = f"Erro geral no processamento do ano {year}: {e}"
            errors.append(error_msg)
            logger.error(error_msg)
            
        finally:
            session.close()
            
        return processed_count, error_count, errors
    
    def _extract_page_number(self, filename: str) -> Optional[int]:
        """Extrai número da página do nome do arquivo"""
        import re
        
        # Padrões para extrair número da página
        patterns = [
            r'page[-_]?(\d+)',
            r'p(\d+)',
            r'(\d+)$',  # Número no final
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename.lower())
            if match:
                return int(match.group(1))
                
        return None
    
    def create_processing_log(self, process_type: str, status: str, 
                            start_time: datetime, end_time: datetime = None,
                            records_processed: int = 0, records_successful: int = 0,
                            records_failed: int = 0, error_message: str = None) -> None:
        """Cria log de processamento"""
        
        session = self.db_manager.get_session()
        
        try:
            duration = None
            if end_time:
                duration = (end_time - start_time).total_seconds()
            
            log_entry = ProcessingLog(
                process_type=process_type,
                status=status,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                records_processed=records_processed,
                records_successful=records_successful,
                records_failed=records_failed,
                error_message=error_message
            )
            
            session.add(log_entry)
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"Erro ao criar log de processamento: {e}")
        finally:
            session.close()
    
    def process_all_years(self) -> Dict[int, Tuple[int, int, List[str]]]:
        """Processa todas as imagens de todos os anos"""
        years = [2021, 2022, 2023, 2024]
        results = {}
        
        start_time = datetime.utcnow()
        total_processed = 0
        total_errors = 0
        
        logger.info("Iniciando processamento de todas as imagens...")
        
        try:
            for year in years:
                year_start = datetime.utcnow()
                processed, errors, error_list = self.process_image_directory(year)
                year_end = datetime.utcnow()
                
                results[year] = (processed, errors, error_list)
                total_processed += processed
                total_errors += errors
                
                # Log do processamento do ano
                self.create_processing_log(
                    process_type=f'image_indexing_{year}',
                    status='completed' if errors == 0 else 'completed_with_errors',
                    start_time=year_start,
                    end_time=year_end,
                    records_processed=processed + errors,
                    records_successful=processed,
                    records_failed=errors,
                    error_message='; '.join(error_list[:5]) if error_list else None
                )
            
            end_time = datetime.utcnow()
            
            # Log geral do processamento
            self.create_processing_log(
                process_type='image_indexing_all',
                status='completed',
                start_time=start_time,
                end_time=end_time,
                records_processed=total_processed + total_errors,
                records_successful=total_processed,
                records_failed=total_errors
            )
            
            logger.info(f"Processamento concluído: {total_processed} sucessos, {total_errors} erros")
            
        except Exception as e:
            end_time = datetime.utcnow()
            logger.error(f"Erro geral no processamento: {e}")
            
            self.create_processing_log(
                process_type='image_indexing_all',
                status='failed',
                start_time=start_time,
                end_time=end_time,
                error_message=str(e)
            )
            
        return results
    
    def generate_summary_report(self) -> Dict:
        """Gera relatório resumo do processamento"""
        session = self.db_manager.get_session()
        
        try:
            # Contar registros por ano
            year_counts = {}
            for year in [2021, 2022, 2023, 2024]:
                count = session.query(ExtractedData).filter(
                    ExtractedData.source_year == year,
                    ExtractedData.category == 'image_metadata'
                ).count()
                year_counts[year] = count
            
            # Estatísticas gerais
            total_images = session.query(ExtractedData).filter(
                ExtractedData.category == 'image_metadata'
            ).count()
            
            # Logs de processamento
            recent_logs = session.query(ProcessingLog).filter(
                ProcessingLog.process_type.like('image_indexing%')
            ).order_by(ProcessingLog.start_time.desc()).limit(10).all()
            
            report = {
                'total_images_indexed': total_images,
                'images_by_year': year_counts,
                'recent_processing_logs': [
                    {
                        'process_type': log.process_type,
                        'status': log.status,
                        'start_time': log.start_time.isoformat(),
                        'records_processed': log.records_processed,
                        'records_successful': log.records_successful,
                        'records_failed': log.records_failed
                    } for log in recent_logs
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return {'error': str(e)}
        finally:
            session.close()

def main():
    """Função principal"""
    logger.info("=== Iniciando Indexação de Imagens ===")
    
    indexer = ImageIndexer()
    
    # Processar todas as imagens
    results = indexer.process_all_years()
    
    # Exibir resultados
    print("\n=== RESULTADOS DO PROCESSAMENTO ===")
    for year, (processed, errors, error_list) in results.items():
        print(f"Ano {year}: {processed} processadas, {errors} erros")
        if error_list:
            print(f"  Primeiros erros: {error_list[:3]}")
    
    # Gerar relatório
    report = indexer.generate_summary_report()
    print("\n=== RELATÓRIO FINAL ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    logger.info("=== Indexação Concluída ===")

if __name__ == "__main__":
    main()