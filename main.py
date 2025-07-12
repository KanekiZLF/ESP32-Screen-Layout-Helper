# Ferramenta gráfica para auxiliar na criação de layouts de tela para microcontroladores (ESP32) com displays TFT.
# Desenvolvido por Luiz F. R. Pimentel

import tkinter
from tkinter import messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import struct
import json
import webbrowser

# --- Funções de Configuração ---

def load_config():
    """Carrega a configuração de um arquivo JSON. Se não existir, cria com o padrão."""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Retorna uma configuração padrão se o arquivo não for encontrado ou estiver corrompido.
        return {"language": "en"}

def save_config(config):
    """Salva a configuração atual em um arquivo JSON."""
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

# --- Dicionário de Traduções ---
# Armazena todas as strings da UI para facilitar a internacionalização (inglês e português).
TRANSLATIONS = {
    "en": {
        "window_title": "TFT Screen Layout Helper", "general_settings": "General Settings",
        "screen_width": "Width:", "screen_height": "Height:", "update_screen_size": "Update Screen Size",
        "output_memory_type": "Output Memory Type:", "internal_memory": "Internal Memory",
        "microsd": "Micro SD", "use_transparency": "Use transparency (Color Key)",
        "generate_button": "Generate Code / Files", "import_image_button": "Import Image",
        "elements_on_screen": "Elements on Screen", "element_w": "W:", "element_h": "H:",
        "apply_resize": "Apply", "delete_selected": "Delete Selected", "language_button": "Language: English",
        "about_button": "About", "about_window_title": "About",
        "about_content": "This tool was created to assist in the development of\nvisual interfaces for ESP32 with TFT displays.",
        "created_by": "Created by: Luiz F. R. Pimentel", "copy_button_text": "Copy to Clipboard",
        "copied_text": "Copied!", "code_generated_title": "Generated Code",
        "title_error": "Error", "title_warning": "Warning", "title_info": "Information", "title_success": "Success",
        "error_image_process": "Could not process image:\n{path}\n\nError: {e}",
        "error_value_must_be_int": "Width and height must be integer numbers.",
        "warning_no_element_selected": "No element selected in the list.",
        "error_dims_must_be_int": "The new dimensions (W and H) must be integer numbers.",
        "info_no_elements_to_generate": "No elements on screen to generate code.",
        "error_generation_aborted": "File generation was aborted due to an image error.",
        "error_file_save": "Could not save the file:\n{filepath}\n\nError: {e}",
        "info_sd_files_success": "Files for SD card successfully generated in the folder:\n{folder}",
        "error_file_open": "Could not open the image file.\n\nError: {e}",
        "save_layout_button": "Save Layout", "load_layout_button": "Load Layout",
        "info_no_layout_to_save": "There is nothing on the canvas to save.",
        "info_layout_saved_success": "Layout successfully saved in:\n{filepath}",
        "error_invalid_layout_file": "The selected file is not a valid layout file or is corrupted.",
        "info_layout_loaded_success": "Layout successfully loaded.",
        "clear_all_button": "Clear All",
        "confirm_clear_title": "Confirm Clear",
        "confirm_clear_message": "Are you sure you want to clear all elements?\nThis action cannot be undone.",
        "about_tab_title": "About",
        "donation_tab_title": "Donation",
        "links_tab_title": "Links",
        "version_text": "Version 1.1 (July 2025)",
        "donation_message_1": "If you found this tool useful, please consider making a donation to support its development.",
        "donation_message_2": "Scan the QR Code below to donate via PIX:",
        "qr_code_not_found": "QR Code image (pix_qrcode.png)\nnot found in the project folder.",
        "find_me_on_github": "Find me on GitHub (click to open):",
        "how_to_use_section_title": "How to Use",
        "how_to_use_link_text": "Click here to watch the tutorial video on YouTube"
    },
    "pt": {
        "window_title": "TFT Screen Layout Helper", "general_settings": "Configurações Gerais",
        "screen_width": "Largura:", "screen_height": "Altura:", "update_screen_size": "Atualizar Tamanho da Tela",
        "output_memory_type": "Tipo de Memória de Saída:", "internal_memory": "Memória Interna",
        "microsd": "Micro SD", "use_transparency": "Usar transparência (Color Key)",
        "generate_button": "Gerar Código / Arquivos", "import_image_button": "Importar Imagem",
        "elements_on_screen": "Elementos na Tela", "element_w": "L:", "element_h": "A:",
        "apply_resize": "Aplicar", "delete_selected": "Excluir Selecionado", "language_button": "Idioma: Português",
        "about_button": "Sobre", "about_window_title": "Sobre",
        "about_content": "Esta ferramenta foi criada para auxiliar no desenvolvimento\nde interfaces visuais para ESP32 com displays TFT.",
        "created_by": "Criado por: Luiz F. R. Pimentel", "copy_button_text": "Copiar para a Área de Transferência",
        "copied_text": "Copiado!", "code_generated_title": "Código Gerado",
        "title_error": "Erro", "title_warning": "Aviso", "title_info": "Informação", "title_success": "Sucesso",
        "error_image_process": "Não foi possível processar a imagem:\n{path}\n\nErro: {e}",
        "error_value_must_be_int": "Largura e altura devem ser números inteiros.",
        "warning_no_element_selected": "Nenhum elemento selecionado na lista.",
        "error_dims_must_be_int": "As novas dimensões (L e A) devem ser números inteiros.",
        "info_no_elements_to_generate": "Nenhum elemento na tela para gerar o código.",
        "error_generation_aborted": "A geração de arquivos foi interrompida devido a um erro na imagem.",
        "error_file_save": "Não foi possível salvar o arquivo:\n{filepath}\n\nErro: {e}",
        "info_sd_files_success": "Arquivos para SD gerados com sucesso na pasta:\n{folder}",
        "error_file_open": "Não foi possível abrir o arquivo de imagem.\n\nErro: {e}",
        "save_layout_button": "Salvar Layout", "load_layout_button": "Carregar Layout",
        "info_no_layout_to_save": "Não há nada no canvas para salvar.",
        "info_layout_saved_success": "Layout salvo com sucesso em:\n{filepath}",
        "error_invalid_layout_file": "O arquivo selecionado não é um arquivo de layout válido ou está corrompido.",
        "info_layout_loaded_success": "Layout carregado com sucesso.",
        "clear_all_button": "Limpar Tudo",
        "confirm_clear_title": "Confirmar Limpeza",
        "confirm_clear_message": "Tem certeza que deseja limpar todos os elementos?\nEsta ação não pode ser desfeita.",
        "about_tab_title": "Sobre",
        "donation_tab_title": "Doação",
        "links_tab_title": "Links",
        "version_text": "Versão 1.1 (Julho 2025)",
        "donation_message_1": "Se esta ferramenta foi útil para você, considere fazer uma doação para apoiar o desenvolvimento.",
        "donation_message_2": "Aponte a câmera do seu celular para\n o QR Code abaixo para doar via PIX:",
        "qr_code_not_found": "Imagem do QR Code (pix_qrcode.png)\nnão encontrada na pasta do projeto.",
        "find_me_on_github": "Me encontre no GitHub (clique para abrir):",
        "how_to_use_section_title": "Como Usar",
        "how_to_use_link_text": "Clique aqui para assistir ao vídeo tutorial no YouTube"
    }
}

