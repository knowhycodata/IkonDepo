import tkinter as tk
from tkinter import ttk
from urllib.parse import urlparse
import pyperclip

class GitHubRawConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Raw Link Dönüştürücü")
        self.root.geometry("600x300")
        
        # Ana frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Başlık
        title_label = ttk.Label(main_frame, text="GitHub Raw Link Dönüştürücü", font=('Helvetica', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Giriş alanı
        input_label = ttk.Label(main_frame, text="GitHub Linkini Yapıştırın:")
        input_label.grid(row=1, column=0, columnspan=2, pady=(10,5))
        
        self.input_entry = ttk.Entry(main_frame, width=70)
        self.input_entry.grid(row=2, column=0, columnspan=2, pady=(0,10))
        
        # Dönüştür butonu
        convert_button = ttk.Button(main_frame, text="Dönüştür", command=self.convert_link)
        convert_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Sonuç alanı
        result_label = ttk.Label(main_frame, text="Raw Link:")
        result_label.grid(row=4, column=0, columnspan=2, pady=(10,5))
        
        self.result_entry = ttk.Entry(main_frame, width=70)
        self.result_entry.grid(row=5, column=0, columnspan=2)
        
        # Kopyala butonu
        copy_button = ttk.Button(main_frame, text="Kopyala", command=self.copy_result)
        copy_button.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Durum mesajı
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=7, column=0, columnspan=2, pady=5)

    def convert_link(self):
        github_link = self.input_entry.get().strip()
        
        try:
            # Link formatını kontrol et
            if not github_link.startswith("https://github.com"):
                raise ValueError("Geçerli bir GitHub linki değil!")
            
            # URL'yi parçalara ayır
            parsed = urlparse(github_link)
            path_parts = parsed.path.split('/')
            
            # "blob" kontrolü ve değiştirme
            if "blob" in path_parts:
                # Raw URL formatını oluştur
                raw_parts = ["https://raw.githubusercontent.com"]
                raw_parts.extend(path_parts[1:])  # İlk '/' karakterini atla
                raw_parts.remove("blob")  # "blob" kelimesini kaldır
                
                raw_url = '/'.join(raw_parts)
                
                self.result_entry.delete(0, tk.END)
                self.result_entry.insert(0, raw_url)
                self.status_label.config(text="Link başarıyla dönüştürüldü!", foreground="green")
            else:
                raise ValueError("Link 'blob' içermiyor!")
                
        except Exception as e:
            self.status_label.config(text=f"Hata: {str(e)}", foreground="red")
            self.result_entry.delete(0, tk.END)

    def copy_result(self):
        raw_link = self.result_entry.get()
        if raw_link:
            pyperclip.copy(raw_link)
            self.status_label.config(text="Link panoya kopyalandı!", foreground="green")
        else:
            self.status_label.config(text="Kopyalanacak link bulunamadı!", foreground="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubRawConverter(root)
    root.mainloop()
