import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import time
import json
from jsonschema import validate, ValidationError

LARGEFONT = ("Verdana", 35)

class tkinterApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Database Schema Generator")
        self.geometry("1500x650")

        # Create a container frame
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Create a canvas to make the content scrollable
        canvas = tk.Canvas(container)
        canvas.pack(side="left", fill="both", expand=True)

        # Create a vertical scrollbar linked to the canvas
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the canvas to work with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas to contain all the widgets
        self.main_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        self.frames = {}

        frame = StartPage(self.main_frame, self)
        self.frames[StartPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.bind("<KeyRelease>", self._on_key_release)

        self.tag_configure("keyword", foreground="orange")
        self.tag_configure("string", foreground="green")
        self.tag_configure("comment", foreground="grey")
        self.tag_configure("number", foreground="blue")
        self.tag_configure("braces", foreground="yellow")
        self.tag_configure("colon", foreground="red")

    def _on_key_release(self, event):
        self._highlight_syntax()

    def _highlight_syntax(self):
        self.remove_tags("1.0", tk.END)
        for pattern, tag in self.get_patterns():
            start = 1.0
            while True:
                pos = self.search(pattern, start, tk.END, regexp=True)
                if not pos:
                    break
                end = f"{pos}+{len(self.get(pos, pos + ' lineend'))}c"
                self.tag_add(tag, pos, end)
                start = end

    def remove_tags(self, start, end):
        for tag in ["keyword", "string", "comment", "number", "braces", "colon"]:
            self.tag_remove(tag, start, end)

    @staticmethod
    def get_patterns():
        return [
            (r'\b(true|false|null)\b', "keyword"),
            (r'".*?"', "string"),
            (r'//.*', "comment"),
            (r'\b\d+\b', "number"),
            (r'[{}[\]]', "braces"),
            (r':', "colon")
        ]


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Left side of the split view
        left_frame = tk.Frame(self)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_rowconfigure(1, weight=1)

        conn_frame = tk.Frame(left_frame)
        conn_frame.grid(row=0, column=0, sticky="ew")

        # Database connection entries
        db_url_label = tk.Label(conn_frame, text="Database URL:")
        db_url_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.db_url_entry = tk.Entry(conn_frame, width=40)
        self.db_url_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        uid_label = tk.Label(conn_frame, text="UID:")
        uid_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.uid_entry = tk.Entry(conn_frame, width=40)
        self.uid_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        password_label = tk.Label(conn_frame, text="Password:")
        password_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = tk.Entry(conn_frame, show="*", width=40)
        self.password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        server_label = tk.Label(conn_frame, text="Server:")
        server_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.server_entry = tk.Entry(conn_frame, width=40)
        self.server_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        connect_btn = tk.Button(conn_frame, text="Connect", command=self.connect_db)
        connect_btn.grid(row=4, column=1, padx=5, pady=10, sticky="w")

        text_frame = tk.Frame(left_frame)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        self.text_scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL)
        self.text_area = CustomText(text_frame, wrap=tk.WORD, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white", yscrollcommand=self.text_scrollbar.set)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_scrollbar.config(command=self.text_area.yview)
        self.text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area.insert(tk.END, "Imported JSON will be shown here.")
        self.text_area.config(state=tk.DISABLED)

        # Icon buttons to the right of the input text field
        icon_frame = tk.Frame(left_frame)
        icon_frame.grid(row=1, column=1, sticky="ns", padx=(5, 0))

        import_img = ImageTk.PhotoImage(Image.open("import.png").resize((40, 40)))
        edit_img = ImageTk.PhotoImage(Image.open("edit.png").resize((40, 40)))
        download_img = ImageTk.PhotoImage(Image.open("download.png").resize((40, 40)))

        import_btn = tk.Button(icon_frame, image=import_img, command=self.import_schema)
        import_btn.image = import_img
        import_btn.pack(pady=5)

        edit_btn = tk.Button(icon_frame, image=edit_img, command=self.edit_json)
        edit_btn.image = edit_img
        edit_btn.pack(pady=5)

        download_btn = tk.Button(icon_frame, image=download_img, command=self.download_schema)
        download_btn.image = download_img
        download_btn.pack(pady=5)

        # Button frame at the bottom
        btn_frame = tk.Frame(left_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5, padx=10)

        save_btn = tk.Button(btn_frame, text="Save", command=self.save_schema, width=12, height=2)
        save_btn.pack(side=tk.LEFT, padx=5)

        self.generate_btn = tk.Button(btn_frame, text="Generate", command=self.check_and_generate, width=12, height=2)
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = tk.Button(btn_frame, text="Reset", command=self.reset_text, width=12, height=2)
        reset_btn.pack(side=tk.LEFT, padx=5)

        compile_btn = tk.Button(btn_frame, text="Compile", command=self.check_and_compile, width=12, height=2)
        compile_btn.pack(side=tk.LEFT, padx=5)

        # Right side of the split view
        right_frame = tk.Frame(self, bg="#fff")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self.log_text = tk.Text(right_frame, wrap=tk.WORD, bg="#fff", fg="#000")
        self.log_text.grid(row=0, column=0, sticky="nsew")

        self.is_schema_valid = False

    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def connect_db(self):
        db_url = self.db_url_entry.get()
        uid = self.uid_entry.get()
        password = self.password_entry.get()
        server = self.server_entry.get()
        # Simulate database connection
        self.log_message("Connecting to the database...")
        threading.Thread(target=self.simulate_connection).start()

    def simulate_connection(self):
        time.sleep(3)  # Simulating delay for connection
        self.log_message("Connected to the database!")

    def import_schema(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                schema = file.read()
                self.text_area.config(state=tk.NORMAL)
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, schema)
                self.text_area.config(state=tk.DISABLED)
                self.log_message("Schema imported successfully!")

    def edit_json(self):
        self.text_area.config(state=tk.NORMAL)

    def save_schema(self):
        self.text_area.config(state=tk.DISABLED)
        self.log_message("Schema saved!")

    def download_schema(self):
        schema = self.text_area.get("1.0", tk.END).strip()
        if schema:
            save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
            if save_path:
                with open(save_path, 'w') as file:
                    file.write(schema)
                self.log_message("Schema downloaded successfully!")

    def reset_text(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)
        self.log_message("Text reset.")

    def check_and_generate(self):
        try:
            json_data = self.text_area.get("1.0", tk.END).strip()
            if not json_data:
                raise ValueError("No JSON data found.")
            json_obj = json.loads(json_data)
            # Additional validation logic here
            self.is_schema_valid = True
            self.log_message("JSON schema is valid.")
        except json.JSONDecodeError as e:
            self.is_schema_valid = False
            self.log_message(f"Invalid JSON format: {e}")
        except ValueError as e:
            self.is_schema_valid = False
            self.log_message(str(e))

    def check_and_compile(self):
        self.check_and_generate()
        if self.is_schema_valid:
            self.log_message("Compiling schema...")
            threading.Thread(target=self.simulate_compilation).start()

    def simulate_compilation(self):
        time.sleep(3)  # Simulating delay for compilation
        self.log_message("Schema compiled successfully!")

app = tkinterApp()
app.mainloop()
