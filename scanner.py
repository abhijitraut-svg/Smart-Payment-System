import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import qrcode
import datetime
import os
from PIL import Image, ImageTk

#Globals
history_window = None
history_text = None

#Helper Functions

def log_transaction(method, amount):
    """Write a new transaction entry and refresh history if open"""
    # Ensure file exists and append
    with open("transactions.txt", "a", encoding="utf-8") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{now} | Method: {method} | Amount: ₹{amount}\n")
    
    # Refresh GUI history if window is open
    update_history_window()


def update_history_window():
    """Refresh the transaction history window (if open)"""
    global history_text
    if history_text:  # only update if widget exists
        if os.path.exists("transactions.txt"):
            with open("transactions.txt", "r", encoding="utf-8") as f:
                data = f.read()
        else:
            data = "No transaction history found."

        history_text.config(state=tk.NORMAL)
        history_text.delete(1.0, tk.END)
        history_text.insert(tk.END, data)
        history_text.config(state=tk.DISABLED)


def show_transaction_history():
    """Show or bring up the transaction history window"""
    global history_window, history_text

    # If already open, refresh it
    if history_window and tk.Toplevel.winfo_exists(history_window):
        update_history_window()
        history_window.lift()
        return

    history_window = tk.Toplevel(root)
    history_window.title("Transaction History")
    history_window.geometry("460x420")
    history_window.config(bg="#f8f9fa")

    tk.Label(
        history_window,
        text="📜 Transaction History",
        font=("Arial", 14, "bold"),
        bg="#f8f9fa",
    ).pack(pady=10)

    history_text = scrolledtext.ScrolledText(
        history_window, width=55, height=20, wrap=tk.WORD, font=("Arial", 10)
    )
    history_text.pack(padx=10, pady=10)

    # Enable live refresh every 2 seconds
    def auto_refresh():
        update_history_window()
        if tk.Toplevel.winfo_exists(history_window):
            history_window.after(2000, auto_refresh)

    auto_refresh()  # Start periodic refresh


def generate_qr():
    """Generate and display UPI QR code"""
    upi_id = upi_entry.get().strip()
    if not upi_id:
        messagebox.showerror("Error", "Please enter your UPI ID first!")
        return

    app_choice = app_var.get()
    amount = simpledialog.askstring("Payment Amount", f"Enter amount for {app_choice}: ₹")
    if not amount:
        return

    # Create UPI payment URL and QR code
    url = f"upi://pay?pa={upi_id}&pn=Recipient%20Name&am={amount}"
    qr = qrcode.make(url)
    qr.save("temp_qr.png")

    # Show QR image
    qr_img = Image.open("temp_qr.png").resize((200, 200))
    qr_photo = ImageTk.PhotoImage(qr_img)

    qr_window = tk.Toplevel(root)
    qr_window.title(f"{app_choice} QR Code")
    qr_window.config(bg="white")

    tk.Label(
        qr_window,
        text=f"{app_choice} Payment QR",
        font=("Arial", 14, "bold"),
        bg="white",
    ).pack(pady=10)
    tk.Label(qr_window, image=qr_photo, bg="white").pack(pady=5)
    qr_window.qr_photo = qr_photo  # prevent garbage collection

    messagebox.showinfo("Success", f"✅ {app_choice} QR Code generated successfully!")
    log_transaction(app_choice, amount)


def pay_cash():
    """Handle cash payment"""
    amount = simpledialog.askstring("Cash Payment", "Enter cash payment amount: ₹")
    if amount:
        messagebox.showinfo("Success", f"💵 Cash payment of ₹{amount} recorded successfully!")
        log_transaction("Cash", amount)


#GUI SETUP
root = tk.Tk()
root.title("💳 Smart Payment System")
root.geometry("500x520")
root.config(bg="#e9ecef")

tk.Label(
    root, text="Smart Payment System", font=("Arial", 18, "bold"), bg="#e9ecef", fg="#212529"
).pack(pady=20)

tk.Label(root, text="Enter your UPI ID:", font=("Arial", 12), bg="#e9ecef").pack()
upi_entry = tk.Entry(root, width=35, font=("Arial", 12))
upi_entry.pack(pady=5)

tk.Label(root, text="Select Payment App:", font=("Arial", 12), bg="#e9ecef").pack(pady=10)
app_var = tk.StringVar(value="PhonePe")

frame = tk.Frame(root, bg="#e9ecef")
frame.pack()
for app in ["PhonePe", "Paytm", "Google Pay"]:
    tk.Radiobutton(frame, text=app, variable=app_var, value=app, bg="#e9ecef", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)

tk.Button(root, text="📱 Pay via QR", command=generate_qr, width=18, bg="#007bff", fg="white", font=("Arial", 12, "bold")).pack(pady=15)
tk.Button(root, text="💵 Pay by Cash", command=pay_cash, width=18, bg="#28a745", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
tk.Button(root, text="📜 View History", command=show_transaction_history, width=18, bg="#6c757d", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
tk.Button(root, text="❌ Exit", command=root.quit, width=18, bg="#dc3545", fg="white", font=("Arial", 12, "bold")).pack(pady=20)

root.mainloop()