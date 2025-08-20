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
            
            # 6. Orientações práticas (se existir)
            if diet_data.get('practical_guidance'):
                elements.extend(self._create_practical_guidance_section(diet_data))
            
            # 7. Dados da fonte nutricional
            elements.extend(self._create_data_source_section(diet_data))
            
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
        """Cria página de capa usando dados do JSON"""
        elements = []
        
        elements.append(Spacer(1, 1 * cm))
        
        # Logo e título
        title = Paragraph("🍃 ShapeMateAI", self.styles['title'])
        elements.append(title)
        
        subtitle = Paragraph("Plano Alimentar Personalizado", self.styles['subtitle'])
        elements.append(subtitle)
        
        elements.append(Spacer(1, 2 * cm))
        
        # Nome do paciente
        patient_info = diet_data['patient_info']
        if isinstance(patient_info, dict):
            patient_name = patient_info.get('name', 'Paciente')
        else:
            patient_name = 'Paciente'
        patient_title = Paragraph(f"Elaborado para: <b>{patient_name}</b>", self.styles['section_header'])
        elements.append(patient_title)
        
        elements.append(Spacer(1, 1 * cm))
        
        # Data de geração
        generated_at = diet_data.get('generated_at', datetime.now().isoformat())
        try:
            # Parse da data ISO
            gen_date = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
            formatted_date = gen_date.strftime("%d/%m/%Y às %H:%M")
        except:
            formatted_date = datetime.now().strftime("%d/%m/%Y às %H:%M")
        
        date_text = Paragraph(f"Gerado em: {formatted_date}", self.styles['normal_text'])
        elements.append(date_text)
        
        # Informações da fonte de dados
        elements.append(Spacer(1, 2 * cm))
        data_source = diet_data.get('nutrition_data_source', {})
        source_name = data_source.get('primary_source', 'USDA FoodData Central API')
        foods_analyzed = data_source.get('foods_analyzed', 'N/A')
        
        api_info = Paragraph(
            f"<b>Dados Nutricionais:</b> {source_name}<br/>"
            f"<b>Alimentos Analisados:</b> {foods_analyzed}<br/>"
            f"<b>Cálculos:</b> Taxa Metabólica Basal (TMB) personalizada<br/>"
            f"<b>Precisão:</b> Dados oficiais per 100g",
            self.styles['normal_text']
        )
        elements.append(api_info)
        
        return elements
    
    def _create_patient_info_section(self, diet_data: Dict[str, Any]) -> List:
        """Cria seção com informações do paciente"""
        elements = []
        patient_info = diet_data['patient_info']
        if not isinstance(patient_info, dict):
            # Se não for dicionário, criar um dicionário padrão
            patient_info = {
                'name': 'Paciente',
                'age': 'Não informado',
                'gender': 'Não informado',
                'weight_kg': 'Não informado',
                'height_cm': 'Não informado',
                'activity_level': 'Não informado',
                'primary_objective': 'Não informado'
            }
        
        section_title = Paragraph("📋 Informações do Paciente", self.styles['section_header'])
        elements.append(section_title)
        
        # Formatar dados do paciente
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
        nutrition_calc = diet_data['nutritional_calculations']
        
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
            
            macro_data = [['Macronutriente', 'Gramas/dia', 'Percentual', 'Calorias/dia']]
            
            for macro_name, macro_values in macros.items():
                if isinstance(macro_values, dict):
                    display_name = macro_name.replace('_', ' ').title()
                    macro_data.append([
                        display_name,
                        f"{macro_values.get('grams_per_day', 'N/A')} g",
                        f"{macro_values.get('percentage', 'N/A')}%",
                        f"{macro_values.get('kcal_per_day', 'N/A')} kcal"
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
        """Cria seção com menu semanal usando dados diretos do JSON"""
        elements = []
        weekly_menu = diet_data.get('weekly_menu', {})
        
        section_title = Paragraph("🍽️ Menu Semanal", self.styles['section_header'])
        elements.append(section_title)
        
        # Mapeamento de nomes de refeições
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
        ordered_days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        # Se a estrutura vier com chaves diferentes, mantém ordem de entrada no final
        extra_days = [k for k in weekly_menu.keys() if str(k).lower() not in ordered_days]
        days_iter = ordered_days + extra_days

        for day in days_iter:
            if day not in weekly_menu:
                continue
            daily_menu = weekly_menu[day]
            # Título do dia (PT-BR)
            day_pt = day_names.get(str(day).lower(), str(day).title())
            day_title = Paragraph(f"<b>{day_pt}</b>", self.styles['bold_text'])
            elements.append(day_title)
            
            # Para cada refeição do dia
            for meal_key, meal_data in daily_menu.items():
                if not meal_data:
                    continue
                
                meal_name = meal_names.get(meal_key, meal_key.title())
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
                        display_name = item.get('name_pt') or item.get('name_en', '')
                        portion = item.get('portion_grams', 0)
                        kcal = item.get('kcal', 0)
                        food_items.append(f"• {display_name} - {portion}g ({kcal} kcal)")
                    
                    option_text = f"<b>{option_name}:</b><br/>"
                    option_text += "<br/>".join(food_items)
                    option_text += f"<br/><i>Total: {totals.get('kcal', 0)} kcal</i>"
                    
                    option_para = Paragraph(option_text, self.styles['normal_text'])
                    elements.append(option_para)
                    elements.append(Spacer(1, 0.2 * cm))
            
            elements.append(Spacer(1, 0.5 * cm))
        
        return elements
    
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
                category_title = Paragraph(f"<b>{category}</b>", self.styles['bold_text'])
                elements.append(category_title)
                
                item_data = [['Item', 'Quantidade Estimada']]
                for item in category_items:
                    name_pt = item.get('name_pt', item.get('name_en', ''))
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
    
    def _create_practical_guidance_section(self, diet_data: Dict[str, Any]) -> List:
        """Cria seção com orientações práticas"""
        elements = []
        guidance = diet_data.get('practical_guidance', {})
        
        section_title = Paragraph("💡 Orientações Práticas", self.styles['section_header'])
        elements.append(section_title)
        
        for guidance_key, tips in guidance.items():
            if tips:
                guidance_title = guidance_key.replace('_', ' ').title()
                tip_title = Paragraph(f"<b>{guidance_title}</b>", self.styles['bold_text'])
                elements.append(tip_title)
                
                if isinstance(tips, list):
                    for tip in tips:
                        tip_text = Paragraph(f"• {tip}", self.styles['normal_text'])
                        elements.append(tip_text)
                else:
                    tip_text = Paragraph(str(tips), self.styles['normal_text'])
                    elements.append(tip_text)
                
                elements.append(Spacer(1, 0.3 * cm))
        
        return elements
    
    def _create_data_source_section(self, diet_data: Dict[str, Any]) -> List:
        """Cria seção com informações da fonte de dados"""
        elements = []
        
        elements.append(Spacer(1, 1 * cm))
        
        data_source = diet_data.get('nutrition_data_source', {})
        source_name = data_source.get('primary_source', 'USDA FoodData Central API')
        foods_count = data_source.get('foods_analyzed', 'N/A')
        last_updated = data_source.get('last_updated', 'N/A')
        
        footer_info = Paragraph(
            f"<b>Fonte dos Dados Nutricionais:</b> {source_name}<br/>"
            f"<b>Alimentos Analisados:</b> {foods_count}<br/>"
            f"<b>Última Atualização:</b> {last_updated}<br/><br/>"
            f"<b>ShapeMateAI</b> - Nutrição Inteligente e Personalizada<br/>"
            f"Todos os cálculos baseados em dados oficiais e metodologia científica.",
            self.styles['small_text']
        )
        elements.append(footer_info)
        
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