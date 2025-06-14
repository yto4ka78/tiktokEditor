import tkinter as tk
from tkinter import filedialog, messagebox, LEFT, Listbox, Scrollbar, END, PhotoImage
import customtkinter as ctk
import os
import json
import time
import random
import threading
from videoeditor.middleware import checkName, load_last_outh_path, save_outh_video_path, save_loop_video_path, load_last_loop_path
from videoeditor.outils import cleanup_videos_folder, download_video, delete_video, prepare_and_merge_ffmpeg_70_30, prepare_and_merge_ffmpeg_youTube_blur_bars, prepare_and_merge_ffmpeg_50_50, prepare_and_merge_ffmpeg_30_70, handle_prepare_and_merge_ffmpeg_diagonal_mask, prepare_and_merge_ffmpeg_your_blur_bars, handle_prepare_and_merge_ffmpeg_your_blur_bars
from videoeditor.variables import Styles, Variables


def build_interface(window):
    def select_video():
        last_path = load_last_loop_path()
        initial_dir = os.path.dirname(last_path) if last_path else os.path.expanduser("~")
        
        choice = messagebox.askyesno("Выбор", "Вы хотите выбрать папку с видео?")
        if choice:
            directory = filedialog.askdirectory(
                title="Выберите папку с видео",
                initialdir=initial_dir
            )
            if directory:
                video_files = [f for f in os.listdir(directory) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
                if video_files:
                    random_video = random.choice(video_files)
                    full_path = os.path.join(directory, random_video)
                    loop_entry.delete(0, END)
                    loop_entry.insert(0, full_path)
                    save_loop_video_path(full_path)
                else:
                    messagebox.showerror("Ошибка", "В выбранной папке нет видео файлов")
        else:
            file_path = filedialog.askopenfilename(
                title="Выберите видео",
                filetypes=[("Видео файлы", "*.mp4 *.avi *.mov *.mkv"), ("Все файлы", "*.*")],
                initialdir=initial_dir
            )
            if file_path:
                loop_entry.delete(0, END)
                loop_entry.insert(0, file_path)
                save_loop_video_path(file_path)

    def select_directory_for_video():
        last_path = load_last_outh_path()
        initial_dir = os.path.dirname(last_path) if last_path else os.path.expanduser("~")
        
        directory = filedialog.askdirectory(
            title="Выберите папку для сохранения",
            initialdir=initial_dir
        )
        if directory:
            directory_entry.delete(0, END)
            directory_entry.insert(0, directory)
            save_outh_video_path(directory)

    def start():
        def update_processing_info(text, frame):
            def update():
                for widget in frame.winfo_children():
                    widget.destroy()
                tk.Label(frame, text=text, bg=Styles.BACKGROUND, fg=Styles.COLOR_TEXT, anchor="w", justify="left").pack(fill="both", expand=True)
            frame.after(0, update)

        def run_processing():
            url = url_entry.get()
            loop = loop_entry.get()
            directoryToExport = directory_entry.get()
            
            if not url:
                messagebox.showerror("Ошибка", "Введите ссылку на видео")
                return
                
            if selected.get() != "blur_bars" and not loop:
                messagebox.showerror("Ошибка", "Выберите комбинируемое видео")
                return
                
            if not directoryToExport:
                messagebox.showerror("Ошибка", "Выберите папку для сохранения")
                return

            video_path = download_video(url, "videos", on_update=lambda text: update_processing_info(text, info_of_processing_process))
            output_path = checkName(directoryToExport)
            #output_path = os.path.join(directoryToExport, "output.mp4")
            try:
                match selected.get():
                    case "70_30":
                        prepare_and_merge_ffmpeg_70_30(video_path, loop, output_path, on_update=lambda text: update_processing_info(text, info_of_processing_process))
                    case "50_50":
                        prepare_and_merge_ffmpeg_50_50(video_path, loop, output_path, on_update=lambda text: update_processing_info(text, info_of_processing_process))
                    case "30_70":
                        prepare_and_merge_ffmpeg_30_70(video_path, loop, output_path, on_update=lambda text: update_processing_info(text, info_of_processing_process))
                    case "your_blur_bars":
                        handle_prepare_and_merge_ffmpeg_your_blur_bars(video_path, loop, output_path, on_update=lambda text: update_processing_info(text, info_of_processing_process))
                    case "youTube_blur_bars":
                        prepare_and_merge_ffmpeg_youTube_blur_bars(video_path, output_path, on_update=lambda text: update_processing_info(text, info_of_processing_process))
                    case "line":
                        handle_prepare_and_merge_ffmpeg_diagonal_mask(video_path, loop, output_path, on_update=lambda text: update_processing_info(text, info_of_processing_process))
                    
                delete_video(video_path)
                messagebox.showinfo("Готово", f"Видео сохранено в {output_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        threading.Thread(target=run_processing).start()          



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
    
    # Загружаем последний использованный путь к loop видео
    last_loop = load_last_loop_path()
    if last_loop:
        loop_entry.insert(0, last_loop)
    
    select_button = ctk.CTkButton(file_frame, text="Выбрать видео", command=select_video, height=40, fg_color=Styles.COLOR_BUTTON)
    select_button.pack(side='left')

    tk.Label(frame, text="Папка для сохранения", font=("Courrier", 10), bg=Styles.BACKGROUND, fg=Styles.COLOR_TEXT).pack(anchor='nw')
    
    # Создаем фрейм для кнопки и поля ввода директории
    directory_frame = tk.Frame(frame, bg=Styles.BACKGROUND)
    directory_frame.pack(fill='x', pady=(0, 10))
    
    directory_entry = ctk.CTkEntry(directory_frame, width=600, height=40, corner_radius=10)
    directory_entry.pack(side='left', padx=(0, 10), fill='x', expand=True)
    
    # Загружаем последнюю использованную директорию
    last_directory = load_last_outh_path()
    if last_directory:
        directory_entry.insert(0, last_directory)
    
    select_directory_button = ctk.CTkButton(directory_frame, text="Выбрать папку", command=select_directory_for_video, height=40, fg_color=Styles.COLOR_BUTTON)
    select_directory_button.pack(side='left')

    # Создаем фрейм для выбора режима
    choise_mode = tk.Frame(frame, bg=Styles.BACKGROUND)
    choise_mode.pack(fill='x', pady=(0, 10))

    selected = tk.StringVar(value="70_30")

    mode_frame = tk.Frame(choise_mode, bg=Styles.BACKGROUND)
    mode_frame.pack(fill='x', pady=(0, 10))

    # Фрейм для первой радиокнопки и её изображения
    radio_frame1 = tk.Frame(mode_frame, bg=Styles.BACKGROUND)
    radio_frame1.pack(side='left', pady=(5, 0), padx=10)

    canvas1 = tk.Canvas(radio_frame1, width=100, height=100, bg=Styles.BACKGROUND, highlightthickness=0)
    canvas1.pack()

    try:
        image1 = PhotoImage(file="videoeditor/icons/70_30.png").subsample(6, 6)
        canvas1.image = image1  # Сохраняем ссылку на изображение
        canvas1.create_image(50, 60, anchor='center', image=image1)  # Центрируем изображение

        radio1 = ctk.CTkRadioButton(
            canvas1,
            text="",
            variable=selected,
            value="70_30",
            fg_color=Styles.COLOR_BUTTON,
            border_color=Styles.COLOR_BUTTON,
            hover_color=Styles.COLOR_BUTTON,
        )
        radio1.place(x=40, y=5)  # Размещаем радиокнопку по центру сверху
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")

    # Фрейм для второй радиокнопки и её изображения
    radio_frame2 = tk.Frame(mode_frame, bg=Styles.BACKGROUND)
    radio_frame2.pack(side='left', pady=(5, 0), padx=10)

    canvas2 = tk.Canvas(radio_frame2, width=100, height=100, bg=Styles.BACKGROUND, highlightthickness=0)
    canvas2.pack()

    try:
        image2 = PhotoImage(file="videoeditor/icons/50_50.png").subsample(6, 6)
        canvas2.image = image2  # Сохраняем ссылку на изображение
        canvas2.create_image(50, 60, anchor='center', image=image2)  # Центрируем изображение

        radio2 = ctk.CTkRadioButton(
            canvas2,
            text="",
            variable=selected,
            value="50_50",
            fg_color=Styles.COLOR_BUTTON,
            border_color=Styles.COLOR_BUTTON,
            hover_color=Styles.COLOR_BUTTON,
        )
        radio2.place(x=40, y=5)  # Размещаем радиокнопку по центру сверху
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")

    # Фрейм для третьей радиокнопки и её изображения
    radio_frame3 = tk.Frame(mode_frame, bg=Styles.BACKGROUND)
    radio_frame3.pack(side='left', pady=(5, 0), padx=10)

    canvas3 = tk.Canvas(radio_frame3, width=100, height=100, bg=Styles.BACKGROUND, highlightthickness=0)
    canvas3.pack()

    try:
        image3 = PhotoImage(file="videoeditor/icons/30_70.png").subsample(6, 6)
        canvas3.image = image3  # Сохраняем ссылку на изображение
        canvas3.create_image(50, 60, anchor='center', image=image3)  # Центрируем изображение

        radio3 = ctk.CTkRadioButton(
            canvas3,
            text="",
            variable=selected,
            value="30_70",
            fg_color=Styles.COLOR_BUTTON,
            border_color=Styles.COLOR_BUTTON,
            hover_color=Styles.COLOR_BUTTON,

        )
        radio3.place(x=40, y=5)  # Размещаем радиокнопку по центру сверху
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")

    # Фрейм для четвертой радиокнопки и её изображения
    radio_frame4 = tk.Frame(mode_frame, bg=Styles.BACKGROUND)
    radio_frame4.pack(side='left', pady=(5, 0), padx=10)

    canvas4 = tk.Canvas(radio_frame4, width=100, height=100, bg=Styles.BACKGROUND, highlightthickness=0)
    canvas4.pack()

    try:
        image4 = PhotoImage(file="videoeditor/icons/your_blur_bars.png").subsample(6, 6)
        canvas4.image = image4  # Сохраняем ссылку на изображение
        canvas4.create_image(50, 60, anchor='center', image=image4)  # Центрируем изображение

        radio4 = ctk.CTkRadioButton(
            canvas4,
            text="",
            variable=selected,
            value="your_blur_bars",
            fg_color=Styles.COLOR_BUTTON,
            border_color=Styles.COLOR_BUTTON,
            hover_color=Styles.COLOR_BUTTON,
        )
        radio4.place(x=40, y=5)  # Размещаем радиокнопку по центру сверху
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")


     # Фрейм для пятой радиокнопки и её изображения
    radio_frame5 = tk.Frame(mode_frame, bg=Styles.BACKGROUND)
    radio_frame5.pack(side='left', pady=(5, 0), padx=10)

    canvas5 = tk.Canvas(radio_frame5, width=100, height=100, bg=Styles.BACKGROUND, highlightthickness=0)
    canvas5.pack()

    try:
        image5 = PhotoImage(file="videoeditor/icons/youtube_loop.png").subsample(6, 6)
        canvas5.image = image5  # Сохраняем ссылку на изображение
        canvas5.create_image(50, 60, anchor='center', image=image5)  # Центрируем изображение

        radio5 = ctk.CTkRadioButton(
            canvas5,
            text="",
            variable=selected,
            value="youTube_blur_bars",
            fg_color=Styles.COLOR_BUTTON,
            border_color=Styles.COLOR_BUTTON,
            hover_color=Styles.COLOR_BUTTON,
        )
        radio5.place(x=40, y=5)  # Размещаем радиокнопку по центру сверху
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")

    # Фрейм для шестой радиокнопки и её изображения
    radio_frame6 = tk.Frame(mode_frame, bg=Styles.BACKGROUND)
    radio_frame6.pack(side='left', pady=(5, 0), padx=10)

    canvas6 = tk.Canvas(radio_frame6, width=100, height=100, bg=Styles.BACKGROUND, highlightthickness=0)
    canvas6.pack()

    try:
        image6 = PhotoImage(file="videoeditor/icons/line.png").subsample(6, 6)
        canvas6.image = image6  # Сохраняем ссылку на изображение
        canvas6.create_image(50, 60, anchor='center', image=image6)  # Центрируем изображение

        radio6 = ctk.CTkRadioButton(
            canvas6,
            text="",
            variable=selected,
            value="line",
            fg_color=Styles.COLOR_BUTTON,
            border_color=Styles.COLOR_BUTTON,
            hover_color=Styles.COLOR_BUTTON,
        )
        radio6.place(x=40, y=5)  # Размещаем радиокнопку по центру сверху
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")

    info_of_processing_process = tk.Frame(frame, bg=Styles.BACKGROUND)
    info_of_processing_process.pack(fill="both", expand=True)
    
    submit_button = ctk.CTkButton(frame, text="Смонтировать", command=start, height=40, fg_color=Styles.COLOR_BUTTON)
    submit_button.pack(pady=10)

    frame.pack(anchor='nw', padx=10, pady=10)
