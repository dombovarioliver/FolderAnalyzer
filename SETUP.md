# 🛠️ Telepítési és Konfigurációs Útmutató (SETUP)

Ez a dokumentum lépésről lépésre bemutatja, hogyan konfigurálhatod és indíthatod el a **FolderAnalyzer Pro** alkalmazást fejlesztői (Python) vagy felhasználói (.exe) környezetben.

---

## 📋 Előfeltételek ellenőrzése

A szoftver futtatásához a következő komponensek megléte szükséges a gazdagépen:
1. **Python 3.10, 3.11 vagy újabb** (Letölthető: [python.org](https://www.python.org/))
   - *FONTOS:* Telepítéskor pipáld be az **"Add python.exe to PATH"** opciót!
2. **Google AI Studio hozzáférés** (A felhős Gemini API eléréséhez)
3. **Internetkapcsolat** (Az API hívásokhoz és a Whisper modell első letöltéséhez)

---

## 🔑 1. Lépés: Gemini API Kulcs Beszerzése és Beállítása

A FolderAnalyzer Pro nem tárol beégetett API kulcsokat a kód biztonsága érdekében. A program a Windows rendszer környezeti változói közül olvassa ki a kulcsot.

### API Kulcs igénylése:
1. Navigálj a [Google AI Studio](https://aistudio.google.com/) oldalra.
2. Jelentkezz be a Google fiókoddal.
3. Kattints a **"Get API key"** gombra, majd hozz létre egy új kulcsot (*Create API key*).
4. Másold ki a kapott hosszú karaktersorozatot a vágólapra.

### Környezeti Változó Beállítása Windows 10/11-en:
1. Nyomd meg a **Windows gombot** a billentyűzeteden, és gépeld be: `környezeti változó`.
2. Válaszd a **"Rendszer környezeti változóinak szerkesztése"** lehetőséget.
3. A felugró kis ablak alján kattints a **"Környezeti változók..."** gombra.
4. A felső táblázatban (**[Felhasználónév] felhasználói változói**) kattints az **"Új..."** gombra.
5. Add meg a következő értékeket (pontosan, szóközök nélkül):
   - **Változó neve:** `GEMINI_API_KEY`
   - **Változó értéke:** *[Ide másold be az igénylés során kapott kulcsot]*
6. Kattints az **OK** gombra az összes ablak bezárásához.

> 🚨 **RENDKÍVÜL FONTOS:** Ha a kulcs mentésekor nyitva volt a VS Code, a PyCharm vagy bármilyen terminál ablak, **zárd be és nyisd meg újra őket**! A futtató környezetek csak az újraindítás után képesek beolvasni a Windows új memóriáját.

---

## 📦 2. Lépés: Függőségek Telepítése

Nyiss egy terminált (PowerShell vagy CMD) a projekt `src` mappájában, majd futtasd a következő parancsot az összes szükséges AI és GUI könyvtár egyidejű telepítéséhez:

```bash
python -m pip install customtkinter google-genai requests pandas openpyxl python-docx pymupdf pillow numpy openai-whisper