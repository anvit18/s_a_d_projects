import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def compile_and_run_java_app():
    try:
        # Path to your Java file
        java_file_path = "path/to/your/JavaFile.java"
        
        # Compile the Java file
        compile_command = ["javac", java_file_path]
        subprocess.run(compile_command, check=True)
        
        # Get the directory and the filename without extension
        java_file_dir = os.path.dirname(java_file_path)
        java_file_name = os.path.basename(java_file_path).replace(".java", "")
        
        # Change directory to the Java file location
        os.chdir(java_file_dir)
        
        # Run the compiled Java class
        run_command = ["java", java_file_name]
        subprocess.Popen(run_command)
        
        # Show a success message
        messagebox.showinfo("Success", "Java application launched successfully!")
    except subprocess.CalledProcessError as e:
        # Show an error message if compilation fails
        messagebox.showerror("Compilation Error", f"Failed to compile Java application: {e}")
    except Exception as e:
        # Show an error message if something else goes wrong
        messagebox.showerror("Error", f"Failed to launch Java application: {e}")

# Create the main window
root = tk.Tk()
root.title("Java App Launcher")

# Create a button to compile and run the Java application
launch_button = tk.Button(root, text="Compile and Run Java App", command=compile_and_run_java_app)
launch_button.pack(pady=20)

# Start the GUI event loop
root.mainloop()