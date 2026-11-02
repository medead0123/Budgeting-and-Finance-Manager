import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

import models
import database

# Matplotlib integration
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class BudgetGoalsApp(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # 1. Main Structural Split: Sidebar vs Workspace Canvas
        self.sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=240)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        self.workspace_container = ttk.Frame(self, padding=25)
        self.workspace_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Build Left App Logo Context
        lbl_logo = tk.Label(self.sidebar, text="UNIX BUDGET", bg="#11131A", fg="#FFFFFF", font=("Segoe UI", 14, "bold"), anchor="w", padx=20)
        lbl_logo.pack(fill=tk.X, pady=(25, 30))
        
        # 2. Setup the Hidden Notebook Component to Manage State Transitions Safely
        self.notebook = ttk.Notebook(self.workspace_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_income = ttk.Frame(self.notebook)
        self.tab_expenses = ttk.Frame(self.notebook)
        self.tab_savings = ttk.Frame(self.notebook)
        self.tab_budget = ttk.Frame(self.notebook)
        self.tab_analytics = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_dashboard)
        self.notebook.add(self.tab_income)
        self.notebook.add(self.tab_expenses)
        self.notebook.add(self.tab_savings)
        self.notebook.add(self.tab_budget)
        self.notebook.add(self.tab_analytics)
        self.notebook.add(self.tab_settings)
        
        # 3. Inject Left Dynamic Side Navigation Controls
        self.nav_buttons = []
        nav_specs = [
            ("Dashboard", 0),
            ("Income Manager", 1),
            ("Expenses Log", 2),
            ("Savings Goals", 3),
            ("Budget Planner", 4),
            ("Flow Analytics", 5),
            ("System Tools", 6)
        ]
        
        for name, index in nav_specs:
            btn = tk.Button(self.sidebar, text=f"  {name}", bg="#11131A", fg="#A3AED0", activebackground="#1F2431", 
                            activeforeground="#FFFFFF", font=("Segoe UI", 10, "bold" if index==0 else "normal"), bd=0, relief="flat", anchor="w", padx=15, pady=10)
            btn.config(command=lambda idx=index, b=btn: self.switch_tab_view(idx, b))
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.nav_buttons.append(btn)
            
        # Highlight initial view button selection state
        self.nav_buttons[0].config(bg="#252B3A", fg="#FFFFFF")

        # Initialize core application logic channels
        self.setup_dashboard()
        self.setup_income_view()
        self.setup_expenses_view()
        self.setup_savings_view()
        self.setup_budget_view()
        self.setup_analytics_view()
        self.setup_settings_view()
        
        self.refresh_all()

    def switch_tab_view(self, tab_index, clicked_button):
        """Transitions pages smoothly and updates the sidebar indicator states."""
        self.notebook.select(tab_index)
        for btn in self.nav_buttons:
            btn.config(bg="#11131A", fg="#A3AED0")  # Reset unselected buttons
        clicked_button.config(bg="#252B3A", fg="#FFFFFF") # Accent selected button

    def refresh_all(self):
        self.update_dashboard_metrics()
        self.load_income_table()
        self.load_expenses_table()
        self.load_savings_table()
        self.load_budget_analysis()
        self.render_charts()

    # ==========================================
    # SYSTEM DASHBOARD (CARD LAYOUT GRID)
    # ==========================================
    def setup_dashboard(self):
        header_frame = ttk.Frame(self.tab_dashboard)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Dashboard", style="Heading.TLabel").pack(anchor=tk.W)
        ttk.Label(header_frame, text="Overview of your finances", style="Subheading.TLabel").pack(anchor=tk.W)
        
        cards_frame = ttk.Frame(self.tab_dashboard)
        cards_frame.pack(fill=tk.X, pady=10)
        
        self.metric_cards = {}
        metrics = [("Total Balance", "balance"), ("Monthly Income", "income"), ("Monthly Expenses", "expense"), ("Savings Target", "savings")]
        
        for idx, (title, key) in enumerate(metrics):
            card = ttk.Frame(cards_frame, style="Card.TFrame", padding=15)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)
            
            ttk.Label(card, text=title, style="CardMuted.TLabel").pack(anchor=tk.W)
            lbl_cv = ttk.Label(card, text="$0.00", font=("Segoe UI", 16, "bold"), style="CardLabel.TLabel")
            lbl_cv.pack(anchor=tk.W, pady=(6, 0))
            self.metric_cards[key] = lbl_cv

        bottom_frame = ttk.Frame(self.tab_dashboard, padding=(0, 20, 0, 0))
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # Encapsulate recent records into a nice card frame container
        table_card = ttk.Frame(bottom_frame, style="Card.TFrame", padding=15)
        table_card.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(table_card, text="Recent Transactions", font=("Segoe UI", 11, "bold"), style="CardLabel.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        self.tree_recent = ttk.Treeview(table_card, columns=("Date", "Type", "Category", "Amount"), show="headings")
        for col in ("Date", "Type", "Category", "Amount"):
            self.tree_recent.heading(col, text=col.upper())
            self.tree_recent.column(col, anchor=tk.W, width=120)
        self.tree_recent.pack(fill=tk.BOTH, expand=True)

    def update_dashboard_metrics(self):
        data = models.get_dashboard_metrics()
        self.metric_cards['income'].config(text=f"${data['income']:,.2f}")
        self.metric_cards['expense'].config(text=f"${data['expense']:,.2f}")
        self.metric_cards['savings'].config(text=f"${data['savings']:,.2f}")
        self.metric_cards['balance'].config(text=f"${data['balance']:,.2f}")
        
        for r in self.tree_recent.get_children():
            self.tree_recent.delete(r)
        for tx in models.get_recent_transactions()[:8]:
            self.tree_recent.insert("", tk.END, values=(tx['date'], tx['type'].upper(), tx['category'], f"${tx['amount']:,.2f}"))

    # ==========================================
    # INCOME PROFILE VIEW
    # ==========================================
    def setup_income_view(self):
        ttk.Label(self.tab_income, text="Income Registry", style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(self.tab_income, text="Track and manage recurring inflows", style="Subheading.TLabel").pack(anchor=tk.W, pady=(0, 15))
        
        container = ttk.Frame(self.tab_income)
        container.pack(fill=tk.BOTH, expand=True)
        
        form_frame = ttk.Frame(container, style="Card.TFrame", padding=20)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        ttk.Label(form_frame, text="Transaction Date", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_inc_date = ttk.Entry(form_frame, width=25)
        self.ent_inc_date.pack(anchor=tk.W, pady=(0, 10))
        self.ent_inc_date.insert(0, datetime.today().strftime('%Y-%m-%d'))
        
        ttk.Label(form_frame, text="Source Label", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_inc_source = ttk.Entry(form_frame, width=25)
        self.ent_inc_source.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(form_frame, text="Category Stream", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.cb_inc_cat = ttk.Combobox(form_frame, values=["Salary", "Freelance", "Investments", "Gifts", "Other"], width=22, state="readonly")
        self.cb_inc_cat.current(0)
        self.cb_inc_cat.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(form_frame, text="Amount Received ($)", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_inc_amount = ttk.Entry(form_frame, width=25)
        self.ent_inc_amount.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(form_frame, text="Optional Notes", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_inc_notes = ttk.Entry(form_frame, width=25)
        self.ent_inc_notes.pack(anchor=tk.W, pady=(0, 20))
        
        ttk.Button(form_frame, text="SAVE TRANSACTION", command=self.save_income_action).pack(fill=tk.X, pady=3)
        ttk.Button(form_frame, text="CLEAR FORM", style="Secondary.TButton", command=self.clear_income_form).pack(fill=tk.X, pady=3)
        ttk.Button(form_frame, text="DELETE ENTRY", style="Secondary.TButton", command=self.delete_income_action).pack(fill=tk.X, pady=(15, 3))
        
        display_frame = ttk.Frame(container, style="Card.TFrame", padding=15)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        search_frame = ttk.Frame(display_frame, style="Card.TFrame")
        search_frame.pack(fill=tk.X, pady=(0, 15))
        self.ent_inc_search = ttk.Entry(search_frame, width=35)
        self.ent_inc_search.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(search_frame, text="Filter Log", style="Secondary.TButton", command=self.load_income_table).pack(side=tk.LEFT)
        
        self.tree_inc = ttk.Treeview(display_frame, columns=("ID", "Date", "Source", "Category", "Amount", "Notes"), show="headings")
        for col in ("ID", "Date", "Source", "Category", "Amount", "Notes"):
            self.tree_inc.heading(col, text=col.upper())
            self.tree_inc.column(col, width=90 if col in ("ID", "Amount") else 120)
        self.tree_inc.pack(fill=tk.BOTH, expand=True)
        self.tree_inc.bind("<<TreeviewSelect>>", self.on_income_select)
        
        self.selected_income_id = None

    def load_income_table(self):
        for r in self.tree_inc.get_children():
            self.tree_inc.delete(r)
        q = self.ent_inc_search.get().strip() or None
        for row in models.get_all_income(q):
            self.tree_inc.insert("", tk.END, values=(row['id'], row['date'], row['source'], row['category'], f"{row['amount']:.2f}", row['notes']))

    def save_income_action(self):
        try:
            dt = self.ent_inc_date.get()
            src = self.ent_inc_source.get().strip()
            cat = self.cb_inc_cat.get()
            amt = float(self.ent_inc_amount.get())
            notes = self.ent_inc_notes.get().strip()
            if not src or amt <= 0: return
            if self.selected_income_id is None:
                models.add_income(dt, src, cat, amt, notes)
            else:
                models.update_income(self.selected_income_id, dt, src, cat, amt, notes)
            self.clear_income_form()
            self.refresh_all()
        except Exception as e: messagebox.showerror("Error", str(e))

    def on_income_select(self, event):
        sel = self.tree_inc.selection()
        if not sel: return
        vals = self.tree_inc.item(sel[0], 'values')
        self.selected_income_id = vals[0]
        self.ent_inc_date.delete(0, tk.END)
        self.ent_inc_date.insert(0, vals[1])
        self.ent_inc_source.delete(0, tk.END)
        self.ent_inc_source.insert(0, vals[2])
        self.cb_inc_cat.set(vals[3])
        self.ent_inc_amount.delete(0, tk.END)
        self.ent_inc_amount.insert(0, vals[4])
        self.ent_inc_notes.delete(0, tk.END)
        self.ent_inc_notes.insert(0, vals[5] if vals[5] != "None" else "")

    def delete_income_action(self):
        if self.selected_income_id is not None:
            models.delete_income(self.selected_income_id)
            self.clear_income_form()
            self.refresh_all()

    def clear_income_form(self):
        self.selected_income_id = None
        self.ent_inc_source.delete(0, tk.END)
        self.ent_inc_amount.delete(0, tk.END)
        self.ent_inc_notes.delete(0, tk.END)

    # ==========================================
    # EXPENSES MODULE
    # ==========================================
    def setup_expenses_view(self):
        ttk.Label(self.tab_expenses, text="Expense Register", style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 5))
        container = ttk.Frame(self.tab_expenses)
        container.pack(fill=tk.BOTH, expand=True)
        
        form_frame = ttk.Frame(container, style="Card.TFrame", padding=20)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        ttk.Label(form_frame, text="Date", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_exp_date = ttk.Entry(form_frame, width=25)
        self.ent_exp_date.pack(anchor=tk.W, pady=(0, 10))
        self.ent_exp_date.insert(0, datetime.today().strftime('%Y-%m-%d'))
        
        ttk.Label(form_frame, text="Category Allocation", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.cb_exp_cat = ttk.Combobox(form_frame, values=models.get_custom_categories(), width=22)
        self.cb_exp_cat.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(form_frame, text="Value Cost ($)", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_exp_amount = ttk.Entry(form_frame, width=25)
        self.ent_exp_amount.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(form_frame, text="Payment Context", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.cb_exp_pay = ttk.Combobox(form_frame, values=["Cash", "Credit Card", "Debit Card", "Bank Transfer"], width=22, state="readonly")
        self.cb_exp_pay.current(1)
        self.cb_exp_pay.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(form_frame, text="Brief Description", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_exp_desc = ttk.Entry(form_frame, width=25)
        self.ent_exp_desc.pack(anchor=tk.W, pady=(0, 20))
        
        ttk.Button(form_frame, text="COMMIT LOG", command=self.save_expense_action).pack(fill=tk.X, pady=3)
        ttk.Button(form_frame, text="CLEAR", style="Secondary.TButton", command=self.clear_expense_form).pack(fill=tk.X, pady=3)
        
        display_frame = ttk.Frame(container, style="Card.TFrame", padding=15)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.tree_exp = ttk.Treeview(display_frame, columns=("ID", "Date", "Category", "Amount", "Method", "Description"), show="headings")
        for col in ("ID", "Date", "Category", "Amount", "Method", "Description"):
            self.tree_exp.heading(col, text=col.upper())
            self.tree_exp.column(col, width=100)
        self.tree_exp.pack(fill=tk.BOTH, expand=True)
        self.tree_exp.bind("<<TreeviewSelect>>", self.on_expense_select)
        
        self.selected_expense_id = None

    def load_expenses_table(self):
        for r in self.tree_exp.get_children():
            self.tree_exp.delete(r)
        for row in models.get_all_expenses():
            self.tree_exp.insert("", tk.END, values=(row['id'], row['date'], row['category'], f"{row['amount']:.2f}", row['payment_method'], row['description']))

    def save_expense_action(self):
        try:
            dt = self.ent_exp_date.get()
            cat = self.cb_exp_cat.get().strip()
            amt = float(self.ent_exp_amount.get())
            pay = self.cb_exp_pay.get()
            desc = self.ent_exp_desc.get().strip()
            if not cat or amt <= 0: return
            if self.selected_expense_id is None:
                models.add_expense(dt, cat, amt, pay, desc, "")
            else:
                models.update_expense(self.selected_expense_id, dt, cat, amt, pay, desc, "")
            self.clear_expense_form()
            self.refresh_all()
        except Exception as e: messagebox.showerror("Error", str(e))

    def on_expense_select(self, event):
        sel = self.tree_exp.selection()
        if not sel: return
        vals = self.tree_exp.item(sel[0], 'values')
        self.selected_expense_id = vals[0]
        self.ent_exp_date.delete(0, tk.END)
        self.ent_exp_date.insert(0, vals[1])
        self.cb_exp_cat.set(vals[2])
        self.ent_exp_amount.delete(0, tk.END)
        self.ent_exp_amount.insert(0, vals[3])
        self.cb_exp_pay.set(vals[4])
        self.ent_exp_desc.delete(0, tk.END)
        self.ent_exp_desc.insert(0, vals[5])

    def clear_expense_form(self):
        self.selected_expense_id = None
        self.ent_exp_amount.delete(0, tk.END)
        self.ent_exp_desc.delete(0, tk.END)

    # ==========================================
    # SAVINGS TARGET TRACKS
    # ==========================================
    def setup_savings_view(self):
        ttk.Label(self.tab_savings, text="Financial Goals Profile", style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 15))
        
        container = ttk.Frame(self.tab_savings)
        container.pack(fill=tk.BOTH, expand=True)
        
        form_frame = ttk.Frame(container, style="Card.TFrame", padding=20)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        ttk.Label(form_frame, text="Goal Target Descriptor", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_g_name = ttk.Entry(form_frame, width=25)
        self.ent_g_name.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(form_frame, text="Target Value Required ($)", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_g_target = ttk.Entry(form_frame, width=25)
        self.ent_g_target.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(form_frame, text="Current Contributed Base ($)", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_g_current = ttk.Entry(form_frame, width=25)
        self.ent_g_current.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(form_frame, text="Deadline Threshold", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_g_dead = ttk.Entry(form_frame, width=25)
        self.ent_g_dead.pack(anchor=tk.W, pady=(0, 20))
        self.ent_g_dead.insert(0, "2026-12-31")
        
        ttk.Button(form_frame, text="SAVE OBJECTIVE", command=self.save_goal_action).pack(fill=tk.X, pady=3)
        ttk.Button(form_frame, text="DELETE TARGET", style="Secondary.TButton", command=self.delete_goal_action).pack(fill=tk.X, pady=3)
        
        self.display_scroll_frame = ttk.Frame(container, style="Card.TFrame", padding=15)
        self.display_scroll_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas_goals = tk.Canvas(self.display_scroll_frame, bg="#FFFFFF", bd=0, highlightthickness=0)
        self.canvas_goals.pack(fill=tk.BOTH, expand=True)
        self.selected_goal_id = None

    def load_savings_table(self):
        for widget in self.canvas_goals.winfo_children():
            widget.destroy()
        goals = models.get_all_goals()
        for g in goals:
            target = g['target_amount'] if g['target_amount'] > 0 else 1.0
            pct = min((g['current_amount'] / target) * 100, 100.0)
            
            g_frame = ttk.Frame(self.canvas_goals, style="Card.TFrame", padding=12)
            g_frame.pack(fill=tk.X, pady=6)
            
            ttk.Label(g_frame, text=g['name'].upper(), font=("Segoe UI", 10, "bold"), style="CardLabel.TLabel").pack(anchor=tk.W)
            pb = ttk.Progressbar(g_frame, maximum=100, style="TProgressbar")
            pb.pack(fill=tk.X, pady=(6, 4))
            pb['value'] = pct
            
            ttk.Label(g_frame, text=f"{pct:.1f}% Match Completed", style="CardMuted.TLabel").pack(anchor=tk.W)

    def save_goal_action(self):
        try:
            nm = self.ent_g_name.get().strip()
            tgt = float(self.ent_g_target.get())
            cur = float(self.ent_g_current.get())
            dl = self.ent_g_dead.get()
            if not nm or tgt <= 0: return
            if self.selected_goal_id is None:
                models.add_goal(nm, tgt, cur, dl, "")
            else:
                models.update_goal(self.selected_goal_id, nm, tgt, cur, dl, "")
            self.refresh_all()
        except Exception as e: messagebox.showerror("Error", str(e))

    def delete_goal_action(self):
        if self.selected_goal_id is not None:
            models.delete_goal(self.selected_goal_id)
            self.refresh_all()

    # ==========================================
    # BUDGET PLANNER
    # ==========================================
    def setup_budget_view(self):
        ttk.Label(self.tab_budget, text="Limits Configuration", style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 15))
        container = ttk.Frame(self.tab_budget)
        container.pack(fill=tk.BOTH, expand=True)
        
        form_frame = ttk.Frame(container, style="Card.TFrame", padding=20)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        ttk.Label(form_frame, text="Month Index", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_b_month = ttk.Entry(form_frame, width=25)
        self.ent_b_month.pack(anchor=tk.W, pady=(0, 10))
        self.ent_b_month.insert(0, datetime.today().strftime('%Y-%m'))
        
        ttk.Label(form_frame, text="Category Allocation", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.cb_b_cat = ttk.Combobox(form_frame, values=models.BUILTIN_CATEGORIES, width=22, state="readonly")
        self.cb_b_cat.current(0)
        self.cb_b_cat.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(form_frame, text="Assigned Threshold Limit ($)", style="CardMuted.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.ent_b_amount = ttk.Entry(form_frame, width=25)
        self.ent_b_amount.pack(anchor=tk.W, pady=(0, 20))
        
        ttk.Button(form_frame, text="SAVE BUDGET LIMIT", command=self.save_budget_action).pack(fill=tk.X, pady=3)
        
        display_frame = ttk.Frame(container, style="Card.TFrame", padding=15)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.tree_budget = ttk.Treeview(display_frame, columns=("Category", "Budgeted", "Actual Spending", "Remaining Balance"), show="headings")
        for col in ("Category", "Budgeted", "Actual Spending", "Remaining Balance"):
            self.tree_budget.heading(col, text=col.upper())
            self.tree_budget.column(col, width=120)
        self.tree_budget.pack(fill=tk.BOTH, expand=True)

    def save_budget_action(self):
        try:
            m = self.ent_b_month.get().strip()
            cat = self.cb_b_cat.get()
            amt = float(self.ent_b_amount.get())
            models.set_budget(m, cat, amt)
            self.refresh_all()
        except Exception as e: messagebox.showerror("Error", str(e))

    def load_budget_analysis(self):
        for r in self.tree_budget.get_children():
            self.tree_budget.delete(r)
        m = self.ent_b_month.get().strip()
        try:
            comparison = models.get_budget_vs_actual(m)
            for row in comparison:
                self.tree_budget.insert("", tk.END, values=(row['category'], f"${row['budgeted']:,.2f}", f"${row['actual']:,.2f}", f"${row['remaining']:,.2f}"))
        except: pass

    # ==========================================
    # ANALYTICS WORKSPACE
    # ==========================================
    def setup_analytics_view(self):
        self.scroll_analytics = ttk.Frame(self.tab_analytics)
        self.scroll_analytics.pack(fill=tk.BOTH, expand=True)

    def render_charts(self):
        for widget in self.scroll_analytics.winfo_children():
            widget.destroy()

        # Build a dual-pane minimalist graph canvas layout that perfectly matches the reference image
        fig = Figure(figsize=(10, 4.5), dpi=100, facecolor='#FFFFFF')
        
        # 1. Total Expenditures Trend Path
        ax1 = fig.add_subplot(121, facecolor='#FFFFFF')
        exp_data = models.get_all_expenses()
        cat_totals = {}
        for e in exp_data:
            cat_totals[e['category']] = cat_totals.get(e['category'], 0.0) + e['amount']
            
        if cat_totals:
            ax1.pie(list(cat_totals.values()), labels=list(cat_totals.keys()), colors=['#11131A', '#3A4252', '#637085', '#91A1B8', '#C3D1E6'], 
                    textprops={'fontsize': 8}, wedgeprops={'linewidth': 1, 'edgecolor': '#FFFFFF'}, autopct='%1.0f%%')
        ax1.set_title("SPENDING MATRIX BY SECTOR", fontsize=9, fontweight='bold', color='#1E2229')

        # 2. Dynamic Performance Overview Bar Graph
        ax2 = fig.add_subplot(122, facecolor='#FFFFFF')
        metrics = models.get_dashboard_metrics()
        ax2.bar(["Inflows", "Outflows"], [metrics['income'], metrics['expense']], color=['#11131A', '#91A1B8'], width=0.4)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#EAEFF5')
        ax2.spines['bottom'].set_color('#EAEFF5')
        ax2.tick_params(labelsize=8, colors='#8A94A6')
        ax2.set_title("TOTAL FINANCIAL STREAMS LOG", fontsize=9, fontweight='bold', color='#1E2229')
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.scroll_analytics)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ==========================================
    # SETTINGS LOG INTERFACE
    # ==========================================
    def setup_settings_view(self):
        container = ttk.Frame(self.tab_settings, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        card = ttk.Frame(container, style="Card.TFrame", padding=20)
        card.pack(fill=tk.X, pady=10)
        
        ttk.Label(card, text="Data Engine Integrity Controls", font=("Segoe UI", 12, "bold"), style="CardLabel.TLabel").pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Button(card, text="CREATE BACKUP DATA POOL", command=self.backup_action).pack(anchor=tk.W, pady=4)
        ttk.Button(card, text="RESTORE FROM ARCHIVE FILE", style="Secondary.TButton", command=self.restore_action).pack(anchor=tk.W, pady=4)

    def backup_action(self):
        fn = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database Files", "*.db")])
        if fn and database.backup_database(fn):
            messagebox.showinfo("Success", "Backup generated successfully.")

    def restore_action(self):
        fn = filedialog.askopenfilename(filetypes=[("Database Files", "*.db")])
        if fn and messagebox.askyesno("Confirm", "Replace current database snapshot?"):
            if database.restore_database(fn):
                messagebox.showinfo("Success", "System data safely restored.")
                self.refresh_all()