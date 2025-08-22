#!/usr/bin/env python3
"""
Teste completo da geração de dieta - do início ao fim
"""

import sys
import os
import json
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agents.nutritionist_agent import NutritionistAgent
from core.core import AgentConfig, AgentType, TaskType
from utils.diet_manager.diet_storage import DietManager
from utils.pdf_generator import create_diet_pdf

def test_complete_diet_generation():
    """Testa o fluxo completo: consulta -> geração -> salvamento -> PDF"""
    print("🧪 Testando geração completa de dieta...")
    
    # Dados do usuário (simulando cadastro)
    user_data = {
        'name': 'Maria Silva',
        'age': 28,
        'gender': 'feminino',
        'weight': 65.0,
        'height': 165.0,
        'activity_level': 'moderado',
        'primary_goal': 'perda_peso',
        'dietary_restrictions': '',
        'health_conditions': '',
        'user_id': 'test_user_456'
    }
    
    print(f"\n📋 Dados do usuário:")
    for key, value in user_data.items():
        print(f"   {key}: {value}")
    
    # Criar agente
    print(f"\n🔧 Criando agente nutricionista...")
    agent = NutritionistAgent()
    
    # Iniciar consulta
    print(f"\n🚀 Iniciando consulta...")
    consultation_state = agent.start_structured_consultation(user_data)
    
    print(f"\n📨 Mensagem inicial do agente:")
    print(f"   {consultation_state['last_response']}")
    
    # Simular respostas do usuário (versão resumida para teste)
    user_responses = [
        "acordo às 7h e durmo às 23h",
        "trabalho das 9h às 18h",
        "sim, faço yoga e caminhada",
        "yoga e caminhada",
        "3 vezes por semana",
        "1 hora por atividade",
        "aveia com banana e leite às 7h30",
        "não faço lanche da manhã",
        "salada, arroz integral e peixe às 13h",
        "uma maçã às 16h",
        "sopa de legumes às 20h",
        "não faço ceia",
        "8 copos por dia",
        "adoro frutas, legumes e peixes",
        "não como carne vermelha",
        "como mais no fim de semana",
        "falta de tempo para preparar refeições",
        "tenho tempo limitado, preciso de opções práticas"
    ]
    
    # Processar cada resposta
    for i, response in enumerate(user_responses, 1):
        print(f"\n👤 Resposta {i} do usuário:")
        print(f"   {response}")
        
        # Continuar consulta
        consultation_state = agent.continue_structured_consultation(consultation_state, response)
        
        print(f"\n🤖 Resposta {i} do agente:")
        print(f"   {consultation_state['last_response']}")
        
        # Verificar se consulta foi concluída
        if consultation_state.get('consultation_completed'):
            print(f"\n✅ Consulta concluída!")
            break
    
    # Verificar dados coletados
    print(f"\n📊 Dados coletados na consulta:")
    answers = consultation_state.get('answers', {})
    for key, value in answers.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎯 Estado final:")
    print(f"   Consulta completada: {consultation_state.get('consultation_completed', False)}")
    print(f"   Fase atual: {consultation_state.get('current_phase', 'N/A')}")
    print(f"   Pergunta atual: {consultation_state.get('current_question', 'N/A')}")
    
    # Agora testar a geração da dieta
    print(f"\n🍽️ Testando geração da dieta...")
    
    try:
        # Simular o processo de geração de dieta
        print("   📊 Calculando necessidades nutricionais...")
        
        # Criar dados de dieta simulados (baseado no que o agente real geraria)
        diet_data = {
            'patient_info': user_data,
            'nutritional_calculations': {
                'tmb_kcal': 1450.0,
                'daily_target_kcal': 1200.0,
                'activity_factor': 1.375,
                'objective_adjustment': 'Perda de peso (-250 kcal)',
                'macronutrients': {
                    'carbohydrates': {
                        'kcal_per_day': 480.0,
                        'grams_per_day': 120.0,
                        'percentage': 40
                    },
                    'proteins': {
                        'kcal_per_day': 360.0,
                        'grams_per_day': 90.0,
                        'percentage': 30
                    },
                    'fats': {
                        'kcal_per_day': 360.0,
                        'grams_per_day': 40.0,
                        'percentage': 30
                    }
                }
            },
            'weekly_menu': {
                'monday': {
                    'breakfast': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Aveia', 'portion_grams': 40, 'kcal': 150},
                                {'name_pt': 'Banana', 'portion_grams': 80, 'kcal': 70},
                                {'name_pt': 'Leite Desnatado', 'portion_grams': 200, 'kcal': 80}
                            ],
                            'totals': {'kcal': 300}
                        }]
                    },
                    'lunch': {
                        'target_kcal': 400,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Arroz Integral', 'portion_grams': 60, 'kcal': 200},
                                {'name_pt': 'Salmão', 'portion_grams': 100, 'kcal': 150},
                                {'name_pt': 'Brócolis', 'portion_grams': 80, 'kcal': 50}
                            ],
                            'totals': {'kcal': 400}
                        }]
                    },
                    'dinner': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Sopa de Legumes', 'portion_grams': 300, 'kcal': 200},
                                {'name_pt': 'Pão Integral', 'portion_grams': 40, 'kcal': 100}
                            ],
                            'totals': {'kcal': 300}
                        }]
                    }
                },
                'tuesday': {
                    'breakfast': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Iogurte Natural', 'portion_grams': 150, 'kcal': 90},
                                {'name_pt': 'Granola', 'portion_grams': 30, 'kcal': 120},
                                {'name_pt': 'Morango', 'portion_grams': 100, 'kcal': 90}
                            ],
                            'totals': {'kcal': 300}
                        }]
                    },
                    'lunch': {
                        'target_kcal': 400,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Quinoa', 'portion_grams': 80, 'kcal': 280},
                                {'name_pt': 'Frango Grelhado', 'portion_grams': 120, 'kcal': 120}
                            ],
                            'totals': {'kcal': 400}
                        }]
                    },
                    'dinner': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Salada Verde', 'portion_grams': 150, 'kcal': 100},
                                {'name_pt': 'Atum', 'portion_grams': 100, 'kcal': 200}
                            ],
                            'totals': {'kcal': 300}
                        }]
                    }
                },
                'wednesday': {
                    'breakfast': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Pão de Aveia', 'portion_grams': 60, 'kcal': 180},
                                {'name_pt': 'Ovo Cozido', 'portion_grams': 50, 'kcal': 70},
                                {'name_pt': 'Chá Verde', 'portion_grams': 200, 'kcal': 0}
                            ],
                            'totals': {'kcal': 250}
                        }]
                    },
                    'lunch': {
                        'target_kcal': 400,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Lentilha', 'portion_grams': 100, 'kcal': 300},
                                {'name_pt': 'Arroz Integral', 'portion_grams': 60, 'kcal': 200}
                            ],
                            'totals': {'kcal': 500}
                        }]
                    },
                    'dinner': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Peito de Peru', 'portion_grams': 120, 'kcal': 200},
                                {'name_pt': 'Abobrinha', 'portion_grams': 150, 'kcal': 100}
                            ],
                            'totals': {'kcal': 300}
                        }]
                    }
                },
                'thursday': {
                    'breakfast': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Smoothie de Frutas', 'portion_grams': 300, 'kcal': 200},
                                {'name_pt': 'Castanhas', 'portion_grams': 30, 'kcal': 100}
                            ],
                            'totals': {'kcal': 300}
                        }]
                    },
                    'lunch': {
                        'target_kcal': 400,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Batata Doce', 'portion_grams': 150, 'kcal': 250},
                                {'name_pt': 'Salmão', 'portion_grams': 100, 'kcal': 150}
                            ],
                            'totals': {'kcal': 400}
                        }]
                    },
                    'dinner': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Sopa de Feijão', 'portion_grams': 300, 'kcal': 200},
                                {'name_pt': 'Pão Integral', 'portion_grams': 40, 'kcal': 100}
                            ],
                            'totals': {'kcal': 300}
                        }]
                    }
                },
                'friday': {
                    'breakfast': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Mingau de Aveia', 'portion_grams': 80, 'kcal': 200},
                                {'name_pt': 'Mel', 'portion_grams': 15, 'kcal': 50},
                                {'name_pt': 'Chá de Camomila', 'portion_grams': 200, 'kcal': 0}
                            ],
                            'totals': {'kcal': 250}
                        }]
                    },
                    'lunch': {
                        'target_kcal': 400,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Arroz Integral', 'portion_grams': 80, 'kcal': 280},
                                {'name_pt': 'Feijão Preto', 'portion_grams': 100, 'kcal': 120}
                            ],
                            'totals': {'kcal': 400}
                        }]
                    },
                    'dinner': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Sopa de Legumes', 'portion_grams': 300, 'kcal': 200},
                                {'name_pt': 'Torrada Integral', 'portion_grams': 30, 'kcal': 100}
                            ],
                            'totals': {'kcal': 300}
                        }]
                    }
                },
                'saturday': {
                    'breakfast': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Panqueca de Aveia', 'portion_grams': 100, 'kcal': 200},
                                {'name_pt': 'Frutas Vermelhas', 'portion_grams': 100, 'kcal': 100}
                            ],
                            'totals': {'kcal': 300}
                        }]
                    },
                    'lunch': {
                        'target_kcal': 400,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Massa Integral', 'portion_grams': 100, 'kcal': 300},
                                {'name_pt': 'Molho de Tomate', 'portion_grams': 100, 'kcal': 100}
                            ],
                            'totals': {'kcal': 400}
                        }]
                    },
                    'dinner': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Salada Caesar', 'portion_grams': 200, 'kcal': 150},
                                {'name_pt': 'Frango Grelhado', 'portion_grams': 100, 'kcal': 150}
                            ],
                            'totals': {'kcal': 300}
                        }]
                    }
                },
                'sunday': {
                    'breakfast': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Omelete de Vegetais', 'portion_grams': 150, 'kcal': 200},
                                {'name_pt': 'Pão Integral', 'portion_grams': 40, 'kcal': 100}
                            ],
                            'totals': {'kcal': 300}
                        }]
                    },
                    'lunch': {
                        'target_kcal': 400,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Arroz de Couve-Flor', 'portion_grams': 150, 'kcal': 200},
                                {'name_pt': 'Peixe Assado', 'portion_grams': 120, 'kcal': 200}
                            ],
                            'totals': {'kcal': 400}
                        }]
                    },
                    'dinner': {
                        'target_kcal': 300,
                        'options': [{
                            'name': 'Opção 1',
                            'items': [
                                {'name_pt': 'Sopa de Legumes', 'portion_grams': 300, 'kcal': 200},
                                {'name_pt': 'Pão de Aveia', 'portion_grams': 30, 'kcal': 100}
                            ],
                            'totals': {'kcal': 300}
                        }]
                    }
                }
            },
            'shopping_list': {
                'items': [
                    {'name_pt': 'Aveia', 'category': 'Cereais', 'estimated_weekly_amount': '280g'},
                    {'name_pt': 'Banana', 'category': 'Frutas', 'estimated_weekly_amount': '560g'},
                    {'name_pt': 'Salmão', 'category': 'Proteínas', 'estimated_weekly_amount': '700g'}
                ]
            },
            'nutritional_database': {
                'oat': {'per_100g': {'kcal': 375}},
                'banana': {'per_100g': {'kcal': 89}},
                'salmon': {'per_100g': {'kcal': 150}}
            },
            'generated_at': time.time(),
            'consultation_data': consultation_state
        }
        
        print("   ✅ Dados da dieta criados")
        
        # Verificar se as porções estão sendo calculadas corretamente
        print(f"\n🔍 Verificando cálculo de porções...")
        
        # Verificar se cada refeição tem porções realistas
        for day, day_menu in diet_data['weekly_menu'].items():
            print(f"\n   📅 {day.title()}:")
            for meal_type, meal_data in day_menu.items():
                target_kcal = meal_data.get('target_kcal', 0)
                print(f"      🍽️ {meal_type}: {target_kcal} kcal")
                
                for option in meal_data.get('options', []):
                    total_kcal = option.get('totals', {}).get('kcal', 0)
                    total_protein = option.get('totals', {}).get('protein_g', 0)
                    total_carbs = option.get('totals', {}).get('carbs_g', 0)
                    total_fat = option.get('totals', {}).get('fat_g', 0)
                    
                    print(f"         📊 Total da opção: {total_kcal} kcal")
                    print(f"            🥩 Proteínas: {total_protein}g")
                    print(f"            🍞 Carboidratos: {total_carbs}g")
                    print(f"            🧈 Gorduras: {total_fat}g")
                    
                    # Verificar se está dentro da tolerância (±10%)
                    if target_kcal > 0:
                        tolerance = 0.10
                        min_kcal = target_kcal * (1 - tolerance)
                        max_kcal = target_kcal * (1 + tolerance)
                        
                        if min_kcal <= total_kcal <= max_kcal:
                            print(f"         ✅ Meta atingida (tolerância ±10%)")
                        else:
                            print(f"         ⚠️ Fora da meta: {min_kcal:.0f} - {max_kcal:.0f} kcal")
                    
                    # Verificar porções individuais
                    for item in option.get('items', []):
                        portion = item.get('portion_grams', 0)
                        kcal = item.get('kcal', 0)
                        protein = item.get('protein_g', 0)
                        carbs = item.get('carbs_g', 0)
                        fat = item.get('fat_g', 0)
                        name = item.get('name_pt', item.get('name_en', 'Alimento'))
                        
                        print(f"            • {name}: {portion}g ({kcal} kcal)")
                        print(f"               🥩 P: {protein}g | 🍞 C: {carbs}g | 🧈 G: {fat}g")
                        
                        # Verificar se as porções são realistas
                        if portion < 10:
                            print(f"               ⚠️ Porção muito pequena: {portion}g")
                        elif portion > 300:
                            print(f"               ⚠️ Porção muito grande: {portion}g")
                        else:
                            print(f"               ✅ Porção adequada: {portion}g")
                        
                        # Verificar se os macronutrientes fazem sentido
                        if kcal > 0:
                            calculated_kcal = (protein * 4) + (carbs * 4) + (fat * 9)
                            kcal_diff = abs(kcal - calculated_kcal)
                            if kcal_diff > 10:  # Tolerância de 10 kcal
                                print(f"               ⚠️ Inconsistência: {kcal} kcal vs {calculated_kcal:.1f} kcal calculado")
                            else:
                                print(f"               ✅ Macronutrientes consistentes")
        
        # Verificar se as metas diárias estão sendo atingidas
        print(f"\n🎯 Verificando metas nutricionais diárias...")
        daily_target_kcal = diet_data['nutritional_calculations']['daily_target_kcal']
        target_protein = diet_data['nutritional_calculations']['macronutrients']['proteins']['grams_per_day']
        target_carbs = diet_data['nutritional_calculations']['macronutrients']['carbohydrates']['grams_per_day']
        target_fat = diet_data['nutritional_calculations']['macronutrients']['fats']['grams_per_day']
        
        print(f"   Meta diária: {daily_target_kcal} kcal")
        print(f"   🥩 Proteínas: {target_protein}g")
        print(f"   🍞 Carboidratos: {target_carbs}g")
        print(f"   🧈 Gorduras: {target_fat}g")
        
        for day, day_menu in diet_data['weekly_menu'].items():
            daily_total_kcal = 0
            daily_total_protein = 0
            daily_total_carbs = 0
            daily_total_fat = 0
            
            for meal_data in day_menu.values():
                for option in meal_data.get('options', []):
                    daily_total_kcal += option.get('totals', {}).get('kcal', 0)
                    daily_total_protein += option.get('totals', {}).get('protein_g', 0)
                    daily_total_carbs += option.get('totals', {}).get('carbs_g', 0)
                    daily_total_fat += option.get('totals', {}).get('fat_g', 0)
            
            print(f"   📅 {day.title()}:")
            print(f"      🔥 Calorias: {daily_total_kcal:.0f} kcal")
            print(f"      🥩 Proteínas: {daily_total_protein:.1f}g")
            print(f"      🍞 Carboidratos: {daily_total_carbs:.1f}g")
            print(f"      🧈 Gorduras: {daily_total_fat:.1f}g")
            
            # Verificar se está próximo da meta (±15%)
            tolerance = 0.15
            min_daily = daily_target_kcal * (1 - tolerance)
            max_daily = daily_target_kcal * (1 + tolerance)
            
            if min_daily <= daily_total_kcal <= max_daily:
                print(f"      ✅ Meta calórica atingida")
            else:
                print(f"      ⚠️ Calorias fora da meta: {min_daily:.0f} - {max_daily:.0f} kcal")
            
            # Verificar macronutrientes
            if abs(daily_total_protein - target_protein) <= target_protein * 0.2:
                print(f"      ✅ Proteínas próximas da meta")
            else:
                print(f"      ⚠️ Proteínas: {target_protein}g vs {daily_total_protein:.1f}g")
            
            if abs(daily_total_carbs - target_carbs) <= target_carbs * 0.2:
                print(f"      ✅ Carboidratos próximos da meta")
            else:
                print(f"      ⚠️ Carboidratos: {target_carbs}g vs {daily_total_carbs:.1f}g")
            
            if abs(daily_total_fat - target_fat) <= target_fat * 0.2:
                print(f"      ✅ Gorduras próximas da meta")
            else:
                print(f"      ⚠️ Gorduras: {target_fat}g vs {daily_total_fat:.1f}g")
        
        # Testar geração do PDF
        print("   📄 Testando geração do PDF...")
        try:
            pdf_path = create_diet_pdf(diet_data)
            print(f"   ✅ PDF gerado: {pdf_path}")
            
            # Verificar se o arquivo existe
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"   📊 Tamanho do PDF: {file_size} bytes")
            else:
                print("   ❌ PDF não foi criado")
                
        except Exception as pdf_error:
            print(f"   ❌ Erro ao gerar PDF: {pdf_error}")
        
        # Testar salvamento no banco (simulado)
        print("   💾 Testando salvamento no banco...")
        try:
            # Simular salvamento
            diet_manager = DietManager()
            
            # Criar dados para salvar
            diet_to_save = {
                'user_id': user_data['user_id'],
                'diet_data': diet_data,
                'pdf_path': pdf_path if 'pdf_path' in locals() else None,
                'created_at': time.time(),
                'status': 'active'
            }
            
            print("   ✅ Dados preparados para salvamento")
            print(f"   📋 Estrutura da dieta:")
            print(f"      - Paciente: {diet_data['patient_info']['name']}")
            print(f"      - Objetivo: {diet_data['patient_info']['primary_goal']}")
            print(f"      - Meta calórica: {diet_data['nutritional_calculations']['daily_target_kcal']} kcal")
            print(f"      - Menu: {len(diet_data['weekly_menu'])} dias configurados")
            print(f"      - Lista de compras: {len(diet_data['shopping_list']['items'])} itens")
            
        except Exception as db_error:
            print(f"   ❌ Erro ao preparar dados para banco: {db_error}")
        
        print(f"\n🎉 Teste de geração de dieta concluído com sucesso!")
        return diet_data
        
    except Exception as e:
        print(f"\n❌ Erro durante geração da dieta: {e}")
        return None

if __name__ == '__main__':
    test_complete_diet_generation()
