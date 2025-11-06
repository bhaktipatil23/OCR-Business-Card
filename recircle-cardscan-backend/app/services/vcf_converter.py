import csv
import os
from typing import List, Dict
from app.config import settings

class VCFConverter:
    
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.vcf_path = os.path.join(settings.OUTPUT_CSV_PATH, f"{batch_id}_contacts.vcf")
    
    def csv_to_vcf(self, csv_file_path: str) -> str:
        """Convert CSV file to VCF format"""
        try:
            vcf_content = []
            
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Skip empty rows or rows with only phone numbers
                    if not row.get('Name') or row.get('Name').strip() == '':
                        continue
                    
                    vcf_entry = self._create_vcf_entry(row)
                    vcf_content.append(vcf_entry)
            
            # Write VCF file
            with open(self.vcf_path, 'w', encoding='utf-8') as vcffile:
                vcffile.write('\n'.join(vcf_content))
            
            print(f"✅ VCF file created: {self.vcf_path}")
            return self.vcf_path
            
        except Exception as e:
            print(f"❌ VCF conversion error: {e}")
            raise e
    
    def _create_vcf_entry(self, row: Dict[str, str]) -> str:
        """Create a single VCF entry from CSV row"""
        vcf_lines = []
        
        # Start vCard
        vcf_lines.append("BEGIN:VCARD")
        vcf_lines.append("VERSION:3.0")
        
        # Name
        name = row.get('Name', '').strip()
        if name and name != 'N/A':
            vcf_lines.append(f"FN:{name}")
            # Split name for structured name field
            name_parts = name.split()
            if len(name_parts) >= 2:
                vcf_lines.append(f"N:{name_parts[-1]};{' '.join(name_parts[:-1])};;;")
            else:
                vcf_lines.append(f"N:{name};;;;")
        
        # Phone numbers
        phone = row.get('Phone', '').strip()
        if phone and phone != 'N/A':
            # Handle multiple phone numbers
            phones = [p.strip() for p in phone.split(',') if p.strip()]
            for i, phone_num in enumerate(phones):
                if len(phone_num) == 10:  # Mobile
                    vcf_lines.append(f"TEL;TYPE=CELL:+91{phone_num}")
                elif len(phone_num) > 10:  # Landline
                    vcf_lines.append(f"TEL;TYPE=WORK:{phone_num}")
                else:
                    vcf_lines.append(f"TEL:{phone_num}")
        
        # Email
        email = row.get('Email', '').strip()
        if email and email != 'N/A':
            emails = [e.strip() for e in email.split(',') if e.strip()]
            for email_addr in emails:
                vcf_lines.append(f"EMAIL:{email_addr}")
        
        # Organization
        company = row.get('Company', '').strip()
        if company and company != 'N/A':
            vcf_lines.append(f"ORG:{company}")
        
        # Title/Designation
        designation = row.get('Designation', '').strip()
        if designation and designation != 'N/A':
            vcf_lines.append(f"TITLE:{designation}")
        
        # Address
        address = row.get('Address', '').strip()
        if address and address != 'N/A':
            vcf_lines.append(f"ADR:;;{address};;;;")
        
        # End vCard
        vcf_lines.append("END:VCARD")
        
        return '\n'.join(vcf_lines)
    
    def get_vcf_path(self) -> str:
        """Get the VCF file path"""
        return self.vcf_path