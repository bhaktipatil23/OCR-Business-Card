import google.generativeai as genai
from PIL import Image
from app.config import settings
from typing import Dict, List
import json
from app.utils.logger import app_logger

class BusinessCardValidator:
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def validate_business_card(self, image_path: str) -> Dict:
        """Validate if the uploaded image is a business card"""
        try:
            pass
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            prompt = """
Analyze the uploaded image and determine if it is a business card.

A business card typically contains:
- Person's name and job title
- Company/organization name
- Contact information (phone, email, address)
- Logo or branding elements
- Professional layout in standard card dimensions

Please respond with:
1. YES or NO - whether this is a business card
2. Confidence level (High/Medium/Low)
3. Brief explanation of your determination
4. If YES, list the key information visible on the card

Format your response as:
Business Card: [YES/NO]
Confidence: [High/Medium/Low]
Reasoning: [Your explanation]
Information Found: [List if applicable]
"""
            
            generation_config = {
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            pass
            response = self.model.generate_content(
                [prompt, image],
                generation_config=generation_config
            )
            pass
            
            # Parse the response
            response_text = response.text.strip()
            
            # Extract information from response
            is_business_card = "YES" in response_text.upper() and "Business Card:" in response_text
            
            # Extract confidence level
            confidence = "Medium"  # default
            if "Confidence: High" in response_text:
                confidence = "High"
            elif "Confidence: Low" in response_text:
                confidence = "Low"
            
            # Extract reasoning
            reasoning = "Unable to determine"
            if "Reasoning:" in response_text:
                reasoning_start = response_text.find("Reasoning:") + 10
                reasoning_end = response_text.find("Information Found:", reasoning_start)
                if reasoning_end == -1:
                    reasoning = response_text[reasoning_start:].strip()
                else:
                    reasoning = response_text[reasoning_start:reasoning_end].strip()
            
            # Extract information found
            information_found = []
            if "Information Found:" in response_text:
                info_start = response_text.find("Information Found:") + 18
                info_text = response_text[info_start:].strip()
                if info_text and info_text != "[List if applicable]":
                    information_found = [info_text]
            
            result = {
                "is_business_card": is_business_card,
                "confidence": confidence,
                "reasoning": reasoning,
                "information_found": information_found,
                "raw_response": response_text
            }
            
            status = "VALID" if is_business_card else "INVALID"
            
            return result
            
        except Exception as e:
            app_logger.error(f"[VALIDATOR] Error validating {image_path}: {e}")
            return {
                "is_business_card": False,
                "confidence": "Low",
                "reasoning": f"Validation failed: {str(e)}",
                "information_found": [],
                "raw_response": ""
            }
    
    async def validate_batch(self, file_list: List[Dict]) -> Dict:
        """Validate multiple files for business card detection"""
        app_logger.info(f"[VALIDATOR] Validating {len(file_list)} files")
        
        results = {
            "valid_business_cards": [],
            "invalid_files": [],
            "validation_summary": {
                "total_files": len(file_list),
                "valid_cards": 0,
                "invalid_files": 0
            }
        }
        
        for i, file_info in enumerate(file_list, 1):
            try:
                pass
                validation_result = await self.validate_business_card(file_info['file_path'])
                
                file_result = {
                    "file_id": file_info['file_id'],
                    "filename": file_info['filename'],
                    "file_path": file_info['file_path'],
                    "validation": validation_result
                }
                
                if validation_result['is_business_card']:
                    results['valid_business_cards'].append(file_result)
                    results['validation_summary']['valid_cards'] += 1
                    pass
                else:
                    results['invalid_files'].append(file_result)
                    results['validation_summary']['invalid_files'] += 1
                    pass
                    
            except Exception as e:
                app_logger.error(f"[VALIDATOR] Error with {file_info['filename']}: {e}")
                file_result = {
                    "file_id": file_info['file_id'],
                    "filename": file_info['filename'],
                    "file_path": file_info['file_path'],
                    "validation": {
                        "is_business_card": False,
                        "confidence": "Low",
                        "reasoning": f"Validation error: {str(e)}",
                        "information_found": [],
                        "raw_response": ""
                    }
                }
                results['invalid_files'].append(file_result)
                results['validation_summary']['invalid_files'] += 1
        
        app_logger.info(f"[VALIDATOR] Completed: {results['validation_summary']['valid_cards']} valid, {results['validation_summary']['invalid_files']} invalid")
        return results