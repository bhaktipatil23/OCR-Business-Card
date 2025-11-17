#!/usr/bin/env python3
"""
Database setup script for Business Card OCR system
Run this script to create the MySQL database and tables
"""

import mysql.connector
from mysql.connector import Error
from app.config import settings
from app.core.database import init_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Create the MySQL database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME}")
            logger.info(f"Database '{settings.DB_NAME}' created or already exists")
            
            # Grant privileges (optional, adjust as needed)
            cursor.execute(f"USE {settings.DB_NAME}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        logger.error(f"Error creating database: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("Starting database setup...")
    
    # Step 1: Create database
    if not create_database():
        logger.error("Failed to create database. Please check your MySQL connection settings.")
        return False
    
    # Step 2: Initialize tables
    if not init_database():
        logger.error("Failed to initialize database tables.")
        return False
    
    logger.info("Database setup completed successfully!")
    logger.info(f"Database: {settings.DB_NAME}")
    logger.info(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)