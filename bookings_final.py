import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import os
from PIL import Image, ImageTk

# --- Database Setup and Utility Functions ---
def connect_db():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect('hall_booking.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            booked_by TEXT NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    return conn

def add_description_column():
    """Ensure the 'description' column exists in the bookings table."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(bookings)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'description' not in columns:
        cursor.execute("ALTER TABLE bookings ADD COLUMN description TEXT")
        conn.commit()
    conn.close()

# --- Booking Functions ---

def convert_to_24hr_format(time_str):
    """Convert 12-hour time format to 24-hour format."""
    return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")

def generate_time_options():
    """Generate time options in 12-hour format with AM/PM."""
    times = []
    for hour in range(8, 18):  # From 8 AM to 6 PM
        for minute in [0, 30]:  # Every half hour
            time_str = f"{hour % 12 or 12}:{minute:02d} {'AM' if hour < 12 else 'PM'}"
            times.append(time_str)
    return times

def show_bookings(booking_date, tree):
    """Display bookings for a specific date, ordered by start time."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE booking_date = ? ORDER BY start_time ASC", (booking_date,))
    bookings = cursor.fetchall()
    
    for booking in tree.get_children():
        tree.delete(booking)  # Clear existing entries
    
    if bookings:
        for booking in bookings:
            tree.insert('', 'end', values=booking)
    else:
        messagebox.showinfo("Info", f"No bookings found for {booking_date}.")
    
    conn.close()

def view_bookings_by_date():
    """Open a window to view bookings for a selected date."""
    view_window = tk.Toplevel()
    view_window.title("View Bookings by Date")
    view_window.configure(bg="#f3f4f6")

    tk.Label(view_window, text="Select Booking Date:", bg="#f3f4f6", font=("Segoe UI", 12)).grid(row=0, column=0, padx=10, pady=10)
    cal = DateEntry(view_window, font=("Segoe UI", 12), width=12)
    cal.grid(row=0, column=1, padx=10, pady=10)

    tree = ttk.Treeview(view_window, columns=('ID', 'Date', 'Start Time', 'End Time', 'Booked By', 'Description'), show='headings')
    tree.heading('ID', text='ID')
    tree.heading('Date', text='Date')
    tree.heading('Start Time', text='Start Time')
    tree.heading('End Time', text='End Time')
    tree.heading('Booked By', text='Booked By')
    tree.heading('Description', text='Description')
    tree.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

    tk.Button(view_window, text="Show Bookings", command=lambda: show_bookings(cal.get_date(), tree), bg="#0078d4", fg="white", font=("Segoe UI", 12)).grid(row=1, columnspan=2, pady=10)
    tk.Button(view_window, text="Print Bookings", command=lambda: print_bookings(tree), bg="#0078d4", fg="white", font=("Segoe UI", 12)).grid(row=3, columnspan=2, pady=10)

def view_all_bookings():
    """Open a window to view all bookings, ordered by start time."""
    view_window = tk.Toplevel()
    view_window.title("Current Bookings")
    view_window.configure(bg="#f3f4f6")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings ORDER BY start_time ASC")  # Order by start time
    bookings = cursor.fetchall()

    tree = ttk.Treeview(view_window, columns=('ID', 'Date', 'Start Time', 'End Time', 'Booked By', 'Description'), show='headings')
    tree.heading('ID', text='ID')
    tree.heading('Date', text='Date')
    tree.heading('Start Time', text='Start Time')
    tree.heading('End Time', text='End Time')
    tree.heading('Booked By', text='Booked By')
    tree.heading('Description', text='Description')
    tree.pack(fill=tk.BOTH, expand=True)

    for booking in bookings:
        tree.insert('', 'end', values=booking)
    
    if not bookings:
        messagebox.showinfo("Info", "No current bookings.")

    conn.close()

    tk.Button(view_window, text="Print Bookings", command=lambda: print_bookings(tree), bg="#0078d4", fg="white", font=("Segoe UI", 12)).pack(pady=10)

