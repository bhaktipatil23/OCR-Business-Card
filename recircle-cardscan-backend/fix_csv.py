import csv
import os

def fix_csv_phone_formatting(csv_path):
    """Fix phone number formatting in existing CSV"""
    temp_path = csv_path + ".tmp"
    
    with open(csv_path, 'r', encoding='utf-8') as infile, \
         open(temp_path, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
        
        for i, row in enumerate(reader):
            if i == 0:  # Header row
                writer.writerow(row)
            else:
                # Fix phone column (index 1)
                if len(row) > 1 and row[1] and row[1] != "N/A":
                    row[1] = "\t" + row[1]
                writer.writerow(row)
    
    # Replace original file
    os.replace(temp_path, csv_path)
    print(f"Fixed: {csv_path}")

# Fix the current CSV file
csv_file = "output/batch_20251117_144801_data.csv"
if os.path.exists(csv_file):
    fix_csv_phone_formatting(csv_file)