# --- Classe Principal da Aplicação ---
class App(ctk.CTk):
    def resize_image(self, image_path, new_width, new_height):
        """Redimensiona uma imagem a partir de seu caminho para as novas dimensões."""
        try:
            w, h = int(new_width), int(new_height)
            if w <= 0 or h <= 0: raise ValueError("Dimensões devem ser positivas")
            img = Image.open(image_path).convert("RGBA")
            # Usa LANCZOS para um redimensionamento de alta qualidade.
            return img.resize((w, h), Image.Resampling.LANCZOS)
        except Exception as e:
            messagebox.showerror(self.get_string("title_error"), self.get_string("error_image_process").format(path=image_path, e=e))
            return None

    def convert_image_data(self, pil_image, use_transparency):
        """Converte os dados de uma imagem PIL para o formato de cor RGB565 (16 bits)."""
        # Cor chave para transparência (Magenta), usada pela biblioteca TFT_eSPI.
        TRANSPARENCY_KEY_COLOR = 0xF81F
        
        if use_transparency:
            img_rgba = pil_image.convert("RGBA")
            pixels_out = []
            # Itera sobre cada pixel; se o canal alfa for baixo, usa a cor de transparência.
            for r, g, b, a in img_rgba.getdata():
                if a < 128: 
                    pixels_out.append(TRANSPARENCY_KEY_COLOR)
                else:
                    # Converte RGB 888 (8 bits por canal) para RGB 565 (5 bits para R, 6 para G, 5 para B).
                    pixels_out.append(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3))
            return pixels_out
        else:
            img_rgb = pil_image.convert("RGB")
            # Converte todos os pixels para RGB565 sem verificar a transparência.
            return [((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3) for r, g, b in img_rgb.getdata()]
            
    def __init__(self):
        super().__init__()
        
        # Carrega a configuração de idioma.
        self.config = load_config()
        self.current_language = self.config.get("language", "en")
        
        self.title(self.get_string("window_title"))
        
        # Define as dimensões e centraliza a janela na tela.
        window_width = 630
        window_height = 660
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        self.resizable(True, True)
        self.minsize(630, 660)
        
        # Configura a aparência da interface.
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Dicionários para gerenciar os elementos na tela.
        self.elements = {}  # Guarda dados (path, x, y, w, h) dos elementos.
        self.element_counter = 0  # Contador para gerar nomes únicos para cada imagem.
        self.tk_images = {}  # Mantém as referências das imagens para o Tkinter não as descartar.
        
        # Configura o layout de grid da janela principal.
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Frame da esquerda, que contém o canvas.
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(10,0), pady=10)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas = tkinter.Canvas(self.left_frame, bg="#2B2B2B", highlightthickness=0)
        self.canvas.grid(row=0, column=0)
        
        # Frame da direita, para os painéis de controle.
        self.right_frame = ctk.CTkFrame(self, width=300)
        self.right_frame.grid(row=0, column=1, rowspan=2, sticky="ns", padx=10, pady=10)

        # Associa os eventos de arrastar e soltar (drag and drop) a itens com a tag "draggable".
        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.on_release)
        self._drag_data = {"x": 0, "y": 0, "item": None} # Dicionário para guardar o estado do arraste.

        # --- Widgets do Painel de Controle ---
        self.controls_frame = ctk.CTkFrame(self.right_frame)
        self.controls_frame.pack(pady=10, padx=10, fill="x")

        # Cabeçalho com configurações gerais.
        header_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15), padx=5)
        header_frame.grid_columnconfigure((0, 1), weight=1) 
        self.general_settings_label = ctk.CTkLabel(header_frame, font=ctk.CTkFont(weight="bold"), text=self.get_string("general_settings"))
        self.general_settings_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        self.language_button = ctk.CTkButton(header_frame, command=self.toggle_language, text=self.get_string("language_button"))
        self.language_button.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        self.about_button = ctk.CTkButton(header_frame, command=self.show_about_window, text=self.get_string("about_button"))
        self.about_button.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        # Controles de tamanho do canvas.
        size_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        size_frame.pack(pady=5, padx=10, fill="x")
        self.width_label = ctk.CTkLabel(size_frame, text=self.get_string("screen_width"))
        self.width_label.grid(row=0, column=0, padx=(0,5))
        self.width_entry = ctk.CTkEntry(size_frame, width=60)
        self.width_entry.insert(0, "240")
        self.width_entry.grid(row=0, column=1)
        self.height_label = ctk.CTkLabel(size_frame, text=self.get_string("screen_height"))
        self.height_label.grid(row=0, column=2, padx=(10,5))
        self.height_entry = ctk.CTkEntry(size_frame, width=60)
        self.height_entry.insert(0, "135")
        self.height_entry.grid(row=0, column=3)
        self.update_size_button = ctk.CTkButton(self.controls_frame, text=self.get_string("update_screen_size"), command=self.update_canvas_size)
        self.update_size_button.pack(pady=10, padx=10, fill="x")
        
        # Controles de geração de código.
        self.output_type_label = ctk.CTkLabel(self.controls_frame, text=self.get_string("output_memory_type"))
        self.output_type_label.pack(padx=10, pady=(10,0))
        self.storage_type_var = ctk.StringVar(value=self.get_string("internal_memory"))
        self.storage_type_menu = ctk.CTkOptionMenu(self.controls_frame, variable=self.storage_type_var, values=[self.get_string("internal_memory"), self.get_string("microsd")])
        self.storage_type_menu.pack(padx=10, pady=5)
        self.transparency_var = ctk.BooleanVar()
        self.transparency_checkbox = ctk.CTkCheckBox(self.controls_frame, text=self.get_string("use_transparency"), onvalue=True, offvalue=False, variable=self.transparency_var)
        self.transparency_checkbox.pack(padx=10, pady=10)
        self.generate_button = ctk.CTkButton(self.controls_frame, text=self.get_string("generate_button"), command=self.generate_output, fg_color="green", hover_color="darkgreen")
        self.generate_button.pack(pady=10, padx=10, fill="x")
        
        # Frame para gerenciamento de elementos (imagens).
        self.elements_frame = ctk.CTkFrame(self.right_frame)
        self.elements_frame.pack(pady=10, padx=10, fill="x")
        self.import_button = ctk.CTkButton(self.elements_frame, text=self.get_string("import_image_button"), command=self.import_image)
        self.import_button.pack(pady=10, padx=10, fill="x")
        
        # Lista de elementos na tela.
        self.listbox = tkinter.Listbox(self.elements_frame, background="#333", foreground="white", selectbackground="#1F6AA5", borderwidth=0, exportselection=False, height=5)
        self.listbox.pack(pady=5, padx=5, fill="x")
        self.listbox.bind("<<ListboxSelect>>", self.on_element_select)
        
        # Controles para redimensionar o elemento selecionado.
        resize_controls_frame = ctk.CTkFrame(self.elements_frame)
        resize_controls_frame.pack(pady=5, padx=5, fill="x")
        self.element_w_label = ctk.CTkLabel(resize_controls_frame, text=self.get_string("element_w"))
        self.element_w_label.pack(side="left", padx=(5,0))
        self.element_w_entry = ctk.CTkEntry(resize_controls_frame, width=50)
        self.element_w_entry.pack(side="left", padx=(0,10))
        self.element_h_label = ctk.CTkLabel(resize_controls_frame, text=self.get_string("element_h"))
        self.element_h_label.pack(side="left")
        self.element_h_entry = ctk.CTkEntry(resize_controls_frame, width=50)
        self.element_h_entry.pack(side="left", padx=(0,10))
        self.resize_button = ctk.CTkButton(resize_controls_frame, text=self.get_string("apply_resize"), command=self.resize_selected_element, width=60)
        self.resize_button.pack(side="left", fill="x", expand=True)

        # Frame para agrupar os botões de exclusão.
        delete_buttons_frame = ctk.CTkFrame(self.elements_frame, fg_color="transparent")
        delete_buttons_frame.pack(pady=(10, 5), padx=5, fill="x")
        delete_buttons_frame.grid_columnconfigure((0, 1), weight=1) # Faz os botões dividirem o espaço.

        self.delete_button = ctk.CTkButton(delete_buttons_frame, text=self.get_string("delete_selected"), fg_color="#C0392B", hover_color="#A93226", command=self.delete_selected)
        self.delete_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.clear_all_button = ctk.CTkButton(delete_buttons_frame, text=self.get_string("clear_all_button"), fg_color="#E74C3C", hover_color="#C0392B", command=self.clear_all_elements)
        self.clear_all_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Frame para os botões de salvar e carregar layout.
        self.save_load_frame = ctk.CTkFrame(self.elements_frame)
        self.save_load_frame.pack(pady=5, padx=5, fill="x")
        self.save_load_frame.grid_columnconfigure((0, 1), weight=1)
        self.save_layout_button = ctk.CTkButton(self.save_load_frame, text=self.get_string("save_layout_button"), command=self.save_layout)
        self.save_layout_button.grid(row=0, column=0, padx=(0,5), sticky="ew")
        self.load_layout_button = ctk.CTkButton(self.save_load_frame, text=self.get_string("load_layout_button"), command=self.load_layout)
        self.load_layout_button.grid(row=0, column=1, padx=(5,0), sticky="ew")
        
        # Inicializa o tamanho do canvas e desenha o grid.
        self.update_canvas_size()

    def get_string(self, key):
        """Obtém uma string de texto do dicionário de traduções com base no idioma atual."""
        return TRANSLATIONS[self.current_language].get(key, key)

    def toggle_language(self):
        """Alterna o idioma entre inglês e português e atualiza a UI."""
        self.current_language = "pt" if self.current_language == "en" else "en"
        self.config["language"] = self.current_language
        save_config(self.config)
        self.update_ui_text()

    def update_ui_text(self):
        """Atualiza todos os textos da interface para o idioma selecionado."""
        self.title(self.get_string("window_title"))
        self.general_settings_label.configure(text=self.get_string("general_settings"))
        self.width_label.configure(text=self.get_string("screen_width"))
        self.height_label.configure(text=self.get_string("screen_height"))
        self.update_size_button.configure(text=self.get_string("update_screen_size"))
        self.output_type_label.configure(text=self.get_string("output_memory_type"))
        storage_values = [self.get_string("internal_memory"), self.get_string("microsd")]
        self.storage_type_menu.configure(values=storage_values)
        if self.storage_type_var.get() not in storage_values:
            self.storage_type_var.set(storage_values[0])
        self.transparency_checkbox.configure(text=self.get_string("use_transparency"))
        self.generate_button.configure(text=self.get_string("generate_button"))
        self.import_button.configure(text=self.get_string("import_image_button"))
        self.resize_button.configure(text=self.get_string("apply_resize"))
        self.delete_button.configure(text=self.get_string("delete_selected"))
        self.clear_all_button.configure(text=self.get_string("clear_all_button"))
        self.language_button.configure(text=self.get_string("language_button"))
        self.about_button.configure(text=self.get_string("about_button"))
        self.save_layout_button.configure(text=self.get_string("save_layout_button"))
        self.load_layout_button.configure(text=self.get_string("load_layout_button"))
        self.element_w_label.configure(text=self.get_string("element_w"))
        self.element_h_label.configure(text=self.get_string("element_h"))

    def show_about_window(self):
        """Cria e exibe a janela 'Sobre' com informações, links e QR code para doação."""
        QR_CODE_IMAGE_PATH = "assets/qrcode_pix.png"
        TUTORIAL_LINK = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 

        about_window = ctk.CTkToplevel(self)
        about_window.title(self.get_string("about_window_title"))
        about_window.geometry("500x650") 
        about_window.resizable(False, False)
        about_window.transient(self) # Mantém a janela 'Sobre' na frente da principal.
        about_window.grab_set() # Bloqueia interações com a janela principal.
        
        # Força a atualização para que as dimensões da janela sejam calculadas.
        about_window.update_idletasks()

        # Lógica para centralizar a janela 'Sobre' em relação à janela principal.
        main_app_x = self.winfo_x()
        main_app_y = self.winfo_y()
        main_app_width = self.winfo_width()
        main_app_height = self.winfo_height()
        about_width = about_window.winfo_width()
        about_height = about_window.winfo_height()
        center_x = main_app_x + (main_app_width // 2) - (about_width // 2)
        center_y = main_app_y + (main_app_height // 2) - (about_height // 2)
        about_window.geometry(f"{about_width}x{about_height}+{center_x}+{center_y}")

        # Frame principal com rolagem.
        main_frame = ctk.CTkScrollableFrame(about_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)

        # Seção: Sobre
        about_frame = ctk.CTkFrame(main_frame)
        about_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        about_frame.grid_columnconfigure(0, weight=1)
        about_content_label = ctk.CTkLabel(about_frame, text=self.get_string("about_content"), wraplength=400, font=ctk.CTkFont(size=14))
        about_content_label.pack(padx=20, pady=(20, 10), fill="x")
        created_by_label = ctk.CTkLabel(about_frame, text=self.get_string("created_by"), font=ctk.CTkFont(size=12, weight="bold"))
        created_by_label.pack(padx=20, pady=10)
        version_label = ctk.CTkLabel(about_frame, text=self.get_string("version_text"), font=ctk.CTkFont(size=10), text_color="gray")
        version_label.pack(padx=20)

        separator1 = ctk.CTkFrame(main_frame, height=2, fg_color="gray30")
        separator1.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        # Seção: Como Usar
        how_to_use_frame = ctk.CTkFrame(main_frame)
        how_to_use_frame.grid(row=2, column=0, sticky="ew", pady=10)
        how_to_use_frame.grid_columnconfigure(0, weight=1)
        how_to_use_title_label = ctk.CTkLabel(how_to_use_frame, text=self.get_string("how_to_use_section_title"), font=ctk.CTkFont(size=16, weight="bold"))
        how_to_use_title_label.pack(padx=20, pady=(10, 5))
        tutorial_link_label = ctk.CTkLabel(how_to_use_frame, text=self.get_string("how_to_use_link_text"), text_color="#3498DB", cursor="hand2", font=ctk.CTkFont(underline=True))
        tutorial_link_label.pack(padx=20, pady=(5, 10))
        tutorial_link_label.bind("<Button-1>", lambda e: webbrowser.open(TUTORIAL_LINK))
        
        separator_htu = ctk.CTkFrame(main_frame, height=2, fg_color="gray30")
        separator_htu.grid(row=3, column=0, sticky="ew", padx=20, pady=10)

        # Seção: Doação
        donation_frame = ctk.CTkFrame(main_frame)
        donation_frame.grid(row=4, column=0, sticky="ew", pady=10)
        donation_frame.grid_columnconfigure(0, weight=1)
        donation_message1_label = ctk.CTkLabel(donation_frame, text=self.get_string("donation_message_1"), wraplength=450)
        donation_message1_label.pack(padx=10, pady=(15, 10), fill="x")
        donation_message2_label = ctk.CTkLabel(donation_frame, text=self.get_string("donation_message_2"), font=ctk.CTkFont(weight="bold"))
        donation_message2_label.pack(padx=10, pady=10)
        try:
            pil_image = Image.open(QR_CODE_IMAGE_PATH)
            qr_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(150, 150))
            qr_label = ctk.CTkLabel(donation_frame, image=qr_image, text="")
            qr_label.pack(padx=10, pady=10)
        except FileNotFoundError:
            qr_label = ctk.CTkLabel(donation_frame, text=self.get_string("qr_code_not_found"), text_color="red", font=ctk.CTkFont(size=14))
            qr_label.pack(padx=10, pady=20)

        separator2 = ctk.CTkFrame(main_frame, height=2, fg_color="gray30")
        separator2.grid(row=5, column=0, sticky="ew", padx=20, pady=10)

        # Seção: Links
        links_frame = ctk.CTkFrame(main_frame)
        links_frame.grid(row=6, column=0, sticky="ew", pady=10)
        links_frame.grid_columnconfigure(0, weight=1)
        find_me_label = ctk.CTkLabel(links_frame, text=self.get_string("find_me_on_github"), font=ctk.CTkFont(size=14))
        find_me_label.pack(padx=20)
        github_link = "https://github.com/KanekiZLF"
        link_label = ctk.CTkLabel(links_frame, text=github_link, text_color="#3498DB", cursor="hand2", font=ctk.CTkFont(size=16, underline=True))
        link_label.pack(padx=20, pady=(5, 20))
        link_label.bind("<Button-1>", lambda e: webbrowser.open(github_link))

    def update_canvas_size(self):
        """Atualiza as dimensões do canvas com base nos valores dos campos de entrada."""
        try:
            new_width = int(self.width_entry.get())
            new_height = int(self.height_entry.get())
            self.canvas.config(width=new_width, height=new_height)
            self.focus_set() # Tira o foco dos campos de entrada.
            self.draw_grid() # Redesenha o grid para o novo tamanho.
        except ValueError:
            messagebox.showerror(self.get_string("title_error"), self.get_string("error_value_must_be_int"))
    
    def draw_grid(self, spacing=10, color="#555555"):
        """Desenha um grid pontilhado no fundo do canvas para auxiliar no alinhamento."""
        self.canvas.delete("grid_line") # Deleta qualquer grid antigo.
        
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
        except ValueError:
            return # Se os valores não forem números, não desenha o grid.

        # Desenha as linhas verticais e horizontais.
        for x in range(0, width, spacing):
            self.canvas.create_line(x, 0, x, height, fill=color, tags="grid_line")
        for y in range(0, height, spacing):
            self.canvas.create_line(0, y, width, y, fill=color, tags="grid_line")
            
        # Joga o grid para o fundo do canvas (atrás de todas as imagens).
        self.canvas.tag_lower("grid_line")

    def on_element_select(self, event=None):
        """Atualiza os campos de dimensão quando um elemento é selecionado na lista."""
        selected_indices = self.listbox.curselection()
        if not selected_indices: return
        
        selected_name = self.listbox.get(selected_indices[0])
        for element in self.elements.values():
            if element['name'] == selected_name:
                self.element_w_entry.delete(0, "end")
                self.element_w_entry.insert(0, str(element['w']))
                self.element_h_entry.delete(0, "end")
                self.element_h_entry.insert(0, str(element['h']))
                break

    def resize_selected_element(self):
        """Redimensiona a imagem do elemento selecionado para os novos valores de W e H."""
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning(self.get_string("title_warning"), self.get_string("warning_no_element_selected"))
            return
        
        selected_name = self.listbox.get(selected_indices[0])
        try:
            new_w = int(self.element_w_entry.get())
            new_h = int(self.element_h_entry.get())
        except ValueError:
            messagebox.showerror(self.get_string("title_error"), self.get_string("error_dims_must_be_int"))
            return
        
        # Encontra o ID do canvas do elemento a ser redimensionado.
        canvas_id_to_resize = None
        for cid, data in self.elements.items():
            if data['name'] == selected_name:
                canvas_id_to_resize = cid
                break
        
        if not canvas_id_to_resize: return
        
        element_data = self.elements[canvas_id_to_resize]
        new_pil_image = self.resize_image(element_data['path'], new_w, new_h)
        if not new_pil_image: return
        
        # Cria uma nova imagem, apaga a antiga e a substitui no canvas e nos dicionários.
        new_tk_image = ImageTk.PhotoImage(new_pil_image)
        new_x = (int(self.width_entry.get()) / 2) - (new_w / 2) # Centraliza a nova imagem.
        new_y = (int(self.height_entry.get()) / 2) - (new_h / 2)
        
        self.canvas.delete(canvas_id_to_resize)
        new_canvas_id = self.canvas.create_image(new_x, new_y, image=new_tk_image, anchor="nw", tags=("draggable", element_data['name']))
        
        # Atualiza os dicionários com os novos dados e o novo ID.
        del self.elements[canvas_id_to_resize]
        del self.tk_images[canvas_id_to_resize]
        element_data.update({'w': new_w, 'h': new_h, 'x': int(new_x), 'y': int(new_y)})
        self.elements[new_canvas_id] = element_data
        self.tk_images[new_canvas_id] = new_tk_image

    def generate_output(self):
        """Chama a função de geração apropriada com base no tipo de armazenamento selecionado."""
        self.focus_set()
        storage_type = self.storage_type_var.get()
        use_transparency = self.transparency_checkbox.get()
        
        if not self.elements:
            messagebox.showinfo(self.get_string("title_info"), self.get_string("info_no_elements_to_generate"))
            return
            
        if storage_type == self.get_string("internal_memory"):
            self.generate_internal_memory_code(use_transparency)
        else:
            self.generate_sd_card_files(use_transparency)

    def generate_internal_memory_code(self, use_transparency):
        """Gera um header C++ (.h) com os dados das imagens em arrays uint16_t."""
        TRANSPARENCY_COLOR_HEX = "0xF81F"
        code_parts = ["// This code was generated by TFT Screen Layout Helper by Luiz F. R. Pimentel\n","// Mode: Internal Memory\n"]
        if use_transparency:
            code_parts.append(f"// Transparency activated with Color Key: {TRANSPARENCY_COLOR_HEX} (Magenta)\n")
        
        code_parts.extend(["\n#pragma once\n\n", "#include <TFT_eSPI.h>\n\n"])
        draw_function_parts = ["void drawLayout(TFT_eSPI& tft) {\n"]
        
        for element in self.elements.values():
            pil_image = self.resize_image(element['path'], element['w'], element['h'])
            if not pil_image: return
            
            rgb565_array = self.convert_image_data(pil_image, use_transparency)
            img_var_name = element['name'].replace('.', '_').replace('-', '_')
            
            # Cria a declaração do array de pixels.
            code_parts.append(f"const uint16_t {img_var_name}_data[{len(rgb565_array)}] = {{\n  ")
            pixel_parts = []
            for i, p in enumerate(rgb565_array):
                pixel_parts.append(f"0x{p:04X}, ")
                # Adiciona uma quebra de linha a cada 16 pixels para melhor formatação.
                if (i + 1) % 16 == 0 and i < len(rgb565_array) - 1:
                    pixel_parts.append("\n  ")
            code_parts.append("".join(pixel_parts))
            code_parts.append("\n};\n\n")
            
            # Cria a chamada de função para desenhar a imagem.
            draw_call = f"  tft.pushImage({element['x']}, {element['y']}, {element['w']}, {element['h']}, {img_var_name}_data"
            if use_transparency:
                draw_call += f", {TRANSPARENCY_COLOR_HEX}"
            draw_call += ");\n"
            draw_function_parts.append(draw_call)
            
        draw_function_parts.append("}\n")
        final_code = "".join(code_parts) + "".join(draw_function_parts)
        self.show_code_window(final_code)

    def generate_sd_card_files(self, use_transparency):
        """Gera arquivos binários (.RAW) para cada imagem e um JSON de layout."""
        output_folder = filedialog.askdirectory(title="Selecione a Pasta de Saída para o Cartão SD")
        if not output_folder: return
        
        layout_data = {
            'author': "Luiz F. R. Pimentel",
            'github': "https://github.com/KanekiZLF",
            'background': None, 
            'icons': []
        }
        
        for i, element in enumerate(self.elements.values()):
            pil_image = self.resize_image(element['path'], element['w'], element['h'])
            if not pil_image:
                messagebox.showerror(self.get_string("title_error"), self.get_string("error_generation_aborted"))
                return
                
            rgb565_array = self.convert_image_data(pil_image, use_transparency)
            
            # Cria um nome de arquivo compatível com sistemas de arquivos mais antigos (8.3).
            base_name = element['name'].split('_')[-1].split('.')[0][:8]
            output_filename = f"{base_name}.RAW"
            output_filepath = os.path.join(output_folder, output_filename)
            
            try:
                with open(output_filepath, 'wb') as f:
                    for pixel in rgb565_array:
                        # Empacota cada pixel como um 'unsigned short' big-endian.
                        f.write(struct.pack('<H', pixel))
            except IOError as e:
                messagebox.showerror(self.get_string("title_error"), self.get_string("error_file_save").format(filepath=output_filepath, e=e))
                return
            
            icon_data = {'file': output_filename, 'x': element['x'], 'y': element['y'], 'w': element['w'], 'h': element['h']}
            if use_transparency:
                icon_data['transparent'] = True
            
            # O primeiro elemento é considerado o fundo.
            if i == 0:
                layout_data['background'] = icon_data
            else:
                layout_data['icons'].append(icon_data)
                
        json_filepath = os.path.join(output_folder, f"Layout_{base_name}.JSON")
        with open(json_filepath, 'w') as f:
            json.dump(layout_data, f, indent=4)
            
        messagebox.showinfo(self.get_string("title_success"), self.get_string("info_sd_files_success").format(folder=output_folder))

    def show_code_window(self, code):
        """Exibe uma nova janela com o código gerado e um botão para copiar."""
        code_window = ctk.CTkToplevel(self)
        code_window.title(self.get_string("code_generated_title"))
        code_window.geometry("700x550")
        code_window.transient(self)
        code_window.grab_set()
        
        main_frame = ctk.CTkFrame(code_window, fg_color="transparent")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        textbox = ctk.CTkTextbox(main_frame, wrap="none", font=("Courier New", 10))
        textbox.grid(row=0, column=0, sticky="nsew")
        textbox.insert("0.0", code)
        
        def copy_to_clipboard():
            """Copia o conteúdo da caixa de texto para a área de transferência."""
            self.clipboard_clear()
            self.clipboard_append(textbox.get("1.0", "end-1c"))
            
            # Feedback visual para o usuário.
            original_text = copy_button.cget("text")
            original_color = copy_button.cget("fg_color")
            copy_button.configure(text=self.get_string("copied_text"), fg_color="green", hover=False)
            def reset_button_state():
                # Verifica se a janela e o botão ainda existem
                if code_window.winfo_exists() and copy_button.winfo_exists():
                    copy_button.configure(text=original_text, fg_color=original_color, hover=True)

            # Agenda a verificação e restauração
            self.after(2000, reset_button_state)
            
        copy_button = ctk.CTkButton(main_frame, text=self.get_string("copy_button_text"), command=copy_to_clipboard)
        copy_button.grid(row=1, column=0, pady=(10,0), sticky="ew")
        
        self.wait_window(code_window)

    def import_image(self):
        """Abre um seletor de arquivos para importar uma imagem para o canvas."""
        filepath = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")])
        if not filepath: return
        
        try:
            pil_image = Image.open(filepath)
        except Exception as e:
            messagebox.showerror(self.get_string("title_error"), self.get_string("error_file_open").format(e=e))
            return
            
        tk_image = ImageTk.PhotoImage(pil_image)
        self.element_counter += 1
        basename = os.path.basename(filepath)
        safe_basename = basename.replace(' ', '_') # Garante que o nome não tenha espaços.
        name = f"img_{self.element_counter}_{safe_basename}"
        
        # Adiciona a imagem ao canvas e aos dicionários de controle.
        canvas_id = self.canvas.create_image(10, 10, image=tk_image, anchor="nw", tags=("draggable", name))
        self.elements[canvas_id] = {'name': name, 'path': filepath, 'x': 10, 'y': 10, 'w': pil_image.width, 'h': pil_image.height}
        self.tk_images[canvas_id] = tk_image
        self.listbox.insert("end", name)

    def delete_selected(self):
        """Exclui o elemento atualmente selecionado na lista do canvas e dos controles."""
        selected_indices = self.listbox.curselection()
        if not selected_indices: return
        
        selected_name = self.listbox.get(selected_indices[0])
        item_to_delete = None
        for canvas_id, data in self.elements.items():
            if data['name'] == selected_name:
                item_to_delete = canvas_id
                break
                
        if item_to_delete:
            self.canvas.delete(item_to_delete)
            del self.elements[item_to_delete]
            del self.tk_images[item_to_delete]
            self.listbox.delete(selected_indices[0])
            self.element_w_entry.delete(0, "end")
            self.element_h_entry.delete(0, "end")
    
    def clear_all_elements(self):
        """Apaga todos os elementos do canvas e da lista, com confirmação do usuário."""
        if not self.elements:
            return # Não faz nada se já estiver vazio.

        # Pede confirmação, pois é uma ação destrutiva.
        confirm = messagebox.askyesno(
            title=self.get_string("confirm_clear_title"),
            message=self.get_string("confirm_clear_message")
        )

        if confirm:
            self.canvas.delete("all") # Apaga todos os itens do canvas.
            self.draw_grid() # Redesenha o grid, que também foi apagado.
            self.listbox.delete(0, "end") # Apaga todos os itens da listbox.
            self.elements.clear() # Limpa as estruturas de dados.
            self.tk_images.clear()
            self.element_counter = 0 # Reinicia o contador.
            self.element_w_entry.delete(0, "end") # Limpa os campos de entrada.
            self.element_h_entry.delete(0, "end")

    def on_press(self, event):
        """Chamado quando um item arrastável é clicado."""
        try:
            # Encontra o item mais próximo do clique.
            canvas_id = self.canvas.find_closest(event.x, event.y)[0]
        except IndexError:
            return # Clicou em uma área vazia do canvas.
            
        self._drag_data["item"] = canvas_id
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        
        # Sincroniza a seleção do canvas com a listbox.
        element_data = self.elements.get(canvas_id)
        if element_data:
            element_name = element_data['name']
            all_items = list(self.listbox.get(0, "end"))
            try:
                index = all_items.index(element_name)
                self.listbox.selection_clear(0, "end")
                self.listbox.selection_set(index)
                self.listbox.activate(index)
                self.listbox.see(index) # Garante que o item selecionado esteja visível.
                self.on_element_select() # Atualiza os campos de W e H.
            except ValueError:
                pass # O item do canvas não está na lista (não deve acontecer).

    def on_drag(self, event):
        """Chamado quando o mouse é movido com o botão pressionado sobre um item."""
        if self._drag_data["item"]:
            dx = event.x - self._drag_data["x"]
            dy = event.y - self._drag_data["y"]
            self.canvas.move(self._drag_data["item"], dx, dy)
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y

    def on_release(self, event):
        """Chamado quando o botão do mouse é solto, finalizando o arraste."""
        if self._drag_data["item"]:
            canvas_id = self._drag_data["item"]
            # Atualiza as coordenadas do elemento no dicionário de dados.
            if canvas_id in self.elements:
                new_x, new_y = self.canvas.coords(canvas_id)
                self.elements[canvas_id]['x'] = int(new_x)
                self.elements[canvas_id]['y'] = int(new_y)
            # Limpa os dados de arraste.
            self._drag_data["item"] = None
            self._drag_data["x"] = 0
            self._drag_data["y"] = 0
            
    def save_layout(self):
        """Salva o estado atual do canvas (elementos e suas propriedades) em um arquivo JSON."""
        if not self.elements:
            messagebox.showinfo(self.get_string("title_info"), self.get_string("info_no_layout_to_save"))
            return
            
        filepath = filedialog.asksaveasfilename(
            title=self.get_string("save_layout_button"),
            defaultextension=".json",
            filetypes=[("Layout Files", "*.json"), ("All Files", "*.*")]
        )
        if not filepath: return
        
        layout_data = {
            "author": "Luiz F. R. Pimentel.",
            "github": "https://github.com/KanekiZLF",
            'canvas_size': {
                'width': self.width_entry.get(),
                'height': self.height_entry.get()
            },
            'elements': list(self.elements.values())
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(layout_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo(self.get_string("title_success"), self.get_string("info_layout_saved_success").format(filepath=filepath))
        except Exception as e:
            messagebox.showerror(self.get_string("title_error"), self.get_string("error_file_save").format(filepath=filepath, e=e))

    def load_layout(self):
        """Carrega um layout de um arquivo JSON, limpando o canvas antes."""
        # Limpa o canvas atual. Se o usuário cancelar a limpeza, o carregamento é abortado.
        self.clear_all_elements()
        if self.elements: 
            return

        filepath = filedialog.askopenfilename(
            title=self.get_string("load_layout_button"),
            filetypes=[("Layout Files", "*.json"), ("All Files", "*.*")]
        )
        if not filepath: return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
        except Exception as e:
            messagebox.showerror(self.get_string("title_error"), f"{self.get_string('error_invalid_layout_file')}\n\nError: {e}")
            return
            
        # Restaura o tamanho do canvas.
        canvas_size = layout_data.get('canvas_size', {'width': 320, 'height': 240})
        self.width_entry.delete(0, "end")
        self.width_entry.insert(0, canvas_size['width'])
        self.height_entry.delete(0, "end")
        self.height_entry.insert(0, canvas_size['height'])
        self.update_canvas_size()
        
        # Recria cada elemento do arquivo de layout.
        for element_data in layout_data.get('elements', []):
            try:
                pil_image = self.resize_image(element_data['path'], element_data['w'], element_data['h'])
                if not pil_image: continue
                
                tk_image = ImageTk.PhotoImage(pil_image)
                name = element_data['name']
                canvas_id = self.canvas.create_image(element_data['x'], element_data['y'], image=tk_image, anchor="nw", tags=("draggable", name))
                
                self.elements[canvas_id] = element_data
                self.tk_images[canvas_id] = tk_image
                self.listbox.insert("end", name)

                # Atualiza o contador de elementos para evitar conflitos de nome.
                try:
                    num = int(name.split('_')[1])
                    if num > self.element_counter:
                        self.element_counter = num
                except (IndexError, ValueError):
                    self.element_counter += 1
            except Exception as e:
                messagebox.showwarning(self.get_string("title_warning"), self.get_string("error_image_process").format(path=element_data.get('path', 'N/A'), e=e))
                
        messagebox.showinfo(self.get_string("title_success"), self.get_string("info_layout_loaded_success"))

# Ponto de entrada da aplicação.
if __name__ == "__main__":
    app = App()
    app.mainloop()