def book_hall():
    """Open a window to book a hall with date, time, and other details."""
    book_window = tk.Toplevel()
    book_window.title("Book Hall")
    book_window.configure(bg="#f3f4f6")

    tk.Label(book_window, text="Select Booking Date:", bg="#f3f4f6", font=("Segoe UI", 12)).grid(row=0, column=0, padx=10, pady=10)
    cal = DateEntry(book_window, font=("Segoe UI", 12), width=12)
    cal.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(book_window, text="Select Start Time:", bg="#f3f4f6", font=("Segoe UI", 12)).grid(row=1, column=0, padx=10, pady=10)
    start_time_combo = ttk.Combobox(book_window, values=generate_time_options(), font=("Segoe UI", 12), state="readonly")
    start_time_combo.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(book_window, text="Select End Time:", bg="#f3f4f6", font=("Segoe UI", 12)).grid(row=2, column=0, padx=10, pady=10)
    end_time_combo = ttk.Combobox(book_window, values=generate_time_options(), font=("Segoe UI", 12), state="readonly")
    end_time_combo.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(book_window, text="Booked By:", bg="#f3f4f6", font=("Segoe UI", 12)).grid(row=3, column=0, padx=10, pady=10)
    booked_by_entry = tk.Entry(book_window, font=("Segoe UI", 12))
    booked_by_entry.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(book_window, text="Description:", bg="#f3f4f6", font=("Segoe UI", 12)).grid(row=4, column=0, padx=10, pady=10)
    description_text = tk.Text(book_window, height=5, width=30, font=("Segoe UI", 12))
    description_text.grid(row=4, column=1, padx=10, pady=10)

    def submit_booking():
        """Submit a new booking to the database."""
        booking_date = cal.get_date()
        start_time = start_time_combo.get()
        end_time = end_time_combo.get()
        booked_by = booked_by_entry.get()
        description = description_text.get("1.0", tk.END).strip()

        # Convert times to 24-hour format
        start_time_24hr = convert_to_24hr_format(start_time)
        end_time_24hr = convert_to_24hr_format(end_time)

        # Prevent booking for past dates
        if booking_date < datetime.now().date():
            messagebox.showerror("Booking Error", "Cannot book for past dates.")
            return

        if not booked_by or not start_time or not end_time:
            messagebox.showerror("Input Error", "All fields are required!")
            return
        
        # Check if the time slot is available
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE booking_date = ? AND ((start_time < ? AND end_time > ?) OR (start_time < ? AND end_time > ?))", 
                       (booking_date, end_time_24hr, start_time_24hr, start_time_24hr, end_time_24hr))
        
        if cursor.fetchone():
            messagebox.showerror("Booking Error", "Time slot is already booked!")
        else:
            cursor.execute("INSERT INTO bookings (booking_date, start_time, end_time, booked_by, description) VALUES (?, ?, ?, ?, ?)",
                           (booking_date, start_time_24hr, end_time_24hr, booked_by, description))
            conn.commit()
            messagebox.showinfo("Success", "Booking successful!")
            book_window.destroy()
        
        conn.close()

    tk.Button(book_window, text="Book Hall", command=submit_booking, bg="#0078d4", fg="white", font=("Segoe UI", 12)).grid(row=5, columnspan=2, pady=10)

# --- Cancel Booking ---
def cancel_booking():
    """Cancel an existing booking by its ID."""
    booking_id = simpledialog.askinteger("Input", "Enter the booking ID to cancel:")
    
    if booking_id is None:
        return
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    
    if cursor.rowcount == 0:
        messagebox.showerror("Cancel Error", "No booking found with that ID.")
    else:
        conn.commit()
        messagebox.showinfo("Success", "Booking canceled successfully.")
    
    conn.close()

# --- Print Bookings ---
def print_bookings(tree):
    """Print all bookings displayed in the treeview to a text file."""
    bookings = ""
    for booking in tree.get_children():
        booking_data = tree.item(booking)['values']
        bookings += f"ID: {booking_data[0]}, Date: {booking_data[1]}, Start Time: {booking_data[2]}, End Time: {booking_data[3]}, Booked By: {booking_data[4]}, Description: {booking_data[5]}\n"
    
    if bookings:
        with open("bookings_report.txt", "w") as f:
            f.write(bookings)
        messagebox.showinfo("Success", "Bookings printed to bookings_report.txt")
    else:
        messagebox.showinfo("Info", "No bookings to print.")

# --- Main Application Window ---
def main_window():
    """Main window setup and event loop."""
    add_description_column()  # Ensure the description column exists

    window = tk.Tk()
    window.title("NDRI Hall Booking")
    window.geometry("500x400")
    window.configure(bg="#f3f4f6")

    # Load the logo image and resize it
    logo_path = r"C:\Users\ndri2\OneDrive - Nepal Development Research Institute\Desktop\Hall Booking App\NDRI-logo.png"
    if os.path.exists(logo_path):
        original_logo = Image.open(logo_path)
        logo = original_logo.resize((350, 100), Image.LANCZOS)
        logo_image = ImageTk.PhotoImage(logo)

        logo_label = tk.Label(window, image=logo_image, bg="#f3f4f6")
        logo_label.image = logo_image  # Keep a reference to avoid garbage collection
        logo_label.pack(pady=10)

    title_label = tk.Label(window, text="NDRI Hall Booking", font=("Segoe UI", 18), bg="#f3f4f6")
    title_label.pack(pady=10)

    button_frame = tk.Frame(window, bg="#f3f4f6")
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="View Bookings by Date", command=view_bookings_by_date, width=20, bg="#0078d4", fg="white", font=("Segoe UI", 12)).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="View All Bookings", command=view_all_bookings, width=20, bg="#0078d4", fg="white", font=("Segoe UI", 12)).grid(row=1, column=0, padx=10)
    tk.Button(button_frame, text="Book Hall", command=book_hall, width=20, bg="#0078d4", fg="white", font=("Segoe UI", 12)).grid(row=1, column=1, padx=10)
    tk.Button(button_frame, text="Cancel Booking", command=cancel_booking, width=20, bg="#0078d4", fg="white", font=("Segoe UI", 12)).grid(row=2, columnspan=2, pady=10)

    window.mainloop()

# Start the application
if __name__ == "__main__":
    main_window()
