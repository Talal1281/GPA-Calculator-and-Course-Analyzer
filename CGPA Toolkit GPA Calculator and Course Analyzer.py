#Name: Talal Malhi 
#Thanks for visting my project! Hope you like it
from tkinter import *
from tkinter import filedialog, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
import tkinter as tk

courses = [] 


def calculate_cgpa():
    total_points = 0
    total_credits = 0
    for course in courses:
        total_points += float(course['gpa']) * int(course['credit'])
        total_credits += int(course['credit'])
    return total_points / total_credits if total_credits else 0


def generate_pie_chart(pdf):
    labels = [course['name'] for course in courses]
    sizes = [int(course['credit']) for course in courses]
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Course Weight Affecting GPA")
    plt.tight_layout()
    pdf.savefig()
    plt.close()


def generate_pdf_report():
    if not courses:
        messagebox.showerror("Error", "No courses available to generate a report.")
        return
    cgpa = calculate_cgpa()
    pdf_file = "course_report.pdf"
    with PdfPages(pdf_file) as pdf:
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        text = f"Course Report\n\n"
        for course in courses:
            text += f"Course: {course['name']}, GPA: {course['gpa']}, Credit: {course['credit']}\n"
        text += f"\nYour CGPA: {cgpa:.2f}"
        ax.text(0.1, 0.9, text, fontsize=12, va='top', wrap=True)
        pdf.savefig(fig)
        plt.close(fig)
        generate_pie_chart(pdf)
    messagebox.showinfo("PDF Generated", f"PDF report has been saved as {pdf_file}!")


def calculate_needed_gpa(target_gpa):
    current_points = sum(float(course['gpa']) * int(course['credit']) for course in courses)
    current_credits = sum(int(course['credit']) for course in courses)
    num_existing_courses = len(courses)
    needed_credits_per_course = 3
    for num_new_courses in range(1, 6):
        total_credits = current_credits + (num_new_courses * needed_credits_per_course)
        total_points_needed = target_gpa * total_credits
        points_to_add = total_points_needed - current_points
        needed_gpa = points_to_add / (num_new_courses * needed_credits_per_course)
        if 0 <= needed_gpa <= 4: 
            return num_new_courses, needed_gpa
    return None, None

