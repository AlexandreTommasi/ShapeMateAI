"""
Gerenciador de Dietas
Armazena e gerencia dietas dos usuários
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DietManager:
    """Gerenciador de dietas dos usuários"""
    
    def __init__(self, db_path: str = "database/shapemate.db"):
        self.db_path = db_path
        self._init_diet_tables()
    
    def _init_diet_tables(self):
        """Inicializa tabelas para dietas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de dietas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_diets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                diet_name VARCHAR(200),
                diet_data TEXT NOT NULL,
                source VARCHAR(50) DEFAULT 'nutritionist',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabela de listas de compras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shopping_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                diet_id INTEGER,
                list_name VARCHAR(200),
                items TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (diet_id) REFERENCES user_diets (id)
            )
        ''')
        
        # Tabela de estoque em casa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS home_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item_name VARCHAR(200) NOT NULL,
                quantity VARCHAR(50),
                unit VARCHAR(20),
                category VARCHAR(100),
                expiration_date DATE,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_diet(self, user_id: int, diet_data: Dict[str, Any], 
                  diet_name: str = None, source: str = "nutritionist") -> int:
        """Salva uma dieta para o usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if not diet_name:
                diet_name = f"Dieta {datetime.now().strftime('%d/%m/%Y')}"
            
            # Desativar dietas anteriores se esta for ativa
            if diet_data.get('is_active', True):
                cursor.execute('''
                    UPDATE user_diets SET is_active = 0 
                    WHERE user_id = ? AND is_active = 1
                ''', (user_id,))
            
            # Inserir nova dieta
            cursor.execute('''
                INSERT INTO user_diets (user_id, diet_name, diet_data, source)
                VALUES (?, ?, ?, ?)
            ''', (user_id, diet_name, json.dumps(diet_data), source))
            
            diet_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Dieta salva para usuário {user_id}: {diet_name}")
            return diet_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao salvar dieta: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_diet(self, user_id: int, diet_id: int = None) -> Optional[Dict[str, Any]]:
        """Obtém a dieta do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if diet_id:
                cursor.execute('''
                    SELECT id, diet_name, diet_data, source, created_at, is_active
                    FROM user_diets 
                    WHERE user_id = ? AND id = ?
                ''', (user_id, diet_id))
            else:
                # Pegar dieta ativa
                cursor.execute('''
                    SELECT id, diet_name, diet_data, source, created_at, is_active
                    FROM user_diets 
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY created_at DESC LIMIT 1
                ''', (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'data': json.loads(result[2]),
                    'source': result[3],
                    'created_at': result[4],
                    'is_active': bool(result[5])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter dieta: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_diet_list(self, user_id: int) -> List[Dict[str, Any]]:
        """Lista todas as dietas do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, diet_name, source, created_at, is_active
                FROM user_diets 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            results = cursor.fetchall()
            
            return [{
                'id': row[0],
                'name': row[1],
                'source': row[2],
                'created_at': row[3],
                'is_active': bool(row[4])
            } for row in results]
            
        except Exception as e:
            logger.error(f"Erro ao listar dietas: {e}")
            return []
        finally:
            conn.close()
    
    def create_shopping_list(self, user_id: int, diet_id: int = None, 
                           custom_items: List[str] = None) -> int:
        """Cria lista de compras baseada na dieta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            items = []
            list_name = f"Lista {datetime.now().strftime('%d/%m/%Y')}"
            
            if diet_id:
                # Extrair ingredientes da dieta
                diet = self.get_user_diet(user_id, diet_id)
                if diet:
                    items = self._extract_ingredients_from_diet(diet['data'])
                    list_name = f"Lista - {diet['name']}"
            
            if custom_items:
                items.extend(custom_items)
            
            # Remover duplicatas
            items = list(set(items))
            
            cursor.execute('''
                INSERT INTO shopping_lists (user_id, diet_id, list_name, items)
                VALUES (?, ?, ?, ?)
            ''', (user_id, diet_id, list_name, json.dumps(items)))
            
            list_id = cursor.lastrowid
            conn.commit()
            
            return list_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao criar lista de compras: {e}")
            raise
        finally:
            conn.close()
    
    def _extract_ingredients_from_diet(self, diet_data: Dict[str, Any]) -> List[str]:
        """Extrai ingredientes da dieta"""
        ingredients = []
        
        meal_plans = diet_data.get('meal_plans', {})
        
        for meal_type, meals in meal_plans.items():
            for meal in meals:
                if isinstance(meal, str):
                    # Extrair ingredientes básicos do texto
                    ingredients.extend(self._parse_ingredients_from_text(meal))
                elif isinstance(meal, dict):
                    if 'ingredients' in meal:
                        ingredients.extend(meal['ingredients'])
        
        return ingredients
    
    def _parse_ingredients_from_text(self, text: str) -> List[str]:
        """Extrai ingredientes de texto livre"""
        # Lista básica de ingredientes comuns
        common_ingredients = [
            'arroz', 'feijão', 'frango', 'carne', 'peixe', 'ovo', 'leite',
            'pão', 'macarrão', 'batata', 'cenoura', 'alface', 'tomate',
            'cebola', 'alho', 'azeite', 'sal', 'açúcar', 'farinha',
            'aveia', 'banana', 'maçã', 'iogurte', 'queijo'
        ]
        
        found_ingredients = []
        text_lower = text.lower()
        
        for ingredient in common_ingredients:
            if ingredient in text_lower:
                found_ingredients.append(ingredient.title())
        
        return found_ingredients
    
    def get_shopping_lists(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtém listas de compras do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, list_name, items, created_at, is_completed
                FROM shopping_lists 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            results = cursor.fetchall()
            
            return [{
                'id': row[0],
                'name': row[1],
                'items': json.loads(row[2]),
                'created_at': row[3],
                'is_completed': bool(row[4])
            } for row in results]
            
        except Exception as e:
            logger.error(f"Erro ao obter listas de compras: {e}")
            return []
        finally:
            conn.close()
    
    def update_inventory_item(self, user_id: int, item_name: str, 
                            quantity: str, unit: str = 'unidade', 
                            category: str = 'geral', expiration_date: str = None):
        """Atualiza item no estoque"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verificar se item já existe
            cursor.execute('''
                SELECT id FROM home_inventory 
                WHERE user_id = ? AND item_name = ?
            ''', (user_id, item_name))
            
            existing = cursor.fetchone()
            
            if existing:
                # Atualizar existente
                cursor.execute('''
                    UPDATE home_inventory 
                    SET quantity = ?, unit = ?, category = ?, 
                        expiration_date = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (quantity, unit, category, expiration_date, existing[0]))
            else:
                # Inserir novo
                cursor.execute('''
                    INSERT INTO home_inventory 
                    (user_id, item_name, quantity, unit, category, expiration_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, item_name, quantity, unit, category, expiration_date))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erro ao atualizar estoque: {e}")
            raise
        finally:
            conn.close()
    
    def get_inventory(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtém estoque do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT item_name, quantity, unit, category, expiration_date, updated_at
                FROM home_inventory 
                WHERE user_id = ?
                ORDER BY category, item_name
            ''', (user_id,))
            
            results = cursor.fetchall()
            
            return [{
                'name': row[0],
                'quantity': row[1],
                'unit': row[2],
                'category': row[3],
                'expiration_date': row[4],
                'updated_at': row[5]
            } for row in results]
            
        except Exception as e:
            logger.error(f"Erro ao obter estoque: {e}")
            return []
        finally:
            conn.close()

# Instância global
diet_manager = DietManager()
