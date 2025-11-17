# MySQL Database Setup for Business Card OCR

This guide will help you set up MySQL database integration for the Business Card OCR system.

## Prerequisites

1. **MySQL Server** installed and running
2. **Python dependencies** installed

## Installation Steps

### 1. Install MySQL Dependencies

```bash
pip install sqlalchemy==2.0.23 mysqlclient==2.2.0 alembic==1.12.1
```

**Note for Windows users:** If you encounter issues installing `mysqlclient`, you may need to:
- Install Microsoft Visual C++ Build Tools
- Or use `pymysql` as an alternative: `pip install pymysql`

### 2. Configure Database Settings

Update the `.env` file with your MySQL credentials:

```env
# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=business_card_ocr
```

### 3. Create Database and Tables

Run the setup script:

```bash
python setup_database.py
```

This script will:
- Create the `business_card_ocr` database if it doesn't exist
- Create all necessary tables
- Verify the connection

### 4. Database Schema

The system creates the following tables:

#### `business_cards`
- Stores uploaded files and extracted data
- Fields: name, phone, email, company, designation, address
- Includes validation results and processing metadata

#### `business_card_edits`
- Tracks all field edits made through the save button
- Maintains edit history with timestamps

#### `processing_batches`
- Tracks batch processing status
- Monitors upload, validation, and processing progress

## Features

### 1. Automatic Data Storage
- All uploaded files are stored in the database
- Extracted OCR data is automatically saved
- Validation results are preserved

### 2. Edit Tracking
- Every field edit is tracked with history
- Old and new values are stored
- Timestamps for all changes

### 3. Batch Management
- Processing status tracking
- Progress monitoring
- Error handling and recovery

## API Endpoints

### Field Updates (Save Button)
```
PATCH /api/v1/preview/{file_id}/update
```
Body:
```json
{
  "field": "name",
  "value": "John Doe"
}
```

### Edit History
```
GET /api/v1/preview/{file_id}/edit-history
```

## Database Operations

### View All Business Cards
```sql
SELECT * FROM business_cards ORDER BY created_at DESC;
```

### View Edit History
```sql
SELECT bc.filename, bce.field_name, bce.old_value, bce.new_value, bce.edited_at
FROM business_card_edits bce
JOIN business_cards bc ON bce.business_card_id = bc.id
ORDER BY bce.edited_at DESC;
```

### Processing Statistics
```sql
SELECT 
    status,
    COUNT(*) as batch_count,
    AVG(total_files) as avg_files_per_batch
FROM processing_batches 
GROUP BY status;
```

## Troubleshooting

### Connection Issues
1. Verify MySQL server is running
2. Check credentials in `.env` file
3. Ensure database user has proper permissions

### Installation Issues
- For Windows: Install Visual C++ Build Tools
- For Linux: Install `python3-dev` and `libmysqlclient-dev`
- Alternative: Use `pymysql` instead of `mysqlclient`

### Performance Optimization
- Add indexes for frequently queried fields
- Consider connection pooling for high traffic
- Regular database maintenance and cleanup

## Security Notes

1. **Never commit database passwords** to version control
2. **Use environment variables** for sensitive configuration
3. **Implement proper user permissions** in MySQL
4. **Regular backups** of the database
5. **SSL connections** for production environments