def main_page():
    home_page = Tk()
    home_page.geometry("550x450")
    home_page.resizable(1, 1)
    home_page.title("Home Page")


    def open_gpa_calculator():
        class GPAApp:
            def __init__(self, window):
                self.window = window
                self.window.title("GPA Calculator")

                frame = tk.Frame(self.window)
                frame.pack(pady=20)

                tk.Button(frame, text="Open CSV", command=self.load_csv).pack(side=tk.LEFT)
                tk.Button(frame, text="Calculate GPA", command=self.calculate_gpa).pack(side=tk.LEFT)
                tk.Button(frame, text="Export PDF", command=lambda: self.export_file('pdf')).pack(side=tk.LEFT)
                tk.Button(frame, text="Export CSV", command=lambda: self.export_file('csv')).pack(side=tk.LEFT)

                self.data = None
                self.result = None

            def load_csv(self):
                file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
                if file_path:
                    self.data = pd.read_csv(file_path)
                    messagebox.showinfo("Information", "CSV Loaded Successfully")

            def calculate_gpa(self):
                if self.data is not None:
                    name_col = [col for col in self.data.columns if 'name' in col.lower()]
                    gpa_col = [col for col in self.data.columns if 'gpa' in col.lower()]
                    credit_col = [col for col in self.data.columns if 'credit' in col.lower()]

                    if not name_col or not gpa_col or not credit_col:
                        missing = ', '.join([
                            "name" if not name_col else "",
                            "gpa" if not gpa_col else "",
                            "credit" if not credit_col else ""
                        ]).strip(', ')
                        messagebox.showerror("Error", f"Missing necessary columns: {missing}")
                        return

                    self.data['Weighted_GPA'] = self.data[gpa_col[0]] * self.data[credit_col[0]]
                    total_credits = self.data[credit_col[0]].sum()
                    if total_credits > 0:
                        final_gpa = self.data['Weighted_GPA'].sum() / total_credits
                        self.result = pd.DataFrame({
                            "Total Credits": [total_credits],
                            "Final GPA": [final_gpa]
                        })
                        messagebox.showinfo("GPA Calculated", f"Total GPA is {final_gpa:.2f}")
                    else:
                        messagebox.showerror("Error", "Total credits are zero, cannot calculate GPA")
                else:
                    messagebox.showerror("Error", "No CSV loaded")

            def export_file(self, filetype):
                if self.result is not None:
                    file_path = filedialog.asksaveasfilename(defaultextension=f".{filetype}")
                    if file_path:
                        if filetype == 'pdf':
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_font("Arial", size=12)
                            pdf.cell(200, 10, txt=f"Total Credits: {self.result['Total Credits'].iloc[0]}", ln=True)
                            pdf.cell(200, 10, txt=f"Final GPA: {self.result['Final GPA'].iloc[0]:.2f}", ln=True)
                            pdf.output(file_path)
                        elif filetype == 'csv':
                            self.result.to_csv(file_path, index=False)
                        messagebox.showinfo("Export Successful", f"File has been saved to {file_path}")
                else:
                    messagebox.showerror("Error", "No results to save")

        gpa_window = tk.Toplevel()
        GPAApp(gpa_window)


    def course_button():
        course_home = Tk()
        course_home.geometry("450x350")
        course_home.resizable(1, 1)
        course_home.title("Course")

        def new_course():
            new_course_window = Toplevel(course_home)
            new_course_window.geometry("300x300")
            new_course_window.title("Add New Course")

            Label(new_course_window, text="Enter Course Name: ").pack()
            enter_course_name = Entry(new_course_window)
            enter_course_name.pack()

            Label(new_course_window, text="Enter Current GPA: ").pack()
            gpa_number_entry = Entry(new_course_window)
            gpa_number_entry.pack()

            Label(new_course_window, text="Enter Credit: ").pack()
            credit_number_entry = Entry(new_course_window)
            credit_number_entry.pack()

            def complete():
                if not enter_course_name.get().strip() or not gpa_number_entry.get().strip() or not credit_number_entry.get().strip():
                    messagebox.showerror("Error", "All fields are required!")
                    return
                try:
                    float(gpa_number_entry.get())
                    int(credit_number_entry.get())
                except ValueError:
                    messagebox.showerror("Error", "Invalid input in GPA or Credit. Please enter valid numbers.")
                    return
                save_course_information(enter_course_name.get(), gpa_number_entry.get(), credit_number_entry.get())

            def save_course_information(name, gpa, credit):
                course_info = {
                    'name': name.strip(),
                    'gpa': gpa.strip(),
                    'credit': credit.strip()
                }
                courses.append(course_info)
                messagebox.showinfo("Success", "Course information saved successfully!")
                new_course_window.destroy()

            Button(new_course_window, text="Save Course", command=complete).pack()

        def generate_results():
            if not courses:
                messagebox.showerror("Error", "No courses added yet.")
                return
            cgpa = calculate_cgpa()
            messagebox.showinfo("Results", f"Your CGPA is: {cgpa:.2f}")
            generate_pdf_report()

        def find_needed_gpa():
            target_window = Toplevel(course_home)
            target_window.geometry("300x200")
            target_window.title("Target GPA")

            Label(target_window, text="Enter Target GPA: ").pack()
            target_gpa_entry = Entry(target_window)
            target_gpa_entry.pack()

            def calculate():
                try:
                    target_gpa = float(target_gpa_entry.get())
                except ValueError:
                    messagebox.showerror("Error", "Invalid input for target GPA.")
                    return
                num_courses, needed_gpa = calculate_needed_gpa(target_gpa)
                if num_courses is None:
                    messagebox.showerror("Error", "It is not possible to achieve the target GPA.")
                else:
                    messagebox.showinfo("Needed GPA", f"To achieve a GPA of {target_gpa:.2f}, you need to take {num_courses} additional courses with an average GPA of {needed_gpa:.2f}.")
                target_window.destroy()

            Button(target_window, text="Calculate", command=calculate).pack()

        Button(course_home, text="New Course", command=new_course).pack()
        Button(course_home, text="Generate Results", command=generate_results).pack()
        Button(course_home, text="What GPA Are You Looking For?", command=find_needed_gpa).pack()
        course_home.mainloop()
    

    student_course = Button(home_page, text="Manually Add Report", command=course_button)
    student_course.pack()
    gpa_button = tk.Button(home_page, text="Open GPA Calculator", command=open_gpa_calculator)
    gpa_button.pack(pady=20)
    home_page.mainloop()


if __name__ == "__main__":
    main_page()
