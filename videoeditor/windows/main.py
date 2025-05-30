import tkinter as tk
from tkinter import filedialog, messagebox, LEFT, Listbox, Scrollbar, END, PhotoImage
import customtkinter as ctk
import os
from videoeditor.outils import download_video, prepare_and_merge_ffmpeg, delete_video
from videoeditor.windows.variables import Styles, Variables


def build_interface(window):
    def select_video():
        file_path = filedialog.askopenfilename(
            title="Выберите видео",
            filetypes=[("Видео файлы", "*.mp4"), ("Все файлы", "*.*")]
        )
        if file_path:
            loop_entry.delete(0, END)
            loop_entry.insert(0, file_path)

    def select_directory_for_video():
        directory = filedialog.askdirectory(
            title="Выберите папку для сохранения",
            initialdir=os.path.expanduser("~")  # Начинаем с домашней директории
        )
        if directory:
            directory_entry.delete(0, END)
            directory_entry.insert(0, directory)

    def start():
        url = url_entry.get()
        loop = loop_entry.get()
        directoryToExport = directory_entry.get()
        if not url or not loop:
            messagebox.showerror("Ошибка", "Введите ссылку и выберите файл")
            return
        if not directoryToExport:
            messagebox.showerror("Ошибка", "Выберите папку для сохранения")
            return
        try:
            video_path = download_video(url, "videos")
            output_path = os.path.join(directoryToExport, "output.mp4")
            prepare_and_merge_ffmpeg(video_path, loop, output_path)
            messagebox.showinfo("Готово", f"Видео сохранено в {output_path}")
            delete_video(video_path)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # Элементы
    frame = tk.Frame(window, bg=Styles.BACKGROUND)

    tk.Label(frame, text="Смонтировать видео:", font=("LexendDeca", 20), bg=Styles.BACKGROUND, fg=Styles.COLOR_TEXT).pack(anchor='nw')
    tk.Label(frame, text="Видео с ютуб:", font=("Courrier", 10), bg=Styles.BACKGROUND, fg=Styles.COLOR_TEXT).pack(anchor='nw')
    
    url_entry = ctk.CTkEntry(frame, width=800, height=40, corner_radius=10, state="normal", text_color=Styles.COLOR_TEXT)
    url_entry.pack(anchor='nw', fill='x', pady=(0, 10))

    tk.Label(frame, text="Выберите комбинируемое видео", font=("Courrier", 10), bg=Styles.BACKGROUND, fg=Styles.COLOR_TEXT).pack(anchor='nw')
    
    # Создаем фрейм для кнопки и поля ввода
    file_frame = tk.Frame(frame, bg=Styles.BACKGROUND)
    file_frame.pack(fill='x', pady=(0, 10))
    
    loop_entry = ctk.CTkEntry(file_frame, width=600, height=40, corner_radius=10)
    loop_entry.pack(side='left', padx=(0, 10), fill='x', expand=True)
    
    select_button = ctk.CTkButton(file_frame, text="Выбрать видео", command=select_video, height=40, fg_color=Styles.COLOR_BUTTON)
    select_button.pack(side='left')

    tk.Label(frame, text="Папка для сохранения", font=("Courrier", 10), bg=Styles.BACKGROUND, fg=Styles.COLOR_TEXT).pack(anchor='nw')
    
    # Создаем фрейм для кнопки и поля ввода директории
    directory_frame = tk.Frame(frame, bg=Styles.BACKGROUND)
    directory_frame.pack(fill='x', pady=(0, 10))
    
    directory_entry = ctk.CTkEntry(directory_frame, width=600, height=40, corner_radius=10)
    directory_entry.pack(side='left', padx=(0, 10), fill='x', expand=True)
    
    select_directory_button = ctk.CTkButton(directory_frame, text="Выбрать папку", command=select_directory_for_video, height=40, fg_color=Styles.COLOR_BUTTON)
    select_directory_button.pack(side='left')

    submit_button = ctk.CTkButton(frame, text="Смонтировать", command=start, height=40, fg_color=Styles.COLOR_BUTTON)
    submit_button.pack(pady=10)


    frame.pack(anchor='nw', padx=10, pady=10)
