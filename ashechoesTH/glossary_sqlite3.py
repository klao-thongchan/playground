import sqlite3
from datetime import datetime
import pandas as pd
from typing import List, Tuple, Optional
import logging

class TranslationDatabase:
    def __init__(self, db_path: str = 'translation_memory.db'):
        """
        Initialize the translation database
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.setup_logging()
        self.initialize_database()

    def setup_logging(self):
        """Configure logging for database operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('translation_db.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def initialize_database(self):
        """Create database tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Main translations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS translations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_text TEXT NOT NULL,
                        target_text TEXT NOT NULL,
                        frequency INTEGER DEFAULT 1,
                        confidence_score FLOAT DEFAULT 1.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index for faster lookups
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_source_text 
                    ON translations(source_text)
                ''')
                
                # History table for tracking changes
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS translation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        translation_id INTEGER,
                        source_text TEXT NOT NULL,
                        target_text TEXT NOT NULL,
                        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (translation_id) REFERENCES translations(id)
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise

    def add_translation(self, source: str, target: str, confidence: float = 1.0) -> bool:
        """
        Add a new translation or update existing one
        
        Args:
            source (str): Source language text
            target (str): Target language text
            confidence (float): Confidence score of the translation
        
        Returns:
            bool: Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if translation exists
                cursor.execute('''
                    SELECT id, frequency, target_text 
                    FROM translations 
                    WHERE source_text = ?
                ''', (source,))
                
                result = cursor.fetchone()
                
                if result:
                    translation_id, frequency, existing_target = result
                    
                    # Update frequency and last_used timestamp
                    cursor.execute('''
                        UPDATE translations 
                        SET frequency = frequency + 1,
                            last_used = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (translation_id,))
                    
                    # Log change in history if target text is different
                    if existing_target != target:
                        cursor.execute('''
                            INSERT INTO translation_history 
                            (translation_id, source_text, target_text)
                            VALUES (?, ?, ?)
                        ''', (translation_id, source, target))
                else:
                    # Insert new translation
                    cursor.execute('''
                        INSERT INTO translations 
                        (source_text, target_text, confidence_score)
                        VALUES (?, ?, ?)
                    ''', (source, target, confidence))
                
                conn.commit()
                self.logger.info(f"Translation added/updated: {source} -> {target}")
                return True
                
        except sqlite3.Error as e:
            self.logger.error(f"Error adding translation: {e}")
            return False

    def get_translation(self, source: str) -> Optional[str]:
        """
        Retrieve translation for source text
        
        Args:
            source (str): Source language text
        
        Returns:
            Optional[str]: Target language text if found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT target_text 
                    FROM translations 
                    WHERE source_text = ?
                    ORDER BY frequency DESC, confidence_score DESC 
                    LIMIT 1
                ''', (source,))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving translation: {e}")
            return None

    def export_to_excel(self, output_path: str) -> bool:
        """
        Export translations to Excel file
        
        Args:
            output_path (str): Path for output Excel file
        
        Returns:
            bool: Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT source_text, target_text, frequency, confidence_score 
                    FROM translations 
                    ORDER BY frequency DESC
                '''
                df = pd.read_sql_query(query, conn)
                df.to_excel(output_path, index=False)
                self.logger.info(f"Translations exported to {output_path}")
                return True
                
        except (sqlite3.Error, pd.errors.EmptyDataError) as e:
            self.logger.error(f"Error exporting translations: {e}")
            return False

    def get_statistics(self) -> dict:
        """
        Get database statistics
        
        Returns:
            dict: Statistics about the translations database
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total count
                cursor.execute('SELECT COUNT(*) FROM translations')
                total_count = cursor.fetchone()[0]
                
                # Get average confidence
                cursor.execute('SELECT AVG(confidence_score) FROM translations')
                avg_confidence = cursor.fetchone()[0]
                
                # Get most frequent translations
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM translations 
                    WHERE frequency > 1
                ''')
                frequent_count = cursor.fetchone()[0]
                
                return {
                    'total_translations': total_count,
                    'average_confidence': round(avg_confidence, 2) if avg_confidence else 0,
                    'frequent_translations': frequent_count,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}

# Usage example
if __name__ == "__main__":
    # Initialize database
    db = TranslationDatabase()
    
    # Add some sample translations
    db.add_translation("白荆回廊", "Ash Echoes", 0.95)
    db.add_translation("白荆穹顶", "ฐาน", 0.92)
    
    # Get a translation
    translation = db.get_translation("白荆回廊")
    print(f"Translation found: {translation}")
    
    # Export to Excel
    db.export_to_excel("translations_export.xlsx")
    
    # Print statistics
    stats = db.get_statistics()
    print("Database Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")