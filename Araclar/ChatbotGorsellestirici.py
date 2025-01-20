import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox, scrolledtext
import webbrowser
from linkcevirici import GitHubRawConverter
import anthropic
import os
import tempfile


class AIPromptWindow:
    def __init__(self, parent, callback):
        self.window = tk.Toplevel(parent)
        self.window.title("AI Prompt")
        self.window.geometry("600x400")
        
        # Prompt giriş alanı
        self.prompt_text = scrolledtext.ScrolledText(self.window, height=10)
        self.prompt_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Gönder butonu
        send_btn = ttk.Button(self.window, text="Gönder", command=lambda: callback(self.prompt_text.get("1.0", "end-1c")))
        send_btn.pack(pady=10)


class AIResponseWindow:
    def __init__(self, parent, response):
        self.window = tk.Toplevel(parent)
        self.window.title("AI Yanıtı")
        self.window.geometry("800x600")
        
        # Yanıt gösterme alanı
        self.response_text = scrolledtext.ScrolledText(self.window, height=30, wrap=tk.WORD)
        self.response_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # AI yanıtını formatla
        formatted_response = str(response)
        if hasattr(response, 'text'):  # TextBlock objesi ise
            formatted_response = response.text
        
        self.response_text.insert("1.0", formatted_response)
        self.response_text.config(state="disabled")
        
        # Kopyala butonu
        copy_btn = ttk.Button(self.window, text="Kopyala", command=self.copy_response)
        copy_btn.pack(pady=10)
    
    def copy_response(self):
        response = self.response_text.get("1.0", "end-1c")
        self.window.clipboard_clear()
        self.window.clipboard_append(response)
        messagebox.showinfo("Kopyalandı", "Yanıt panoya kopyalandı!")

    def send_to_ai(self, prompt):
        """Promptu AI'ya gönderir ve yanıtı gösterir"""
        try:
            # Mevcut kodu al
            self.generate_code()  # Kodu güncelle
            current_code = self.code_text.get("1.0", "end-1c")
            
            # Promptu ve kodu birleştir
            full_prompt = f"{prompt}\n\nMevcut kod:\n```javascript\n{current_code}\n```"
            
            # AI'ya gönder
            message = self.ai_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            # Yanıtı göster
            response_text = message.content[0].text if isinstance(message.content, list) else message.content
            AIResponseWindow(self.root, response_text)
            
        except Exception as e:
            messagebox.showerror("Hata", f"AI yanıtı alınırken bir hata oluştu: {str(e)}")


class PreviewWindow:
    def __init__(self, parent, code):
        self.window = tk.Toplevel(parent)
        self.window.title("Chatbot Önizleme")
        self.window.geometry("1024x768")
        
        # HTML içeriğini oluştur
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Chatbot Önizleme</title>
    <meta charset="UTF-8">
    <style>
        body {{ margin: 0; padding: 20px; font-family: Arial, sans-serif; }}
    </style>
</head>
<body>
    <h2>Chatbot Önizleme</h2>
    <p>Bu sayfada chatbot'unuzun nasıl görüneceğini görebilirsiniz.</p>
    {code}
