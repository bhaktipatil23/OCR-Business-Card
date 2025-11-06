from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    
    MAX_FILE_SIZE_MB: int = 10
    MAX_FILES_PER_BATCH: int = 300
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf"
    TEMP_STORAGE_PATH: str = "./storage"
    OUTPUT_CSV_PATH: str = "./output"
    
    # Gemini AI settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return self.ALLOWED_EXTENSIONS.split(",")

settings = Settings()