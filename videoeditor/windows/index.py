import tkinter as tk
from videoeditor.windows.main import build_interface
from videoeditor.variables import Styles

def main():
    window = tk.Tk()
    window.title("Erik Video Editor")
    window.geometry("800x500")
    window.config(background=Styles.BACKGROUND)

    build_interface(window)
    window.mainloop()

if __name__ == "__main__":
    main()


