# 📁 FolderAnalyzer Pro

A **FolderAnalyzer Pro** egy professzionális, asztali (GUI) alkalmazás, amelyet **Business Analyst (üzleti elemző)** és **Software Architect (szoftverarchitekt)** szerepkörökre optimalizáltunk. Az alkalmazás képes teljes mappaszerkezetek automatikus átvizsgálására, a különböző fájlformátumok intelligens tartalomkinyerésére, valamint a **Google Gemini API** segítségével egy tiszta, sallangmentes, strukturált Markdown (.md) jelentés elkészítésére.

## ✨ Főbb funkciók

- **Multimodális AI elemzés:** Felhőalapú `gemini-2.5-flash` modell használata az azonnali és intelligens válaszokért.
- **Típus-specifikus feldolgozás:** Egyedi üzleti és technikai promptok a különböző fájltípusokhoz a maximális minőség érdekében.
- **Széleskörű formátumtámogatás:**
  - 📄 **Dokumentumok:** `.pdf`, `.docx`, `.txt`, `.md` (szöveges és logikai elemzés)
  - 📊 **Táblázatok:** `.xls`, `.xlsx` (adatstruktúra, entitások és kimutatások)
  - 🖼️ **Képek:** `.png`, `.jpg`, `.jpeg`, `.gif` (UI screenshotok, folyamatábrák, architektúra diagramok natív vizuális elemzése OCR nélkül)
  - 🎵 **Audio:** `.mp3` (Whisper-alapú hang leiratozás és akciópontok kigyűjtése)
- **Modern dizájn:** Dinamikusan átméretezhető, sötét módot támogató, kiber-mátrix stílusú reszponzív CustomTkinter felület.
- **Biztonságos API kezelés:** Az API kulcsot nem tárolja a kód, az a felhasználó saját rendszeréből (környezeti változóból) olvasható be.

---

## 🛠️ Telepítés és előfeltételek

A program futtatásához **Python 3.10+** szükséges.

### 1. A projekt letöltése
Klónozd vagy töltsd le a repozitóriumot a gépedre:
```bash
git clone [https://github.com/dombovarioliver/FolderAnalyzer.git](https://github.com/dombovarioliver/FolderAnalyzer.git)
cd FolderAnalyzer