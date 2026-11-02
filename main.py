import tkinter as tk
import logging
from database import initialize_db
from styles import apply_minimal_theme
from views import BudgetGoalsApp

# Configure logging framework
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Initializing system workspace...")
    
    # Setup SQLite tables if missing
    initialize_db()
    
    # Master application window initialization setup
    root = tk.Tk()
    root.title("BUDGET GOALS MANAGER")
    root.geometry("1100x720")
    root.minsize(1020, 650)
    
    # Enforce Black & White Custom Theme Elements
    apply_minimal_theme(root)
    
    # Initialize Core Application Content Canvas View Tabs Tracker Frame
    app_workspace = BudgetGoalsApp(root)
    app_workspace.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    logging.info("Application context fully loaded. Launching loop engine.")
    root.mainloop()

if __name__ == "__main__":
    main()