</body>
</html>
"""
        # Geçici HTML dosyası oluştur
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
            f.write(html_content)
            self.temp_file = f.name
        
        # Tarayıcıda aç
        webbrowser.open('file://' + os.path.realpath(self.temp_file))
        
        # Pencereyi kapat butonu
        close_btn = ttk.Button(self.window, text="Kapat", command=self.cleanup_and_close)
        close_btn.pack(pady=10)
    
    def cleanup_and_close(self):
        """Geçici dosyayı temizle ve pencereyi kapat"""
        try:
            os.unlink(self.temp_file)
        except:
            pass
        self.window.destroy()


class ChatbotCustomizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot Görsel Özelleştirme Arayüzü")
        self.root.geometry("800x600")

        # Değişkenler
        self.chatflowid_var = tk.StringVar(value="2c47ed1b-015a-493b-aa79-42b9d1631373")
        self.apiHost_var = tk.StringVar(value="https://www.knowhy.site")
        self.topK_var = tk.StringVar(value="")  # İstenirse boş geçilebilir

        # Button (açılma ikonu) ile ilgili değişkenler
        self.btn_bg_color = tk.StringVar(value="#3B81F6")
        self.btn_icon_color = tk.StringVar(value="white")
        self.btn_icon_src = tk.StringVar(value="https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/svg/google-messages.svg")
        self.btn_right_var = tk.IntVar(value=20)
        self.btn_bottom_var = tk.IntVar(value=20)
        self.btn_size_var = tk.IntVar(value=48)
        self.btn_dragdrop_var = tk.BooleanVar(value=True)
        self.btn_auto_open_var = tk.BooleanVar(value=True)
        self.btn_open_delay_var = tk.IntVar(value=2)
        self.btn_auto_open_mobile_var = tk.BooleanVar(value=False)

        # Tooltip ile ilgili değişkenler
        self.tooltip_show_var = tk.BooleanVar(value=True)
        self.tooltip_msg_var = tk.StringVar(value="Merhaba 👋!")
        self.tooltip_bg_color = tk.StringVar(value="black")
        self.tooltip_text_color = tk.StringVar(value="white")
        self.tooltip_font_size = tk.IntVar(value=16)

        # ChatWindow ile ilgili değişkenler
        self.cw_show_title_var = tk.BooleanVar(value=True)
        self.cw_title_var = tk.StringVar(value="Knowhy Bot")
        self.cw_title_avatar_var = tk.StringVar(value="https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/svg/google-messages.svg")
        self.cw_show_agent_msg_var = tk.BooleanVar(value=True)
        self.cw_welcome_msg_var = tk.StringVar(value="Merhaba! Bu özel bir karşılama mesajıdır")
        self.cw_error_msg_var = tk.StringVar(value="Bu özel bir hata mesajıdır")
        self.cw_bg_color = tk.StringVar(value="#ffffff")
        self.cw_bg_image = tk.StringVar(value="")  # resim yolu
        self.cw_height_var = tk.IntVar(value=700)
        self.cw_width_var = tk.IntVar(value=400)
        self.cw_font_size_var = tk.IntVar(value=16)
        self.cw_starter_prompt_size_var = tk.IntVar(value=15)
        self.cw_clear_on_reload_var = tk.BooleanVar(value=False)

        # Bot Mesaj
        self.bot_bg_color = tk.StringVar(value="#f7f8ff")
        self.bot_text_color = tk.StringVar(value="#303235")
        self.bot_show_avatar_var = tk.BooleanVar(value=True)
        self.bot_avatar_src = tk.StringVar(value="https://raw.githubusercontent.com/zahidkhawaja/langchain-chat-nextjs/main/public/parroticon.png")

        # Kullanıcı Mesaj
        self.user_bg_color = tk.StringVar(value="#3B81F6")
        self.user_text_color = tk.StringVar(value="#ffffff")
        self.user_show_avatar_var = tk.BooleanVar(value=True)
        self.user_avatar_src = tk.StringVar(value="https://raw.githubusercontent.com/zahidkhawaja/langchain-chat-nextjs/main/public/usericon.png")

        # Metin giriş alanı (TextInput)
        self.text_placeholder_var = tk.StringVar(value="Sorunuzu yazın")
        self.text_bg_color = tk.StringVar(value="#ffffff")
        self.text_color = tk.StringVar(value="#303235")
        self.text_send_btn_color = tk.StringVar(value="#3B81F6")
        self.text_max_chars_var = tk.IntVar(value=50)
        self.text_max_chars_warning_var = tk.StringVar(value="Karakter sınırını aştınız. Lütfen 50 karakterden az girin.")
        self.text_auto_focus_var = tk.BooleanVar(value=True)
        self.text_send_sound_var = tk.BooleanVar(value=True)
        self.text_receive_sound_var = tk.BooleanVar(value=True)

        # Geri bildirim
        self.feedback_color_var = tk.StringVar(value="#303235")

        # Footer
        self.footer_text_var = tk.StringVar(value="Geliştiren")
        self.footer_company_var = tk.StringVar(value="Knowhy")
        self.footer_company_link_var = tk.StringVar(value="https://knowhy.co")

        # Link çevirici penceresi için değişken
        self.converter_window = None

        # AI client
        self.ai_client = anthropic.Anthropic(
            api_key="---"
        )

        # Arayüzü kur
        self.create_interface()

    def create_interface(self):
        """
        Tkinter arayüzünün ana yapısı. Dikey olarak parametrelerin
        belirlenebileceği sekmeler/tabs (Notebook) kullanıyoruz.
        """
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, pady=10, padx=10)

        # 1. Genel Ayarlar Sekmesi
        frame_general = ttk.Frame(notebook)
        notebook.add(frame_general, text="Genel Ayarlar")
        self.general_settings_ui(frame_general)

        # 2. Tema - Buton Ayarları
        frame_button = ttk.Frame(notebook)
        notebook.add(frame_button, text="Buton Ayarları")
        self.button_settings_ui(frame_button)

        # 3. Tooltip Ayarları
        frame_tooltip = ttk.Frame(notebook)
        notebook.add(frame_tooltip, text="Tooltip Ayarları")
        self.tooltip_settings_ui(frame_tooltip)

        # 4. ChatWindow Ayarları
        frame_cw = ttk.Frame(notebook)
        notebook.add(frame_cw, text="ChatWindow Ayarları")
        self.chatwindow_settings_ui(frame_cw)

        # 5. Mesaj Ayarları (Bot & Kullanıcı)
        frame_messages = ttk.Frame(notebook)
        notebook.add(frame_messages, text="Mesaj Ayarları")
        self.message_settings_ui(frame_messages)

        # 6. Footer & Kod Oluştur
        frame_footer = ttk.Frame(notebook)
        notebook.add(frame_footer, text="Footer & Kod")
        self.footer_and_code_ui(frame_footer)

    def general_settings_ui(self, parent):
        # Chatflow ID
        tk.Label(parent, text="Chatflow ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(parent, textvariable=self.chatflowid_var, width=40).grid(row=0, column=1, padx=5, pady=5)

        # API Host
        tk.Label(parent, text="API Host:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(parent, textvariable=self.apiHost_var, width=40).grid(row=1, column=1, padx=5, pady=5)

        # topK
        tk.Label(parent, text="topK (isteğe bağlı):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(parent, textvariable=self.topK_var, width=40).grid(row=2, column=1, padx=5, pady=5)

    def button_settings_ui(self, parent):
        # Buton Arkaplan Rengi
        tk.Label(parent, text="Buton Rengi:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.btn_bg_color, width=20).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(parent, text="Renk Seç", command=lambda: self.choose_color(self.btn_bg_color)).grid(row=0, column=2, padx=5, pady=5)

        # Icon Rengi
        tk.Label(parent, text="Ikon Rengi:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.btn_icon_color, width=20).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(parent, text="Renk Seç", command=lambda: self.choose_color(self.btn_icon_color)).grid(row=1, column=2, padx=5, pady=5)

        # Icon URL
        tk.Label(parent, text="Icon URL:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.btn_icon_src, width=40).grid(row=2, column=1, padx=5, pady=5, columnspan=2)
        tk.Button(parent, text="Resim Dönüştürücüyü Aç", command=self.open_link_converter).grid(row=2, column=3, padx=5, pady=5)

        # Right / Bottom
        tk.Label(parent, text="Sağdan Mesafe:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.btn_right_var, width=10).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        tk.Label(parent, text="Alttan Mesafe:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.btn_bottom_var, width=10).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Boyut
        tk.Label(parent, text="Buton Boyutu:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.btn_size_var, width=10).grid(row=5, column=1, sticky="w", padx=5, pady=5)

        # Sürükle Bırak
        tk.Checkbutton(parent, text="Drag & Drop (Sürüklenebilir)", variable=self.btn_dragdrop_var).grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Otomatik Açılma
        tk.Checkbutton(parent, text="Otomatik Açılma", variable=self.btn_auto_open_var).grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Açılma Gecikmesi
        tk.Label(parent, text="Açılma Gecikmesi (sn):").grid(row=8, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.btn_open_delay_var, width=10).grid(row=8, column=1, sticky="w", padx=5, pady=5)

        # Mobilde Otomatik Açılma
        tk.Checkbutton(parent, text="Mobilde Otomatik Açma", variable=self.btn_auto_open_mobile_var).grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    def tooltip_settings_ui(self, parent):
        tk.Checkbutton(parent, text="Tooltip Gösterilsin mi?", variable=self.tooltip_show_var).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(parent, text="Tooltip Mesajı:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.tooltip_msg_var, width=40).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Tooltip Arkaplan Rengi:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.tooltip_bg_color, width=20).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(parent, text="Renk Seç", command=lambda: self.choose_color(self.tooltip_bg_color)).grid(row=2, column=2, padx=5, pady=5)

        tk.Label(parent, text="Tooltip Yazı Rengi:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.tooltip_text_color, width=20).grid(row=3, column=1, padx=5, pady=5)
        tk.Button(parent, text="Renk Seç", command=lambda: self.choose_color(self.tooltip_text_color)).grid(row=3, column=2, padx=5, pady=5)

        tk.Label(parent, text="Tooltip Yazı Boyutu:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.tooltip_font_size, width=10).grid(row=4, column=1, sticky="w", padx=5, pady=5)

    def chatwindow_settings_ui(self, parent):
        # Başlık
        tk.Checkbutton(parent, text="Sohbet Penceresi Başlığı Göster", variable=self.cw_show_title_var).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(parent, text="Başlık:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.cw_title_var, width=40).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Başlık Avatar URL:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.cw_title_avatar_var, width=40).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(parent, text="Resim Dönüştürücüyü Aç", command=self.open_link_converter).grid(row=2, column=2, padx=5, pady=5)

        tk.Checkbutton(parent, text="Agent (Bot) Mesajlarını Göster", variable=self.cw_show_agent_msg_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(parent, text="Hoşgeldin Mesajı:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.cw_welcome_msg_var, width=40).grid(row=4, column=1, padx=5, pady=5)

        tk.Label(parent, text="Hata Mesajı:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.cw_error_msg_var, width=40).grid(row=5, column=1, padx=5, pady=5)

        tk.Label(parent, text="Arkaplan Rengi:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.cw_bg_color, width=20).grid(row=6, column=1, padx=5, pady=5)
        tk.Button(parent, text="Renk Seç", command=lambda: self.choose_color(self.cw_bg_color)).grid(row=6, column=2, padx=5, pady=5)

        tk.Label(parent, text="Arkaplan Resmi:").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.cw_bg_image, width=40).grid(row=7, column=1, padx=5, pady=5)
        tk.Button(parent, text="Dosya Seç", command=lambda: self.choose_file(self.cw_bg_image)).grid(row=7, column=2, padx=5, pady=5)

        tk.Label(parent, text="Yükseklik (px):").grid(row=8, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.cw_height_var, width=10).grid(row=8, column=1, sticky="w", padx=5, pady=5)

        tk.Label(parent, text="Genişlik (px):").grid(row=9, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.cw_width_var, width=10).grid(row=9, column=1, sticky="w", padx=5, pady=5)

        tk.Label(parent, text="Yazı Boyutu:").grid(row=10, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.cw_font_size_var, width=10).grid(row=10, column=1, sticky="w", padx=5, pady=5)

        tk.Label(parent, text="Starter Prompt Yazı Boyutu:").grid(row=11, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.cw_starter_prompt_size_var, width=10).grid(row=11, column=1, sticky="w", padx=5, pady=5)

        tk.Checkbutton(parent, text="Sayfa Yenilendiğinde Sohbeti Temizle", variable=self.cw_clear_on_reload_var).grid(row=12, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    def message_settings_ui(self, parent):
        # Bot Mesaj Ayarları
        lbl_frame_bot = ttk.LabelFrame(parent, text="Bot Mesaj Ayarları")
        lbl_frame_bot.pack(fill="x", padx=5, pady=5)

        tk.Label(lbl_frame_bot, text="Arkaplan Rengi:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lbl_frame_bot, textvariable=self.bot_bg_color, width=20).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(lbl_frame_bot, text="Renk Seç", command=lambda: self.choose_color(self.bot_bg_color)).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(lbl_frame_bot, text="Yazı Rengi:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lbl_frame_bot, textvariable=self.bot_text_color, width=20).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(lbl_frame_bot, text="Renk Seç", command=lambda: self.choose_color(self.bot_text_color)).grid(row=1, column=2, padx=5, pady=5)

        tk.Checkbutton(lbl_frame_bot, text="Avatar Göster", variable=self.bot_show_avatar_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(lbl_frame_bot, text="Avatar URL:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lbl_frame_bot, textvariable=self.bot_avatar_src, width=40).grid(row=3, column=1, padx=5, pady=5, columnspan=2)
        tk.Button(lbl_frame_bot, text="Resim Dönüştürücüyü Aç", command=self.open_link_converter).grid(row=3, column=3, padx=5, pady=5)

        # Kullanıcı Mesaj Ayarları
        lbl_frame_user = ttk.LabelFrame(parent, text="Kullanıcı Mesaj Ayarları")
        lbl_frame_user.pack(fill="x", padx=5, pady=5)

        tk.Label(lbl_frame_user, text="Arkaplan Rengi:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lbl_frame_user, textvariable=self.user_bg_color, width=20).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(lbl_frame_user, text="Renk Seç", command=lambda: self.choose_color(self.user_bg_color)).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(lbl_frame_user, text="Yazı Rengi:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lbl_frame_user, textvariable=self.user_text_color, width=20).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(lbl_frame_user, text="Renk Seç", command=lambda: self.choose_color(self.user_text_color)).grid(row=1, column=2, padx=5, pady=5)

        tk.Checkbutton(lbl_frame_user, text="Avatar Göster", variable=self.user_show_avatar_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(lbl_frame_user, text="Avatar URL:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lbl_frame_user, textvariable=self.user_avatar_src, width=40).grid(row=3, column=1, padx=5, pady=5, columnspan=2)
        tk.Button(lbl_frame_user, text="Resim Dönüştürücüyü Aç", command=self.open_link_converter).grid(row=3, column=3, padx=5, pady=5)

        # Metin Girişi Ayarları
        lbl_frame_text = ttk.LabelFrame(parent, text="Metin Girişi (TextInput) Ayarları")
        lbl_frame_text.pack(fill="x", padx=5, pady=5)

        tk.Label(lbl_frame_text, text="Placeholder:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lbl_frame_text, textvariable=self.text_placeholder_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(lbl_frame_text, text="Arkaplan Rengi:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lbl_frame_text, textvariable=self.text_bg_color, width=20).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(lbl_frame_text, text="Renk Seç", command=lambda: self.choose_color(self.text_bg_color)).grid(row=1, column=2, padx=5, pady=5)

        tk.Label(lbl_frame_text, text="Yazı Rengi:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lbl_frame_text, textvariable=self.text_color, width=20).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(lbl_frame_text, text="Renk Seç", command=lambda: self.choose_color(self.text_color)).grid(row=2, column=2, padx=5, pady=5)

        tk.Label(lbl_frame_text, text="Gönder Buton Rengi:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lbl_frame_text, textvariable=self.text_send_btn_color, width=20).grid(row=3, column=1, padx=5, pady=5)
        tk.Button(lbl_frame_text, text="Renk Seç", command=lambda: self.choose_color(self.text_send_btn_color)).grid(row=3, column=2, padx=5, pady=5)

        tk.Label(lbl_frame_text, text="Maks. Karakter:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lbl_frame_text, textvariable=self.text_max_chars_var, width=10).grid(row=4, column=1, sticky="w", padx=5, pady=5)

        tk.Label(lbl_frame_text, text="Aşma Uyarı Mesajı:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(lbl_frame_text, textvariable=self.text_max_chars_warning_var, width=45).grid(row=5, column=1, padx=5, pady=5, columnspan=2)

        tk.Checkbutton(lbl_frame_text, text="Otomatik Odaklanma (autoFocus)", variable=self.text_auto_focus_var).grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        tk.Checkbutton(lbl_frame_text, text="Mesaj Gönderirken Ses Oynat", variable=self.text_send_sound_var).grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        tk.Checkbutton(lbl_frame_text, text="Mesaj Alırken Ses Oynat", variable=self.text_receive_sound_var).grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    def footer_and_code_ui(self, parent):
        # Geri Bildirim Rengi
        tk.Label(parent, text="Geri Bildirim Rengi:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.feedback_color_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(parent, text="Renk Seç", command=lambda: self.choose_color(self.feedback_color_var)).grid(row=0, column=2, padx=5, pady=5)

        # Footer
        tk.Label(parent, text="Footer Yazısı:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.footer_text_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Footer Şirket Adı:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.footer_company_var, width=30).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(parent, text="Footer Şirket Linki:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(parent, textvariable=self.footer_company_link_var, width=30).grid(row=3, column=1, padx=5, pady=5)

        # Kod görüntüleme alanı
        self.code_text = tk.Text(parent, height=10, wrap="word")
        self.code_text.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # Butonlar için frame
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=5)

        # Kod oluştur düğmesi
        generate_btn = tk.Button(btn_frame, text="Kod Oluştur", command=self.generate_code)
        generate_btn.pack(side="left", padx=5)

        # Kodu kopyalama düğmesi
        copy_btn = tk.Button(btn_frame, text="Kopyala", command=self.copy_code)
        copy_btn.pack(side="left", padx=5)

        # Önizleme butonu
        preview_btn = tk.Button(btn_frame, text="Önizle", command=self.show_preview)
        preview_btn.pack(side="left", padx=5)

        # AI'ya yaptır butonu
        ai_btn = tk.Button(btn_frame, text="AI'ya Yaptır", command=self.show_ai_prompt)
        ai_btn.pack(side="left", padx=5)

        # Link açma
        open_link_btn = tk.Button(btn_frame, text="knowhy.co'yu Ziyaret Et", command=self.open_link)
        open_link_btn.pack(side="left", padx=5)

        parent.rowconfigure(4, weight=1)  # Text alanı genişleyebilsin

    def open_link(self):
        webbrowser.open(self.footer_company_link_var.get() or "https://knowhy.co")

    def open_link_converter(self):
        """Link çevirici penceresini açar"""
        if self.converter_window is None or not tk.Toplevel.winfo_exists(self.converter_window):
            self.converter_window = tk.Toplevel(self.root)
            GitHubRawConverter(self.converter_window)
        else:
            self.converter_window.lift()

    def choose_color(self, var):
        color_code = colorchooser.askcolor(title="Renk Seç")
        if color_code[1] is not None:
            var.set(color_code[1])

    def choose_file(self, var):
        file_path = filedialog.askopenfilename(title="Resim Dosyası Seç", filetypes=[("Resim Dosyaları", "*.png *.jpg *.jpeg *.gif"), ("Tümü", "*.*")])
        if file_path:
            var.set(file_path)

    def generate_code(self):
        """
        Tüm değişken değerlerini çekip nihai <script> kodunu derleyip
        code_text alanında görüntüler.
        """
        # Eğer topK boş ise, // topK: X satırı yorumsuz kalabilir. Boş değilse ekleyelim
        topK_line = ""
        if self.topK_var.get().strip():
            topK_line = f"        // topK: {self.topK_var.get()}"

        # <script> metnini oluştur
        script_code = f"""<script type="module">
    import Chatbot from "https://cdn.jsdelivr.net/gh/knowhyco/KnowhyEmbed/dist/web.js"
    Chatbot.init({{
        chatflowid: "{self.chatflowid_var.get()}",
        apiHost: "{self.apiHost_var.get()}",
        chatflowConfig: {{
{topK_line}
        }},
        theme: {{
            button: {{
                backgroundColor: "{self.btn_bg_color.get()}",
                right: {self.btn_right_var.get()},
                bottom: {self.btn_bottom_var.get()},
                size: {self.btn_size_var.get()},
                dragAndDrop: {str(self.btn_dragdrop_var.get()).lower()},
                iconColor: "{self.btn_icon_color.get()}",
                customIconSrc: "{self.btn_icon_src.get()}",
                autoWindowOpen: {{
                    autoOpen: {str(self.btn_auto_open_var.get()).lower()},
                    openDelay: {self.btn_open_delay_var.get()},
                    autoOpenOnMobile: {str(self.btn_auto_open_mobile_var.get()).lower()},
                }},
            }},
            tooltip: {{
                showTooltip: {str(self.tooltip_show_var.get()).lower()},
                tooltipMessage: '{self.tooltip_msg_var.get()}',
                tooltipBackgroundColor: '{self.tooltip_bg_color.get()}',
                tooltipTextColor: '{self.tooltip_text_color.get()}',
                tooltipFontSize: {self.tooltip_font_size.get()},
            }},
            chatWindow: {{
                showTitle: {str(self.cw_show_title_var.get()).lower()},
                title: '{self.cw_title_var.get()}',
                titleAvatarSrc: '{self.cw_title_avatar_var.get()}',
                showAgentMessages: {str(self.cw_show_agent_msg_var.get()).lower()},
                welcomeMessage: '{self.cw_welcome_msg_var.get()}',
                errorMessage: '{self.cw_error_msg_var.get()}',
                backgroundColor: "{self.cw_bg_color.get()}",
                backgroundImage: '{self.cw_bg_image.get()}',
                height: {self.cw_height_var.get()},
                width: {self.cw_width_var.get()},
                fontSize: {self.cw_font_size_var.get()},
                starterPromptFontSize: {self.cw_starter_prompt_size_var.get()},
                clearChatOnReload: {str(self.cw_clear_on_reload_var.get()).lower()},
                botMessage: {{
                    backgroundColor: "{self.bot_bg_color.get()}",
                    textColor: "{self.bot_text_color.get()}",
                    showAvatar: {str(self.bot_show_avatar_var.get()).lower()},
                    avatarSrc: "{self.bot_avatar_src.get()}",
                }},
                userMessage: {{
                    backgroundColor: "{self.user_bg_color.get()}",
                    textColor: "{self.user_text_color.get()}",
                    showAvatar: {str(self.user_show_avatar_var.get()).lower()},
                    avatarSrc: "{self.user_avatar_src.get()}",
                }},
                textInput: {{
                    placeholder: '{self.text_placeholder_var.get()}',
                    backgroundColor: '{self.text_bg_color.get()}',
                    textColor: '{self.text_color.get()}',
                    sendButtonColor: '{self.text_send_btn_color.get()}',
                    maxChars: {self.text_max_chars_var.get()},
                    maxCharsWarningMessage: '{self.text_max_chars_warning_var.get()}',
                    autoFocus: {str(self.text_auto_focus_var.get()).lower()},
                    sendMessageSound: {str(self.text_send_sound_var.get()).lower()},
                    receiveMessageSound: {str(self.text_receive_sound_var.get()).lower()},
                }},
                feedback: {{
                    color: '{self.feedback_color_var.get()}',
                }},
                footer: {{
                    textColor: '#303235',
                    text: '{self.footer_text_var.get()}',
                    company: '{self.footer_company_var.get()}',
                    companyLink: '{self.footer_company_link_var.get()}',
                }}
            }}
        }}
    }})
