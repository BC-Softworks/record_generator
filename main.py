import record_constant.*
import tkinter as tk

# Create window
window = tk.Tk()
window.title('Record Generator')
label = tk.Label(text="Wav file")
entry = tk.Entry()
label.pack()
entry.pack()
button = tk.Button(
    text="Generate",
    width=25,
    height=5,
)
button.pack()
window.mainloop()
