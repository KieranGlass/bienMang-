from tkinter import ttk

def apply_styles():
    style = ttk.Style()

    #Login Btn
    style.configure("login.TButton",background="#ff7043", foreground="white", font=("Arial", 12, "bold"), relief="raised", padding=(10, 5), borderwidth=2, anchor="center")
    style.map("login.TButton", background=[("active", "#b8642d")])

    #Global Sidebar Tabs
    style.configure("Sidebar.TButton",background="#ff7043", foreground="white", font=("Arial", 12, "bold"), relief="raised", padding=(10, 5), borderwidth=2, anchor="center")
    style.map("Sidebar.TButton", background=[("active", "#2c4b7f")])

    #Global Sidebar Background
    style.configure("SidebarBackground.TFrame", background="#003366")

    #Clock Sidebar Background
    style.configure("ClockBackground.TLabel", background="#003366")

    #Day Info Frame Background
    style.configure("dayInfoBackground.TFrame", background="#003366")

    #Child Day Info Frame Background
    style.configure("childDayInfoBackground.TFrame", background="#d9f1fb")

    #Child Day Info Update Btn
    style.configure("update.TButton", background="#2196F3", foreground="black", font=("Arial", 11, "bold"), padding=(6, 5), borderwidth=1, focusthickness=3, focuscolor='none')
    style.map("update.TButton", background=[("active", "#1976D2")])

    #Child Day Info Slider
    style.configure("Horizontal.TScale", troughcolor="white", background="#ff7043")

    #Child Day Info Combobox
    style.configure("childDayInfo.TCombobox", fieldbackground="#white", background="#ff7043", foreground="#000000")

    #Child Day Info Spinbox
    style.configure("childDayInfo.TSpinbox", arrowsize=14, fieldbackground="white", foreground="#000000", background="#ff7043")

    #Child Day Info Complete Btn
    style.configure("complete.TButton", background="#b6e7a6", foreground="black", font=("Arial", 11, "bold"), padding=(6, 5), borderwidth=1, focusthickness=3, focuscolor='none')
    style.map("complete.TButton", background=[("active", "#9bd18a")]) 

    #Day Info back button
    style.configure("dayInfoClose.TButton", background="#f4c2c2", foreground="black", font=("Arial", 12, "bold"), padding=(6, 5), borderwidth=1)
    style.map("dayInfoClose.TButton", background=[("active", "#ff69b4")])

    #Children window data frame
    style.configure("childrenInfo.TFrame", background="#003366")

    #Children control frame
    style.configure("childrenControl.TFrame", background="#d9f1fb")
    style.configure("childrenControl.TFrame.Label", background="#d9f1fb")

    #Add Child Btn
    style.configure("AddChild.TButton", background="#b6e7a6", foreground="black", font=("Arial", 11, "bold"), padding=(6, 5), borderwidth=1)
    style.map("AddChild.TButton", background=[("active", "#9bd18a")])

    #Edit Child Btns
    style.configure("EditChild.TButton", background="#2196F3", foreground="black", font=("Arial", 11, "bold"), padding=(6, 5), borderwidth=1)
    style.map("EditChild.TButton", background=[("active", "#1976D2")])

    #Delete Child Btn
    style.configure("DeleteChild.TButton", background="#f4c2c2", foreground="black", font=("Arial", 11, "bold"), padding=(6, 5), borderwidth=1)
    style.map("DeleteChild.TButton", background=[("active", "#e89cae")])

    style.configure("CustomNotebook.TNotebook", background="#003366", padding=6)
    style.configure("CustomNotebook.TNotebook.Tab", background="#003366", foreground="white", padding=6)
    style.map("CustomNotebook.TNotebook.Tab", background=[("selected", "#ff7043")], foreground=[("selected", "white")])
    
    style.configure("CustomCheck.TCheckbutton", background="#d9f1fb", foreground="black", focuscolor="none")

    #Main Widget Frames
    style.configure("MainBg.TFrame", background="#d9f1fb")
    style.configure("MainBg.TFrame.Label", background="#d9f1fb")

    #Calendar Frames
    style.configure("CalendarBg.TFrame", background="#d9f1fb")

    #Children Window Tview
    style.configure("ChildrenTree.Treeview", font=("Arial", 12), rowheight=30, padding=5)       
    style.configure("ChildrenTreeview.Heading", font=("Arial", 14, "bold"))

    #Menu Save Btn
    style.configure("MenuSave.TButton", background="#b6e7a6", foreground="black", font=("Arial", 11, "bold"), padding=(6, 5), borderwidth=1, focusthickness=3, focuscolor='none')
    style.map("MenuSave.TButton", background=[("active", "#9bd18a")])

    #Menu Select Btn
    style.configure("MenuSelect.TButton", background="#add8e6", foreground="black", font=("Arial", 11, "bold"), padding=(6, 5), borderwidth=1, focusthickness=3, focuscolor='none')
    style.map("MenuSelect.TButton", background=[("active", "#87ceeb")])

    #Register TFrame
    style.configure("Register.TFrame", background="#d9f1fb")

    #Register Select Btn
    style.configure("RegisterSelect.TButton", background="#add8e6", foreground="black", font=("Arial", 11, "bold"), padding=(6, 5), borderwidth=1, focusthickness=3, focuscolor='none')
    style.map("RegisterSelect.TButton", background=[("active", "#87ceeb")])

    #Register Adjust Btn
    style.configure("RegisterAdjust.TButton", background="#add8e6", foreground="black", font=("Arial", 11, "bold"), padding=(6, 5), borderwidth=1, focusthickness=3, focuscolor='none')
    style.map("RegisterAdjust.TButton", background=[("active", "#87ceeb")]) 

    #Register Absent Btn
    style.configure("RegisterAbsent.TButton", background="#ffb6c1", foreground="black", font=("Arial", 11, "bold"), padding=(6, 5), borderwidth=1, focusthickness=3, focuscolor='none')
    style.map("RegisterAbsent.TButton", background=[("active", "#ff69b4")])

    #Register Adjust Cancel Btn
    style.configure("RegisterCancel.TButton", background="#f4c2c2", foreground="black", font=("Arial", 11, "bold"), padding=(6, 5), borderwidth=1)
    style.map("RegisterCancel.TButton", background=[("active", "#e89cae")])

    #Register Adjust Save Btn
    style.configure("Save.TButton", background="#b6e7a6", foreground="black", font=("Arial", 11, "bold"), padding=(6, 5), borderwidth=1)
    style.map("Save.TButton", background=[("active", "#9bd18a")])

    #Reports Window Preview Btn
    style.configure("ReportGreen.TButton", background="#9CF890", font=("Arial", 11, "bold"), padding=(6, 5), foreground="black")
    style.map("ReportGreen.TButton", background=[("active", "#55EC61")])

    #Reports Window Action Btns
    style.configure("ReportBlue.TButton", background="#2196F3", font=("Arial", 11, "bold"), padding=(6, 5), foreground="white")
    style.map("ReportBlue.TButton", background=[("active", "#1976D2")])

    #Reports Window Tview
    style.configure("Treeview", rowheight=25, font=("Helvetica", 10))
    style.configure("Mid.Treeview", rowheight=50, font=("Helvetica", 10))
    style.configure("Tall.Treeview", rowheight=140, font=("Helvetica", 10))
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
    style.map("Treeview", background=[('selected', "#94c7f1")])

    #Settings Frame Background
    style.configure("settingsBackground.TFrame", background="#003366")

    #Setting content Frame Background
    style.configure("settingsContentBackground.TFrame", background="#d9f1fb")
    style.configure("settingsContentBackground.TFrame.Label", background="#d9f1fb", font=("Arial", 11, "bold"))

    #Settings Window Add/Edit btns
    style.configure("SettingsGreen.TButton", background="#b6e7a6", foreground="black", font=("Arial", 10, "bold"), padding=(6, 5))
    style.map("SettingsGreen.TButton", background=[("active", "#9bd18a")])

    #Settings Window Delete/Remove btns
    style.configure("SettingsRed.TButton", background="#FFC0CB", foreground="black", font=("Arial", 10, "bold"), padding=(6, 5))
    style.map("SettingsRed.TButton", background=[("active", "#F3AFBB")])