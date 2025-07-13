import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
from skimage.transform import hough_line, hough_line_peaks
from skimage import io, color, exposure
import sqlite3

def create_database():
    conn = sqlite3.connect('hasta_veritabani.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hasta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT NOT NULL,
            soyad TEXT NOT NULL
        )
    ''')


    sample_patients = [
        ("Ahmet", "Yılmaz"),
        ("Mehmet", "Demir"),
        ("Ayşe", "Kara"),
        ("Fatma", "Çelik"),
        ("Ali", "Koç")
    ]


    for ad, soyad in sample_patients:
        cursor.execute("SELECT * FROM hasta WHERE ad=? AND soyad=?", (ad, soyad))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO hasta (ad, soyad) VALUES (?, ?)", (ad, soyad))

    conn.commit()
    conn.close()

create_database()

class SkolyozKlinikApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Skolyoz Klinik")
        self.root.geometry("900x900")
        self.root.configure(bg="#f3f4f6")

        self.frames = {}
        self.current_frame = None


        self.frames["MainPage"] = MainPage(self)
        self.frames["HastaEklePage"] = HastaEklePage(self)
        self.frames["HastaBilgileriPage"] = HastaBilgileriPage(self)
        self.frames["SkolyozAnaliziPage"] = SkolyozAnaliziPage(self)
        self.show_frame("MainPage")

    def show_frame(self, frame_name):
        if self.current_frame is not None:
            self.current_frame.pack_forget()
        self.current_frame = self.frames[frame_name]
        self.current_frame.pack(fill="both", expand=True)


class MainPage(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller.root, bg="white")
        self.controller = controller

        title_label = tk.Label(self, text="Skolyoz Klinik Uygulaması", font=("Arial", 20, "bold"), bg="white")
        title_label.pack(pady=10)

        date_label = tk.Label(self, text="25 Kasım 2024", font=("Arial", 14), bg="white")
        date_label.pack(pady=5)

        image_label = tk.Label(self, text="🦴", font=("Arial", 60), bg="white")
        image_label.pack(pady=10)

        entry_frame = tk.Frame(self, bg="white", bd=1, relief="solid")
        entry_frame.pack(pady=10, padx=20, fill="x")

        name_label = tk.Label(entry_frame, text="Hasta Ad:", bg="white", font=("Arial", 10))
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.name_entry = tk.Entry(entry_frame, font=("Arial", 10), width=30)
        self.name_entry.grid(row=1, column=0, padx=10, pady=5)

        surname_label = tk.Label(entry_frame, text="Hasta Soyad:", bg="white", font=("Arial", 10))
        surname_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.surname_entry = tk.Entry(entry_frame, font=("Arial", 10), width=30)
        self .surname_entry.grid(row=3, column=0, padx=10, pady=5)

        visit_button = tk.Button(entry_frame, text="Hastaya Git", bg="#e5e7eb", fg="#111827", font=("Arial", 10),
                                 width=20, command=self.hastaya_git)
        visit_button.grid(row=4, column=0, padx=10, pady=5)

        add_button = tk.Button(entry_frame, text="Yeni Hasta Ekle", bg="#e5e7eb", fg="#111827", font=("Arial", 10),
                               width=20, command=lambda: controller.show_frame("HastaEklePage"))
        add_button.grid(row=5, column=0, padx=10, pady=5)

    def hastaya_git(self):
        hasta_adi = self.name_entry.get()
        hasta_soyadi = self.surname_entry.get()

        if not hasta_adi or not hasta_soyadi:
            messagebox.showwarning("Uyarı", "Lütfen hasta adını ve soyadını girin.")
            return

        if self.check_patient_in_database(hasta_adi, hasta_soyadi):
            self.controller.frames["HastaBilgileriPage"].show_info(hasta_adi, hasta_soyadi)
            self.controller.show_frame("HastaBilgileriPage")
        else:
            messagebox.showinfo("Bilgi", "Hasta veritabanında kayıtlı değil. Lütfen yeni hasta ekleyin.")

    def check_patient_in_database(self, ad, soyad):
        conn = sqlite3.connect('hasta_veritabani.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hasta WHERE ad=? AND soyad=?", (ad, soyad))
        result = cursor.fetchone()
        conn.close()
        return result is not None


class HastaBilgileriPage(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller.root, bg="white")
        self.controller = controller

        title_label = tk.Label(self, text="Hasta Bilgileri", font=("Arial", 18, "bold"), bg="white")
        title_label.pack(pady=10)

        self.hasta_ad_label = tk.Label(self, text="", font=("Arial", 14), bg="white")
        self.hasta_ad_label.pack(pady=5)

        self.hasta_soyad_label = tk.Label(self, text="", font=("Arial", 14), bg="white")
        self.hasta_soyad_label.pack(pady=5)

        upload_button = tk.Button(self, text="Görsel Yükle", command=self.upload_image)
        upload_button.pack(pady=10)

        result_label = tk.Label(self, text="Tahmin Sonucu:", font=("Arial", 14), bg="white")
        result_label.pack(pady=10)

        self.tahmin_sonucu_label = tk.Label(self, text="", font=("Arial", 14, "bold"), bg="white")
        self.tahmin_sonucu_label.pack()

        back_button = tk.Button(self, text="Geri Dön", command=lambda: self.controller.show_frame("MainPage"))
        back_button.pack(pady=10)

    def show_info(self, hasta_adi, hasta_soyadi):
        self.hasta_ad_label.config(text=f"Hasta Adı: {hasta_adi}")
        self.hasta_soyad_label.config(text=f"Hasta Soyadı: {hasta_soyadi}")

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="Bir Görsel Seçin",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )

        if file_path:
            image = io.imread(file_path)

            if image.shape[-1] == 4:
                image = image[:, :, :3]

            gray_image = color.rgb2gray(image)
            gray_image = exposure.equalize_hist(gray_image)
            gray_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

            edges = self.detect_edges(gray_image)
            cobb_angle = self.calculate_cobb_angle(edges)

            if cobb_angle is not None:
                self.tahmin_sonucu_label.config(text=f"Cobb Açısı: {cobb_angle:.2f}°")
                self.controller.frames["SkolyozAnaliziPage"].update_cobb_angle(cobb_angle)
            else:
                self.tahmin_sonucu_label.config(text="Cobb açısı hesaplanamadı.")

    def detect_edges(self, gray_image):
        low_threshold = 50
        high_threshold = 150
        edges = cv2.Canny((gray_image * 255).astype(np.uint8), low_threshold, high_threshold)
        return edges

    def calculate_cobb_angle(self, edges):
        try:
            hough_lines = self.detect_lines_using_hough_transform(edges)

            if not hough_lines or len(hough_lines[1]) == 0:
                return None

            angles = hough_lines[1] * 180 / np.pi
            filtered_angles = [angle for angle in angles if abs(angle) > 10]
            if len(filtered_angles) < 2:
                return None

            positive_angles = [angle for angle in filtered_angles if angle > 0]
            negative_angles = [angle for angle in filtered_angles if angle < 0]

            max_positive_angle = max(positive_angles, default=None)
            max_negative_angle = min(negative_angles, default=None)

            if max_positive_angle is not None and max_negative_angle is not None:
                cobb_angle = max_positive_angle - abs(max_negative_angle)
                return cobb_angle

            return None

        except Exception as e:
            print(f"Hata: Cobb açısı hesaplama sırasında bir hata oluştu: {e}")
            return None

    def detect_lines_using_hough_transform(self, edges):
        try:
            h, theta, d = hough_line(edges)
            hough_lines = list(hough_line_peaks(h, theta, d))
            return hough_lines
        except Exception as e:
            print(f"Hough dönüşümü hatası: {e}")
            return []


class HastaEklePage(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller.root, bg="#f3f4f6")
        self.controller = controller
        self.tomography_image_path = None

        header_frame = tk.Frame(self, bg="white")
        header_frame.pack(pady=10, padx=10, fill='x')

        title_label = tk.Label(header_frame, text="Hasta Kayıt", font=("Arial", 16, "bold"), bg="white")
        title_label.pack(side=tk.LEFT)

        date_label = tk.Label(header_frame, text="Muayene Tarihi: 25.11.2024", font=("Arial", 10), bg="white")
        date_label.pack(side=tk.RIGHT)

        self.create_image_frames()
        self.create_entry_fields()
        self.create_buttons()

    def create_image_frames(self):
        images_frame = tk.Frame(self, bg="white")
        images_frame.pack(pady=10, fill='x', padx=10)

        self.photo_frame = tk.Frame(images_frame, bg="white", bd=2, relief="groove")
        self.photo_frame.pack(side=tk.LEFT, padx=5)

        photo_label = tk.Label(self.photo_frame, text="Hasta Fotoğrafı", bg="white", font=("Arial", 10))
        photo_label.pack()

        self.photo_image_label = tk.Label(self.photo_frame, bg="white", height=10, width=20)
        self.photo_image_label.pack()

        self.tomography_frame = tk.Frame(images_frame, bg="white", bd=2, relief="groove")
        self.tomography_frame.pack(side=tk.LEFT, padx=5)

        tomography_label = tk.Label(self.tomography_frame, text="Tomografi Görüntüsü", bg="white", font=("Arial", 10))
        tomography_label.pack()

        self.tomography_image = tk.Label(self.tomography_frame, bg="white", height=10, width=20)
        self.tomography_image.pack()

    def create_entry_fields(self):
        self.name_entry = tk.Entry(self, font=("Arial", 12), width=30)
        self.name_entry.pack(pady=5, padx=10)
        self.name_entry.insert(0, "İsim")

        self.surname_entry = tk.Entry(self, font=("Arial", 12), width=30)
        self.surname_entry.pack(pady=5, padx=10)
        self.surname_entry.insert(0, "Soyisim")

        self.gender_var = tk.StringVar(value="Erkek")
        gender_frame = tk.Frame(self)
        gender_frame.pack(pady=5)

        male_radio = tk.Radiobutton(gender_frame, text="Erkek", variable=self.gender_var, value="Erkek", bg="white")
        male_radio.pack(side=tk.LEFT)

        female_radio = tk.Radiobutton(gender_frame, text="Kadın", variable=self.gender_var, value="Kadın", bg="white")
        female_radio.pack(side=tk.LEFT)

        self.dob_entry = tk.Entry(self, font=("Arial", 12), width=30)
        self.dob_entry.pack(pady=5, padx=10)
        self.dob_entry.insert(0, "Doğum Tarihi (GG/AA/YYYY)")

        self.info_text = tk.Text(self, height=6, width=30)
        self.info_text.pack(pady=5, padx=10)
        self.info_text.insert(tk.END, " ")

    def create_buttons(self):
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        add_photo_button = tk.Button(button_frame, text="Hasta Fotoğrafı Ekle", bg="#d1d5db", command=self.add_photo)
        add_photo_button.pack(side=tk.LEFT, padx=5)

        add_tomography_button = tk.Button(button_frame, text="Tomografi Görüntüsü Ekle", bg="#d1d5db", command=self.add_tomography)
        add_tomography_button.pack(side=tk.LEFT, padx=5)

        analyze_button = tk.Button(self, text="Skolyoz Analizi Gerçekleştir", bg="#d1d5db", command=self.show_skolyoz_analizi)
        analyze_button.pack(pady=10)

        back_button = tk.Button(self, text="Geri", bg="#d1d5db", command=lambda: self.controller.show_frame("MainPage"))
        back_button.pack(pady=10)

    def add_photo(self):
        file_path = filedialog.askopenfilename(
            title="Bir Fotoğraf Seçin",
            filetypes=[("Image Files", "*.jpg"), ("Image Files", "*.jpeg"), ("Image Files", "*.png")]
        )

        if file_path:
            img = Image.open(file_path)
            img = img.resize((150, 150))
            img_tk = ImageTk.PhotoImage(img)

            self.photo_image_label.config(image=img_tk)
            self.photo_image_label.image = img_tk

            messagebox.showinfo("Bilgi", f"Seçilen fotoğraf: {file_path}")

    def add_tomography(self):
        file_path = filedialog.askopenfilename(
            title="Bir Tomografi Görüntüsü Seçin",
            filetypes=[("DICOM Files", "*.dcm"), ("Image Files", "*.jpg"), ("Image Files", "*.jpeg"),
                       ("Image Files", "*.png")]
        )

        if file_path:
            img = Image.open(file_path)
            img = img.resize((150, 150))
            img_tk = ImageTk.PhotoImage(img)

            self.tomography_image.config(image=img_tk)
            self.tomography_image.image = img_tk

            self.tomography_image_path = file_path  # Store the path for later use
            messagebox.showinfo("Bilgi", f"Seçilen tomografi görüntüsü: {file_path}")

    def show_skolyoz_analizi(self):
        name = self.name_entry.get()
        surname = self.surname_entry.get()
        gender = self.gender_var.get()
        dob = self.dob_entry.get()
        info = self.info_text.get("1.0", tk.END).strip()

        # Perform Cobb angle calculation from the uploaded tomography image
        cobb_angle = self.calculate_cobb_angle_from_images()

        self.controller.frames["SkolyozAnaliziPage"].update_patient_info(
            name,
            surname,
            gender,
            dob,
            info,
            cobb_angle
        )
        self.controller.show_frame("SkolyozAnaliziPage")

    def calculate_cobb_angle_from_images(self):
        if not self.tomography_image_path:
            messagebox.showwarning("Uyarı", "Lütfen bir tomografi görüntüsü yükleyin.")
            return None

        # Load the image
        image = cv2.imread(self.tomography_image_path)
        if image is None:
            messagebox.showerror("Hata", "Görsel yüklenemedi.")
            return None

        # Convert to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur
        blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

        # Edge detection
        edges = cv2.Canny(blurred_image, 50, 150)

        # Hough Transform to detect lines
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)

        if lines is None:
            messagebox.showwarning("Uyarı", "Hiçbir çizgi tespit edilemedi.")
            return None

        # Convert lines from polar to Cartesian coordinates
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta)
            angles.append(angle)

        # Filter angles to find the uppermost and lowermost vertebrae
        upper_angle = max(angles)
        lower_angle = min(angles)

        # Calculate Cobb angle
        cobb_angle = upper_angle - lower_angle

        # Ensure the angle is positive
        if cobb_angle < 0:
            cobb_angle = -cobb_angle

        return cobb_angle

class SkolyozAnaliziPage(tk.Frame):
    def __init__(self, controller):
        super().__init__(controller.root, bg="white")
        self.controller = controller

        title_label = tk.Label(self, text="Skolyoz Analizi", font=("Arial", 20, "bold"), bg="white")
        title_label.pack(pady=10)

        self.hasta_ad_label = tk.Label(self, text="", font=("Arial", 14), bg="white")
        self.hasta_ad_label.pack(pady=5)

        self.hasta_soyad_label = tk.Label(self, text="", font=("Arial", 14), bg="white")
        self.hasta_soyad_label.pack(pady=5)

        self.cinsiyet_label = tk.Label(self, text="", font=("Arial", 14), bg="white")
        self.cinsiyet_label.pack(pady=5)

        self.dob_label = tk.Label(self, text="", font=("Arial", 14), bg="white")
        self.dob_label.pack(pady=5)

        self.info_label = tk.Label(self, text="", font=("Arial", 14), bg="white")
        self.info_label.pack(pady=5)

        self.cobb_acisi_label = tk.Label(self, text="", font=("Arial", 14), bg="white")
        self.cobb_acisi_label.pack(pady=5)

        analysis_results_frame = tk.Frame(self, bg="white")
        analysis_results_frame.pack(pady=10)

        results_label = tk.Label(analysis_results_frame, text="Skolyoz Analiz Sonuçları", font=("Arial", 16, "bold"), bg="white")
        results_label.pack()

        self.results_info = tk.Frame(analysis_results_frame, bg="white")
        self.results_info.pack(pady=5)

        self.durum_label = tk.Label(self.results_info, text="Skolyoz Durumu: [Durum]", bg="white")
        self.durum_label.pack(anchor="w")
        self.egri_label = tk.Label(self.results_info, text="Saptanan Eğrilik(ler): [Eğrilikler]", bg="white")
        self.egri_label.pack(anchor="w")
        self.cobb_label = tk.Label(self.results_info, text="Cobb açı(lar)ı: [Cobb Açıları]", bg="white")
        self.cobb_label.pack(anchor="w")
        self.tur_label = tk.Label(self.results_info, text="Skolyoz türü: [Tür]", bg="white")
        self.tur_label.pack(anchor="w")

        treatment_frame = tk.Frame(self, bg="white")
        treatment_frame.pack(pady=10)

        treatment_label = tk.Label(treatment_frame, text="Önerilen Tedaviler", font=("Arial", 16, "bold"), bg="white")
        treatment_label.pack()

        self.tedavi_label = tk.Label(treatment_frame, text="", bg="white")
        self.tedavi_label.pack(anchor="w")

        back_button = tk.Button(self, text="Geri Dön", command=lambda: self.controller.show_frame("HastaEklePage"))
        back_button.pack(pady=10)

    def update_patient_info(self, name, surname, gender, dob, info, cobb_angle):
        self.hasta_ad_label.config(text=f"Hasta Adı: {name}")
        self.hasta_soyad_label.config(text=f"Hasta Soyadı: {surname}")
        self.cinsiyet_label.config(text=f"Cinsiyet: {gender}")
        self.dob_label.config(text=f"Doğum Tarihi: {dob}")
        self.info_label.config(text=f"Ek Bilgiler: {info}")

        self.cobb_acisi_label.config(text=f"Cobb Açısı: {cobb_angle:.2f}°")

        self.update_analysis_results(cobb_angle)

    def update_analysis_results(self, cobb_angle):
        if cobb_angle is None:
            return

        if cobb_angle < 10:
            durum = "Normal"
            egri = "Yok"
            tedavi = "Gözlem yeterli."
        elif 10 <= cobb_angle < 25:
            durum = "Mild Skolyoz"
            egri = f"{cobb_angle:.2f}°"
            tedavi = "Fizik tedavi önerilir."
        elif 25 <= cobb_angle < 40:
            durum = "Moderate Skolyoz"
            egri = f"{cobb_angle:.2f}°"
            tedavi = "Korse kullanımı önerilir."
        else:
            durum = "Severe Skolyoz"
            egri = f"{cobb_angle:.2f}°"
            tedavi = "Cerrahi müdahale önerilir."

        self.durum_label.config(text=f"Skolyoz Durumu: {durum}")
        self.egri_label.config(text=f"Saptanan Eğrilik(ler): {egri}")
        self.cobb_label.config(text=f"Cobb açı(lar)ı: {cobb_angle:.2f}°")
        self.tur_label.config(text=f"Skolyoz türü: {durum}")
        self.tedavi_label.config(text=f"- {tedavi}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SkolyozKlinikApp(root)
    root.mainloop()


