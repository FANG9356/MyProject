import os
import tkinter as tk
from tkinter import ttk
import numpy as np
from tkinter import PhotoImage

def generate_input_fields():
    try:
        num_users = int(entry_num_users.get())
        num_questions = int(entry_num_questions.get()) 
        if num_users <= 0 or num_questions <= 0:
            label_result.config(text="กรุณากรอกจำนวนผู้ทำแบบประเมินและจำนวนคำถามให้ถูกต้อง!")
            return
        for widget in frame_inputs.winfo_children():
            widget.destroy()
        global entry_scores
        entry_scores = []
        for i in range(num_users):
            frame = tk.Frame(frame_inputs)
            frame.pack(fill='x', pady=2)
            label = tk.Label(frame, text=f"ผู้ทำแบบประเมิน {i+1}:", width=15, anchor='w', font=("Arial", 12))  
            label.pack(side='left')
            user_entries = []
            for j in range(num_questions):
                question_label = tk.Label(frame, text=f"ข้อ {j+1}: ", width=10, font=("Arial", 12)) 
                question_label.pack(side='left', padx=2)
                entry = tk.Entry(frame, width=5, font=("Arial", 12))  
                entry.pack(side='left', padx=2)
                user_entries.append(entry)
            entry_scores.append(user_entries)
    except ValueError:
        label_result.config(text="กรุณากรอกจำนวนผู้ทำแบบประเมินและจำนวนคำถามเป็นตัวเลข!")

def calculate_statistics():
    try:
        num_users = len(entry_scores)
        all_ratings = []
        for user_entries in entry_scores:
            ratings = [float(entry.get()) for entry in user_entries]
            all_ratings.append(ratings)
        num_questions = len(all_ratings[0])
        ratings_array = np.array(all_ratings)
        sums = np.sum(ratings_array, axis=1)
        means = np.mean(ratings_array, axis=1)
        std_devs = np.std(ratings_array, axis=1)
        cv_values = (std_devs / means) * 100
        for i in tree.get_children():
            tree.delete(i)
        for i in range(num_users):
            tree.insert("", "end", values=(i+1, num_questions, sums[i], f"{means[i]:.2f}", f"{std_devs[i]:.2f}", f"{cv_values[i]:.2f}"))
    except ValueError:
        label_result.config(text="กรุณากรอกคะแนนเป็นตัวเลข!")
    except ZeroDivisionError:
        label_result.config(text="ค่าเฉลี่ยเป็น 0 ทำให้ไม่สามารถคำนวณ C.V. ได้!")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("โปรแกรมคำนวณ แบบประเมินการใช้งาน")
    root.geometry("800x800")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "sun.png")
    if os.path.exists(icon_path):
        icon = PhotoImage(file=icon_path)
        root.iconphoto(True, icon)

    label_num_users = tk.Label(root, text="จำนวนผู้ทำแบบประเมิน:", font=("Arial", 12))
    label_num_users.pack()
    entry_num_users = tk.Entry(root, width=30, font=("Arial", 12))  
    entry_num_users.pack()

    label_num_questions = tk.Label(root, text="จำนวนคำถาม:", font=("Arial", 12))
    label_num_questions.pack()
    entry_num_questions = tk.Entry(root, width=30, font=("Arial", 12))  
    entry_num_questions.pack()

    button_generate = tk.Button(root, text="สร้างช่องกรอกคะแนน", command=generate_input_fields, font=("Arial", 12))  
    button_generate.pack(pady=5)

    canvas_input = tk.Canvas(root)
    scrollbar_input_v = tk.Scrollbar(root, orient="vertical", command=canvas_input.yview)
    scrollbar_input_h = tk.Scrollbar(root, orient="horizontal", command=canvas_input.xview)
    canvas_input.configure(yscrollcommand=scrollbar_input_v.set, xscrollcommand=scrollbar_input_h.set)

    frame_inputs = tk.Frame(canvas_input)
    canvas_input.create_window((0, 0), window=frame_inputs, anchor="nw")

    scrollbar_input_v.pack(side="right", fill="y")
    scrollbar_input_h.pack(side="bottom", fill="x")
    canvas_input.pack(expand=True, fill="both", padx=10, pady=10)

    def on_mouse_wheel(event):
        canvas_input.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas_input.bind_all("<MouseWheel>", on_mouse_wheel)

    def on_frame_configure(event):
        canvas_input.configure(scrollregion=canvas_input.bbox("all"))
    frame_inputs.bind("<Configure>", on_frame_configure)

    button_calculate = tk.Button(root, text="คำนวณผลลัพธ์", command=calculate_statistics, font=("Arial", 12))  
    button_calculate.pack(pady=10)

    frame_result = tk.Frame(root)
    frame_result.pack(fill="both", padx=10, pady=5, expand=True)  

    columns = ("กลุ่มตัวอย่าง", "จำนวนข้อที่ตอบ", "คะแนนรวม", "ค่าเฉลี่ย", "S.D.", "C.V. (%)")
    tree = ttk.Treeview(frame_result, columns=columns, show="headings", height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    label_result = tk.Label(root, text="", fg="red", font=("Arial", 12))
    label_result.pack(pady=10)

    root.mainloop()
