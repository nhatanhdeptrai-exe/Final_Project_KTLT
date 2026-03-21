"""ExcelHandler — Đọc/ghi dữ liệu XLSX. Files: guests.xlsx, invoices.xlsx"""
import os
from typing import Dict, List, Optional
import pandas as pd


class ExcelHandler:
    @staticmethod
    def _ensure_file(file_path: str) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            df = pd.DataFrame()
            df.to_excel(file_path, index=False, engine='openpyxl')

    @staticmethod
    def load(file_path: str) -> pd.DataFrame:
        ExcelHandler._ensure_file(file_path)
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            # Convert all columns to object to avoid dtype conflicts
            for col in df.columns:
                df[col] = df[col].astype(object)
            # Replace NaN with None
            df = df.where(df.notna(), None)
            return df
        except:
            return pd.DataFrame()

    @staticmethod
    def save(file_path: str, df: pd.DataFrame) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_excel(file_path, index=False, engine='openpyxl')

    @staticmethod
    def add_item(file_path: str, item: Dict) -> Dict:
        df = ExcelHandler.load(file_path)
        # Auto ID
        if 'id' in df.columns and len(df) > 0:
            max_id = int(df['id'].max())
        else:
            max_id = 0
        item['id'] = max_id + 1
        new_row = pd.DataFrame([item])
        df = pd.concat([df, new_row], ignore_index=True)
        ExcelHandler.save(file_path, df)
        return item

    @staticmethod
    def update_item(file_path: str, item_id: int, updates: Dict) -> bool:
        df = ExcelHandler.load(file_path)
        if 'id' not in df.columns: return False
        mask = df['id'] == item_id
        if not mask.any(): return False
        for key, value in updates.items():
            if key != 'id':
                df.loc[mask, key] = value
        ExcelHandler.save(file_path, df)
        return True

    @staticmethod
    def delete_item(file_path: str, item_id: int) -> bool:
        df = ExcelHandler.load(file_path)
        if 'id' not in df.columns: return False
        mask = df['id'] == item_id
        if not mask.any(): return False
        df = df[~mask]
        ExcelHandler.save(file_path, df)
        return True

    @staticmethod
    def find_by_id(file_path: str, item_id: int) -> Optional[Dict]:
        df = ExcelHandler.load(file_path)
        if 'id' not in df.columns: return None
        row = df[df['id'] == item_id]
        if row.empty: return None
        return row.iloc[0].to_dict()

    @staticmethod
    def get_all(file_path: str) -> List[Dict]:
        df = ExcelHandler.load(file_path)
        if df.empty: return []
        return df.to_dict('records')
