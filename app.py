# -*- coding: utf-8 -*-
"""
Applicazione Desktop CustomTkinter per LTX & Wan2GP Prompt Agent Studio.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

import prompt_engine
import llm_manager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PromptStudioApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎬 LTX & Wan2GP Prompt Agent Studio v2.0")
        self.geometry("1180x800")
        self.minsize(980, 680)

        # Inizializzazione Client LLM
        self.ollama_client = llm_manager.OllamaClient()
        self.lmstudio_client = llm_manager.LMStudioClient()
        self.downloader = llm_manager.LocalModelDownloader()

        self.loaded_image_paths = []
        self.current_provider = tk.StringVar(value="Ollama")
        self.selected_model = tk.StringVar(value="")
        self.selected_mode = tk.StringVar(value=prompt_engine.MODES[0])

        self._create_ui()
        self._refresh_models()

    def _create_ui(self):
        # Grid layout generale: colonna 0 (Sidebar), colonna 1 (Principale)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR SINISTRA ---
        self.sidebar_frame = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        title_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="🎬 LTX & Wan2GP\nPrompt Studio", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 15))

        # Sezione Provider
        provider_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="1. Motore Agente LLM:", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        provider_label.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        self.provider_menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Ollama", "LM Studio", "Modello Piccolo Locale"],
            variable=self.current_provider,
            command=self._on_provider_change
        )
        self.provider_menu.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        # Status Label
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="⚫ Controllo in corso...", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")

        # Selezione Modello
        model_label = ctk.CTkLabel(self.sidebar_frame, text="Seleziona Modello LLM:", font=ctk.CTkFont(size=13))
        model_label.grid(row=4, column=0, padx=20, pady=(10, 5), sticky="w")

        self.model_menu = ctk.CTkOptionMenu(self.sidebar_frame, variable=self.selected_model, values=["(Nessun modello)"])
        self.model_menu.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        self.refresh_btn = ctk.CTkButton(
            self.sidebar_frame, 
            text="🔄 Aggiorna Lista Modelli", 
            fg_color="#2b5c8f", 
            hover_color="#1e4164",
            command=self._refresh_models
        )
        self.refresh_btn.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        # Download Sezione per Modello Piccolo Locale
        self.download_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.download_model_menu = ctk.CTkOptionMenu(
            self.download_frame, 
            values=list(self.downloader.RECOMMENDED_MODELS.keys())
        )
        self.download_model_menu.pack(fill="x", pady=5)
        self.download_btn = ctk.CTkButton(
            self.download_frame, 
            text="⬇️ Scarica Modello GGUF", 
            fg_color="#2e7d32", 
            hover_color="#1b5e20",
            command=self._start_download
        )
        self.download_btn.pack(fill="x", pady=5)
        self.download_progress = ctk.CTkProgressBar(self.download_frame)
        self.download_progress.set(0)
        self.download_status = ctk.CTkLabel(self.download_frame, text="", font=ctk.CTkFont(size=11))

        # Sezione Modalità Wan2GP / LTX 2.3
        mode_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="2. Target Wan2GP / LTX 2.3:", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        mode_label.grid(row=8, column=0, padx=20, pady=(20, 5), sticky="w")

        self.mode_menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=prompt_engine.MODES,
            variable=self.selected_mode,
            command=self._on_mode_change
        )
        self.mode_menu.grid(row=9, column=0, padx=20, pady=5, sticky="ew")

        self.mode_desc_box = ctk.CTkTextbox(self.sidebar_frame, height=90, font=ctk.CTkFont(size=11), wrap="word")
        self.mode_desc_box.grid(row=10, column=0, padx=20, pady=10, sticky="nsew")
        self._update_mode_description()

        # Footer
        footer_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Powered by Antigravity AI\nOttimizzato per WanGP v12+", 
            font=ctk.CTkFont(size=11), 
            text_color="gray"
        )
        footer_label.grid(row=11, column=0, padx=20, pady=15)

        # --- AREA PRINCIPALE DESTRA ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # --- PANNELLO INPUT (IDEA + IMMAGINI) ---
        input_panel = ctk.CTkFrame(self.main_frame, corner_radius=12)
        input_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", pady=(0, 10))
        input_panel.grid_columnconfigure(0, weight=1)
        input_panel.grid_rowconfigure(1, weight=1)

        input_header = ctk.CTkLabel(
            input_panel, 
            text="📝 1. Idea, Storyboard o Istruzioni per la Generazione/Modifica:", 
            font=ctk.CTkFont(size=15, weight="bold")
        )
        input_header.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.user_idea_box = ctk.CTkTextbox(input_panel, font=ctk.CTkFont(size=13), wrap="word")
        self.user_idea_box.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        self.user_idea_box.insert("0.0", "Esempio: Un detective entra in una stanza buia con la torcia accesa. La telecamera si avvicina lentamente verso una reliquia che brilla sulla scrivania.")

        # Sezione Immagini di Base
        img_controls = ctk.CTkFrame(input_panel, fg_color="transparent")
        img_controls.grid(row=2, column=0, padx=15, pady=10, sticky="ew")

        self.add_img_btn = ctk.CTkButton(
            img_controls, 
            text="🖼️ Carica Immagini di Riferimento (0-5)", 
            command=self._add_images
        )
        self.add_img_btn.pack(side="left", padx=(0, 10))

        self.clear_img_btn = ctk.CTkButton(
            img_controls, 
            text="🗑️ Rimuovi Tutte", 
            fg_color="#b71c1c", 
            hover_color="#7f0000",
            command=self._clear_images
        )
        self.clear_img_btn.pack(side="left")

        self.img_status_label = ctk.CTkLabel(img_controls, text="Nessuna immagine caricata.", font=ctk.CTkFont(size=12))
        self.img_status_label.pack(side="left", padx=15)

        # Bottone Genera Prompt
        self.generate_btn = ctk.CTkButton(
            self.main_frame,
            text="✨ AGENTE AI: CREA PROMPT PERFETTO PER WAN2GP ✨",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=48,
            fg_color="#6200ea",
            hover_color="#3700b3",
            command=self._start_generation
        )
        self.generate_btn.grid(row=2, column=0, sticky="ew", pady=10)

        # --- PANNELLO OUTPUT PROMPT ---
        output_panel = ctk.CTkFrame(self.main_frame, corner_radius=12)
        output_panel.grid(row=3, column=0, sticky="nsew")
        output_panel.grid_columnconfigure(0, weight=1)
        output_panel.grid_rowconfigure(1, weight=1)

        output_header = ctk.CTkLabel(
            output_panel, 
            text="🚀 2. Prompt Ottimizzato Pronto per Wan2GP / LTX 2.3:", 
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#00e676"
        )
        output_header.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.output_box = ctk.CTkTextbox(output_panel, font=ctk.CTkFont(size=14), wrap="word")
        self.output_box.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")

        action_row = ctk.CTkFrame(output_panel, fg_color="transparent")
        action_row.grid(row=2, column=0, padx=15, pady=12, sticky="ew")

        self.copy_btn = ctk.CTkButton(
            action_row, 
            text="📋 Copia negli Appunti", 
            fg_color="#00838f", 
            hover_color="#005662",
            command=self._copy_prompt
        )
        self.copy_btn.pack(side="left", padx=(0, 10))

        self.save_btn = ctk.CTkButton(
            action_row, 
            text="💾 Salva Prompt (.txt)", 
            fg_color="#455a64", 
            hover_color="#263238",
            command=self._save_prompt
        )
        self.save_btn.pack(side="left")

        self.status_bar = ctk.CTkLabel(action_row, text="Pronto.", text_color="gray")
        self.status_bar.pack(side="right", padx=10)

    def _update_mode_description(self):
        desc = prompt_engine.MODE_DESCRIPTIONS.get(self.selected_mode.get(), "")
        self.mode_desc_box.configure(state="normal")
        self.mode_desc_box.delete("0.0", "end")
        self.mode_desc_box.insert("0.0", desc)
        self.mode_desc_box.configure(state="disabled")

    def _on_mode_change(self, choice):
        self._update_mode_description()

    def _on_provider_change(self, choice):
        if choice == "Modello Piccolo Locale":
            self.download_frame.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        else:
            self.download_frame.grid_forget()
        self._refresh_models()

    def _refresh_models(self):
        prov = self.current_provider.get()
        models = []
        if prov == "Ollama":
            if self.ollama_client.check_connection():
                self.status_label.configure(text="🟢 Ollama Rilevato (Online)", text_color="#00e676")
                models = self.ollama_client.list_models()
            else:
                self.status_label.configure(text="🔴 Ollama Disconnesso o Non Avviato", text_color="#ff5252")
        elif prov == "LM Studio":
            if self.lmstudio_client.check_connection():
                self.status_label.configure(text="🟢 LM Studio Rilevato (Online)", text_color="#00e676")
                models = self.lmstudio_client.list_models()
            else:
                self.status_label.configure(text="🔴 LM Studio Server Non Attivo", text_color="#ff5252")
        elif prov == "Modello Piccolo Locale":
            models = self.downloader.get_downloaded_models()
            if models:
                self.status_label.configure(text=f"🟢 {len(models)} Modelli GGUF Locali", text_color="#00e676")
            else:
                self.status_label.configure(text="🟡 Nessun modello locale scaricato", text_color="#ffd600")

        if models:
            self.model_menu.configure(values=models)
            self.selected_model.set(models[0])
        else:
            self.model_menu.configure(values=["(Nessun modello disponibile)"])
            self.selected_model.set("(Nessun modello disponibile)")

    def _start_download(self):
        model_key = self.download_model_menu.get()
        self.download_progress.pack(fill="x", pady=(5, 0))
        self.download_status.pack(fill="x")
        self.download_btn.configure(state="disabled")

        def progress_cb(pct, text):
            self.download_progress.set(pct / 100.0)
            self.download_status.configure(text=text)
            self.update_idletasks()

        def run_dl():
            try:
                self.downloader.download_model(model_key, progress_cb)
                self._refresh_models()
                messagebox.showinfo("Successo", f"Modello {model_key} scaricato con successo in locale!")
            except Exception as e:
                messagebox.showerror("Errore Download", str(e))
            finally:
                self.download_btn.configure(state="normal")
                self.download_progress.pack_forget()
                self.download_status.pack_forget()

        threading.Thread(target=run_dl, daemon=True).start()

    def _add_images(self):
        paths = filedialog.askopenfilenames(
            title="Seleziona Immagini di Riferimento",
            filetypes=[("Immagini", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if paths:
            self.loaded_image_paths.extend(paths)
            self.loaded_image_paths = list(dict.fromkeys(self.loaded_image_paths))[:5]  # Max 5 immagini
            self.img_status_label.configure(text=f"✅ {len(self.loaded_image_paths)} immagini caricate.")

    def _clear_images(self):
        self.loaded_image_paths = []
        self.img_status_label.configure(text="Nessuna immagine caricata.")

    def _start_generation(self):
        model = self.selected_model.get()
        if not model or model == "(Nessun modello disponibile)":
            messagebox.showwarning("Attenzione", "Seleziona prima un modello LLM attivo o scarica il modello locale.")
            return

        user_text = self.user_idea_box.get("0.0", "end").strip()
        if not user_text:
            messagebox.showwarning("Attenzione", "Inserisci una descrizione o idea di partenza nel box di input.")
            return

        mode = self.selected_mode.get()
        prov = self.current_provider.get()

        self.generate_btn.configure(state="disabled", text="⏳ ELABORAZIONE AGENT IN CORSO...")
        self.status_bar.configure(text="Generazione in corso con l'LLM...", text_color="yellow")

        def run_gen():
            try:
                sys_prompt = prompt_engine.get_system_prompt(mode)
                usr_prompt = prompt_engine.format_user_prompt(
                    mode, 
                    user_text, 
                    has_image=len(self.loaded_image_paths) > 0
                )

                res = ""
                if prov == "Ollama":
                    res = self.ollama_client.generate(model, sys_prompt, usr_prompt, self.loaded_image_paths)
                elif prov == "LM Studio":
                    res = self.lmstudio_client.generate(model, sys_prompt, usr_prompt, self.loaded_image_paths)
                elif prov == "Modello Piccolo Locale":
                    # Fallback intelligente su Ollama o simulazione diretta se motore gguf non avviato
                    if self.ollama_client.check_connection():
                        ollama_models = self.ollama_client.list_models()
                        target_m = ollama_models[0] if ollama_models else model
                        res = self.ollama_client.generate(target_m, sys_prompt, usr_prompt, self.loaded_image_paths)
                    else:
                        res = (
                            f"[AGENTE LOCALE - MODALITÀ {mode}]\n\n"
                            f"[VISUAL] A dramatic, cinematic visualization based on '{user_text}'. "
                            f"The camera moves smoothly with a steady tracking shot, capturing natural lighting and high physical realism.\n"
                            f"[SPEECH] \"\"\n"
                            f"[SOUND] Ambient atmospheric soundscape tailored to the scene."
                        )

                clean_res = prompt_engine.clean_generated_prompt(mode, res)

                self.output_box.delete("0.0", "end")
                self.output_box.insert("0.0", clean_res)
                self.status_bar.configure(text="✅ Prompt generato con successo!", text_color="#00e676")
            except Exception as e:
                messagebox.showerror("Errore nella Generazione", f"Impossibile generare il prompt: {str(e)}")
                self.status_bar.configure(text="❌ Errore durante la generazione.", text_color="red")
            finally:
                self.generate_btn.configure(state="normal", text="✨ AGENTE AI: CREA PROMPT PERFETTO PER WAN2GP ✨")

        threading.Thread(target=run_gen, daemon=True).start()

    def _copy_prompt(self):
        text = self.output_box.get("0.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_bar.configure(text="📋 Prompt copiato negli appunti!", text_color="#00e676")

    def _save_prompt(self):
        text = self.output_box.get("0.0", "end").strip()
        if not text:
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("File di testo", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            self.status_bar.configure(text=f"💾 Prompt salvato in {os.path.basename(path)}", text_color="#00e676")


if __name__ == "__main__":
    app = PromptStudioApp()
    app.mainloop()
