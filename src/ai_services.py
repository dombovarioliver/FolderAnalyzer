import os
import threading
from google import genai
from google.genai import types 

class GeminiAIManager:
    """A Google Gemini API hívásokért, a szigorított promptok összeállításáért és szálkezelésért felelős szolgáltatás (SRP)."""
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = model_name
        self.lock = threading.Lock()
        self.client = None

    def ensure_server_is_running(self, log_callback):
        """Környezet ellenőrzése. A felhős API-hoz szükséges kulcs meglétét ellenőrizzük."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            log_callback("❌ HIBA: A GEMINI_API_KEY környezeti változó nem található!")
            log_callback("Kérlek állítsd be a rendszer környezeti változói között.")
            return
        
        try:
            self.client = genai.Client(api_key=api_key)
            log_callback("✅ Gemini API kliens sikeresen inicializálva.")
        except Exception as e:
            log_callback(f"❌ Kliens hiba: {str(e)}")

    def ensure_model_is_ready(self, log_callback):
        """Felhős modellnél ellenőrizzük az összeköttetést."""
        if self.client:
            log_callback(f"✅ {self.model_name} felhős modell kapcsolat kész!")

    def analyze_file(self, file_name: str, relative_path: str, ext: str, extracted_text: str = "", byte_data: bytes = None) -> str:
        """
        Összeállítja a specifikus promptot a kiterjesztés alapján, és végrehajtja a hívást.
        A címszavakat megtartja, de tömörített, átlátható reprezentációt követel meg.
        """
        if not self.client:
            return "Hiba: A Gemini kliens nincs inicializálva!"

        # Védelem túl hosszú nyers szövegek ellen (pl. óriási Excel stringek levágása a hiba elkerülésére)
        if len(extracted_text) > 40000:
            extracted_text = extracted_text[:40000] + "\n...[A forrásszöveg a mérete miatt le lett vágva a hiba elkerülése érdekében]..."

        # 1. KÉP ÁG
        if byte_data and ext in ['.jpg', '.jpeg', '.png', '.gif']:
            prompt = (
                "Te egy Senior Software Architect és Technical Writer vagy.\n"
                "Készíts strukturált, de tömör szakmai elemzést a képről.\n\n"
                "KÖTELEZŐ KIMENETI FORMÁTUM (Minden mező új sorba kerüljön, dupla sorközzel elválasztva!):\n"
                f"### {file_name}\n\n"
                f"**Mappa útvonal:** `{relative_path}`\n\n"
                "**Kontextus:** [Kép típusa, pl. UI képernyőkép, architektúra diagram]\n\n"
                "**Fő gondolat:** [Elsődleges cél 1 mondatban]\n\n"
                "**Tartalmi összefoglaló és Kulcspontok:**\n"
                "- [Fő egységek, modulok és kapcsolatok listája, címszavas, tömör formában]\n\n"
                "**Formai és Tartalmi Minőség, Hiányosságok:**\n"
                "- [Formai minőség és iparági szinten elvárható, de hiányzó elemek indoklással, sablonok nélkül]\n"
            )
            
        # 2. EXCEL ÁG
        elif ext in ['.xls', '.xlsx']:
            prompt = (
                "Te egy Senior Business Analyst és Adatmodellező vagy.\n"
                "Készíts egy átlátható, címszavas, de tömör struktúra-összefoglalót az Excel táblázatról. Ne listázd ki egyesével a végtelen oszlopokat, csoportosítsd őket logikailag!\n\n"
                "KÖTELEZŐ KIMENETI FORMÁTUM (Minden mező új sorba kerüljön, dupla sorközzel elválasztva!):\n"
                f"### {file_name}\n\n"
                f"**Mappa útvonal:** `{relative_path}`\n\n"
                "**Kontextus:** [Adatstruktúra típusa, pl. DTO mapping, Riport]\n\n"
                "**Fő gondolat:** [Az adathalmaz funkcionális célja 1 mondatban]\n\n"
                "**Tartalmi összefoglaló és Kulcspontok:**\n"
                "[Mutasd be a főbb munkalapokat, entitásokat vagy adatcsoportokat. Használj vastagított címszavakat, és csak a legfontosabb attribútumokat/kulcsokat emeld ki tömören!]\n\n"
                "**Formai és Tartalmi Minőség, Hiányosságok:**\n"
                "- [Az adatstruktúra átláthatósága és az iparági szinten elvárható hiányzó elemek rövid indoklással]\n\n"
                f"<source_text>\n{extracted_text}\n</source_text>"
            )
            
        # 3. AUDIÓ ÁG
        elif ext == '.mp3':
            prompt = (
                "Te egy Senior Business Analyst vagy.\n"
                "Készíts tömör, címszavas összefoglalót a hanganyag leiratáról.\n\n"
                "KÖTELEZŐ KIMENETI FORMÁTUM (Minden mező új sorba kerüljön, dupla sorközzel elválasztva!):\n"
                f"### {file_name}\n\n"
                f"**Mappa útvonal:** `{relative_path}`\n\n"
                "**Kontextus:** [A megbeszélés típusa]\n\n"
                "**Fő gondolat:** [Fókusz és konklúzió 1 mondatban]\n\n"
                "**Tartalmi összefoglaló és Akciópontok:**\n"
                "[A megbeszélés fő témakörei címszavakban, a hozzájuk tartozó legfontosabb döntésekkel és felelősökkel.]\n\n"
                "**Formai és Tartalmi Minőség, Hiányosságok:**\n"
                "- [A megbeszélés strukturáltsága és a jegyzőkönyvből hiányzó formális elemek]\n\n"
                f"<source_text>\n{extracted_text}\n</source_text>"
            )
            
        # 4. ÁLTALÁNOS DOKUMENTUM ÁG
        else:
            prompt = (
                "Te egy Senior Technical Writer és Rendszerelemző vagy.\n"
                "Készíts egy jól tagolt, címszavas, de felesleges részletezésektől mentes, tömör összefoglalót a dokumentumról.\n\n"
                "KÖTELEZŐ KIMENETI FORMÁTUM (Minden mező új sorba kerüljön, dupla sorközzel elválasztva!):\n"
                f"### {file_name}\n\n"
                f"**Mappa útvonal:** `{relative_path}`\n\n"
                "**Kontextus:** [Dokumentum típusa, pl. Release Notes, Funkcionális specifikáció]\n\n"
                "**Contect_text:** [A tartalom lényegega 1 mondatban]\n\n"
                "**Tartalmi összefoglaló és Kulcspontok:**\n"
                "[Kövesd a forrás belső tagolását (pl. verziók vagy fejezetek szerint). Használj egyértelmű címszavakat, és alatta tömör, listás összefoglalást a legfontosabb tényekről, funkciókról, elkerülve a feleslegesen hosszú mondatokat.]\n\n"
                "**Formai és Tartalmi Minőség, Hiányosságok:**\n"
                "- [A dokumentum felépítésének minősége és az adott dokumentumtípusnál elvárható hiányzó szakmai elemek rövid indoklással]\n\n"
                f"<source_text>\n{extracted_text}\n</source_text>"
            )

        # 5. GLOBÁLISAN KÉNYSZERÍTŐ UTASÍTÁSOK
        prompt += (
            "\n"
            "SZIGORÚ UTASÍTÁSOK A FELDOLGOZÁSHOZ:\n\n"
            "SZEREP ÉS FORMAT:\n"
            "- Maradj szigorúan objektív, tényközlő, de tömör. Kerüld a terjengős magyarázatokat.\n"
            "- A cél egy jól áttekinthető, CÍMSZAVAS reprezentáció, nem pedig a forrásanyag mondatról mondatra való bemásolása.\n\n"
            "TARTALMI KORLÁTOZÁS:\n"
            "- Ha a forrásanyag (pl. egy Excel vagy specifikáció) túl sok hasonló elemet vagy oszlopot tartalmaz, csoportosítsd őket logikai kategóriákba vagy címszavak alá ahelyett, hogy végtelen listát gyártanál.\n"
            "- Ne hagyj ki strukturális egységet (verziót vagy munkalapot), de azok tartalmát lényegre törően, kulcsszavakban foglald össze!\n\n"
            "FORMÁZÁS ÉS MEGJELENÉS:\n"
            "- A választ közvetlenül a megadott sablon szerinti ### jellel kezdd, bevezető vagy záró szöveg nélkül.\n"
            "- A Markdown összecsúszások elkerülése érdekében MINDEN címsor (legyen az ### Fájlnév vagy belső verziószám, fejezetszám) ELŐTT ÉS UTÁN KÖTELEZŐEN hagyj egy teljesen üres sort!\n"
            "- SOHA ne folyasd össze a szekciókat: Minden egyes fő sablon-szekció után tegyél egy üres sort (dupla sorköz).\n"
        )

        with self.lock:
            try:
                # Az új felhős API megköveteli a tiszta models/ előtagot a stabilitásért
                full_model_name = self.model_name
                if not full_model_name.startswith("models/"):
                    full_model_name = f"models/{full_model_name}"

                # Bemenet összeállítása
                if byte_data and ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    mime_maps = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif'}
                    mime_type = mime_maps.get(ext, 'image/jpeg')
                    
                    # Most már a types.Part hibátlanul le fog futni az importálás miatt!
                    img_part = types.Part.from_bytes(
                        data=byte_data,
                        mime_type=mime_type
                    )
                    contents = [img_part, prompt]
                else:
                    # Ha nincs kép, sima stringként adjuk át, így garantáltan nem dob 400-as hibát
                    contents = prompt
                
                # API hívás végrehajtása
                response = self.client.models.generate_content(
                    model=full_model_name,
                    contents=contents
                )
                return response.text if response.text else "Nem érkezett válasz."
                
            except Exception as e:
                raise e