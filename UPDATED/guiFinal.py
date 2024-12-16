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
        self.geometry("1800x600")  # Adjusted width to fit the split view

        # Create the banner at the top
        banner_frame = tk.Frame(self, bg="red")
        banner_frame.pack(fill=tk.X, pady=0)
        banner_label = tk.Label(banner_frame, text="WELLS FARGO", bg="red", fg="yellow", font=("Helvetica", 24))
        banner_label.pack(side=tk.LEFT, padx=10)
        yellow_banner = tk.Label(self, bg="yellow", height=1)
        yellow_banner.pack(fill=tk.X, pady=0)

        # Create the split view container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True, pady=(0, 10))

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        self.frames = {}

        frame = StartPage(container, self)
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

        self.columnconfigure(0, weight=1, uniform="a")
        self.columnconfigure(1, weight=1, uniform="a")

        # Left side of the split view
        left_frame = tk.Frame(self)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

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
        self.text_area = CustomText(text_frame, wrap=tk.WORD, width=70, height=30, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white", yscrollcommand=self.text_scrollbar.set)
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
        right_frame = tk.Frame(self, bg="#fff")  # Changed background color
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.log_text = tk.Text(right_frame, wrap=tk.WORD, bg="#fff", fg="#000")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # self.initial_label = ttk.Label(right_frame, text="Output Screen", font=LARGEFONT, background="#fff")
        # self.initial_label.pack(expand=True, anchor=tk.CENTER)

        self.is_schema_valid = False

    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.initial_label.config(text="")

    def connect_db(self):
        db_url = self.db_url_entry.get()
        uid = self.uid_entry.get()
        password = self.password_entry.get()
        server = self.server_entry.get()

        if not all([db_url, uid, password, server]):
            messagebox.showwarning("Warning", "All fields are required.")
            return

        conn_info = {
            "Database URL": db_url,
            "UID": uid,
            "Password": password,
            "Server": server
        }

        self.save_connection_info(conn_info)

        self.log_message("Connected to the database.")
        self.import_schema_from_file("test.json")

    def save_connection_info(self, conn_info):
        try:
            with open("connection_info.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        data.update(conn_info)

        with open("connection_info.json", "w") as file:
            json.dump(data, file)

    def import_schema_from_file(self, filepath):
        try:
            with open(filepath, "r") as file:
                schema = file.read()
                self.text_area.config(state=tk.NORMAL)
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, schema)
                self.text_area.config(state=tk.DISABLED)
                self.log_message("JSON file imported successfully.")
        except Exception as e:
            self.log_message("Failed to import JSON file.")
            messagebox.showerror("Error", "Failed to import JSON file.")

    def check_and_generate(self):
        if not self.is_schema_valid:
            messagebox.showwarning("Warning", "Compile the schema first.")
            return
        self.show_package_module_popup()

    def show_package_module_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Enter Package and Module")
        popup.geometry("300x200")  # Adjusted size of the popup window

        tk.Label(popup, text="Package:").pack(pady=5)
        package_entry = tk.Entry(popup)
        package_entry.pack(pady=5)

        tk.Label(popup, text="Module:").pack(pady=5)
        module_entry = tk.Entry(popup)
        module_entry.pack(pady=5)

        def on_submit():
            package = package_entry.get()
            module = module_entry.get()
            if package and module:
                popup.destroy()
                self.save_package_module_info(package, module)
                self.generate(package, module)
            else:
                messagebox.showwarning("Warning", "Package and Module cannot be empty.")

        submit_btn = tk.Button(popup, text="Submit", command=on_submit)
        submit_btn.pack(pady=10)

    def save_package_module_info(self, package, module):
        try:
            with open("connection_info.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        data.update({"Package": package, "Module": module})

        with open("connection_info.json", "w") as file:
            json.dump(data, file)

    def generate(self, package, module):
        self.log_message("Generating schema...")
        self.show_loading_screen()
        t = threading.Thread(target=self.generate_schema, args=(package, module))
        t.start()

    def show_loading_screen(self):
        self.initial_label.config(text="Loading...")
        self.log_message("Loading...")

    def compile_schema(self):
        schema_text = self.text_area.get("1.0", tk.END).strip()
        example_schema = {
            "type": "object",
            "properties": {
                "TableName": {
                    "type": "object",
                    "properties": {
                        "columns": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "nullable": {"type": "boolean"},
                                    "default": {"type": ["string", "null"]},
                                    "autoincrement": {"type": "boolean"},
                                    "comment": {"type": ["string", "null"]},
                                    "identity": {
                                        "type": ["object", "null"],
                                        "properties": {
                                            "start": {"type": "integer"},
                                            "increment": {"type": "integer"}
                                        },
                                        "required": ["start", "increment"]
                                    }
                                },
                                "required": ["name", "type"]
                            }
                        },
                        "primary_keys": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "constrained_columns": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": ["name", "constrained_columns"]
                        },
                        "foreign_keys": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "columns": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "referenced_table": {"type": "string"},
                                    "referenced_columns": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "indexes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "columns": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "unique": {"type": "boolean"}
                                }
                            }
                        }
                    },
                    "required":

 ["columns", "primary_keys"]
                }
            },
            "required": ["TableName"]
        }

        schema_text = schema_text.rstrip()
        try:
            schema = json.loads(schema_text)
            validate(instance=schema, schema=example_schema)  # Validate an empty instance against the schema
            self.compiled_successfully = True
            self.is_schema_valid = True
            self.generate_btn.config(state=tk.NORMAL)
            self.log_message("JSON schema is valid and compiled successfully.")
        except json.JSONDecodeError:
            self.compiled_successfully = False
            messagebox.showerror("Json compiler error", "Invalid JSON format.")
        except ValidationError as e:
            self.compiled_successfully = False
            messagebox.showerror("Json compiler error", f"Schema validation error: {e.message}")
        except Exception as e:
            self.compiled_successfully = False
            messagebox.showerror("Json compiler error", f"Compilation error: {str(e)}")

    def import_schema(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                self.import_schema_from_file(file_path)
            except Exception as e:
                messagebox.showerror("Error", "Failed to import JSON file.")

    def edit_json(self):
        self.text_area.config(state=tk.NORMAL)
        self.log_message("JSON text area is now editable.")

    def download_schema(self):
        if not self.is_schema_valid:
            messagebox.showwarning("Warning", "Compile the schema first.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            schema_text = self.text_area.get("1.0", tk.END).strip()
            with open(file_path, "w") as file:
                file.write(schema_text)
            self.log_message("JSON schema downloaded successfully.")

    def reset_text(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, "Imported JSON will be shown here.")
        self.text_area.config(state=tk.DISABLED)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.initial_label.config(text="Output Screen")
        self.log_message("Reset the text area.")

    def generate_schema(self, package, module):
        steps = ["Generating classes...", "Generating entity...", "Generating repository..."]
        for step in steps:
            self.log_message(step)
            time.sleep(1)  # Simulate the time taken for each step

        try:
            with open("apilogs.json", "r") as file:
                schema = file.read()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.delete("1.0", tk.END)
                self.log_text.insert(tk.END, schema)
                self.log_text.config(state=tk.DISABLED)
                self.log_message("Schema generation completed.")
        except Exception as e:
            self.log_message("Failed to load generated schema.")
            messagebox.showerror("Error", "Failed to load generated schema.")

    def check_and_compile(self):
        schema_text = self.text_area.get("1.0", tk.END).strip()
        if not schema_text or schema_text == "Imported JSON will be shown here.":
            messagebox.showwarning("Warning", "Please import or enter a JSON schema first.")
        else:
            self.compile_schema()

    def save_schema(self):
        if not self.is_schema_valid:
            messagebox.showwarning("Warning", "Compile the schema first.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            schema_text = self.text_area.get("1.0", tk.END).strip()
            with open(file_path, "w") as file:
                file.write(schema_text)
            self.log_message("JSON schema saved successfully.")


if __name__ == "__main__":
    app = tkinterApp()
    app.mainloop()
