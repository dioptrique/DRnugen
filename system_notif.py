import subprocess
import tkinter as tk
from tkinter import scrolledtext

def notify_linux(title, message):
    subprocess.run(["notify-send", title, message])



def popup_text(title, text):
    root = tk.Tk()
    root.title(title)
    root.geometry('400x200')
    txt = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    txt.pack(expand=True, fill='both')
    txt.insert(tk.END, text)
    txt.configure(state='disabled')  # read-only
    root.mainloop()

#popup_text("💡 Dr Nugen", "Claim: Lemon water boosts metabolism\nAccuracy: 40%\nExplanation: While hydration may help slightly, there's no strong evidence that lemon itself improves metabolism.")
#notify_linux("💡 Dr Nugen", "Claim: Lemon water boosts metabolism\nAccuracy: 40%")
