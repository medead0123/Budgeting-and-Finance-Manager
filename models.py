import csv
from datetime import datetime
from database import get_connection

BUILTIN_CATEGORIES = [
    "Housing", "Food", "Transport", "Utilities", "Healthcare",
    "Shopping", "Entertainment", "Education", "Travel", "Investments", "Other"
]

def get_custom_categories():
    """Fetches custom expense categories currently saved dynamically by users."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM expenses")
    cats = [row['category'] for row in cursor.fetchall()]
    conn.close()
    
    all_cats = list(set(BUILTIN_CATEGORIES + cats))
    return sorted(all_cats)

# --- Income Operations ---
def add_income(date, source, category, amount, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO income (date, source, category, amount, notes) VALUES (?, ?, ?, ?, ?)",
                   (date, source, category, float(amount), notes))
    conn.commit()
    conn.close()

def get_all_income(search_query=None):
    conn = get_connection()
    cursor = conn.cursor()
    if search_query:
        q = f"%{search_query}%"
        cursor.execute("SELECT * FROM income WHERE source LIKE ? OR category LIKE ? OR notes LIKE ? ORDER BY date DESC", (q, q, q))
    else:
        cursor.execute("SELECT * FROM income ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_income(income_id, date, source, category, amount, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE income SET date=?, source=?, category=?, amount=?, notes=? WHERE id=?",
                   (date, source, category, float(amount), notes, income_id))
    conn.commit()
    conn.close()

def delete_income(income_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM income WHERE id=?", (income_id,))
    conn.commit()
    conn.close()

# --- Expense Operations ---
def add_expense(date, category, amount, payment_method, description, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, category, amount, payment_method, description, notes) VALUES (?, ?, ?, ?, ?, ?)",
                   (date, category, float(amount), payment_method, description, notes))
    conn.commit()
    conn.close()

def get_all_expenses(search_query=None):
    conn = get_connection()
    cursor = conn.cursor()
    if search_query:
        q = f"%{search_query}%"
        cursor.execute("SELECT * FROM expenses WHERE category LIKE ? OR description LIKE ? OR notes LIKE ? ORDER BY date DESC", (q, q, q))
    else:
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_expense(expense_id, date, category, amount, payment_method, description, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE expenses SET date=?, category=?, amount=?, payment_method=?, description=?, notes=? WHERE id=?",
                   (date, category, float(amount), payment_method, description, notes, expense_id))
    conn.commit()
    conn.close()

def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()

# --- Savings Goals Operations ---
def add_goal(name, target, current, deadline, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO savings_goals (name, target_amount, current_amount, deadline, notes) VALUES (?, ?, ?, ?, ?)",
                   (name, float(target), float(current), deadline, notes))
    conn.commit()
    conn.close()

def get_all_goals():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM savings_goals ORDER BY deadline ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_goal(goal_id, name, target, current, deadline, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE savings_goals SET name=?, target_amount=?, current_amount=?, deadline=?, notes=? WHERE id=?",
                   (name, float(target), float(current), deadline, notes, goal_id))
    conn.commit()
    conn.close()

def delete_goal(goal_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM savings_goals WHERE id=?", (goal_id,))
    conn.commit()
    conn.close()

# --- Budget Planner Operations ---
def set_budget(month, category, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (month, category, allocated_amount) 
        VALUES (?, ?, ?)
        ON CONFLICT(month, category) DO UPDATE SET allocated_amount=excluded.allocated_amount
    """, (month, category, float(amount)))
    conn.commit()
    conn.close()

def get_budgets_for_month(month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budgets WHERE month=?", (month,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_budget_vs_actual(month):
    """Calculates budgeted targets vs actual expenditure for a given month format 'YYYY-MM'"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get budgets
    cursor.execute("SELECT category, allocated_amount FROM budgets WHERE month=?", (month,))
    budgets = {row['category']: row['allocated_amount'] for row in cursor.fetchall()}
    
    # Get actuals
    like_month = f"{month}%"
    cursor.execute("SELECT category, SUM(amount) as total FROM expenses WHERE date LIKE ? GROUP BY category", (like_month,))
    actuals = {row['category']: row['total'] for row in cursor.fetchall()}
    
    conn.close()
    
    comparison = []
    all_cats = set(list(budgets.keys()) + list(actuals.keys()))
    for cat in all_cats:
        b_amt = budgets.get(cat, 0.0)
        a_amt = actuals.get(cat, 0.0)
        comparison.append({
            'category': cat,
            'budgeted': b_amt,
            'actual': a_amt,
            'remaining': b_amt - a_amt
        })
    return comparison

# --- Metrics & Calculations ---
def get_dashboard_metrics():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(amount) FROM income")
    total_income = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_expense = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT SUM(current_amount) FROM savings_goals")
    total_savings = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT COUNT(*) FROM savings_goals WHERE current_amount < target_amount")
    active_goals = cursor.fetchone()[0] or 0
    
    conn.close()
    return {
        'income': total_income,
        'expense': total_expense,
        'savings': total_savings,
        'balance': total_income - total_expense,
        'active_goals': active_goals
    }

def get_recent_transactions():
    conn = get_connection()
    cursor = conn.cursor()
    transactions = []
    
    cursor.execute("SELECT id, date, source AS details, category, amount, 'Income' as type FROM income ORDER BY date DESC LIMIT 5")
    for r in cursor.fetchall():
        transactions.append(dict(r))
        
    cursor.execute("SELECT id, date, description AS details, category, amount, 'Expense' as type FROM expenses ORDER BY date DESC LIMIT 5")
    for r in cursor.fetchall():
        transactions.append(dict(r))
        
    transactions.sort(key=lambda x: x['date'], reverse=True)
    conn.close()
    return transactions[:7]

# --- Reporting Exports ---
def export_to_csv(filename, report_type="All"):
    conn = get_connection()
    cursor = conn.cursor()
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        if report_type in ("All", "Income"):
            writer.writerow(["--- INCOME RECORDS ---"])
            writer.writerow(["ID", "Date", "Source", "Category", "Amount", "Notes"])
            cursor.execute("SELECT * FROM income ORDER BY date DESC")
            for row in cursor.fetchall():
                writer.writerow(list(row))
            writer.writerow([])
            
        if report_type in ("All", "Expenses"):
            writer.writerow(["--- EXPENSE RECORDS ---"])
            writer.writerow(["ID", "Date", "Category", "Amount", "Payment Method", "Description", "Notes"])
            cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
            for row in cursor.fetchall():
                writer.writerow(list(row))
            writer.writerow([])
            
        if report_type in ("All", "Savings"):
            writer.writerow(["--- SAVINGS GOALS ---"])
            writer.writerow(["ID", "Goal Name", "Target Amount", "Current Amount", "Deadline", "Notes"])
            cursor.execute("SELECT * FROM savings_goals")
            for row in cursor.fetchall():
                writer.writerow(list(row))
    conn.close()