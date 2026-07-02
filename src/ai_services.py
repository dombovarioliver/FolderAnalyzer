import os
import threading
from google import genai
from google.genai import types

class GeminiAIManager:
    """A Google Gemini API hívásokért és szálkezelésért felelős szolgáltatás (SRP)."""
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = model_name
        self.lock = threading.Lock()
        self.client = None

    def ensure_server_is_running(self, log_callback):
        """Környezet ellenőrzése. Mivel ez felhős API, a kulcs meglétét ellenőrizzük."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            log_callback("❌ HIBA: A GEMINI_API_KEY környezeti változó nem található!")
            log_callback("Kérlek állítsd be a Windowsban a rendszer környezeti változói között.")
            return
        
        try:
            self.client = genai.Client(api_key=api_key)
            log_callback("✅ Gemini API kliens sikeresen inicializálva.")
        except Exception as e:
            log_callback(f"❌ Kliens hiba: {str(e)}")

    def ensure_model_is_ready(self, log_callback):
        """Felhős modellnél nincs letöltés, a szerver azonnal kész."""
        if self.client:
            log_callback(f"✅ {self.model_name} felhős modell kapcsolat kész!")

    def query_model(self, prompt, mime_type=None, byte_data=None):
        """Univerzális hívás szöveghez vagy csatolt bináris fájlokhoz (szálbiztos)."""
        if not self.client:
            return "Hiba: A Gemini kliens nincs inicializálva!"

        with self.lock:
            try:
                contents = []
                
                if byte_data and mime_type:
                    part = types.Part.from_bytes(
                        data=byte_data,
                        mime_type=mime_type,
                    )
                    contents.append(part)
                
                contents.append(prompt)

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents
                )
                return response.text if response.text else "Nem érkezett válasz."
            except Exception as e:
                return f"Gemini API hiba: {str(e)}"