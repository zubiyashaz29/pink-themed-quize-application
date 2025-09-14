import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# ------------------ DATABASE SETUP ------------------
conn = sqlite3.connect("quiz_database.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    option4 TEXT,
    correct_answer TEXT,
    explanation TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    score INTEGER NOT NULL
)''')

cursor.execute("SELECT COUNT(*) FROM questions")
if cursor.fetchone()[0] == 0:
    questions = [
        ("What is the output of print(2 ** 3)?", "4", "8", "16", "2", "8", "2 raised to the power of 3 is 8."),
        ("What is the correct way to define a function in Python?", "function my_function():", "def my_function():", "function: my_function()", "def: my_function()", "def my_function():", "In Python, functions are defined using the 'def' keyword."),
        ("What is the type of the object `type([])`?", "list", "type", "object", "None", "type", "The type of an empty list is 'type', which is a class for types."),
        ("Which of the following is an immutable type in Python?", "list", "tuple", "set", "dict", "tuple", "A tuple is an immutable data type, while lists, sets, and dicts are mutable."),
        ("How do you add a comment in Python?", "// This is a comment", "# This is a comment", "/* This is a comment */", "<!-- This is a comment -->", "# This is a comment", "In Python, comments are added with a '#' symbol."),
        ("Which keyword is used to handle exceptions in python?", "except", "catch", "error", "try", "except", "The except block catches the error and prevents the program from crashing."),
        ("Which of the following is a valid variable name in Python?", "1variable", "my-variable", "my_variable", "if", "my_variable", "Variable names in Python cannot start with a number or be reserved words."),
        ("What is the purpose of indentation in Python?", "To make the code look neat", "To define the blocks of code", "To comment out lines of code", "To increase execution speed", "To define the blocks of code", "Python uses indentation to define code blocks."),
        ("What is the correct file extension for Python files?", ".pyt", ".python", ".py", ".pt", ".py", "Python files are saved with the .py extension."),
        ("What is the purpose of break statement in Python?", "To skip an iteration in a loop", "To terminate a loop prematurely", "To return a value from a function", "To exit the Python interpreter", "To terminate a loop prematurely", "The break statement exits a loop early when a condition is met."),
    ]
    cursor.executemany("INSERT INTO questions (question, option1, option2, option3, option4, correct_answer, explanation) VALUES (?, ?, ?, ?, ?, ?, ?)", questions)
    conn.commit()

# ------------------ GUI CLASS ------------------

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Quiz App")
        self.root.geometry("750x600")
        self.root.configure(bg="#ffe6f0")
        self.username = ""
        self.setup_styles()
        self.show_login()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 12), background="#ffe6f0")
        style.configure("Header.TLabel", font=("Arial", 20, "bold"), foreground="#d63384", background="#ffe6f0")
        style.configure("Bold.TButton",
                        font=("Arial Black", 13),
                        padding=10,
                        relief="raised",
                        borderwidth=3,
                        background="#d63384",
                        foreground="black")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()
        frame = tk.Frame(self.root, bg="#ffe6f0")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(frame, text="Login to Python Quiz App", style="Header.TLabel").pack(pady=10)

        ttk.Label(frame, text="Username:").pack()
        self.username_entry = ttk.Entry(frame, width=30)
        self.username_entry.pack(pady=5)

        ttk.Label(frame, text="Password:").pack()
        self.password_entry = ttk.Entry(frame, width=30, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(frame, text="Login", command=self.login, style="Bold.TButton").pack(pady=5)
        ttk.Button(frame, text="Register", command=self.register, style="Bold.TButton").pack(pady=5)
        ttk.Button(frame, text="View Scores", command=self.view_scores, style="Bold.TButton").pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        if cursor.fetchone():
            self.username = username
            self.start_quiz()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful! You can now log in.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")

    def start_quiz(self):
        self.score = 0
        self.current_question_index = 0
        cursor.execute("SELECT * FROM questions")
        self.questions = cursor.fetchall()
        self.show_question()

    def show_question(self):
        self.clear_window()
        if self.current_question_index >= len(self.questions):
            self.finish_quiz()
            return

        q = self.questions[self.current_question_index]
        self.correct_answer = q[6]
        self.explanation = q[7]
        options = [q[2], q[3], q[4], q[5]]

        frame = tk.Frame(self.root, bg="#ffe6f0")
        frame.place(relx=0.5, rely=0.1, anchor="n")

        ttk.Label(frame, text=f"Question {self.current_question_index + 1}", style="Header.TLabel").pack(pady=10)
        ttk.Label(frame, text=q[1], wraplength=600).pack(pady=5)

        self.selected = tk.StringVar()

        for option in options:
            ttk.Radiobutton(frame, text=option, variable=self.selected, value=option).pack(anchor="w", padx=20)

        ttk.Button(frame, text="Submit Answer", command=self.evaluate_answer).pack(pady=10)

    def evaluate_answer(self):
        selected = self.selected.get()
        if not selected:
            messagebox.showwarning("No selection", "Please choose an answer.")
            return
        if selected == self.correct_answer:
            self.score += 1
            messagebox.showinfo("Correct ✅", f"Explanation: {self.explanation}")
        else:
            messagebox.showerror("Incorrect ❌", f"Correct: {self.correct_answer}\nExplanation: {self.explanation}")
        self.current_question_index += 1
        self.show_question()

    def finish_quiz(self):
        cursor.execute("INSERT INTO scores (username, score) VALUES (?, ?)", (self.username, self.score))
        conn.commit()
        messagebox.showinfo("Quiz Completed 🎉", f"{self.username}, you scored {self.score}/10")
        self.show_login()

    def view_scores(self):
        self.clear_window()
        frame = tk.Frame(self.root, bg="#ffe6f0")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(frame, text="Top Scores 🏆", style="Header.TLabel").pack(pady=10)

        cursor.execute("SELECT username, score FROM scores ORDER BY id DESC LIMIT 10")
        for u, s in cursor.fetchall():
            ttk.Label(frame, text=f"{u}: {s} points").pack()

        ttk.Button(frame, text="Back", command=self.show_login).pack(pady=10)

# ------------------ RUN APP ------------------

root = tk.Tk()
app = QuizApp(root)
root.mainloop()