"""
PDF Generator para Dietas Personalizadas do ShapeMateAI
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
    """Gerador de PDF personalizado para dietas do ShapeMateAI"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 2 * cm
        
        # Cores do ShapeMateAI
        self.primary_color = HexColor('#2E7D32')      # Verde principal
        self.secondary_color = HexColor('#4CAF50')    # Verde secundário
        self.accent_color = HexColor('#66BB6A')       # Verde claro
        self.text_color = HexColor('#1B5E20')         # Verde escuro
        self.bg_color = HexColor('#F1F8E9')           # Verde muito claro
        
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
                alignment=TA_CENTER,
                fontName='Helvetica'
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
                alignment=TA_JUSTIFY
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
        """Gera PDF completo da dieta personalizada"""
        try:
            logger.info(f"🎨 Gerando PDF da dieta personalizada: {output_path}")
            
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
            
            # 2. Informações do paciente
            elements.extend(self._create_patient_info_section(diet_data))
            elements.append(PageBreak())
            
            # 3. Cálculos nutricionais
            elements.extend(self._create_nutrition_calculations_section(diet_data))
            elements.append(PageBreak())
            
            # 4. Menu semanal
            elements.extend(self._create_weekly_menu_section(diet_data))
            elements.append(PageBreak())
            
            # 5. Lista de compras
            elements.extend(self._create_shopping_list_section(diet_data))
            elements.append(PageBreak())
            
            # 6. Orientações práticas
            elements.extend(self._create_practical_guidance_section(diet_data))
            
            # 7. Rodapé com dados da API
            elements.extend(self._create_footer_section(diet_data))
            
            # Gerar PDF
            doc.build(elements, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
            
            logger.info(f"✅ PDF gerado com sucesso: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {str(e)}")
            raise RuntimeError(f"Falha na geração do PDF: {str(e)}") from e
    
    def _create_cover_page(self, diet_data: Dict[str, Any]) -> List:
        """Cria página de capa do PDF"""
        elements = []
        
        # Logo e título principal
        elements.append(Spacer(1, 1 * cm))
        
        title = Paragraph("🏃‍♂️ ShapeMateAI", self.styles['title'])
        elements.append(title)
        
        subtitle = Paragraph("Plano Alimentar Personalizado", self.styles['subtitle'])
        elements.append(subtitle)
        
        elements.append(Spacer(1, 2 * cm))
        
        # Nome do paciente
        patient_name = diet_data.get('patient_info', {}).get('name', 'Paciente')
        patient_title = Paragraph(f"Elaborado para: <b>{patient_name}</b>", self.styles['section_header'])
        elements.append(patient_title)
        
        elements.append(Spacer(1, 1 * cm))
        
        # Data de geração
        generated_date = datetime.now().strftime("%d/%m/%Y às %H:%M")
        date_text = Paragraph(f"Gerado em: {generated_date}", self.styles['normal_text'])
        elements.append(date_text)
        
        # Informações da API
        elements.append(Spacer(1, 2 * cm))
        api_info = Paragraph(
            "<b>Dados Nutricionais:</b> USDA FoodData Central API<br/>"
            "<b>Cálculos:</b> Taxa Metabólica Basal (TMB) personalizada<br/>"
            "<b>Precisão:</b> Dados oficiais do Departamento de Agricultura dos EUA",
            self.styles['normal_text']
        )
        elements.append(api_info)
        
        return elements
    
    def _create_patient_info_section(self, diet_data: Dict[str, Any]) -> List:
        """Cria seção com informações do paciente"""
        elements = []
        patient_info = diet_data.get('patient_info', {})
        
        # Título da seção
        section_title = Paragraph("📋 Informações do Paciente", self.styles['section_header'])
        elements.append(section_title)
        
        # Tabela com informações
        patient_data = [
            ['Nome:', patient_info.get('name', 'Não informado')],
            ['Idade:', f"{patient_info.get('age', 'Não informado')} anos"],
            ['Sexo:', patient_info.get('gender', 'Não informado')],
            ['Peso:', f"{patient_info.get('weight_kg', 'Não informado')} kg"],
            ['Altura:', f"{patient_info.get('height_cm', 'Não informado')} cm"],
            ['Nível de Atividade:', patient_info.get('activity_level', 'Não informado')],
            ['Objetivo Principal:', patient_info.get('primary_objective', 'Não informado')]
        ]
        
        patient_table = Table(patient_data, colWidths=[4*cm, 10*cm])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.bg_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.text_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.bg_color]),
            ('GRID', (0, 0), (-1, -1), 1, self.primary_color)
        ]))
        
        elements.append(patient_table)
        
        return elements
    
    def _create_nutrition_calculations_section(self, diet_data: Dict[str, Any]) -> List:
        """Cria seção com cálculos nutricionais"""
        elements = []
        nutrition_calc = diet_data.get('nutritional_calculations', {})
        
        # Título da seção
        section_title = Paragraph("📊 Cálculos Nutricionais", self.styles['section_header'])
        elements.append(section_title)
        
        # TMB e calorias
        tmb_info = Paragraph(
            f"<b>Taxa Metabólica Basal (TMB):</b> {nutrition_calc.get('tmb_kcal', 'N/A')} kcal/dia<br/>"
            f"<b>Meta Calórica Diária:</b> {nutrition_calc.get('daily_target_kcal', 'N/A')} kcal<br/>"
            f"<b>Fator de Atividade:</b> {nutrition_calc.get('activity_factor', 'N/A')}<br/>"
            f"<b>Ajuste para Objetivo:</b> {nutrition_calc.get('objective_adjustment', 'N/A')}",
            self.styles['normal_text']
        )
        elements.append(tmb_info)
        
        elements.append(Spacer(1, 0.5 * cm))
        
        # Macronutrientes
        macros = nutrition_calc.get('macronutrients', {})
        if macros:
            macro_title = Paragraph("🔢 Distribuição de Macronutrientes", self.styles['section_header'])
            elements.append(macro_title)
            
            macro_data = [
                ['Macronutriente', 'Gramas/dia', 'Percentual', 'Calorias/dia']
            ]
            
            for macro_name, macro_data_item in macros.items():
                if isinstance(macro_data_item, dict):
                    macro_data.append([
                        macro_name.replace('_', ' ').title(),
                        f"{macro_data_item.get('grams_per_day', 'N/A')} g",
                        f"{macro_data_item.get('percentage', 'N/A')}%",
                        f"{macro_data_item.get('kcal_per_day', 'N/A')} kcal"
                    ])
            
            macro_table = Table(macro_data, colWidths=[4*cm, 3*cm, 3*cm, 4*cm])
            macro_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.bg_color]),
                ('GRID', (0, 0), (-1, -1), 1, self.primary_color)
            ]))
            
            elements.append(macro_table)
        
        return elements
    
    def _create_weekly_menu_section(self, diet_data: Dict[str, Any]) -> List:
        """Cria seção com menu semanal"""
        elements = []
        weekly_menu = diet_data.get('weekly_menu', {})
        
        # Título da seção
        section_title = Paragraph("🍽️ Menu Semanal", self.styles['section_header'])
        elements.append(section_title)
        
        # Para cada dia da semana
        for day, daily_menu in weekly_menu.items():
            # Título do dia
            day_title = Paragraph(f"<b>{day}</b>", self.styles['bold_text'])
            elements.append(day_title)
            
            # Tabela das refeições do dia
            meal_data = [['Refeição', 'Meta (kcal)', 'Alimentos']]
            
            meal_names = {
                'breakfast': 'Café da Manhã',
                'morning_snack': 'Lanche da Manhã',
                'lunch': 'Almoço',
                'afternoon_snack': 'Lanche da Tarde',
                'dinner': 'Jantar'
            }
            
            for meal_key, meal_info in daily_menu.items():
                meal_name = meal_names.get(meal_key, meal_key)
                target_kcal = meal_info.get('target_kcal', 0)
                foods = meal_info.get('foods', [])
                
                food_list = []
                for food_item in foods:
                    food_name = food_item.get('food', '')
                    portion = food_item.get('portion', '')
                    # Traduzir nome do alimento
                    translated_name = self._translate_food_name(food_name)
                    food_list.append(f"• {translated_name} ({portion})")
                
                foods_text = '<br/>'.join(food_list) if food_list else 'A definir'
                
                meal_data.append([
                    meal_name,
                    f"{target_kcal} kcal",
                    foods_text
                ])
            
            daily_table = Table(meal_data, colWidths=[4*cm, 3*cm, 7*cm])
            daily_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.secondary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.bg_color]),
                ('GRID', (0, 0), (-1, -1), 1, self.secondary_color)
            ]))
            
            elements.append(daily_table)
            elements.append(Spacer(1, 0.3 * cm))
        
        return elements
    
    def _create_shopping_list_section(self, diet_data: Dict[str, Any]) -> List:
        """Cria seção com lista de compras"""
        elements = []
        shopping_list = diet_data.get('shopping_list', [])
        
        # Título da seção
        section_title = Paragraph("🛒 Lista de Compras Semanal", self.styles['section_header'])
        elements.append(section_title)
        
        if shopping_list:
            # Agrupar por categoria
            categories = {}
            for item in shopping_list:
                category = item.get('category', 'Outros')
                if category not in categories:
                    categories[category] = []
                categories[category].append(item)
            
            # Para cada categoria
            for category, items in categories.items():
                category_title = Paragraph(f"<b>{category}</b>", self.styles['bold_text'])
                elements.append(category_title)
                
                item_data = [['Item', 'Quantidade Estimada']]
                for item in items:
                    item_data.append([
                        item.get('item', ''),
                        item.get('estimated_weekly_amount', 'A definir')
                    ])
                
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
        
        return elements
    
    def _create_practical_guidance_section(self, diet_data: Dict[str, Any]) -> List:
        """Cria seção com orientações práticas"""
        elements = []
        guidance = diet_data.get('practical_guidance', {})
        
        # Título da seção
        section_title = Paragraph("💡 Orientações Práticas", self.styles['section_header'])
        elements.append(section_title)
        
        # Para cada tipo de orientação
        guidance_titles = {
            'meal_timing': '⏰ Horários das Refeições',
            'hydration': '💧 Hidratação',
            'preparation_tips': '👨‍🍳 Dicas de Preparo',
            'personalized_tips': '🎯 Dicas Personalizadas'
        }
        
        for guidance_key, tips in guidance.items():
            if tips and guidance_key in guidance_titles:
                tip_title = Paragraph(guidance_titles[guidance_key], self.styles['bold_text'])
                elements.append(tip_title)
                
                for tip in tips:
                    tip_text = Paragraph(f"• {tip}", self.styles['normal_text'])
                    elements.append(tip_text)
                
                elements.append(Spacer(1, 0.3 * cm))
        
        return elements
    
    def _create_footer_section(self, diet_data: Dict[str, Any]) -> List:
        """Cria rodapé com informações da API"""
        elements = []
        
        elements.append(Spacer(1, 1 * cm))
        
        footer_info = Paragraph(
            "<b>Dados Nutricionais:</b> Este plano foi elaborado utilizando dados oficiais da "
            "USDA FoodData Central API, garantindo precisão e confiabilidade das informações nutricionais. "
            "Os cálculos de TMB foram baseados na fórmula de Harris-Benedict atualizada.<br/><br/>"
            "<b>ShapeMateAI</b> - Nutrição Inteligente e Personalizada",
            self.styles['small_text']
        )
        elements.append(footer_info)
        
        return elements
    
    def _translate_food_name(self, english_name: str) -> str:
        """Traduz nome do alimento do inglês para português"""
        translation_map = {
            'cooked white rice': 'Arroz branco cozido',
            'cooked black beans': 'Feijão preto cozido',
            'grilled chicken breast': 'Peito de frango grelhado',
            'sweet potato': 'Batata doce',
            'banana': 'Banana',
            'boiled egg': 'Ovo cozido',
            'whole milk': 'Leite integral',
            'oats': 'Aveia',
            'broccoli': 'Brócolis',
            'spinach': 'Espinafre',
            'apple': 'Maçã',
            'tomato': 'Tomate',
            'olive oil': 'Azeite de oliva',
            'salmon': 'Salmão',
            'greek yogurt': 'Iogurte grego',
            'almonds': 'Amêndoas',
            'avocado': 'Abacate',
            'quinoa': 'Quinoa'
        }
        
        return translation_map.get(english_name, english_name.title())
    
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
    """Função utilitária para criar PDF da dieta"""
    try:
        # Definir diretório de saída
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), 'generated_diets')
        
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Nome do arquivo
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
