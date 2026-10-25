import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class GradeCalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("โปรแกรมคำนวณเกรด GPA & GPAX")
        self.geometry("600x700")
        self.gpa_records = []
        
        self.main_scroll_frame = ctk.CTkScrollableFrame(self)
        self.main_scroll_frame.pack(fill="both", expand=True)
        
        self.create_widgets()

    def create_widgets(self):
        gpa_frame = ctk.CTkFrame(self.main_scroll_frame)
        gpa_frame.pack(padx=20, pady=20, fill="x")

        ctk.CTkLabel(gpa_frame, text="คำนวณเกรด GPA รายเทอม", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 20))

        input_frame = ctk.CTkFrame(gpa_frame)
        input_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(input_frame, text="ชื่อวิชา:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.subject_entry = ctk.CTkEntry(input_frame, width=250)
        self.subject_entry.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(input_frame, text="หน่วยกิต:", font=ctk.CTkFont(size=12)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.credit_entry = ctk.CTkEntry(input_frame, width=100)
        self.credit_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(input_frame, text="คะแนนที่ได้รับ (0-100):", font=ctk.CTkFont(size=12)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.score_entry = ctk.CTkEntry(input_frame, width=100)
        self.score_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        add_button = ctk.CTkButton(gpa_frame, text="เพิ่มวิชา", command=self.add_subject, font=ctk.CTkFont(size=12, weight="bold"))
        add_button.pack(pady=(5, 15))

        self.subject_list_frame = ctk.CTkFrame(gpa_frame)
        self.subject_list_frame.pack(fill="x", padx=15, pady=10)

        calc_gpa_button = ctk.CTkButton(gpa_frame, text="คำนวณ GPA เทอมนี้", command=self.calculate_gpa, font=ctk.CTkFont(size=12, weight="bold"))
        calc_gpa_button.pack(pady=(10, 5))

        self.gpa_result_label = ctk.CTkLabel(gpa_frame, text="GPA เทอมนี้: -", font=ctk.CTkFont(size=18, weight="bold"))
        self.gpa_result_label.pack(pady=5)
        
        reset_button = ctk.CTkButton(gpa_frame, text="รีเซ็ต", command=self.reset_gpa_data, fg_color="red", hover_color="#c43b3b", font=ctk.CTkFont(size=12, weight="bold"))
        reset_button.pack(pady=5)

        gpax_frame = ctk.CTkFrame(self.main_scroll_frame)
        gpax_frame.pack(padx=20, pady=20, fill="x")
        
        ctk.CTkLabel(gpax_frame, text="คำนวณเกรด GPAX สะสม", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 20))

        gpax_input_frame = ctk.CTkFrame(gpax_frame)
        gpax_input_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(gpax_input_frame, text="GPA ที่ผ่านมา:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.prev_gpa_entry = ctk.CTkEntry(gpax_input_frame, width=100)
        self.prev_gpa_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(gpax_input_frame, text="หน่วยกิตสะสมที่ผ่านมา:", font=ctk.CTkFont(size=12)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.prev_credit_entry = ctk.CTkEntry(gpax_input_frame, width=100)
        self.prev_credit_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        calc_gpax_button = ctk.CTkButton(gpax_frame, text="คำนวณ GPAX", command=self.calculate_gpax, font=ctk.CTkFont(size=12, weight="bold"))
        calc_gpax_button.pack(pady=(5, 10))

        self.gpax_result_label = ctk.CTkLabel(gpax_frame, text="GPAX สะสม: -", font=ctk.CTkFont(size=18, weight="bold"))
        self.gpax_result_label.pack(pady=5)

    def add_subject(self):
        try:
            subject = self.subject_entry.get().strip()
            credit = float(self.credit_entry.get())
            score = float(self.score_entry.get())

            if not subject:
                messagebox.showerror("ข้อผิดพลาด", "กรุณาใส่ชื่อวิชา")
                return
            if not (0 <= score <= 100) or credit <= 0:
                messagebox.showerror("ข้อผิดพลาด", "กรุณาใส่หน่วยกิตและคะแนนให้ถูกต้อง")
                return

            grade_point = self.get_grade_point(score)
            grade = self.get_grade(score)
            
            self.gpa_records.append({"credit": credit, "grade_point": grade_point})
            
            subject_text = f"{subject} | หน่วยกิต: {credit} | เกรด: {grade}"
            ctk.CTkLabel(self.subject_list_frame, text=subject_text).pack(anchor="w", padx=5, pady=2)
            
            self.subject_entry.delete(0, "end")
            self.credit_entry.delete(0, "end")
            self.score_entry.delete(0, "end")

        except ValueError:
            messagebox.showerror("ข้อผิดพลาด", "กรุณาใส่ข้อมูลเป็นตัวเลขที่ถูกต้อง")

    def get_grade_point(self, score):
        if score >= 80: return 4.0
        elif score >= 75: return 3.5
        elif score >= 70: return 3.0
        elif score >= 65: return 2.5
        elif score >= 60: return 2.0
        elif score >= 55: return 1.5
        elif score >= 50: return 1.0
        else: return 0.0

    def get_grade(self, score):
        if score >= 80: return "A"
        elif score >= 75: return "B+"
        elif score >= 70: return "B"
        elif score >= 65: return "C+"
        elif score >= 60: return "C"
        elif score >= 55: return "D+"
        elif score >= 50: return "D"
        else: return "F"

    def calculate_gpa(self):
        if not self.gpa_records:
            messagebox.showinfo("แจ้งเตือน", "กรุณาเพิ่มวิชาก่อนคำนวณ GPA")
            return
        
        total_credit = sum(rec['credit'] for rec in self.gpa_records)
        total_grade_point = sum(rec['credit'] * rec['grade_point'] for rec in self.gpa_records)
        
        if total_credit == 0:
            gpa = 0.0
        else:
            gpa = total_grade_point / total_credit
            
        self.gpa_result_label.configure(text=f"GPA เทอมนี้: {gpa:.2f}")

    def reset_gpa_data(self):
        self.gpa_records = []
        for widget in self.subject_list_frame.winfo_children():
            widget.destroy()
        self.gpa_result_label.configure(text="GPA เทอมนี้: -")

    def calculate_gpax(self):
        try:
            prev_gpa = float(self.prev_gpa_entry.get())
            prev_credit = float(self.prev_credit_entry.get())
            
            if not self.gpa_records:
                messagebox.showinfo("แจ้งเตือน", "กรุณาคำนวณ GPA เทอมปัจจุบันก่อน")
                return
            
            if prev_credit <= 0 or not (0 <= prev_gpa <= 4):
                messagebox.showerror("ข้อผิดพลาด", "กรุณาใส่ข้อมูล GPA และหน่วยกิตที่ผ่านมาให้ถูกต้อง")
                return

            current_total_credit = sum(rec['credit'] for rec in self.gpa_records)
            current_total_grade_point = sum(rec['credit'] * rec['grade_point'] for rec in self.gpa_records)

            gpax_numerator = (prev_gpa * prev_credit) + current_total_grade_point
            gpax_denominator = prev_credit + current_total_credit
            
            if gpax_denominator == 0:
                gpax = 0.0
            else:
                gpax = gpax_numerator / gpax_denominator
            
            self.gpax_result_label.configure(text=f"GPAX สะสม: {gpax:.2f}")

        except ValueError:
            messagebox.showerror("ข้อผิดพลาด", "กรุณาใส่ข้อมูลเป็นตัวเลขที่ถูกต้อง")

if __name__ == "__main__":
    app = GradeCalculatorApp()
    app.mainloop()
