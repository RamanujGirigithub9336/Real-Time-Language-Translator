# translator_gui.py
import threading
import customtkinter as ctk
from translator_backend import LANGUAGES, process_translation

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Swadeshi Voice Translator")
        self.geometry("600x600")
        ctk.set_appearance_mode("Dark")

        self.source_lang = ctk.StringVar(value="English")
        self.target_lang = ctk.StringVar(value="Hindi")

        ctk.CTkLabel(self, text="Source Language").pack(pady=5)
        self.source_menu = ctk.CTkOptionMenu(self, values=list(LANGUAGES.keys()), variable=self.source_lang)
        self.source_menu.pack(pady=5)

        ctk.CTkLabel(self, text="Target Language").pack(pady=5)
        self.target_menu = ctk.CTkOptionMenu(self, values=list(LANGUAGES.keys()), variable=self.target_lang)
        self.target_menu.pack(pady=5)

        self.chat_frame = ctk.CTkScrollableFrame(self, width=550, height=350)
        self.chat_frame.pack(pady=10)
        self.message_widgets = []

        self.listen_button = ctk.CTkButton(self, text="🎤 Start Listening", command=self.start_thread)
        self.listen_button.pack(pady=10)

    def start_thread(self):
        threading.Thread(target=self.listen_and_translate, daemon=True).start()

    def listen_and_translate(self):
        src = self.source_lang.get()
        tgt = self.target_lang.get()
        transcription, translation = process_translation(src, tgt)
        self.add_chat_message(transcription, translation)

    def add_chat_message(self, original, translated):
        msg = f"🗣 {original}\n🌐 {translated}"
        frame = ctk.CTkFrame(self.chat_frame, fg_color="#1f1f1f")
        frame.pack(padx=10, pady=5, fill="x", anchor="w")

        label = ctk.CTkLabel(frame, text=msg, justify="left", wraplength=480)
        label.pack(padx=8, pady=4)
        self.message_widgets.append(label)
        self.chat_frame._parent_canvas.yview_moveto(1.0)

if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
