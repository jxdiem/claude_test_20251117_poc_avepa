"""
Utility per gestione database SQLite
"""
import sqlite3
from contextlib import contextmanager
from typing import Generator
import os

class DatabaseManager:
    """Gestore connessioni database SQLite"""

    def __init__(self, db_path: str):
        """
        Inizializza il database manager

        Args:
            db_path: Path al file database SQLite
        """
        self.db_path = db_path
        # Crea directory se non esiste
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager per gestione connessione database

        Yields:
            Connessione SQLite
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permette accesso per nome colonna
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def execute_script(self, script: str) -> None:
        """
        Esegue uno script SQL

        Args:
            script: Script SQL da eseguire
        """
        with self.get_connection() as conn:
            conn.executescript(script)

    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Esegue una query e ritorna i risultati

        Args:
            query: Query SQL
            params: Parametri per la query

        Returns:
            Lista di risultati (dict)
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Esegue una query di update/insert/delete

        Args:
            query: Query SQL
            params: Parametri per la query

        Returns:
            ID dell'ultimo record inserito o numero righe modificate
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