</script>"""

        # Mevcut metin temizle ve yeni kodu yerleştir
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert(tk.END, script_code)

    def copy_code(self):
        """Kodu panoya kopyalar."""
        code = self.code_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        messagebox.showinfo("Kopyalandı", "Kod panoya kopyalandı!")

    def show_ai_prompt(self):
        """AI prompt penceresini açar"""
        AIPromptWindow(self.root, self.send_to_ai)
    
    def send_to_ai(self, prompt):
        """Promptu AI'ya gönderir ve yanıtı gösterir"""
        try:
            # Mevcut kodu al
            self.generate_code()  # Kodu güncelle
            current_code = self.code_text.get("1.0", "end-1c")
            
            # Promptu ve kodu birleştir
            full_prompt = f"{prompt}\n\nMevcut kod:\n```javascript\n{current_code}\n```"
            
            # AI'ya gönder
            message = self.ai_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            # Yanıtı göster
            response_text = message.content[0].text if isinstance(message.content, list) else message.content
            AIResponseWindow(self.root, response_text)
            
        except Exception as e:
            messagebox.showerror("Hata", f"AI yanıtı alınırken bir hata oluştu: {str(e)}")

    def show_preview(self):
        """Önizleme penceresini açar"""
        try:
            # Önce kodu güncelle
            self.generate_code()
            current_code = self.code_text.get("1.0", "end-1c")
            
            # Önizleme penceresini aç
            PreviewWindow(self.root, current_code)
        except Exception as e:
            messagebox.showerror("Hata", f"Önizleme oluşturulurken bir hata oluştu: {str(e)}")


def main():
    root = tk.Tk()
    app = ChatbotCustomizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
