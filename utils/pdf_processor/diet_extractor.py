"""
PDF Processor para extrair informações de dietas
Converte PDFs de dietas para o formato padrão do sistema
"""

import PyPDF2
import re
import json
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DietPDFProcessor:
    """Processador de PDFs de dietas"""
    
    def __init__(self):
        self.standard_format = {
            "personal_info": {},
            "nutrition_plan": {},
            "meal_plans": {
                "breakfast": [],
                "lunch": [],
                "dinner": [],
                "snacks": []
            },
            "recommendations": {},
            "restrictions": []
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrai texto do PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {e}")
            raise
    
    def parse_diet_content(self, text: str) -> Dict[str, Any]:
        """Analisa o conteúdo do texto e extrai informações da dieta"""
        diet_data = self.standard_format.copy()
        
        try:
            # Extrair informações pessoais
            diet_data["personal_info"] = self._extract_personal_info(text)
            
            # Extrair plano nutricional
            diet_data["nutrition_plan"] = self._extract_nutrition_plan(text)
            
            # Extrair planos de refeições
            diet_data["meal_plans"] = self._extract_meal_plans(text)
            
            # Extrair recomendações
            diet_data["recommendations"] = self._extract_recommendations(text)
            
            # Extrair restrições
            diet_data["restrictions"] = self._extract_restrictions(text)
            
            return diet_data
            
        except Exception as e:
            logger.error(f"Erro ao analisar conteúdo da dieta: {e}")
            raise
    
    def _extract_personal_info(self, text: str) -> Dict[str, Any]:
        """Extrai informações pessoais do texto"""
        info = {}
        
        # Padrões comuns
        patterns = {
            'name': r'nome[:\s]+([A-Za-záàâãéèêíìôõóòúùûüç\s]+)',
            'age': r'idade[:\s]+(\d+)',
            'weight': r'peso[:\s]+(\d+\.?\d*)\s*kg',
            'height': r'altura[:\s]+(\d+\.?\d*)\s*[cm]?',
            'goal': r'objetivo[:\s]+([^.\n]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                info[key] = match.group(1).strip()
        
        return info
    
    def _extract_nutrition_plan(self, text: str) -> Dict[str, Any]:
        """Extrai informações do plano nutricional"""
        plan = {}
        
        # Padrões para valores nutricionais
        patterns = {
            'daily_calories': r'calorias[:\s]+(\d+)',
            'protein': r'proteína[s]?[:\s]+(\d+\.?\d*)\s*g',
            'carbs': r'carboidrato[s]?[:\s]+(\d+\.?\d*)\s*g',
            'fat': r'gordura[s]?[:\s]+(\d+\.?\d*)\s*g'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                plan[key] = float(match.group(1))
        
        return plan
    
    def _extract_meal_plans(self, text: str) -> Dict[str, List]:
        """Extrai planos de refeições"""
        meals = {
            "breakfast": [],
            "lunch": [],
            "dinner": [],
            "snacks": []
        }
        
        # Mapeamento de termos
        meal_patterns = {
            'breakfast': r'café\s*da\s*manhã[:\s]+(.*?)(?=almoço|lanche|jantar|$)',
            'lunch': r'almoço[:\s]+(.*?)(?=lanche|jantar|café|$)',
            'dinner': r'jantar[:\s]+(.*?)(?=lanche|café|almoço|$)',
            'snacks': r'lanche[:\s]+(.*?)(?=café|almoço|jantar|$)'
        }
        
        for meal_type, pattern in meal_patterns.items():
            match = re.search(pattern, text.lower(), re.DOTALL)
            if match:
                meal_content = match.group(1).strip()
                # Dividir por linhas e filtrar vazias
                items = [item.strip() for item in meal_content.split('\n') if item.strip()]
                meals[meal_type] = items[:5]  # Limitar a 5 itens
        
        return meals
    
    def _extract_recommendations(self, text: str) -> Dict[str, Any]:
        """Extrai recomendações"""
        recommendations = {}
        
        # Padrões para recomendações
        patterns = {
            'water_intake': r'água[:\s]+(\d+\.?\d*)\s*litros?',
            'exercise': r'exercício[s]?[:\s]+([^.\n]+)',
            'supplements': r'suplemento[s]?[:\s]+([^.\n]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                recommendations[key] = match.group(1).strip()
        
        return recommendations
    
    def _extract_restrictions(self, text: str) -> List[str]:
        """Extrai restrições alimentares"""
        restrictions = []
        
        # Padrões para restrições
        restriction_patterns = [
            r'não\s+pode[:\s]+([^.\n]+)',
            r'evitar[:\s]+([^.\n]+)',
            r'restrição[:\s]+([^.\n]+)',
            r'alergia[:\s]+([^.\n]+)'
        ]
        
        for pattern in restriction_patterns:
            matches = re.findall(pattern, text.lower())
            restrictions.extend([match.strip() for match in matches])
        
        return list(set(restrictions))  # Remover duplicatas
    
    def process_pdf_to_standard_format(self, pdf_path: str) -> Dict[str, Any]:
        """Processa PDF completo e retorna no formato padrão"""
        try:
            # Extrair texto
            text = self.extract_text_from_pdf(pdf_path)
            
            # Analisar conteúdo
            diet_data = self.parse_diet_content(text)
            
            # Adicionar metadados
            diet_data["metadata"] = {
                "source": "pdf_upload",
                "original_file": Path(pdf_path).name,
                "processed_at": __import__('datetime').datetime.now().isoformat()
            }
            
            return diet_data
            
        except Exception as e:
            logger.error(f"Erro ao processar PDF: {e}")
            raise
    
    def validate_diet_data(self, diet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e completa dados da dieta"""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Verificar informações essenciais
        if not diet_data.get("meal_plans", {}).get("breakfast"):
            validation_result["warnings"].append("Café da manhã não encontrado")
        
        if not diet_data.get("meal_plans", {}).get("lunch"):
            validation_result["warnings"].append("Almoço não encontrado")
        
        if not diet_data.get("meal_plans", {}).get("dinner"):
            validation_result["warnings"].append("Jantar não encontrado")
        
        if not diet_data.get("nutrition_plan", {}).get("daily_calories"):
            validation_result["warnings"].append("Valor calórico diário não encontrado")
        
        return validation_result

def process_uploaded_diet(file_path: str) -> Dict[str, Any]:
    """Função principal para processar dieta enviada"""
    processor = DietPDFProcessor()
    
    try:
        # Processar PDF
        diet_data = processor.process_pdf_to_standard_format(file_path)
        
        # Validar dados
        validation = processor.validate_diet_data(diet_data)
        
        return {
            "success": True,
            "diet_data": diet_data,
            "validation": validation
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "diet_data": None,
            "validation": None
        }
