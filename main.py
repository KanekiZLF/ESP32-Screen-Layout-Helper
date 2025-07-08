# main.py - Versão Final com tratamento de erro aprimorado

import tkinter
from tkinter import messagebox # ### ADICIONADO para mostrar pop-ups de erro
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import struct
import json

# --- Funções Auxiliares ---

### ATUALIZADO: resize_image agora mostra um pop-up em caso de erro ###
def resize_image(image_path, new_width, new_height):
    try:
        img = Image.open(image_path).convert("RGBA")
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    except Exception as e:
        # Em vez de um print silencioso, mostramos um erro claro para o usuário
        messagebox.showerror("Erro de Imagem", f"Não foi possível processar a imagem:\n{image_path}\n\nErro: {e}")
        return None

# ... (o resto das funções auxiliares e a classe App continuam iguais até generate_sd_card_files) ...
def convert_image_data(pil_image, use_transparency):
    TRANSPARENCY_KEY_COLOR = 0xF81F
    if use_transparency:
        img_rgba = pil_image.convert("RGBA")
        pixels_out = []
        for r, g, b, a in img_rgba.getdata():
            if a < 128:
                pixels_out.append(TRANSPARENCY_KEY_COLOR)
            else:
                pixels_out.append(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3))
        return pixels_out
    else:
        img_rgb = pil_image.convert("RGB")
        return [((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3) for r, g, b in img_rgb.getdata()]

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ESP32 Screen Layout Helper")
        self.geometry("850x600")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.elements = {}
        self.element_counter = 0
        self.tk_images = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.screen_width = 320
        self.screen_height = 240
        self.canvas = tkinter.Canvas(self.left_frame, width=self.screen_width, height=self.screen_height, bg="#2B2B2B")
        self.canvas.grid(row=0, column=0)
        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.on_release)
        self._drag_data = {"x": 0, "y": 0, "item": None}
        self.right_frame = ctk.CTkFrame(self, width=280)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        controls_frame = ctk.CTkFrame(self.right_frame)
        controls_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(controls_frame, text="Configurações Gerais", font=ctk.CTkFont(weight="bold")).pack()
        size_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        size_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(size_frame, text="Largura:").grid(row=0, column=0, padx=(0,5))
        self.width_entry = ctk.CTkEntry(size_frame, width=60)
        self.width_entry.insert(0, str(self.screen_width))
        self.width_entry.grid(row=0, column=1)
        ctk.CTkLabel(size_frame, text="Altura:").grid(row=0, column=2, padx=(10,5))
        self.height_entry = ctk.CTkEntry(size_frame, width=60)
        self.height_entry.insert(0, str(self.screen_height))
        self.height_entry.grid(row=0, column=3)
        ctk.CTkButton(controls_frame, text="Atualizar Tamanho da Tela", command=self.update_canvas_size).pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(controls_frame, text="Tipo de Memória de Saída:").pack(padx=10, pady=(10,0))
        self.storage_type_var = ctk.StringVar(value="Memória Interna")
        self.storage_type_menu = ctk.CTkOptionMenu(controls_frame, values=["Memória Interna", "Micro SD"], variable=self.storage_type_var)
        self.storage_type_menu.pack(padx=10, pady=5)
        self.transparency_var = ctk.BooleanVar()
        self.transparency_checkbox = ctk.CTkCheckBox(controls_frame, text="Usar transparência (Color Key)", variable=self.transparency_var)
        self.transparency_checkbox.pack(padx=10, pady=10)
        self.generate_button = ctk.CTkButton(controls_frame, text="Gerar Código / Arquivos", command=self.generate_output, fg_color="green", hover_color="darkgreen")
        self.generate_button.pack(pady=10, padx=10, fill="x")
        elements_frame = ctk.CTkFrame(self.right_frame)
        elements_frame.pack(pady=10, padx=10, fill="both", expand=True)
        ctk.CTkButton(elements_frame, text="Importar Imagem", command=self.import_image).pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(elements_frame, text="Elementos na Tela").pack()
        self.listbox = tkinter.Listbox(elements_frame, background="#333", foreground="white", selectbackground="#1F6AA5", borderwidth=0)
        self.listbox.pack(pady=5, padx=5, fill="both", expand=True)
        ctk.CTkButton(elements_frame, text="Excluir Selecionado", command=self.delete_selected, fg_color="red", hover_color="darkred").pack(pady=5, padx=10, fill="x")
        
    def update_canvas_size(self):
        try:
            new_width = int(self.width_entry.get())
            new_height = int(self.height_entry.get())
            self.screen_width = new_width
            self.screen_height = new_height
            self.canvas.config(width=self.screen_width, height=self.screen_height)
            self.focus_set()
        except ValueError:
            messagebox.showerror("Erro de Valor", "Largura e altura devem ser números inteiros.")

    def generate_output(self):
        self.focus_set()
        storage_type = self.storage_type_var.get()
        use_transparency = self.transparency_var.get()
        if not self.elements:
            messagebox.showinfo("Informação", "Nenhum elemento na tela para gerar o código.")
            return
        if storage_type == "Memória Interna":
            self.generate_internal_memory_code(use_transparency)
        else:
            self.generate_sd_card_files(use_transparency)

    def generate_internal_memory_code(self, use_transparency):
        # ... (esta função não precisa de mudanças) ...
        code_parts = ["// Código gerado pelo Screen Layout Helper\n","// Modo: Memória Interna\n","#pragma once\n\n","#include <TFT_eSPI.h>\n\n"]
        draw_function_parts = ["void drawLayout(TFT_eSPI& tft) {\n"]
        TRANSPARENCY_COLOR_HEX = "0xF81F"
        for element in self.elements.values():
            pil_image = resize_image(element['path'], element['w'], element['h'])
            if not pil_image: return # Se houve erro na imagem, para a geração
            rgb565_array = convert_image_data(pil_image, use_transparency)
            img_var_name = element['name'].replace('.', '_').replace('-', '_')
            code_parts.append(f"const uint16_t {img_var_name}_data[{len(rgb565_array)}] = {{\n  ")
            pixel_parts = [f"0x{p:04X}, " for p in rgb565_array]
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

    ### ATUALIZADO: generate_sd_card_files agora tem um try-except para salvar os arquivos ###
    def generate_sd_card_files(self, use_transparency):
        output_folder = ctk.filedialog.askdirectory(title="Selecione a Pasta de Saída para o Cartão SD")
        if not output_folder: return
        
        layout_data = {'background': None, 'icons': []}
        
        for i, element in enumerate(self.elements.values()):
            pil_image = resize_image(element['path'], element['w'], element['h'])
            # Se a função resize_image falhar, ela já mostrou um erro e retornou None.
            # Aqui nós paramos a geração para evitar criar um JSON incompleto.
            if not pil_image:
                messagebox.showerror("Geração Interrompida", "A geração de arquivos foi interrompida devido a um erro na imagem.")
                return 

            rgb565_array = convert_image_data(pil_image, use_transparency)
            
            base_name = element['name'].split('_')[-1].split('.')[0][:8].upper()
            output_filename = f"{base_name}.RAW"
            output_filepath = os.path.join(output_folder, output_filename)
            
            try:
                # Tenta salvar o arquivo binário .raw
                with open(output_filepath, 'wb') as f:
                    for pixel in rgb565_array:
                        f.write(struct.pack('>H', pixel))
            except IOError as e:
                messagebox.showerror("Erro de Arquivo", f"Não foi possível salvar o arquivo:\n{output_filepath}\n\nErro: {e}")
                return # Interrompe a geração se não conseguir salvar um arquivo

            # Adiciona a informação ao dicionário de layout
            icon_data = {'file': output_filename, 'x': element['x'], 'y': element['y'], 'w': element['w'], 'h': element['h']}
            if use_transparency:
                icon_data['transparent'] = True
            
            # Assume que a primeira imagem adicionada é o fundo
            if i == 0:
                layout_data['background'] = icon_data
            else:
                layout_data['icons'].append(icon_data)

        # Salva o arquivo layout.json somente se tudo deu certo
        json_filepath = os.path.join(output_folder, 'LAYOUT.JSON')
        with open(json_filepath, 'w') as f:
            json.dump(layout_data, f, indent=4)
        
        messagebox.showinfo("Sucesso", f"Arquivos para SD gerados com sucesso na pasta:\n{output_folder}")

    def show_code_window(self, code):
        code_window = ctk.CTkToplevel(self)
        code_window.title("Código Gerado (layout.h)")
        code_window.geometry("700x500")
        code_window.transient(self)
        code_window.grab_set()
        textbox = ctk.CTkTextbox(code_window, wrap="none", font=("Courier New", 10))
        textbox.pack(padx=10, pady=10, fill="both", expand=True)
        textbox.insert("0.0", code)
        self.wait_window(code_window) 
        
    def import_image(self):
        filepath = ctk.filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")])
        if not filepath: return
        try:
            pil_image = Image.open(filepath)
        except Exception as e:
            messagebox.showerror("Erro ao Abrir", f"Não foi possível abrir o arquivo de imagem.\n\nErro: {e}")
            return
        tk_image = ImageTk.PhotoImage(pil_image)
        self.element_counter += 1
        name = f"el_{self.element_counter}_{os.path.basename(filepath)}"
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
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.canvas.move(self._drag_data["item"], dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_release(self, event):
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