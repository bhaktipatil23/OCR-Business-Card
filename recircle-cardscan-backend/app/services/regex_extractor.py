import re
from typing import Dict, Optional

class RegexExtractor:
    
    def __init__(self):
        # Define regex patterns
        self.patterns = {
            'name': r'([A-Z][a-z]+\s+[A-Z][a-z]+)',
            'phone': r'(\+91[\s-]?\d{5}[\s-]?\d{5}|\d{10})',
            'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'company': r'([A-Z][A-Za-z\s&.]+(?:Pvt\.?\s*Ltd\.?|Industries|International|Corporation|Corp\.?))',
            'designation': r'(Managing\s+Director|Director|Manager|CEO|Executive|AGM)'
        }
    
    def extract_all(self, raw_text: str) -> Dict[str, Optional[str]]:
        """Extract all fields from raw text"""
        print(f"\n🔍 RAW TEXT FROM VISION AI:")
        print(f"'{raw_text}'")
        print(f"Length: {len(raw_text)} characters\n")
        
        extracted = {}
        
        for field, pattern in self.patterns.items():
            match = re.search(pattern, raw_text, re.IGNORECASE)
            if match:
                if field == 'name':
                    extracted[field] = match.group(1).strip()
                elif field == 'designation':
                    extracted[field] = match.group(1).strip()
                elif field == 'company':
                    extracted[field] = match.group(1).strip()
                else:
                    extracted[field] = match.group(0).strip()
                print(f"✅ Extracted {field}: {extracted[field]}")
            else:
                extracted[field] = "N/A"
                print(f"⚠️  No {field} found")
        
        return extracted