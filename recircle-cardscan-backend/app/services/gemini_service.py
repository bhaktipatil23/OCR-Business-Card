import google.generativeai as genai
from PIL import Image, ImageEnhance, ImageFilter
import base64
import io
from app.config import settings
from typing import Dict, Optional, List
import json
from app.services.gemini_memory import GeminiMemoryManager
import numpy as np
import cv2


class GeminiService:
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.memory = GeminiMemoryManager()
    
    async def extract_document_data(self, image_path: str, custom_prompt_id: str = None) -> list:
        """Extract structured data from business card using dynamic prompts"""
        if custom_prompt_id:
            return await self.extract_with_memory_prompt(image_path, custom_prompt_id)
        else:
            return await self.extract_business_card_data(image_path)
    

    
    async def extract_business_card_data(self, image_path: str) -> list:
        """Extract structured data from business card using stored prompt from Gemini memory"""
        try:
            # Try to get prompt from memory first
            stored_prompt = await self.memory.get_prompt("business_card_extraction")
            if stored_prompt:
                print("✅ Using stored prompt from Gemini memory")
                return await self.extract_with_memory_prompt(image_path, "business_card_extraction")
            
            print("⚠️ No stored prompt found, using hardcoded prompt")
            # Load and enhance image
            image = self._enhance_image_for_ocr(image_path)
            
            # Create enhanced prompt for better data extraction
            prompt = """
You are an expert OCR system specialized in business card data extraction. Analyze this business card image with extreme precision and extract ALL visible text.

⚠️ MULTIPLE CARDS DETECTION - CRITICAL:
• FIRST, check if the image contains MULTIPLE business cards (side-by-side, stacked, or in a grid)
• Look for: Repeated layouts, multiple sets of contact information, duplicate company logos, card boundaries/edges
• If MULTIPLE CARDS detected: Extract data for EACH card separately as individual JSON objects in an array
• If SINGLE CARD: Return one JSON object in an array

🔍 SCANNING PROTOCOL (Execute in this exact order):

STEP 1 - VISUAL SURVEY:
• Scan the ENTIRE image from top-left to bottom-right
• Identify if there are MULTIPLE business cards in the image (look for card boundaries, repeated information)
• If multiple cards: Process each card individually from left-to-right, top-to-bottom
• Examine all four corners and edges carefully of EACH card
• Check logos, watermarks, and background elements
• Look for text in ALL orientations: horizontal, vertical, diagonal, upside-down, curved
• Identify text in different fonts, sizes, and colors (including light/faded text)
• Check for embossed, raised, or textured text

STEP 2 - NUMBER DETECTION (CRITICAL - MOST MISSED FIELD):
• Phone numbers are THE HIGHEST PRIORITY - find every single digit sequence
• Scan EVERYWHERE: top, bottom, left, right margins, corners, near logos, in fine print
• Look for these patterns:
  - Mobile: 10 digits (9876543210)
  - With country code: +91 9876543210, 0091-9876543210
  - Formatted: 98765-43210, 98765 43210, (98765) 43210, 987.654.3210
  - With spaces: 98 76 54 32 10, 9 8 7 6 5 4 3 2 1 0
  - Landline/Telephone: (011) 12345678, 011-12345678, STD code + number
  - Office: Main line + extensions (e.g., 1140583000, 1140583001)
  - Telephone with area codes: (022) 12345678, 080-12345678
  - Multiple numbers: usually listed vertically or with separators
• Extract EVERY sequence of 8-13 consecutive digits or digit groups
• Include numbers near icons: 📞 ☎ 📱 or labels: "M:", "Ph:", "Tel:", "Mob:", "O:", "Cell:", "Telephone:", "Landline:"
• Check QR codes vicinity - numbers often printed nearby

STEP 3 - TEXT FIELD EXTRACTION:

NAME (Person's name):
• Primary location: Center, top, or prominently displayed
• Visual cues: Largest font, bold, different color, centered
• Look for: First name + Last name, full names with middle initials
• Prefixes: Mr., Mrs., Ms., Dr., Er., Prof., CA, Adv.
• Cultural names: Include all parts (e.g., "Nishant Kumar Choradia")
• Fallback: If no person name, use the most prominent company representative name

EMAIL (Critical - often small text):
• Find ALL instances of @ symbol
• Common locations: Bottom of card, footer, near phone numbers
• Patterns: name@domain.com, firstname.lastname@company.co.in
• Multiple emails: personal + office, sales@, info@, contact@
• Domain extensions: .com, .in, .co.in, .net, .org, .co, .io
• Check very small text and fine print

COMPANY (Business/Organization name):
• Primary location: Top or center, often with logo
• Visual cues: Distinctive font, company colors, letterhead style
• Legal entities: Pvt. Ltd., Private Limited, LLP, Ltd., Inc., Corp., LLC
• Name formats: "ABC Industries", "XYZ Pvt. Ltd.", "PQR GROUP"
• Check logo text - company name often integrated into logo design
• Multiple lines: Company name may span 2-3 lines

DESIGNATION (Job title/role):
• Location: Below name, near name, or in separate section
• Titles: Director, Manager, CEO, MD, VP, Executive, Officer, Head
• Roles: Proprietor, Partner, Owner, Founder, Co-Founder
• Departments: Sales, Marketing, HR, Operations, Business Development
• Functional: "Sales Executive", "Marketing Manager", "Business Head"
• Regional: "Regional Manager - North", "Area Sales Manager"

ADDRESS (Physical address):
• Complete address including street, area, city, state, pincode
• Look for: Street names, area names, city names, state names, PIN codes
• Common formats: "123 Main St, Area Name, City, State - 400001"
• May span multiple lines on the card
• Include: Building names, landmarks, postal codes

STEP 4 - ADDITIONAL ELEMENTS TO CHECK:
• Website URLs (www., https://, .com, .in)
• Physical address (street, city, state, pincode)
• Fax numbers (often labeled "F:" or "Fax:")
• WhatsApp numbers (may have WhatsApp icon)
• Social media handles (LinkedIn, Twitter, Instagram icons/handles)
• Secondary contacts or departments
• Taglines or business descriptions (may contain business type info)

📋 OUTPUT FORMAT:

**If SINGLE card detected:**
Return an array with ONE JSON object:
[
  {
    "name": "Full Person Name",
    "phone": "phone1,phone2,phone3",
    "email": "email1@domain.com,email2@company.in",
    "company": "Complete Company Name",
    "designation": "Job Title/Position",
    "address": "Full Address"
  }
]

**If MULTIPLE cards detected (2, 3, 4+ cards):**
Return an array with SEPARATE JSON object for EACH card:
[
  {
    "name": "Person Name Card 1",
    "phone": "phone1,phone2",
    "email": "email1@domain.com",
    "company": "Company Name Card 1",
    "designation": "Job Title Card 1"
  },
  {
    "name": "Person Name Card 2",
    "phone": "phone3,phone4",
    "email": "email2@domain.com",
    "company": "Company Name Card 2",
    "designation": "Job Title Card 2"
  }
]

⚠️ CRITICAL RULES:

1. MULTIPLE CARDS HANDLING:
   • Always check if image contains multiple business cards FIRST
   • Process each card independently - don't mix data between cards
   • Maintain spatial awareness - which data belongs to which card
   • Return separate JSON objects for each distinct card
   • If 2 identical cards: Extract both separately (may have same data)

2. PHONE NUMBERS - ABSOLUTE PRIORITY:
2. PHONE NUMBERS - ABSOLUTE PRIORITY:
   • For EACH card separately, find ALL phone numbers
   • Missing phone numbers is UNACCEPTABLE
   • Scan each card at least 3 times specifically for numbers
   • Check every corner, every line of text on each card
   • Extract ALL number sequences 10+ digits per card
   • Format: Remove all spaces, hyphens, parentheses - just digits
   • Multiple phones per card: comma-separated, no spaces: "9876543210,1234567890"

3. COMPLETENESS:
3. COMPLETENESS:
   • Extract data for EACH card separately - don't skip any card
   • Use "N/A" ONLY if you've scanned the entire card 3 times and absolutely nothing exists
   • Partial information is better than N/A
   • If text is partially visible/cut off, extract what you can see
   • If unsure between two options, include both

4. ACCURACY:
4. ACCURACY:
   • Extract text exactly as written (preserve capitalization for names)
   • Don't add punctuation that isn't there
   • Don't correct spelling - extract as-is
   • No explanations, no markdown formatting, no code blocks
   • Return ONLY a JSON array (even for single card: return array with one object)

5. SPECIAL CASES:
   • Multiple people on one card: Use primary/most prominent name
   • Multiple companies: Use main/largest company name
   • No person name: Use company name in "name" field
   • Bilingual cards: Extract English text; if no English, extract other language

✅ QUALITY CHECKLIST (Verify before returning JSON):
□ Checked if image contains MULTIPLE business cards
□ If multiple cards: Created separate JSON object for each card
□ Scanned entire image including all margins and corners of each card
□ Found and extracted ALL phone numbers for each card (checked 3 times per card)
□ Located email address for each card (checked bottom, footer, fine print)
□ Identified person's name for each card (checked large text, bold text, center)
□ Found company name for each card (checked logo, top, letterhead)
□ Extracted designation/title for each card (checked near name)
□ All digit-only phone numbers with no formatting
□ Multiple values separated by commas with no spaces
□ Valid JSON ARRAY format with no extra text (always return array)

🎯 EXAMPLES OF PERFECT EXTRACTION:

**Example 1 - SINGLE CARD:**
[
  {"name": "NISHANT CHORADIA", "phone": "9377359469,8971972679", "email": "nishant.petrotech@gmail.com", "company": "PETROTECH GROUP", "designation": "Director", "address": "123 Business Park, Sector 15, Gurgaon, Haryana - 122001"}
]

**Example 2 - TWO CARDS in one image:**
[
  {"name": "Divyank Bahuguna", "phone": "1140583000,1140583001,9717844029", "email": "mktg14@globusdelhi.com", "company": "Globus Transitos Pvt. Ltd.", "designation": "Executive - Business Development", "address": "Plot 45, Industrial Area, New Delhi - 110020"},
  {"name": "Manishkumar Shah", "phone": "9712588230,02240123456", "email": "sales@marutindia.com", "company": "MANHATTEN INTERNATIONAL IMPEX", "designation": "Director", "address": "Office 301, Trade Center, Mumbai, Maharashtra - 400001"}
]

**Example 3 - THREE IDENTICAL CARDS:**
[
  {"name": "Amit Kumar", "phone": "9876543210", "email": "amit@company.com", "company": "Tech Solutions", "designation": "Manager", "address": "456 Tech Hub, Bangalore, Karnataka - 560001"},
  {"name": "Amit Kumar", "phone": "9876543210", "email": "amit@company.com", "company": "Tech Solutions", "designation": "Manager", "address": "456 Tech Hub, Bangalore, Karnataka - 560001"},
  {"name": "Amit Kumar", "phone": "9876543210", "email": "amit@company.com", "company": "Tech Solutions", "designation": "Manager", "address": "456 Tech Hub, Bangalore, Karnataka - 560001"}
]

NOW ANALYZE THE IMAGE AND RETURN ONLY THE JSON ARRAY OUTPUT.
"""
            
            # Generate content with image and prompt - use high quality settings
            generation_config = {
                "temperature": 0.05,  # Ultra-low temperature for maximum consistency
                "top_p": 0.75,
                "top_k": 30,
                "max_output_tokens": 2048,
            }
            
            # Add retry logic for rate limiting
            import time
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(
                        [prompt, image],
                        generation_config=generation_config
                    )
                    break
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        if attempt < max_retries - 1:
                            print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue
                    raise e
            
            # Debug: Print raw response
            print(f"\n🔍 RAW GEMINI RESPONSE:")
            print(f"'{response.text}'")
            print(f"Length: {len(response.text)} characters\n")
            
            # Parse JSON response
            try:
                # Clean response text
                response_text = response.text.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                elif response_text.startswith('```'):
                    response_text = response_text[3:]
                
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                response_text = response_text.strip()
                
                # Fix common JSON issues
                response_text = response_text.replace(': N/A,', ': "N/A",').replace(': N/A}', ': "N/A"}')
                
                # Extract JSON if there's extra text
                if '[' in response_text and ']' in response_text:
                    start = response_text.find('[')
                    end = response_text.rfind(']') + 1
                    response_text = response_text[start:end]
                elif '{' in response_text and '}' in response_text:
                    # Handle case where single object returned instead of array
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    response_text = '[' + response_text[start:end] + ']'
                
                # Parse the JSON array
                extracted_cards = json.loads(response_text)
                
                # Ensure it's a list
                if not isinstance(extracted_cards, list):
                    extracted_cards = [extracted_cards]
                
                # For multi-page processing, return single complete records without splitting phone numbers
                all_records = []
                for card_data in extracted_cards:
                    # Create single complete record instead of multiple records
                    complete_record = {
                        "name": card_data.get('name', 'N/A'),
                        "phone": self._clean_phone_numbers(card_data.get('phone', 'N/A')),
                        "email": card_data.get('email', 'N/A'),
                        "company": card_data.get('company', 'N/A'),
                        "designation": card_data.get('designation', 'N/A'),
                        "address": card_data.get('address', 'N/A')
                    }
                    all_records.append(complete_record)
                
                print(f"✅ Gemini extracted {len(extracted_cards)} card(s) with {len(all_records)} complete record(s)")
                return all_records
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Raw response: {response.text}")
                return [self._get_default_data()]
                
        except Exception as e:
            print(f"❌ Gemini extraction error: {e}")
            return [self._get_default_data()]
    

    
    def _clean_phone_numbers(self, phone_str: str) -> str:
        """Clean and combine phone numbers without splitting into separate records"""
        if not phone_str or phone_str == 'N/A':
            return 'N/A'
        
        phones = []
        for phone in phone_str.split(','):
            clean_phone = ''.join(filter(str.isdigit, phone.strip()))
            
            # Remove +91 if phone number is longer than 10 digits and starts with 91
            if len(clean_phone) > 10 and clean_phone.startswith('91'):
                clean_phone = clean_phone[2:]  # Remove the '91' prefix
            
            # Accept 8-digit landlines, 10-digit mobiles and 11-12 digit numbers (with STD codes)
            if 8 <= len(clean_phone) <= 12 and clean_phone not in phones:
                phones.append(clean_phone)
        
        return ','.join(phones) if phones else 'N/A'
    
    def _enhance_image_for_ocr(self, image_path: str) -> Image.Image:
        """Enhance image brightness, contrast, and sharpness for better OCR"""
        try:
            # Load image
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance brightness (increase by 20%)
            brightness_enhancer = ImageEnhance.Brightness(image)
            image = brightness_enhancer.enhance(1.2)
            
            # Enhance contrast (increase by 30%)
            contrast_enhancer = ImageEnhance.Contrast(image)
            image = contrast_enhancer.enhance(1.3)
            
            # Enhance sharpness (increase by 50%)
            sharpness_enhancer = ImageEnhance.Sharpness(image)
            image = sharpness_enhancer.enhance(1.5)
            
            # Apply unsharp mask for better text clarity
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            print("✅ Image enhanced for better OCR")
            return image
            
        except Exception as e:
            print(f"⚠️ Image enhancement failed, using original: {e}")
            return Image.open(image_path)
    
    def _get_default_data(self) -> Dict[str, str]:
        """Return default N/A values for business cards"""
        return {
            "name": "N/A",
            "phone": "N/A", 
            "email": "N/A",
            "company": "N/A",
            "designation": "N/A",
            "address": "N/A"
        }
    

    

    

    

    

    

    
    async def extract_with_memory_prompt(self, image_path: str, prompt_id: str) -> list:
        """Extract data using stored prompt from Gemini memory"""
        try:
            image = Image.open(image_path)
            
            # Get prompt from memory
            stored_prompt = await self.memory.get_prompt(prompt_id)
            if not stored_prompt:
                print(f"❌ Prompt '{prompt_id}' not found in memory, using default")
                return await self.extract_business_card_data(image_path)
            
            print(f"✅ Using stored prompt: {prompt_id}")
            
            generation_config = {
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            response = self.model.generate_content([stored_prompt, image], generation_config=generation_config)
            
            print(f"🔍 MEMORY PROMPT RESPONSE: {response.text[:200]}...")
            
            # Parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            if '[' in response_text and ']' in response_text:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                response_text = response_text[start:end]
            elif '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                response_text = '[' + response_text[start:end] + ']'
            
            extracted_data = json.loads(response_text)
            if not isinstance(extracted_data, list):
                extracted_data = [extracted_data]
            
            return extracted_data
            
        except Exception as e:
            print(f"❌ Memory prompt extraction error: {e}")
            return [self._get_default_data()]