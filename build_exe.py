# -*- coding: utf-8 -*-
"""
Script di Compilazione per LTX & Wan2GP Prompt Agent Studio.
Genera un eseguibile Windows standalone (.exe) usando PyInstaller.
"""

import os
import sys
import PyInstaller.__main__

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def build():
    print("Avvio compilazione di LTX_Prompt_Studio.exe in corso...")
    
    args = [
        "app.py",
        "--name=LTX_Prompt_Studio",
        "--onefile",
        "--noconsole",
        "--clean",
        "--collect-all=customtkinter",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=requests",
        "--hidden-import=prompt_engine",
        "--hidden-import=llm_manager",
    ]
    
    PyInstaller.__main__.run(args)
    print("\nCompilazione terminata con successo! L'eseguibile si trova nella cartella 'dist/LTX_Prompt_Studio.exe'.")

if __name__ == "__main__":
    build()
