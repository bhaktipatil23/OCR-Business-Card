#!/usr/bin/env python3
"""
Database Migration Runner for Business Card OCR System
Executes SQL migration scripts and tracks migration history
"""

import mysql.connector
import pymysql
from pathlib import Path
import logging
from app.config import settings
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigrationRunner:
    def __init__(self):
        self.migrations_dir = Path(__file__).parent / "migrations"
        self.connection = None
        
    def connect_database(self):
        """Connect to MySQL database"""
        try:
            # Try pymysql first
            self.connection = pymysql.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD or '',
                charset='utf8mb4',
                autocommit=False
            )
            logger.info("Connected to MySQL using pymysql")
            return True
        except Exception as e:
            logger.error(f"Failed to connect with pymysql: {e}")
            
        try:
            # Fallback to mysql.connector
            self.connection = mysql.connector.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD or '',
                charset='utf8mb4',
                autocommit=False
            )
            logger.info("Connected to MySQL using mysql.connector")
            return True
        except Exception as e:
            logger.error(f"Failed to connect with mysql.connector: {e}")
            return False
    
    def execute_sql_file(self, file_path: Path):
        """Execute SQL file with proper statement separation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            cursor = self.connection.cursor()
            
            # Split SQL content by semicolons and execute each statement
            statements = []
            current_statement = ""
            in_delimiter = False
            
            for line in sql_content.split('\n'):
                line = line.strip()
                
                # Handle DELIMITER statements
                if line.startswith('DELIMITER'):
                    in_delimiter = True
                    continue
                elif line == '//' and in_delimiter:
                    in_delimiter = False
                    if current_statement.strip():
                        statements.append(current_statement.strip())
                        current_statement = ""
                    continue
                
                if line and not line.startswith('--'):
                    current_statement += line + "\n"
                    
                    if not in_delimiter and line.endswith(';'):
                        statements.append(current_statement.strip())
                        current_statement = ""
            
            # Add any remaining statement
            if current_statement.strip():
                statements.append(current_statement.strip())
            
            # Execute each statement
            for i, statement in enumerate(statements):
                if statement and not statement.startswith('--'):
                    try:
                        cursor.execute(statement)
                        logger.info(f"Executed statement {i+1}/{len(statements)}")
                    except Exception as e:
                        logger.error(f"Error executing statement {i+1}: {e}")
                        logger.error(f"Statement: {statement[:200]}...")
                        raise
            
            self.connection.commit()
            cursor.close()
            logger.info(f"Successfully executed migration: {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing migration {file_path.name}: {e}")
            self.connection.rollback()
            return False
    
    def get_executed_migrations(self):
        """Get list of already executed migrations"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("USE business_card_ocr")
            cursor.execute("""
                SELECT migration_name 
                FROM migration_log 
                WHERE success = TRUE 
                ORDER BY executed_at
            """)
            executed = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return executed
        except Exception as e:
            logger.warning(f"Could not get migration history: {e}")
            return []
    
    def run_migrations(self):
        """Run all pending migrations"""
        if not self.connect_database():
            logger.error("Could not connect to database")
            return False
        
        # Get list of migration files
        migration_files = sorted([
            f for f in self.migrations_dir.glob("*.sql")
            if f.is_file()
        ])
        
        if not migration_files:
            logger.warning("No migration files found")
            return True
        
        # Get executed migrations
        executed_migrations = self.get_executed_migrations()
        
        # Run pending migrations
        success_count = 0
        for migration_file in migration_files:
            migration_name = migration_file.stem
            
            if migration_name in executed_migrations:
                logger.info(f"Skipping already executed migration: {migration_name}")
                continue
            
            logger.info(f"Running migration: {migration_name}")
            if self.execute_sql_file(migration_file):
                success_count += 1
            else:
                logger.error(f"Migration failed: {migration_name}")
                break
        
        self.connection.close()
        logger.info(f"Migration completed. {success_count} migrations executed.")
        return success_count > 0
    
    def show_database_info(self):
        """Display database schema information"""
        if not self.connect_database():
            return
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("USE business_card_ocr")
            
            # Show tables
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            print("\n" + "="*50)
            print("DATABASE SCHEMA INFORMATION")
            print("="*50)
            print(f"Database: business_card_ocr")
            print(f"Tables: {len(tables)}")
            
            for table in tables:
                print(f"\n--- Table: {table} ---")
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                
                for col in columns:
                    field, type_, null, key, default, extra = col
                    key_info = f" [{key}]" if key else ""
                    null_info = "NULL" if null == "YES" else "NOT NULL"
                    print(f"  {field}: {type_} {null_info}{key_info}")
            
            # Show foreign keys
            print(f"\n--- Foreign Key Constraints ---")
            cursor.execute("""
                SELECT 
                    CONSTRAINT_NAME,
                    TABLE_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA = 'business_card_ocr' 
                  AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            
            fks = cursor.fetchall()
            for fk in fks:
                constraint, table, column, ref_table, ref_column = fk
                print(f"  {table}.{column} -> {ref_table}.{ref_column}")
            
            # Show views
            cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
            views = cursor.fetchall()
            if views:
                print(f"\n--- Views ---")
                for view in views:
                    print(f"  {view[0]}")
            
            cursor.close()
            self.connection.close()
            
        except Exception as e:
            logger.error(f"Error showing database info: {e}")

def main():
    """Main function"""
    runner = MigrationRunner()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        runner.show_database_info()
    else:
        print("Business Card OCR - Database Migration Runner")
        print("=" * 50)
        
        if runner.run_migrations():
            print("\n✅ All migrations completed successfully!")
            print("\nTo view database schema information, run:")
            print("python run_migration.py --info")
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)

if __name__ == "__main__":
    main()