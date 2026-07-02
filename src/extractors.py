import os
import fitz
import docx
import pandas as pd
from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    """Absztrakt alaposztály minden szövegkinyerőhöz (OCP / LSP)."""
    @abstractmethod
    def extract(self, file_path, is_cancelled_fn, lock=None):
        """Visszatérési érték: (szöveges_tartalom, mime_type, nyers_bájtok)"""
        pass

class TextExtractor(BaseExtractor):
    def extract(self, file_path, is_cancelled_fn, lock=None):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read(), None, None

class PdfExtractor(BaseExtractor):
    def extract(self, file_path, is_cancelled_fn, lock=None):
        text = ""
        doc = fitz.open(file_path)
        for page in doc:
            if is_cancelled_fn(): break
            text += page.get_text("text") + "\n"
        doc.close()
        return text, None, None

class DocxExtractor(BaseExtractor):
    def extract(self, file_path, is_cancelled_fn, lock=None):
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs]), None, None

class ExcelExtractor(BaseExtractor):
    def extract(self, file_path, is_cancelled_fn, lock=None):
        df = pd.read_excel(file_path)
        return df.to_string(), None, None

class AudioExtractor(BaseExtractor):
    def __init__(self):
        import whisper  
        self.model = whisper.load_model("base")
    def extract(self, file_path, is_cancelled_fn, lock=None):
        if lock:
            with lock:
                if is_cancelled_fn(): return "", None, None
                result = self.model.transcribe(file_path, language="hu")
                return result["text"], None, None
        return "", None, None

class ImageExtractor(BaseExtractor):
    """Multimodális képkezelő: nem lokális OCR-t használ, hanem bájtokat ad át a Gemini-nek."""
    def extract(self, file_path, is_cancelled_fn, lock=None):
        ext = os.path.splitext(file_path)[1].lower()
        mime_maps = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif'}
        mime_type = mime_maps.get(ext, 'image/jpeg')
        
        with open(file_path, 'rb') as f:
            byte_data = f.read()
            
        return "", mime_type, byte_data

class ExtractorRegistry:
    """A különböző fájlformátumok regisztere (DIP)."""
    def __init__(self):
        self._extractors = {}
    
    def register(self, extensions, extractor: BaseExtractor):
        for ext in extensions:
            self._extractors[ext.lower()] = extractor
            
    def get_extractor(self, file_path) -> BaseExtractor:
        ext = os.path.splitext(file_path)[1].lower()
        return self._extractors.get(ext)
        
    def get_supported_extensions(self):
        return list(self._extractors.keys())