"""
PDF Generator para Dietas Personalizadas - Sem traduções hardcoded
"""

import os
import io
from typing import Dict, Any, List
from datetime import datetime
import logging

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors

logger = logging.getLogger(__name__)


class ShapeMatePDFGenerator:
    """Gerador de PDF para dietas - usando dados diretos do JSON"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 2 * cm
        
        # Cores do ShapeMateAI
        self.primary_color = HexColor('#2E7D32')
        self.secondary_color = HexColor('#4CAF50')
        self.accent_color = HexColor('#66BB6A')
        self.text_color = HexColor('#1B5E20')
        self.bg_color = HexColor('#F1F8E9')
        
        # Configurar estilos
        self.styles = self._create_custom_styles()
    
    def _create_custom_styles(self) -> Dict[str, ParagraphStyle]:
        """Cria estilos customizados para o PDF"""
        base_styles = getSampleStyleSheet()
        
        custom_styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=self.primary_color,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ),
            'subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent=base_styles['Heading2'],
                fontSize=16,
                spaceAfter=15,
                textColor=self.secondary_color,
                alignment=TA_LEFT,
                fontName='Helvetica-Bold'
            ),
            'section_header': ParagraphStyle(
                'SectionHeader',
                parent=base_styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=20,
                textColor=self.primary_color,
                fontName='Helvetica-Bold',
                borderWidth=1,
                borderColor=self.primary_color,
                borderPadding=5,
                backColor=self.bg_color
            ),
            'normal_text': ParagraphStyle(
                'NormalText',
                parent=base_styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                textColor=self.text_color,
                fontName='Helvetica',
                alignment=TA_LEFT
            ),
            'bold_text': ParagraphStyle(
                'BoldText',
                parent=base_styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                textColor=self.text_color,
                fontName='Helvetica-Bold'
            ),
            'small_text': ParagraphStyle(
                'SmallText',
                parent=base_styles['Normal'],
                fontSize=8,
                spaceAfter=4,
                textColor=self.text_color,
                fontName='Helvetica'
            )
        }
        
        return custom_styles
    
    def generate_diet_pdf(self, diet_data: Dict[str, Any], output_path: str) -> str:
        """Gera PDF completo da dieta personalizada usando dados diretos do JSON"""
        try:
            logger.info(f"🎨 Gerando PDF da dieta: {output_path}")
            
            # Validar estrutura do JSON
            self._validate_diet_data(diet_data)
            
            # Criar documento PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            
            # Criar elementos do PDF
            elements = []
            
            # 1. Página de capa
            elements.extend(self._create_cover_page(diet_data))
            elements.append(PageBreak())
            
            # 2. Menu semanal
            elements.extend(self._create_weekly_menu_section(diet_data))
            elements.append(PageBreak())
            
            # 3. Lista de compras
            elements.extend(self._create_shopping_list_section(diet_data))
            
            # Gerar PDF
            doc.build(elements, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
            
            logger.info(f"✅ PDF gerado com sucesso: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {str(e)}")
            raise RuntimeError(f"Falha na geração do PDF: {str(e)}") from e
    
    def _validate_diet_data(self, diet_data: Dict[str, Any]):
        """Valida se o JSON da dieta tem a estrutura necessária"""
        required_sections = ['patient_info', 'nutritional_calculations', 'weekly_menu']
        
        for section in required_sections:
            if section not in diet_data:
                raise ValueError(f"Seção obrigatória '{section}' não encontrada no JSON da dieta")
        
        # Validar seções específicas
        patient_info = diet_data['patient_info']
        if not isinstance(patient_info, dict) or not patient_info.get('name'):
            raise ValueError("Nome do paciente não encontrado ou formato inválido")
        
        nutritional_calc = diet_data['nutritional_calculations']
        if not nutritional_calc.get('daily_target_kcal'):
            raise ValueError("Meta calórica diária não encontrada")
        
        weekly_menu = diet_data['weekly_menu']
        if not weekly_menu:
            raise ValueError("Menu semanal não encontrado")
    
    def _create_cover_page(self, diet_data: Dict[str, Any]) -> List:
        """Cria a página de capa com informações do paciente e cálculos nutricionais"""
        elements = []
        
        # Título principal
        title = Paragraph("ShapeMateAI - Plano Alimentar Personalizado", self.styles['title'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Informações do paciente
        patient_title = Paragraph("Informações do Paciente", self.styles['subtitle'])
        elements.append(patient_title)
        elements.append(Spacer(1, 15))
        
        patient_info = diet_data['patient_info']
        
        # Dados do paciente com formatação melhorada
        patient_data = [
            ["Nome:", patient_info.get('name', 'Não informado')],
            ["Idade:", f"{patient_info.get('age', 'Não informado')} anos" if patient_info.get('age') else "Não informado"],
            ["Sexo:", patient_info.get('gender', 'Não informado')],
            ["Peso:", f"{patient_info.get('weight', 'Não informado')} kg" if patient_info.get('weight') else "Não informado"],
            ["Altura:", f"{patient_info.get('height', 'Não informado')} cm" if patient_info.get('height') else "Não informado"],
            ["Nível de Atividade:", patient_info.get('activity_level', 'Não informado')],
            ["Objetivo Principal:", patient_info.get('primary_goal', 'Não informado')]
        ]
        
        # Criar tabela com dados do paciente
        patient_table = Table(patient_data, colWidths=[100, 200])
        patient_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(patient_table)
        elements.append(Spacer(1, 20))
        
        # Cálculos nutricionais
        nutritional_calculations = diet_data.get('nutritional_calculations', {})
        if nutritional_calculations:
            calc_title = Paragraph("Cálculos Nutricionais", self.styles['subtitle'])
            elements.append(calc_title)
            elements.append(Spacer(1, 15))
            
            # TMB e meta calórica
            tmb = nutritional_calculations.get('tmb_kcal', 0)
            daily_target = nutritional_calculations.get('daily_target_kcal', 0)
            activity_factor = nutritional_calculations.get('activity_factor', 0)
            
            calc_data = [
                ["Taxa Metabólica Basal (TMB):", f"{tmb:.1f} kcal/dia"],
                ["Meta Calórica Diária:", f"{daily_target:.1f} kcal/dia"],
                ["Fator de Atividade:", f"{activity_factor:.3f}"],
            ]
            
            if 'objective_adjustment' in nutritional_calculations:
                calc_data.append(["Ajuste por Objetivo:", nutritional_calculations['objective_adjustment']])
            
            calc_table = Table(calc_data, colWidths=[150, 150])
            calc_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(calc_table)
            elements.append(Spacer(1, 20))
            
            # Distribuição de macronutrientes
            if 'macronutrients' in nutritional_calculations:
                macro_title = Paragraph("Distribuição de Macronutrientes", self.styles['subtitle'])
                elements.append(macro_title)
                elements.append(Spacer(1, 15))
                
                macros = nutritional_calculations['macronutrients']
                
                # Traduzir nomes dos macronutrientes
                macro_names = {
                    'carbohydrates': 'Carboidratos',
                    'proteins': 'Proteínas',
                    'fats': 'Gorduras'
                }
                
                macro_data = [["Macronutriente", "Gramas/dia", "Percentual", "Calorias/dia"]]
                
                for macro_key, macro_info in macros.items():
                    macro_name = macro_names.get(macro_key, macro_key.title())
                    grams = macro_info.get('grams_per_day', 0)
                    percentage = macro_info.get('percentage', 0)
                    kcal = macro_info.get('kcal_per_day', 0)
                    
                    macro_data.append([
                        macro_name,
                        f"{grams:.1f} g",
                        f"{percentage}%",
                        f"{kcal:.1f} kcal"
                    ])
                
                macro_table = Table(macro_data, colWidths=[100, 80, 80, 100])
                macro_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ]))
                elements.append(macro_table)
        
        # Data de geração
        elements.append(Spacer(1, 20))
        generation_date = datetime.now().strftime("%d/%m/%Y às %H:%M")
        date_text = Paragraph(f"Gerado em: {generation_date}", self.styles['normal_text'])
        elements.append(date_text)
        
        return elements
    
    def _create_weekly_menu_section(self, diet_data: Dict[str, Any]) -> List:
        """Cria seção com menu semanal usando dados diretos do JSON"""
        elements = []
        weekly_menu = diet_data.get('weekly_menu', {})
        nutritional_calculations = diet_data.get('nutritional_calculations', {})
        
        section_title = Paragraph("🍽️ Menu Semanal", self.styles['section_header'])
        elements.append(section_title)
        
        # Mapeamento de nomes de refeições em PT-BR
        meal_names = {
            'breakfast': '☀️ Café da Manhã',
            'morning_snack': '🥤 Lanche da Manhã',
            'lunch': '🍽️ Almoço',
            'afternoon_snack': '🍎 Lanche da Tarde',
            'dinner': '🌙 Jantar',
            'evening_snack': '🌙 Ceia'
        }
        
        # Tradução de dias para PT-BR
        day_names = {
            'monday': 'Segunda-feira',
            'tuesday': 'Terça-feira',
            'wednesday': 'Quarta-feira',
            'thursday': 'Quinta-feira',
            'friday': 'Sexta-feira',
            'saturday': 'Sábado',
            'sunday': 'Domingo'
        }

        # Ordem fixa dos dias (Monday -> Sunday)
        ordered_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in ordered_days:
            if day not in weekly_menu:
                continue
            daily_menu = weekly_menu[day]
            
            # Título do dia (PT-BR)
            day_pt = day_names.get(str(day).lower(), str(day).title())
            day_title = Paragraph(f"<b>{day_pt}</b>", self.styles['bold_text'])
            elements.append(day_title)
            
            # Calcular macros diários para este dia
            daily_macros = self._calculate_daily_macros(daily_menu)
            
            # Para cada refeição do dia
            for meal_key, meal_data in daily_menu.items():
                if not meal_data:
                    continue
                
                meal_name = meal_names.get(meal_key, meal_key.replace('_', ' ').title())
                target_kcal = meal_data.get('target_kcal', 0)
                
                # Título da refeição
                meal_title = Paragraph(f"{meal_name} - {target_kcal} kcal", self.styles['bold_text'])
                elements.append(meal_title)
                
                # Opções da refeição
                options = meal_data.get('options', [])
                for i, option in enumerate(options, 1):
                    option_name = option.get('name', f'Opção {i}')
                    items = option.get('items', [])
                    totals = option.get('totals', {})
                    
                    # Lista de alimentos da opção
                    food_items = []
                    for item in items:
                        # Priorizar nome em português
                        display_name = item.get('name_pt') or item.get('name_en') or 'Alimento'
                        portion = item.get('portion_grams') or item.get('quantity_g') or 0
                        kcal = item.get('kcal') or 0
                        # Formatação clara
                        food_items.append(f"• {display_name} - {portion}g ({kcal} kcal)")
                    
                    option_text = f"<b>{option_name}:</b><br/>"
                    option_text += "<br/>".join(food_items)
                    total_kcal = totals.get('kcal', 0)
                    option_text += f"<br/><b>Total da opção: {total_kcal} kcal</b>"
                    
                    option_para = Paragraph(option_text, self.styles['normal_text'])
                    elements.append(option_para)
                    elements.append(Spacer(1, 0.3 * cm))
            
            # Adicionar resumo dos macros do dia
            if daily_macros:
                elements.append(Spacer(1, 0.3 * cm))
                elements.extend(self._create_daily_macro_summary(daily_macros, nutritional_calculations))
            
            elements.append(Spacer(1, 0.5 * cm))
        
        return elements
    
    def _calculate_daily_macros(self, daily_menu: Dict[str, Any]) -> Dict[str, float]:
        """Calcula os macronutrientes consumidos em um dia"""
        daily_macros = {
            'kcal': 0,
            'protein_g': 0,
            'carbs_g': 0,
            'fat_g': 0
        }
        
        for meal_data in daily_menu.values():
            if not meal_data:
                continue
                
            options = meal_data.get('options', [])
            for option in options:
                items = option.get('items', [])
                for item in items:
                    # Calorias
                    kcal = item.get('kcal', 0)
                    daily_macros['kcal'] += kcal
                    
                    # Proteínas (estimativa baseada em calorias)
                    protein_kcal = kcal * 0.3  # 30% das calorias
                    protein_g = protein_kcal / 4  # 4 kcal por grama
                    daily_macros['protein_g'] += protein_g
                    
                    # Carboidratos (estimativa baseada em calorias)
                    carbs_kcal = kcal * 0.4  # 40% das calorias
                    carbs_g = carbs_kcal / 4  # 4 kcal por grama
                    daily_macros['carbs_g'] += carbs_g
                    
                    # Gorduras (estimativa baseada em calorias)
                    fat_kcal = kcal * 0.3  # 30% das calorias
                    fat_g = fat_kcal / 9  # 9 kcal por grama
                    daily_macros['fat_g'] += fat_g
        
        return daily_macros
    
    def _create_daily_macro_summary(self, daily_macros: Dict[str, float], nutritional_calculations: Dict[str, Any]) -> List:
        """Cria resumo dos macronutrientes do dia com comparação com as metas"""
        elements = []
        
        # Título do resumo
        summary_title = Paragraph("📊 Resumo Nutricional do Dia", self.styles['bold_text'])
        elements.append(summary_title)
        
        # Obter metas diárias
        target_macros = nutritional_calculations.get('macronutrients', {})
        
        # Criar tabela de comparação
        macro_data = [["Macronutriente", "Consumido", "Meta", "Status"]]
        
        # Calorias
        target_kcal = nutritional_calculations.get('daily_target_kcal', 0)
        kcal_status = self._get_macro_status(daily_macros['kcal'], target_kcal, 0.1)  # 10% de tolerância
        macro_data.append([
            "Calorias",
            f"{daily_macros['kcal']:.0f} kcal",
            f"{target_kcal:.0f} kcal",
            kcal_status
        ])
        
        # Proteínas
        target_protein = target_macros.get('proteins', {}).get('grams_per_day', 0)
        protein_status = self._get_macro_status(daily_macros['protein_g'], target_protein, 0.15)  # 15% de tolerância
        macro_data.append([
            "Proteínas",
            f"{daily_macros['protein_g']:.1f} g",
            f"{target_protein:.1f} g",
            protein_status
        ])
        
        # Carboidratos
        target_carbs = target_macros.get('carbohydrates', {}).get('grams_per_day', 0)
        carbs_status = self._get_macro_status(daily_macros['carbs_g'], target_carbs, 0.15)  # 15% de tolerância
        macro_data.append([
            "Carboidratos",
            f"{daily_macros['carbs_g']:.1f} g",
            f"{target_carbs:.1f} g",
            carbs_status
        ])
        
        # Gorduras
        target_fat = target_macros.get('fats', {}).get('grams_per_day', 0)
        fat_status = self._get_macro_status(daily_macros['fat_g'], target_fat, 0.15)  # 15% de tolerância
        macro_data.append([
            "Gorduras",
            f"{daily_macros['fat_g']:.1f} g",
            f"{target_fat:.1f} g",
            fat_status
        ])
        
        # Criar tabela
        macro_table = Table(macro_data, colWidths=[80, 80, 80, 60])
        macro_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ]))
        
        elements.append(macro_table)
        elements.append(Spacer(1, 0.2 * cm))
        
        return elements
    
    def _get_macro_status(self, consumed: float, target: float, tolerance: float) -> str:
        """Retorna o status de um macronutriente baseado na tolerância"""
        if target == 0:
            return "N/A"
        
        ratio = consumed / target
        if abs(ratio - 1.0) <= tolerance:
            return "✅"
        elif ratio < 1.0:
            return "⚠️"
        else:
            return "❌"
    
    def _create_shopping_list_section(self, diet_data: Dict[str, Any]) -> List:
        """Cria seção com lista de compras"""
        elements = []
        shopping_list = diet_data.get('shopping_list', {})
        
        section_title = Paragraph("🛒 Lista de Compras", self.styles['section_header'])
        elements.append(section_title)
        
        items = shopping_list.get('items', [])
        if items:
            # Agrupar por categoria
            categories = {}
            for item in items:
                category = item.get('category', 'Outros')
                if category not in categories:
                    categories[category] = []
                categories[category].append(item)
            
            # Para cada categoria
            for category, category_items in categories.items():
                category_title = Paragraph(f"<b>{category.title()}</b>", self.styles['bold_text'])
                elements.append(category_title)
                
                item_data = [['Item', 'Quantidade Semanal']]
                for item in category_items:
                    # Priorizar nome em português
                    name_pt = item.get('name_pt') or item.get('name_en') or 'Item'
                    amount = item.get('estimated_weekly_amount', 'A definir')
                    item_data.append([name_pt, amount])
                
                category_table = Table(item_data, colWidths=[8*cm, 4*cm])
                category_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.accent_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.bg_color]),
                    ('GRID', (0, 0), (-1, -1), 1, self.accent_color)
                ]))
                
                elements.append(category_table)
                elements.append(Spacer(1, 0.3 * cm))
        else:
            no_list_text = Paragraph("Lista de compras será personalizada conforme suas preferências coletadas.", self.styles['normal_text'])
            elements.append(no_list_text)
        
        return elements
    
    def _add_header_footer(self, canvas, doc):
        """Adiciona cabeçalho e rodapé às páginas"""
        canvas.saveState()
        
        # Cabeçalho
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(self.primary_color)
        canvas.drawString(doc.leftMargin, doc.height + doc.topMargin - 0.5*cm, "ShapeMateAI - Plano Alimentar Personalizado")
        
        # Rodapé
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(self.text_color)
        canvas.drawRightString(
            doc.width + doc.rightMargin, 
            0.5*cm, 
            f"Página {doc.page}"
        )
        
        canvas.restoreState()


def create_diet_pdf(diet_data: Dict[str, Any], output_dir: str = None) -> str:
    """Função utilitária para criar PDF da dieta sem traduções hardcoded"""
    try:
        # Definir diretório de saída
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), 'generated_diets')
        
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Nome do arquivo baseado nos dados do JSON
        patient_name = diet_data.get('patient_info', {}).get('name', 'Paciente')
        safe_name = "".join(c for c in patient_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dieta_{safe_name}_{timestamp}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        # Gerar PDF
        generator = ShapeMatePDFGenerator()
        return generator.generate_diet_pdf(diet_data, output_path)
        
    except Exception as e:
        logger.error(f"Erro ao criar PDF da dieta: {str(e)}")
        raise RuntimeError(f"Falha na criação do PDF: {str(e)}") from e