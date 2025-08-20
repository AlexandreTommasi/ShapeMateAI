"""
Persistent USDA Food Cache
Stores per-100g nutrition for foods to avoid repeated API calls.
"""
from __future__ import annotations
import sqlite3
from typing import Dict, Any, List, Optional, Callable
import os
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join("database", "shapemate.db")

@dataclass
class CachedFood:
    name_en: str
    fdc_id: Optional[str]
    kcal_per_100g: float
    protein_g: float
    carbs_g: float
    fat_g: float

class FoodCache:
    def __init__(self, db_path: str = DB_PATH, fetcher: Optional[Callable[[str], Optional[Dict[str, Any]]]] = None):
        self.db_path = db_path
        self._ensure_table()
        self.fetcher = fetcher

    def _ensure_table(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS usda_food_cache (
                name_en TEXT PRIMARY KEY,
                fdc_id TEXT,
                kcal_per_100g REAL,
                protein_g REAL,
                carbs_g REAL,
                fat_g REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()

    def get(self, name_en: str) -> Optional[CachedFood]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT name_en, fdc_id, kcal_per_100g, protein_g, carbs_g, fat_g FROM usda_food_cache WHERE name_en = ?", (name_en.lower(),))
        row = cur.fetchone()
        conn.close()
        if row:
            return CachedFood(*row)
        return None

    def set(self, name_en: str, data: Dict[str, Any], fdc_id: Optional[str] = None):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO usda_food_cache (name_en, fdc_id, kcal_per_100g, protein_g, carbs_g, fat_g)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(name_en) DO UPDATE SET
                fdc_id=excluded.fdc_id,
                kcal_per_100g=excluded.kcal_per_100g,
                protein_g=excluded.protein_g,
                carbs_g=excluded.carbs_g,
                fat_g=excluded.fat_g,
                updated_at=CURRENT_TIMESTAMP
            """,
            (
                name_en.lower(),
                fdc_id,
                float(data.get("calories_per_100g") or data.get("kcal") or 0.0),
                float(data.get("protein_g") or 0.0),
                float(data.get("carbs_g") or 0.0),
                float(data.get("fat_g") or 0.0),
            ),
        )
        conn.commit()
        conn.close()

    def prefetch(self, names: List[str]) -> Dict[str, CachedFood]:
        out: Dict[str, CachedFood] = {}
        missing: List[str] = []
        for n in names:
            item = self.get(n)
            if item:
                out[n] = item
            else:
                missing.append(n)
        # Fetch missing via fetcher if provided
        for n in missing:
            try:
                if not self.fetcher:
                    continue
                data = self.fetcher(n)
                if not data:
                    continue
                # normalize to per-100g shape
                norm = {
                    "calories_per_100g": float(data.get("calories_per_100g") or data.get("kcal") or 0.0),
                    "protein_g": float(data.get("protein_g") or 0.0),
                    "carbs_g": float(data.get("carbs_g") or 0.0),
                    "fat_g": float(data.get("fat_g") or 0.0),
                }
                self.set(n, norm, data.get("fdc_id"))
                cached = self.get(n)
                if cached:
                    out[n] = cached
            except Exception as e:
                logger.warning(f"Failed to fetch {n}: {e}")
        return out

    def as_dict(self, name_en: str) -> Optional[Dict[str, Any]]:
        c = self.get(name_en)
        if not c:
            return None
        return {
            "name": name_en,
            "calories_per_100g": c.kcal_per_100g,
            "protein_g": c.protein_g,
            "carbs_g": c.carbs_g,
            "fat_g": c.fat_g,
            "source": "USDA_CACHE",
            "description": "USDA cached per-100g"
        }
