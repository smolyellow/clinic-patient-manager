import tkinter as tk
from tkinter import ttk, messagebox

import database


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clinic Patient Manager")
        self.geometry("800x600")
        self.resizable(True, True)

        # Container that stacks frames on top of each other
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for FrameClass in (MainPage, PatientsPage, MedicinesPage):
            frame = FrameClass(container, self)
            self.frames[FrameClass] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainPage)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()


# ── Page 1: Main ──────────────────────────────────────────────────────────────

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(
            self,
            text="Clinic Patient Manager",
            font=("Helvetica", 22, "bold"),
        ).pack(pady=(80, 40))

        btn_patients = tk.Button(
            self,
            text="Patients",
            font=("Helvetica", 14),
            width=20,
            command=lambda: controller.show_frame(PatientsPage),
        )
        btn_patients.pack(pady=12)

        btn_medicines = tk.Button(
            self,
            text="Medicines",
            font=("Helvetica", 14),
            width=20,
            command=lambda: controller.show_frame(MedicinesPage),
        )
        btn_medicines.pack(pady=12)


# ── Page 2: Patients ──────────────────────────────────────────────────────────

class PatientsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ── Top bar ──────────────────────────────────────────────────────────
        top_bar = tk.Frame(self)
        top_bar.pack(fill="x", padx=16, pady=(16, 8))

        tk.Button(
            top_bar,
            text="← Back",
            command=lambda: controller.show_frame(MainPage),
        ).pack(side="left")

        tk.Label(top_bar, text="Patients", font=("Helvetica", 16, "bold")).pack(side="left", padx=16)

        # ── Search bar ───────────────────────────────────────────────────────
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=16, pady=4)

        tk.Label(search_frame, text="Search:").pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", padx=8)

        tk.Button(search_frame, text="Search", command=self._refresh).pack(side="left")

        # ── Display area (Treeview) ───────────────────────────────────────────
        columns = ("id", "name", "iden_type", "iden_info", "phone_number")
        display_frame = tk.Frame(self)
        display_frame.pack(fill="both", expand=True, padx=16, pady=8)

        self.tree = ttk.Treeview(display_frame, columns=columns, show="headings")
        headers = ("ID", "Name", "ID Type", "ID Info", "Phone")
        col_widths = (50, 200, 100, 150, 120)
        for col, header, width in zip(columns, headers, col_widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(display_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ── Add new patient button ────────────────────────────────────────────
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=16, pady=(4, 16))

        tk.Button(
            btn_frame,
            text="Add New Patient",
            font=("Helvetica", 12),
            command=self._open_add_patient_dialog,
        ).pack(side="right")

    def on_show(self):
        self._refresh()

    def _refresh(self):
        query = self.search_var.get()
        rows = database.search_patients(query)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def _open_add_patient_dialog(self):
        AddPatientDialog(self, self.controller)


class AddPatientDialog(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.title("Add New Patient")
        self.geometry("420x500")
        self.resizable(False, False)
        self.grab_set()
        self.parent_page = parent

        fields = [
            ("Full Name *", "name"),
            ("Citizen (1=Yes, 0=No)", "citizen"),
            ("ID Type *", "iden_type"),
            ("ID Info *", "iden_info"),
            ("Birthdate (YYYY-MM-DD)", "birthdate"),
            ("Gender (1=Male, 0=Female)", "gender"),
            ("Married (1=Yes, 0=No)", "married"),
            ("Phone Number", "phone_number"),
        ]

        self.entries = {}
        form_frame = tk.Frame(self, padx=20, pady=20)
        form_frame.pack(fill="both", expand=True)

        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, anchor="w").grid(row=i, column=0, sticky="w", pady=4)
            entry = tk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, pady=4, padx=8)
            self.entries[key] = entry

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=(0, 16))
        tk.Button(btn_frame, text="Save", command=self._save).pack(side="right", padx=4)
        tk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")

    def _save(self):
        name = self.entries["name"].get().strip()
        iden_type = self.entries["iden_type"].get().strip()
        iden_info = self.entries["iden_info"].get().strip()
        if not name or not iden_type or not iden_info:
            messagebox.showerror("Validation Error", "Name, ID Type, and ID Info are required.", parent=self)
            return

        citizen_raw = self.entries["citizen"].get().strip()
        citizen = int(citizen_raw) if citizen_raw in ("0", "1") else None

        birthdate = self.entries["birthdate"].get().strip() or None

        gender_raw = self.entries["gender"].get().strip()
        gender = int(gender_raw) if gender_raw in ("0", "1") else None

        married_raw = self.entries["married"].get().strip()
        married = int(married_raw) if married_raw in ("0", "1") else None

        phone_number = self.entries["phone_number"].get().strip() or None

        try:
            database.add_patient(name, citizen, iden_type, iden_info, birthdate, gender, married, phone_number)
            messagebox.showinfo("Success", f"Patient '{name}' added successfully.", parent=self)
            self.parent_page._refresh()
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)


# ── Page 3: Medicines ─────────────────────────────────────────────────────────

class MedicinesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ── Top bar ──────────────────────────────────────────────────────────
        top_bar = tk.Frame(self)
        top_bar.pack(fill="x", padx=16, pady=(16, 8))

        tk.Button(
            top_bar,
            text="← Back",
            command=lambda: controller.show_frame(MainPage),
        ).pack(side="left")

        tk.Label(top_bar, text="Medicines", font=("Helvetica", 16, "bold")).pack(side="left", padx=16)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=60)

        tk.Button(
            btn_frame,
            text="Add Liquid Medicine",
            font=("Helvetica", 14),
            width=24,
            command=self._open_add_medicine_dialog,
        ).pack(pady=14)

        tk.Button(
            btn_frame,
            text="View Liquid Medicines",
            font=("Helvetica", 14),
            width=24,
            command=self._open_view_medicines_dialog,
        ).pack(pady=14)

    def _open_add_medicine_dialog(self):
        AddMedicineDialog(self)

    def _open_view_medicines_dialog(self):
        ViewMedicinesDialog(self)


class AddMedicineDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Liquid Medicine")
        self.geometry("320x160")
        self.resizable(False, False)
        self.grab_set()

        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Medicine Name *", anchor="w").grid(row=0, column=0, sticky="w", pady=6)
        self.name_entry = tk.Entry(form, width=28)
        self.name_entry.grid(row=0, column=1, pady=6, padx=8)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=(0, 14))
        tk.Button(btn_frame, text="Save", command=self._save).pack(side="right", padx=4)
        tk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")

    def _save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Medicine name is required.", parent=self)
            return
        try:
            database.add_liquid_medicine(name)
            messagebox.showinfo("Success", f"Medicine '{name}' added.", parent=self)
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self)


class ViewMedicinesDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Liquid Medicines")
        self.geometry("400x360")
        self.grab_set()

        columns = ("id", "name")
        frame = tk.Frame(self, padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.heading("id", text="ID")
        tree.column("id", width=60, anchor="center")
        tree.heading("name", text="Name")
        tree.column("name", width=280, anchor="w")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for row in database.get_all_liquid_medicines():
            tree.insert("", "end", values=row)

        tk.Button(self, text="Close", command=self.destroy).pack(pady=(0, 12))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    database.init_db()
    app = App()
    app.mainloop()
