# main.py - Versão Final com funções auxiliares movidas para dentro da classe App

import tkinter
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import struct
import json

# --- Funções de Configuração ---
def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"language": "en"}

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

# --- Dicionário de Traduções ---
TRANSLATIONS = {
    "en": {
        "window_title": "ESP32 Screen Layout Helper", "general_settings": "General Settings",
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
        "error_file_open": "Could not open the image file.\n\nError: {e}"
    },
    "pt": {
        "window_title": "ESP32 Screen Layout Helper", "general_settings": "Configurações Gerais",
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
        "error_file_open": "Não foi possível abrir o arquivo de imagem.\n\nErro: {e}"
    }
}

# --- Classe Principal da Aplicação ---
class App(ctk.CTk):
    ### CORREÇÃO: Funções movidas para dentro da classe para se tornarem métodos ###
    def resize_image(self, image_path, new_width, new_height):
        try:
            w, h = int(new_width), int(new_height)
            if w <= 0 or h <= 0: raise ValueError("Dimensões devem ser positivas")
            img = Image.open(image_path).convert("RGBA")
            return img.resize((w, h), Image.Resampling.LANCZOS)
        except Exception as e:
            messagebox.showerror(self.get_string("title_error"), self.get_string("error_image_process").format(path=image_path, e=e))
            return None

    def convert_image_data(self, pil_image, use_transparency):
        TRANSPARENCY_KEY_COLOR = 0xF81F
        if use_transparency:
            img_rgba = pil_image.convert("RGBA")
            pixels_out = []
            for r, g, b, a in img_rgba.getdata():
                if a < 128: pixels_out.append(TRANSPARENCY_KEY_COLOR)
                else: pixels_out.append(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3))
            return pixels_out
        else:
            img_rgb = pil_image.convert("RGB")
            return [((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3) for r, g, b in img_rgb.getdata()]
            
    def __init__(self):
        super().__init__()

        self.config = load_config()
        self.current_language = self.config.get("language", "en")
        
        self.title(self.get_string("window_title"))
        
        window_width = 630
        window_height = 750
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        self.elements = {}
        self.element_counter = 0
        self.tk_images = {}
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(10,0), pady=10)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas = tkinter.Canvas(self.left_frame, bg="#2B2B2B", highlightthickness=0)
        self.canvas.grid(row=0, column=0)

        self.right_frame = ctk.CTkFrame(self, width=300)
        self.right_frame.grid(row=0, column=1, sticky="ns", padx=10, pady=10)

        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.on_release)
        self._drag_data = {"x": 0, "y": 0, "item": None}

        self.controls_frame = ctk.CTkFrame(self.right_frame)
        self.controls_frame.pack(pady=10, padx=10, fill="x")

        header_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15), padx=5)
        header_frame.grid_columnconfigure((0, 1), weight=1) 

        self.general_settings_label = ctk.CTkLabel(header_frame, font=ctk.CTkFont(weight="bold"))
        self.general_settings_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        self.language_button = ctk.CTkButton(header_frame, command=self.toggle_language)
        self.language_button.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        
        self.about_button = ctk.CTkButton(header_frame, command=self.show_about_window)
        self.about_button.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        size_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        size_frame.pack(pady=5, padx=10, fill="x")
        self.width_label = ctk.CTkLabel(size_frame)
        self.width_label.grid(row=0, column=0, padx=(0,5))
        self.width_entry = ctk.CTkEntry(size_frame, width=60)
        self.width_entry.insert(0, "240")
        self.width_entry.grid(row=0, column=1)
        self.height_label = ctk.CTkLabel(size_frame)
        self.height_label.grid(row=0, column=2, padx=(10,5))
        self.height_entry = ctk.CTkEntry(size_frame, width=60)
        self.height_entry.insert(0, "135")
        self.height_entry.grid(row=0, column=3)
        self.update_size_button = ctk.CTkButton(self.controls_frame, command=self.update_canvas_size)
        self.update_size_button.pack(pady=10, padx=10, fill="x")
        
        self.output_type_label = ctk.CTkLabel(self.controls_frame)
        self.output_type_label.pack(padx=10, pady=(10,0))
        self.storage_type_var = ctk.StringVar()
        self.storage_type_menu = ctk.CTkOptionMenu(self.controls_frame, variable=self.storage_type_var)
        self.storage_type_menu.pack(padx=10, pady=5)

        self.transparency_var = ctk.BooleanVar()
        self.transparency_checkbox = ctk.CTkCheckBox(self.controls_frame, onvalue=True, offvalue=False, variable=self.transparency_var)
        self.transparency_checkbox.pack(padx=10, pady=10)

        self.generate_button = ctk.CTkButton(self.controls_frame, command=self.generate_output, fg_color="green", hover_color="darkgreen")
        self.generate_button.pack(pady=10, padx=10, fill="x")
        
        self.elements_frame = ctk.CTkFrame(self.right_frame)
        self.elements_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.import_button = ctk.CTkButton(self.elements_frame, command=self.import_image)
        self.import_button.pack(pady=10, padx=10, fill="x")
        self.elements_label = ctk.CTkLabel(self.elements_frame)
        self.elements_label.pack()
        self.listbox = tkinter.Listbox(self.elements_frame, background="#333", foreground="white", selectbackground="#1F6AA5", borderwidth=0, exportselection=False)
        self.listbox.pack(pady=5, padx=5, fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_element_select)
        
        resize_controls_frame = ctk.CTkFrame(self.elements_frame)
        resize_controls_frame.pack(pady=5, padx=5, fill="x")
        self.element_w_label = ctk.CTkLabel(resize_controls_frame)
        self.element_w_label.pack(side="left", padx=(5,0))
        self.element_w_entry = ctk.CTkEntry(resize_controls_frame, width=50)
        self.element_w_entry.pack(side="left", padx=(0,10))
        self.element_h_label = ctk.CTkLabel(resize_controls_frame)
        self.element_h_label.pack(side="left")
        self.element_h_entry = ctk.CTkEntry(resize_controls_frame, width=50)
        self.element_h_entry.pack(side="left", padx=(0,10))
        self.resize_button = ctk.CTkButton(resize_controls_frame, command=self.resize_selected_element, width=60)
        self.resize_button.pack(side="left", fill="x", expand=True)
        
        self.delete_button = ctk.CTkButton(self.elements_frame, fg_color="red", hover_color="darkred", command=self.delete_selected)
        self.delete_button.pack(pady=(10,5), padx=5, fill="x")
        
        self.update_ui_text()
        self.update_canvas_size()

    def get_string(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)

    def toggle_language(self):
        self.current_language = "pt" if self.current_language == "en" else "en"
        self.config["language"] = self.current_language
        save_config(self.config)
        self.update_ui_text()

    def update_ui_text(self):
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
        self.elements_label.configure(text=self.get_string("elements_on_screen"))
        self.element_w_label.configure(text=self.get_string("element_w"))
        self.element_h_label.configure(text=self.get_string("element_h"))
        self.resize_button.configure(text=self.get_string("apply_resize"))
        self.delete_button.configure(text=self.get_string("delete_selected"))
        self.language_button.configure(text=self.get_string("language_button"))
        self.about_button.configure(text=self.get_string("about_button"))

    def show_about_window(self):
        about_window = ctk.CTkToplevel(self)
        about_window.title(self.get_string("about_window_title"))
        about_window.geometry("450x200")
        about_window.resizable(False, False)
        about_window.transient(self)
        about_window.grab_set()
        label1 = ctk.CTkLabel(about_window, text=self.get_string("about_content"), wraplength=400, font=ctk.CTkFont(size=14))
        label1.pack(pady=20, padx=20)
        label2 = ctk.CTkLabel(about_window, text=self.get_string("created_by"), font=ctk.CTkFont(size=12, weight="bold"))
        label2.pack(pady=10)

    def update_canvas_size(self):
        try:
            new_width = int(self.width_entry.get())
            new_height = int(self.height_entry.get())
            self.canvas.config(width=new_width, height=new_height)
            self.focus_set()
        except ValueError:
            messagebox.showerror(self.get_string("title_error"), self.get_string("error_value_must_be_int"))

    def on_element_select(self, event=None):
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
        canvas_id_to_resize = None
        for cid, data in self.elements.items():
            if data['name'] == selected_name:
                canvas_id_to_resize = cid
                break
        if not canvas_id_to_resize: return
        element_data = self.elements[canvas_id_to_resize]
        
        # Chamada corrigida para usar o método da classe
        new_pil_image = self.resize_image(element_data['path'], new_w, new_h)
        if not new_pil_image: return
        
        new_tk_image = ImageTk.PhotoImage(new_pil_image)
        new_x = (int(self.width_entry.get()) / 2) - (new_w / 2)
        new_y = (int(self.height_entry.get()) / 2) - (new_h / 2)
        self.canvas.delete(canvas_id_to_resize)
        new_canvas_id = self.canvas.create_image(new_x, new_y, image=new_tk_image, anchor="nw", tags=("draggable", element_data['name']))
        del self.elements[canvas_id_to_resize]
        del self.tk_images[canvas_id_to_resize]
        element_data['w'] = new_w
        element_data['h'] = new_h
        element_data['x'] = int(new_x)
        element_data['y'] = int(new_y)
        self.elements[new_canvas_id] = element_data
        self.tk_images[new_canvas_id] = new_tk_image

    def generate_output(self):
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
        TRANSPARENCY_COLOR_HEX = "0xF81F"
        code_parts = ["// Código gerado pelo Screen Layout Helper by Luiz F. R. Pimentel\n","// Modo: Memória Interna\n"]
        if use_transparency:
            code_parts.append(f"// Transparência ativada com Color Key: {TRANSPARENCY_COLOR_HEX} (Magenta)\n")
        code_parts.extend(["\n#pragma once\n\n", "#include <TFT_eSPI.h>\n\n"])
        draw_function_parts = ["void drawLayout(TFT_eSPI& tft) {\n"]
        for element in self.elements.values():
            pil_image = self.resize_image(element['path'], element['w'], element['h'])
            if not pil_image: return
            rgb565_array = self.convert_image_data(pil_image, use_transparency)
            img_var_name = element['name'].replace('.', '_').replace('-', '_')
            code_parts.append(f"const uint16_t {img_var_name}_data[{len(rgb565_array)}] = {{\n  ")
            pixel_parts = []
            for i, p in enumerate(rgb565_array):
                pixel_parts.append(f"0x{p:04X}, ")
                if (i + 1) % 16 == 0 and i < len(rgb565_array) - 1:
                    pixel_parts.append("\n  ")
            code_parts.append("".join(pixel_parts))
            code_parts.append("\n};\n\n")
            draw_call = f"  tft.pushImage({element['x']}, {element['y']}, {element['w']}, {element['h']}, {img_var_name}_data"
            if use_transparency:
                draw_call += f", {TRANSPARENCY_COLOR_HEX}"
            draw_call += ");\n"
            draw_function_parts.append(draw_call)
        draw_function_parts.append("}\n")
        final_code = "".join(code_parts) + "".join(draw_function_parts)
        self.show_code_window(final_code)

    def generate_sd_card_files(self, use_transparency):
        output_folder = ctk.filedialog.askdirectory(title="Selecione a Pasta de Saída para o Cartão SD")
        if not output_folder: return
        layout_data = {'background': None, 'icons': []}
        for i, element in enumerate(self.elements.values()):
            pil_image = self.resize_image(element['path'], element['w'], element['h'])
            if not pil_image:
                messagebox.showerror(self.get_string("title_error"), self.get_string("error_generation_aborted"))
                return
            rgb565_array = self.convert_image_data(pil_image, use_transparency)
            base_name = element['name'].split('_')[-1].split('.')[0][:8].upper()
            output_filename = f"{base_name}.RAW"
            output_filepath = os.path.join(output_folder, output_filename)
            try:
                with open(output_filepath, 'wb') as f:
                    for pixel in rgb565_array:
                        f.write(struct.pack('>H', pixel))
            except IOError as e:
                messagebox.showerror(self.get_string("title_error"), self.get_string("error_file_save").format(filepath=output_filepath, e=e))
                return
            icon_data = {'file': output_filename, 'x': element['x'], 'y': element['y'], 'w': element['w'], 'h': element['h']}
            if use_transparency:
                icon_data['transparent'] = True
            if i == 0:
                layout_data['background'] = icon_data
            else:
                layout_data['icons'].append(icon_data)
        json_filepath = os.path.join(output_folder, 'LAYOUT.JSON')
        with open(json_filepath, 'w') as f:
            json.dump(layout_data, f, indent=4)
        messagebox.showinfo(self.get_string("title_success"), self.get_string("info_sd_files_success").format(folder=output_folder))

    def show_code_window(self, code):
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
            clipboard_text = textbox.get("1.0", "end-1c")
            self.clipboard_clear()
            self.clipboard_append(clipboard_text)
            original_text = self.get_string("copy_button_text")
            original_color = copy_button.cget("fg_color")
            copy_button.configure(text=self.get_string("copied_text"), fg_color="green", hover=False)
            self.after(2000, lambda: copy_button.configure(text=original_text, fg_color=original_color, hover=True))
        copy_button = ctk.CTkButton(main_frame, text=self.get_string("copy_button_text"), command=copy_to_clipboard)
        copy_button.grid(row=1, column=0, pady=(10,0), sticky="ew")
        self.wait_window(code_window) 
        
    def import_image(self):
        filepath = ctk.filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")])
        if not filepath: return
        try:
            pil_image = Image.open(filepath)
        except Exception as e:
            messagebox.showerror(self.get_string("title_error"), self.get_string("error_file_open").format(e=e))
            return
        tk_image = ImageTk.PhotoImage(pil_image)
        self.element_counter += 1
        basename = os.path.basename(filepath)
        safe_basename = basename.replace(' ', '_')
        name = f"el_{self.element_counter}_{safe_basename}"
        canvas_id = self.canvas.create_image(10, 10, image=tk_image, anchor="nw", tags=("draggable", name))
        self.elements[canvas_id] = {'name': name, 'path': filepath, 'x': 10, 'y': 10, 'w': pil_image.width, 'h': pil_image.height}
        self.tk_images[canvas_id] = tk_image
        self.listbox.insert("end", name)

    def delete_selected(self):
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

    def on_press(self, event):
        try: canvas_id = self.canvas.find_closest(event.x, event.y)[0]
        except IndexError: return
        self._drag_data["item"] = canvas_id
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        element_data = self.elements.get(canvas_id)
        if element_data:
            element_name = element_data['name']
            all_items = list(self.listbox.get(0, "end"))
            try:
                index = all_items.index(element_name)
                self.listbox.selection_clear(0, "end")
                self.listbox.selection_set(index)
                self.listbox.activate(index)
                self.listbox.see(index)
                self.on_element_select()
            except ValueError: pass

    def on_drag(self, event):
        if self._drag_data["item"]:
            dx = event.x - self._drag_data["x"]
            dy = event.y - self._drag_data["y"]
            self.canvas.move(self._drag_data["item"], dx, dy)
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y

    def on_release(self, event):
        if self._drag_data["item"]:
            canvas_id = self._drag_data["item"]
            if canvas_id in self.elements:
                new_x, new_y = self.canvas.coords(canvas_id)
                self.elements[canvas_id]['x'] = int(new_x)
                self.elements[canvas_id]['y'] = int(new_y)
            self._drag_data["item"] = None
            self._drag_data["x"] = 0
            self._drag_data["y"] = 0
        
if __name__ == "__main__":
    app = App()
    app.mainloop()