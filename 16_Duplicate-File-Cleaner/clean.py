import customtkinter as ctk
import os
import hashlib
from collections import defaultdict
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class FileCleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("โปรแกรมลบไฟล์ซ้ำ")
        self.geometry("800x600")
        
        self.duplicates = {}
        self.checkboxes = {}
        self.checked_files = []

        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(main_frame, text="โปรแกรมค้นหาไฟล์ซ้ำ", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)

        folder_frame = ctk.CTkFrame(main_frame)
        folder_frame.pack(pady=10, fill="x")
        ctk.CTkLabel(folder_frame, text="เลือกโฟลเดอร์:", font=ctk.CTkFont(size=14)).pack(side="left", padx=10, pady=5)
        
        self.folder_path_label = ctk.CTkLabel(folder_frame, text="ยังไม่ได้เลือกโฟลเดอร์", font=ctk.CTkFont(size=12))
        self.folder_path_label.pack(side="left", padx=10, pady=5, expand=True, fill="x")
        
        browse_button = ctk.CTkButton(folder_frame, text="เรียกดู...", command=self.browse_folder)
        browse_button.pack(side="right", padx=10, pady=5)
        
        self.scan_button = ctk.CTkButton(main_frame, text="เริ่มสแกน", command=self.start_scan)
        self.scan_button.pack(pady=10)

        self.result_frame = ctk.CTkFrame(main_frame)
        self.result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self.result_frame)
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        delete_frame = ctk.CTkFrame(main_frame)
        delete_frame.pack(pady=10, fill="x")
        
        self.status_label = ctk.CTkLabel(delete_frame, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=10, pady=5, expand=True)
        
        delete_button = ctk.CTkButton(delete_frame, text="ลบไฟล์ที่เลือก", command=self.delete_duplicates, fg_color="red", hover_color="#c43b3b")
        delete_button.pack(side="right", padx=10, pady=5)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_label.configure(text=folder_selected)
            self.clear_results()

    def start_scan(self):
        folder_path = self.folder_path_label.cget("text")
        if not os.path.isdir(folder_path):
            messagebox.showerror("ข้อผิดพลาด", "กรุณาเลือกโฟลเดอร์ที่ถูกต้อง")
            return

        self.clear_results()
        self.status_label.configure(text="กำลังสแกน... กรุณารอสักครู่")
        self.update_idletasks()
        
        self.duplicates = self.find_duplicates(folder_path)
        
        if not self.duplicates:
            self.status_label.configure(text="ไม่พบไฟล์ซ้ำในโฟลเดอร์นี้")
        else:
            self.display_duplicates()
            self.status_label.configure(text=f"พบ {len(self.duplicates)} กลุ่มไฟล์ซ้ำ")

    def clear_results(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.checked_files = []
        self.checkboxes = {}

    def display_duplicates(self):
        for i, (file_hash, file_paths) in enumerate(self.duplicates.items()):
            group_label = ctk.CTkLabel(self.scrollable_frame, text=f"กลุ่มที่ {i+1} (Hash: {file_hash[:8]})", font=ctk.CTkFont(size=14, weight="bold"))
            group_label.pack(anchor="w", pady=(10, 5))
            
            for path in file_paths:
                checkbox = ctk.CTkCheckBox(self.scrollable_frame, text=os.path.basename(path), font=ctk.CTkFont(size=12), command=lambda p=path: self.toggle_file_selection(p))
                checkbox.pack(anchor="w", padx=20)
                self.checkboxes[path] = checkbox
    
    def toggle_file_selection(self, file_path):
        if file_path in self.checked_files:
            self.checked_files.remove(file_path)
        else:
            self.checked_files.append(file_path)

    def delete_duplicates(self):
        if not self.checked_files:
            messagebox.showinfo("แจ้งเตือน", "กรุณาเลือกไฟล์ที่ต้องการลบ")
            return

        if not messagebox.askyesno("ยืนยันการลบ", f"คุณต้องการลบ {len(self.checked_files)} ไฟล์นี้ใช่หรือไม่? การกระทำนี้ไม่สามารถย้อนกลับได้"):
            return

        deleted_count = 0
        failed_deletes = []
        for file_path in self.checked_files:
            try:
                os.remove(file_path)
                deleted_count += 1
            except OSError as e:
                failed_deletes.append(file_path)
                print(f"ข้อผิดพลาดในการลบไฟล์ {file_path}: {e}")
        
        if failed_deletes:
            messagebox.showerror("ลบไม่สำเร็จ", f"ไม่สามารถลบไฟล์บางส่วนได้: {len(failed_deletes)} ไฟล์\n\nโปรดตรวจสอบสิทธิ์การเข้าถึง")
        
        messagebox.showinfo("เสร็จสิ้น", f"ลบไฟล์ไปแล้ว {deleted_count} ไฟล์")
        self.start_scan()
        
    def find_duplicates(self, folder_path):
        files_by_size = defaultdict(list)
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if not os.path.exists(file_path) or not os.path.getsize(file_path) > 0:
                    continue
                files_by_size[os.path.getsize(file_path)].append(file_path)

        duplicates = defaultdict(list)
        for size, files in files_by_size.items():
            if len(files) > 1:
                for file_path in files:
                    file_hash = self.hash_file(file_path)
                    if file_hash:
                        duplicates[file_hash].append(file_path)
        
        final_duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
        return final_duplicates

    def hash_file(self, file_path, block_size=65536):
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                buf = f.read(block_size)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = f.read(block_size)
            return hasher.hexdigest()
        except (IOError, PermissionError):
            return None

if __name__ == "__main__":
    app = FileCleanerApp()
    app.mainloop()
