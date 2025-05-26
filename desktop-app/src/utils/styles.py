from tkinter import ttk

def apply_styles():
    style = ttk.Style()

    #Global Sidebar Tabs
    style.configure("Sidebar.TButton",background="#1e3a5f", foreground="white", font=("Arial", 12, "bold"), relief="raised", padding=(10, 5), borderwidth=2, anchor="center")
    style.map("Sidebar.TButton", background=[("active", "#2c4b7f")])

    # Children Window Tview
    style.configure("ChildrenTree.Treeview", font=("Arial", 12), rowheight=30, padding=5)       
    style.configure("ChildrenTreeview.Heading", font=("Arial", 14, "bold"))

    # Menu Select Btn
    style.configure("MenuSelect.TButton", background="#add8e6", foreground="black", borderwidth=1, focusthickness=3, focuscolor='none')
    style.map("MenuSelect.TButton", background=[("active", "#87ceeb")])

    #Register Select Btn
    style.configure("RegisterSelect.TButton", background="#add8e6", foreground="black", borderwidth=1, focusthickness=3, focuscolor='none')
    style.map("RegisterSelect.TButton", background=[("active", "#87ceeb")])

    #Register Adjust Btn
    style.configure("RegisterAdjust.TButton", background="#add8e6", foreground="black", borderwidth=1, focusthickness=3, focuscolor='none')
    style.map("RegisterAdjust.TButton", background=[("active", "#87ceeb")]) 

    #Register Absent Btn
    style.configure("RegisterAbsent.TButton", background="#ffb6c1", foreground="black", borderwidth=1, focusthickness=3, focuscolor='none')
    style.map("RegisterAbsent.TButton", background=[("active", "#ff69b4")])

    #Register Adjust Cancel Btn
    style.configure("RegisterCancel.TButton", background="#f4c2c2", foreground="black", borderwidth=1)
    style.map("RegisterCancel.TButton", background=[("active", "#e89cae")])

    #Register Adjust Save Btn
    style.configure("Save.TButton", background="#b6e7a6", foreground="black", borderwidth=1)
    style.map("Save.TButton", background=[("active", "#9bd18a")])

    #Reports Window Preview Btn
    style.configure("ReportGreen.TButton", background="#9CF890", foreground="black")
    style.map("ReportGreen.TButton", background=[("active", "#55EC61")])

    #Reports Window Action Btns
    style.configure("ReportBlue.TButton", background="#2196F3", foreground="white")
    style.map("ReportBlue.TButton", background=[("active", "#1976D2")])

    #Reports Window Tview
    style.configure("Treeview", rowheight=25, font=("Helvetica", 10))
    style.configure("Mid.Treeview", rowheight=50, font=("Helvetica", 10))
    style.configure("Tall.Treeview", rowheight=140, font=("Helvetica", 10))
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
    style.map("Treeview", background=[('selected', '#d9d9d9')])