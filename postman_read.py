import requests
import tkinter as tk
from tkinter import ttk, scrolledtext

# Function to fetch data from API
def fetch_data():
    url = "https://jsonplaceholder.typicode.com/posts"  # Example API URL
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        display_data(data)
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"Error fetching data: {e}\n")

# Function to display data in the Tkinter window
def display_data(data):
    result_text.delete(1.0, tk.END)  # Clear previous results
    for item in data:
        result_text.insert(tk.END, f"ID: {item['id']}\n")
        result_text.insert(tk.END, f"Title: {item['title']}\n")
        result_text.insert(tk.END, f"Body: {item['body']}\n\n")

# Create the main Tkinter window
root = tk.Tk()
root.title("Postman Results in Tkinter")
root.geometry("800x600")

# Create a frame for better layout
frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

# Create a button to fetch data
fetch_button = ttk.Button(frame, text="Fetch Data", command=fetch_data)
fetch_button.pack(pady=10)

# Create a scrolled text widget to display results
result_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=80, height=30)
result_text.pack(fill=tk.BOTH, expand=True)

# Start the Tkinter event loop
root.mainloop()