import os
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')

from ai_services import GeminiAIManager
from report_writer import ReportWriter
from extractors import (
    ExtractorRegistry, TextExtractor, PdfExtractor, 
    DocxExtractor, ExcelExtractor, AudioExtractor, ImageExtractor
)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class UltimateDocSummarizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FolderAnalyzer Pro — Enterprise Architect Edition")
        self.geometry("950x750")
        self.minsize(850, 650)
        
        if os.path.exists("icon.ico"):
            self.iconbitmap("icon.ico")

        self.selected_folder = ""
        self.is_cancelled = False
        self.executor = None
        
        self.ai_manager = GeminiAIManager(model_name="gemini-2.5-flash")
        self.registry = ExtractorRegistry()
        self.setup_extractors()
        self.create_widgets()
        
        threading.Thread(target=self.initialize_system, daemon=True).start()

    def setup_extractors(self):
        self.registry.register(['.txt', '.md'], TextExtractor())
        self.registry.register(['.pdf'], PdfExtractor())
        self.registry.register(['.docx'], DocxExtractor())
        self.registry.register(['.xls', '.xlsx'], ExcelExtractor())
        self.registry.register(['.mp3'], AudioExtractor())
        self.registry.register(['.jpg', '.jpeg', '.png', '.gif'], ImageExtractor())

    def initialize_system(self):
        self.ai_manager.ensure_server_is_running(self.log)
        self.ai_manager.ensure_model_is_ready(self.log)

    def create_widgets(self):
        self.configure(fg_color=["#F4F6F9", "#0B0F19"])
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=30, pady=25)

        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, text="📁 FolderAnalyzer Pro", 
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=["#1E293B", "#6366F1"]
        )
        self.title_label.pack(side="left")
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame, text="Business Analyst & Software Architect AI Assistant", 
            font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic"),
            text_color=["#64748B", "#94A3B8"]
        )
        self.subtitle_label.pack(side="right", pady=(10, 0))

        self.folder_card = ctk.CTkFrame(
            self.main_container, corner_radius=16, border_width=1, 
            border_color=["#E2E8F0", "#1E293B"], fg_color=["#FFFFFF", "#111827"]
        )
        self.folder_card.pack(fill="x", pady=(0, 20))
        
        self.btn_select_folder = ctk.CTkButton(
            self.folder_card, text="🔍 Mappa Beolvasása", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), height=42, corner_radius=10,
            fg_color=["#4F46E5", "#4338CA"], hover_color=["#6366F1", "#4F46E5"], command=self.select_folder
        )
        self.btn_select_folder.pack(side="left", padx=15, pady=15)

        self.lbl_folder_path = ctk.CTkLabel(
            self.folder_card, text="Válassz ki egy forrásmappát az elemzés indításához...", 
            font=ctk.CTkFont(family="Consolas", size=12), anchor="w", text_color=["#64748B", "#6B7280"]
        )
        self.lbl_folder_path.pack(side="left", fill="x", expand=True, padx=(10, 15))

        self.action_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.action_frame.pack(fill="x", pady=(0, 20))

        self.btn_start = ctk.CTkButton(
            self.action_frame, text="🚀 Elemzés Indítása", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), height=44, width=190, corner_radius=10,
            state="disabled", fg_color=["#10B981", "#059669"], hover_color=["#34D399", "#10B981"], text_color="#FFFFFF"
        )
        self.btn_start.configure(command=self.start_processing_thread)
        self.btn_start.pack(side="left", padx=(0, 12))

        self.btn_cancel = ctk.CTkButton(
            self.action_frame, text="🛑 Mégsem", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), height=44, width=120, corner_radius=10,
            state="disabled", fg_color=["#EF4444", "#DC2626"], hover_color=["#F87171", "#EF4444"], text_color="#FFFFFF"
        )
        self.btn_cancel.configure(command=self.cancel_processing)
        self.btn_cancel.pack(side="left")

        self.progress_label = ctk.CTkLabel(
            self.action_frame, text="● Rendszer készenlétben", 
            font=ctk.CTkFont(family="Segoe UI", weight="bold", size=13), text_color=["#4F46E5", "#818CF8"]
        )
        self.progress_label.pack(side="right", padx=10)

        self.log_frame = ctk.CTkFrame(
            self.main_container, corner_radius=16, border_width=1,
            border_color=["#E2E8F0", "#1E293B"], fg_color=["#FFFFFF", "#111827"]
        )
        self.log_frame.pack(fill="both", expand=True, pady=(0, 15))

        self.log_title = ctk.CTkLabel(
            self.log_frame, text="💻 Rendszernapló & Folyamatfigyelő", 
            font=ctk.CTkFont(family="Segoe UI", weight="bold", size=12), text_color=["#94A3B8", "#4B5563"]
        )
        self.log_title.pack(anchor="w", padx=15, pady=(12, 6))

        self.log_textbox = ctk.CTkTextbox(
            self.log_frame, font=ctk.CTkFont(family="Consolas", size=12), border_width=0,
            fg_color=["#F8FAFC", "#030712"], text_color=["#0F172A", "#10B981"]
        )
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.log_textbox.configure(state="disabled")

        self.footer_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.footer_frame.pack(fill="x")

        self.info_label = ctk.CTkLabel(
            self.footer_frame, text=f"Támogatott modulok: {', '.join(self.registry.get_supported_extensions())}", 
            font=ctk.CTkFont(family="Segoe UI", size=11), text_color=["#64748B", "#4B5563"]
        )
        self.info_label.pack(side="left")

        self.credits_label = ctk.CTkLabel(
            self.footer_frame, text="© 2026 | Dombovári Olivér | Minden jog fenntartva | Verzió 1.2.0", 
            font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"), text_color=["#64748B", "#4B5563"]
        )
        self.credits_label.pack(side="right")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.lbl_folder_path.configure(text=folder, text_color=["#000000", "#FFFFFF"])
            self.btn_start.configure(state="normal")
            self.log(f"📁 Kiválasztott forrásmappa: {folder}")

    def log(self, text):
        if hasattr(self, 'log_textbox') and self.log_textbox.winfo_exists():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", text + "\n")
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")

    def clear_log(self):
        if hasattr(self, 'log_textbox') and self.log_textbox.winfo_exists():
            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.configure(state="disabled")
            self.log("💡 Előző munkafolyamat sikeresen lezárva. Új elemzés indítható.")

    def show_modern_alert(self, title, message, color):
        alert = ctk.CTkToplevel(self)
        alert.title(title)
        alert.geometry("420x220")
        alert.resizable(False, False)
        alert.transient(self)
        alert.grab_set()
        
        alert.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (alert.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (alert.winfo_height() // 2)
        alert.geometry(f"+{x}+{y}")

        card = ctk.CTkFrame(alert, corner_radius=16, fg_color=["#FFFFFF", "#111827"], border_width=1, border_color=["#E2E8F0", "#1E293B"])
        card.pack(fill="both", expand=True, padx=15, pady=15)

        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color=color)
        lbl_title.pack(pady=(15, 5))

        lbl_msg = ctk.CTkLabel(card, text=message, font=ctk.CTkFont(family="Segoe UI", size=13), text_color=["#1E293B", "#E2E8F0"])
        lbl_msg.pack(pady=10, padx=20)

        btn_ok = ctk.CTkButton(card, text="Értem", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), fg_color=color, hover_color=color, height=35, width=100, corner_radius=8, command=alert.destroy)
        btn_ok.pack(pady=(10, 15))
        self.wait_window(alert)

    def start_processing_thread(self):
        self.is_cancelled = False
        self.btn_start.configure(state="disabled")
        self.btn_select_folder.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.progress_label.configure(text="⏳ Feldolgozás elindult...", text_color="#F5A623")
        threading.Thread(target=self.main_process, daemon=True).start()

    def cancel_processing(self):
        self.is_cancelled = True
        self.log("⚠️ Megszakítás folyamatban... Feladatok leállítása.")
        self.btn_cancel.configure(state="disabled")
        if self.executor:
            self.executor.shutdown(wait=False, cancel_futures=True)
        self.reset_gui_after_cancel()

    def process_single_file(self, file_path, index, total):
        if self.is_cancelled: return None
        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        
        extractor = self.registry.get_extractor(file_path)
        if not extractor: return None
        
        self.log(f"🚀 [{index}/{total}] '{file_name}' előkészítése...")
        extracted_text, mime_type, byte_data = extractor.extract(file_path, lambda: self.is_cancelled, self.ai_manager.lock)
        
        if self.is_cancelled: return None
        if not extracted_text and not byte_data: return None
        
        self.log(f"🧠 [{index}/{total}] '{file_name}' elemzése a felhős Gemini AI-val...")
        
        parent_dir = os.path.dirname(self.selected_folder)
        relative_path = os.path.relpath(file_path, parent_dir)

        # Itt szándékosan nem kapjuk el a hibát! Hagyjuk, hogy a szál visszaadja a kivételt a fő szálnak.
        return self.ai_manager.analyze_file(
            file_name=file_name,
            relative_path=relative_path,
            ext=ext,
            extracted_text=extracted_text,
            byte_data=byte_data
        )

    def main_process(self):
        supported_exts = self.registry.get_supported_extensions()
        files_to_process = []

        for root, _, files in os.walk(self.selected_folder):
            if self.is_cancelled: break
            for file in files:
                if os.path.splitext(file)[1].lower() in supported_exts:
                    files_to_process.append(os.path.join(root, file))

        if self.is_cancelled: return
        if not files_to_process:
            messagebox.showinfo("Információ", "Nem találtam támogatott fáljt.")
            self.reset_gui_after_cancel()
            return

        output_file_path = filedialog.asksaveasfilename(
            defaultextension=".md", filetypes=[("Markdown fájl", "*.md")], title="Hova mentsem a jelentést?"
        )
        if not output_file_path:
            self.reset_gui_after_cancel()
            return

        total_files = len(files_to_process)
        self.log(f"🤖 Párhuzamos feldolgozás indítása (max 3 szál)...")

        results = []
        critical_error = None

        with ThreadPoolExecutor(max_workers=3) as executor:
            self.executor = executor
            # Elindítjuk a szálakat
            future_to_file = {
                executor.submit(self.process_single_file, file_path, i, total_files): file_path 
                for i, file_path in enumerate(files_to_process, 1)
            }
            
            # Az as_completed()-nek köszönhetően azonnal reagálunk, amint egy szál végez (vagy hibára fut)
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                file_name = os.path.basename(file_path)
                
                try:
                    res = future.result()
                    if res: 
                        results.append(res)
                except Exception as e:
                    # Itt kapjuk el a szálból visszadobott API hibát, immár biztonságosan a főszál kontextusában!
                    critical_error = f"❌ KRITIKUS API HIBA a(z) '{file_name}' feldolgozásakor: {str(e)}"
                    self.log(critical_error)
                    self.log("🛑 Elemzés megszakítva.")
                    self.cancel_processing()
                    break

        # Ha hiba történt, feldobjuk az ablakot, leállunk és NEM mentünk üres riportot
        if critical_error:
            self.show_modern_alert("Kritikus API Hiba", f"A Gemini leállt.\n\nA feldolgozás megszakadt.", "#EF4444")
            self.reset_gui_after_cancel()
            return

        if self.is_cancelled: return

        md_content = ReportWriter.generate_markdown(self.selected_folder, files_to_process, results)
        
        try:
            ReportWriter.save_to_file(output_file_path, md_content)
            self.progress_label.configure(text="✨ Kész!", text_color="#2EA44F")
            self.show_modern_alert(title="Siker!", message="Az elemzés sikeresen elkészült!\nA jelentés elmentve a kiválasztott helyre.", color="#10B981")
            self.clear_log()
        except Exception as e:
            self.show_modern_alert(title="Hiba történt", message=f"Nem sikerült a mentés:\n{str(e)}", color="#EF4444")

        self.btn_start.configure(state="disabled")
        self.btn_select_folder.configure(state="normal")
        self.btn_cancel.configure(state="disabled")
        self.progress_label.configure(text="● Rendszer készenlétben", text_color=["#4F46E5", "#818CF8"])
        self.lbl_folder_path.configure(text="Válassz ki egy forrásmappát az elemzés indításához...", text_color=["#64748B", "#6B7280"])
        self.folder_card.configure(fg_color=["#FFFFFF", "#111827"])
        self.update()

    def reset_gui_after_cancel(self):
        self.clear_log()
        self.progress_label.configure(text="❌ Megszakítva.", text_color="#D73A49")
        self.btn_start.configure(state="normal")
        self.btn_select_folder.configure(state="normal")
        self.btn_cancel.configure(state="disabled")

if __name__ == "__main__":
    app = UltimateDocSummarizerApp()
    app.mainloop()