import os
import pathlib
import re

class ReportWriter:
    """A jelentés összeállításáért és mentéséért felelős osztály (SRP)."""
    @staticmethod
    def generate_markdown(selected_folder, files_to_process, results) -> str:
        parent_dir = os.path.dirname(selected_folder)
        
        md_content = "# Teljes Mappa Feldolgozási Jelentés (Turbo - Gemini - SOLID)\n\n"
        md_content += f"- **Átvizsgált főmappa:** `{selected_folder}`  \n"
        md_content += f"- **Feldolgozott fájlok:** {len(results)} db  \n\n"
        
        md_content += "## 1. Fájljegyzék (A tartalmazó mappa megnyitásához kattints a linkre)\n\n"
        for f_path in files_to_process:
            relative_path = os.path.relpath(f_path, parent_dir)
            file_dir_path = os.path.dirname(os.path.abspath(f_path))
            file_uri = pathlib.Path(file_dir_path).as_uri()
            
            md_content += f"- [`{relative_path}`]({file_uri}) \n"
        
        md_content += "\n\n---\n\n## 2. Generált Összefoglalók\n\n"
        
        # Tisztítjuk és fűzzük össze a modellektől kapott eredményeket
        cleaned_results = []
        for res in results:
            if res:
                # Szoftveres biztonsági háló: Ha egy Markdown címsor (pl. ## vagy ###) előtt 
                # közvetlenül szöveg van (nincs üres sor), akkor beszúrunk egy \n-t.
                fixed_res = re.sub(r'(?<!\n)\n(#+\s+)', r'\n\n\1', res)
                cleaned_results.append(fixed_res)
                
        md_content += "\n\n---\n\n".join(cleaned_results)
        return md_content

    @staticmethod
    def save_to_file(file_path, content):
        with open(file_path, 'w', encoding='utf-8') as out_f:
            out_f.write(content)