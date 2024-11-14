from django.apps import AppConfig
import sqlite3
from django.conf import settings
import os


class RelatoriosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'relatorios'

    def ready(self):
        # Otimizações do SQLite
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Configurações de performance
            cursor.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging
            cursor.execute('PRAGMA synchronous=NORMAL')  # Menos sync com disco
            cursor.execute('PRAGMA cache_size=-2000')  # Cache de ~2MB
            cursor.execute('PRAGMA temp_store=MEMORY')  # Temp tables na memória
            
            conn.close()
        except Exception as e:
            print(f"Aviso: Não foi possível otimizar o SQLite: {e}")
