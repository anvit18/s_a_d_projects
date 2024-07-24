import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, ttk
import threading
import time

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Database Schema Generator")
        self.root.geometry("900x600")
        self.schema = ""
        self.json_loaded = False
        self.main_frame = None
        self.create_widgets()

    def create_widgets(self):
        # Wells Fargo banner with logo
        banner_frame = tk.Frame(self.root, bg="red")
        banner_frame.pack(fill=tk.X)

        # # Replace 'wells_fargo_logo.png' with the actual path to your logo image
        # logo = tk.PhotoImage(file="wells_fargo_logo.png")
        # logo_label = tk.Label(banner_frame, image=logo, bg="red")
        # logo_label.image = logo  # keep a reference!
        # logo_label.pack(side=tk.LEFT, padx=10, pady=5)

        banner_label = tk.Label(banner_frame, text="WELLS FARGO", bg="red", fg="white", font=("Helvetica", 24))
        banner_label.pack(side=tk.LEFT, padx=10)

        # Thinner yellow line below the red banner
        yellow_banner = tk.Label(self.root, bg="yellow")
        yellow_banner.pack(fill=tk.X, pady=0)

        self.init_main_screen()

    def init_main_screen(self):
        if self.main_frame:
            self.main_frame.destroy()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Database connection string entry
        conn_frame = tk.Frame(self.main_frame)
        conn_frame.pack(fill=tk.X, pady=5)
        self.conn_entry = tk.Entry(conn_frame, width=70)
        self.conn_entry.insert(0, "Database connection string...")
        self.conn_entry.pack(side=tk.LEFT, padx=5)
        connect_btn = tk.Button(conn_frame, text="Connect", command=self.connect_db)
        connect_btn.pack(side=tk.LEFT, padx=5)

        # JSON schema text area
        self.text_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, width=60, height=20)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.text_area.config(state=tk.DISABLED)  # Make text area read-only initially

        # Icon frame beside the text area
        icon_frame = tk.Frame(self.main_frame)
        icon_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))

        # Load icon images (ensure these paths are correct)
        import_icon = tk.PhotoImage(file="import_icon.png")
        edit_icon = tk.PhotoImage(file="edit_icon.png")
        link_icon = tk.PhotoImage(file="link_icon.png")
        download_icon = tk.PhotoImage(file="download_icon.png")

        import_btn = tk.Button(icon_frame, image=import_icon, command=self.import_schema, width=30, height=30)
        import_btn.image = import_icon
        import_btn.pack(pady=5)

        edit_btn = tk.Button(icon_frame, image=edit_icon, command=self.edit_json, width=30, height=30)
        edit_btn.image = edit_icon
        edit_btn.pack(pady=5)

        link_btn = tk.Button(icon_frame, image=link_icon, command=self.add_link, width=30, height=30)
        link_btn.image = link_icon
        link_btn.pack(pady=5)

        download_btn = tk.Button(icon_frame, image=download_icon, command=self.download_schema, width=30, height=30)
        download_btn.image = download_icon
        download_btn.pack(pady=5)

        # Buttons for Save, Generate, Reset
        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        save_btn = tk.Button(btn_frame, text="Save", command=self.save_schema, width=12, height=2)
        save_btn.pack(side=tk.LEFT, padx=5)

        generate_btn = tk.Button(btn_frame, text="Generate", command=self.start_generation, width=12, height=2)
        generate_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = tk.Button(btn_frame, text="Reset", command=self.reset_text, width=12, height=2)
        reset_btn.pack(side=tk.LEFT, padx=5)

    def connect_db(self):
        conn_str = self.conn_entry.get()
        messagebox.showinfo("Connect", f"Connecting to: {conn_str}")

    def save_schema(self):
        if self.json_loaded:
            self.schema = self.text_area.get("1.0", tk.END)
            messagebox.showinfo("Save", "Schema saved within the application.")
        else:
            messagebox.showwarning("Warning", "Please import and edit a schema before saving.")

    def start_generation(self):
        if self.json_loaded:
            self.switch_to_loading_screen()
            threading.Thread(target=self.generate_classes).start()
        else:
            messagebox.showwarning("Warning", "Please import and edit a schema before generating classes.")

    def generate_classes(self):
        loading_messages = [
            "Creating Java classes...",
            "Now calling the API...",
            "Processing data...",
            "Almost done..."
        ]
        for message in loading_messages:
            self.update_loading_message(message)
            time.sleep(2)  # Simulate time taken for each step
        self.display_final_message()

    def update_loading_message(self, message):
        self.loading_label.config(text=message)

    def switch_to_loading_screen(self):
        self.main_frame.destroy()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add loading screen widgets
        self.loading_label = tk.Label(self.main_frame, text="Generating Java classes...", font=("Helvetica", 16))
        self.loading_label.pack(pady=20)

        self.progress_bar = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, padx=20, pady=20)
        self.progress_bar.start()

        back_btn = tk.Button(self.main_frame, text="Back", command=self.init_main_screen, width=12, height=2)
        back_btn.pack(pady=10)

    def display_final_message(self):
        self.progress_bar.stop()
        self.progress_bar.destroy()
        self.loading_label.config(text="Data will be shown here")

    def reset_text(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.config(state=tk.DISABLED)
        self.json_loaded = False

    def import_schema(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                schema = file.read()
            self.text_area.config(state=tk.NORMAL)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, schema)
            self.text_area.config(state=tk.DISABLED)
            self.json_loaded = True
            messagebox.showinfo("Import", f"Schema imported from: {file_path}")

    def edit_json(self):
        if self.json_loaded:
            self.text_area.config(state=tk.NORMAL)
            messagebox.showinfo("Edit", "JSON area is now editable.")
        else:
            messagebox.showwarning("Warning", "Please import a JSON schema before editing.")

    def add_link(self):
        if self.json_loaded:
            link = simpledialog.askstring("Add Link", "Enter the link:")
            if link:
                self.text_area.insert(tk.END, f'"link": "{link}",\n')
        else:
            messagebox.showwarning("Warning", "Please import and edit a JSON schema before adding a link.")

    def download_schema(self):
        if self.json_loaded:
            schema = self.text_area.get("1.0", tk.END)
            file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                     filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(schema)
                messagebox.showinfo("Download", f"Schema downloaded to: {file_path}")
        else:
            messagebox.showwarning("Warning", "Please import and edit a schema before downloading.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
