import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from tkcalendar import DateEntry
import sqlite3

# Database setup
def connect_db():
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

# Add description column if it doesn't exist
def add_description_column():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(bookings)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'description' not in columns:
        cursor.execute("ALTER TABLE bookings ADD COLUMN description TEXT")
        conn.commit()
    conn.close()

# Show bookings for a specific date
def show_bookings(booking_date, tree):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE booking_date = ?", (booking_date,))
    bookings = cursor.fetchall()
    
    for booking in tree.get_children():
        tree.delete(booking)  # Clear existing entries
    
    if bookings:
        for booking in bookings:
            tree.insert('', 'end', values=booking)
    else:
        messagebox.showinfo("Info", f"No bookings found for {booking_date}.")
    
    conn.close()

# View bookings by date
def view_bookings_by_date():
    view_window = tk.Toplevel()
    view_window.title("View Bookings by Date")

    tk.Label(view_window, text="Select Booking Date:").grid(row=0, column=0, padx=5, pady=5)
    cal = DateEntry(view_window)
    cal.grid(row=0, column=1, padx=5, pady=5)

    tree = ttk.Treeview(view_window, columns=('ID', 'Date', 'Start Time', 'End Time', 'Booked By', 'Description'), show='headings')
    tree.heading('ID', text='ID')
    tree.heading('Date', text='Date')
    tree.heading('Start Time', text='Start Time')
    tree.heading('End Time', text='End Time')
    tree.heading('Booked By', text='Booked By')
    tree.heading('Description', text='Description')
    
    tree.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

    # Configure grid weights to allow for resizing
    view_window.grid_rowconfigure(2, weight=1)
    view_window.grid_columnconfigure(1, weight=1)

    tk.Button(view_window, text="Show Bookings", command=lambda: show_bookings(cal.get_date(), tree)).grid(row=1, columnspan=2, pady=10)

# View all bookings
def view_all_bookings():
    view_window = tk.Toplevel()
    view_window.title("Current Bookings")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings")
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

from datetime import datetime

# Book a hall
def book_hall():
    book_window = tk.Toplevel()
    book_window.title("Book Hall")

    tk.Label(book_window, text="Select Booking Date:").grid(row=0, column=0, padx=5, pady=5)
    cal = DateEntry(book_window)
    cal.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(book_window, text="Select Start Time:").grid(row=1, column=0, padx=5, pady=5)
    start_time_entry = tk.Entry(book_window)
    start_time_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(book_window, text="Select End Time:").grid(row=2, column=0, padx=5, pady=5)
    end_time_entry = tk.Entry(book_window)
    end_time_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(book_window, text="Booked By:").grid(row=3, column=0, padx=5, pady=5)
    booked_by_entry = tk.Entry(book_window)
    booked_by_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(book_window, text="Description:").grid(row=4, column=0, padx=5, pady=5)
    description_text = tk.Text(book_window, height=5, width=30)  # Adjust height and width as needed
    description_text.grid(row=4, column=1, padx=5, pady=5)

    def submit_booking():
        booking_date = cal.get_date()
        start_time = start_time_entry.get()
        end_time = end_time_entry.get()
        booked_by = booked_by_entry.get()
        description = description_entry.get()

        # Prevent booking for today or past dates
        if booking_date < datetime.now().date():
            messagebox.showerror("Booking Error", "Cannot book for past dates.")
            return
        if booking_date == datetime.now().date():
            messagebox.showerror("Booking Error", "Cannot book for today.")
            return

        if not booked_by or not start_time or not end_time:
            messagebox.showerror("Input Error", "All fields are required!")
            return
        
        # Check if the time slot is available
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE booking_date = ? AND ((start_time < ? AND end_time > ?) OR (start_time < ? AND end_time > ?))", 
                       (booking_date, end_time, start_time, start_time, end_time))
        
        if cursor.fetchone():
            messagebox.showerror("Booking Error", "Time slot is already booked!")
        else:
            cursor.execute("INSERT INTO bookings (booking_date, start_time, end_time, booked_by, description) VALUES (?, ?, ?, ?, ?)",
                           (booking_date, start_time, end_time, booked_by, description))
            conn.commit()
            messagebox.showinfo("Success", "Booking successful!")
            book_window.destroy()
        
        conn.close()

    tk.Button(book_window, text="Book Hall", command=submit_booking).grid(row=5, columnspan=2, pady=10)



# Cancel a booking
def cancel_booking():
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


from PIL import Image, ImageTk  # Import Image and ImageTk from PIL

# Main application window
def main_window():
    add_description_column()  # Ensure the description column exists

    window = tk.Tk()
    window.title("NDRI Hall Booking")
    window.geometry("400x400")

    # Load the logo image and resize it
    original_logo = Image.open("NDRI-logo.png")  # Load the logo
    logo = original_logo.resize((350, 100), Image.LANCZOS)  # Resize the logo to 100x100 pixels
    logo_image = ImageTk.PhotoImage(logo)  # Convert it to a Tkinter-compatible image

    logo_label = tk.Label(window, image=logo_image)
    logo_label.image = logo_image  # Keep a reference to avoid garbage collection
    logo_label.pack(pady=10)

    title_label = tk.Label(window, text="NDRI Hall Booking", font=("Arial", 16))
    title_label.pack(pady=10)

    button_frame = tk.Frame(window)
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="View Bookings by Date", command=view_bookings_by_date, width=20).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="View All Bookings", command=view_all_bookings, width=20).grid(row=0, column=1, padx=10)
    tk.Button(button_frame, text="Book Hall", command=book_hall, width=20).grid(row=1, column=0, padx=10)
    tk.Button(button_frame, text="Cancel Booking", command=cancel_booking, width=20).grid(row=1, column=1, padx=10)

    window.mainloop()


if __name__ == "__main__":
    main_window()
