import os

class ReportWriter:
    """A jelentés összeállításáért és mentéséért felelős osztály (SRP)."""
    @staticmethod
    def generate_markdown(selected_folder, files_to_process, results) -> str:
        parent_dir = os.path.dirname(selected_folder)
        
        md_content = "# Teljes Mappa Feldolgozási Jelentés (Turbo - Gemini - SOLID)\n\n"
        md_content += f"- **Átvizsgált főmappa:** `{selected_folder}`  \n"
        md_content += f"- **Feldolgozott fájlok:** {len(results)} db  \n\n"
        
        md_content += "## 1. Fájljegyzék\n"
        for f_path in files_to_process:
            relative_path = os.path.relpath(f_path, parent_dir)
            md_content += f"- `{relative_path}` \n"
        
        md_content += "\n---\n\n## 2. Generált Összefoglalók\n\n"
        md_content += "".join(results)
        return md_content

    @staticmethod
    def save_to_file(file_path, content):
        with open(file_path, 'w', encoding='utf-8') as out_f:
            out_f.write(content)