import yt_dlp
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import clips_array
from PIL import Image
import os
import subprocess

def download_video(url, output_path):
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'format': 'bestvideo[height>=720][ext=mp4]+bestaudio[ext=m4a]/best[height>=720]',  # Скачиваем лучшее видео и аудио
        'merge_output_format': 'mp4',  # Объединяем в MP4
        'prefer_ffmpeg': True,  # Включаем использование ffmpeg для объединения
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"Ошибка при скачивании видео: {e}")
        raise e

def delete_video(path):
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"Файл {path} успешно удален")
    except Exception as e:
        print(f"Ошибка при удалении файла {path}: {e}")

def prepare_and_merge_ffmpeg(main_path, loop_path, output_path):
    target_width = 1080
    target_full_height = 1920
    target_half_height = target_full_height // 2 # Целевая высота для каждого клипа (960)
    
    # Команда FFmpeg для масштабирования, обрезки/добавления полей и объединения
    # Фильтр complex_filter объяснение:
    # [0:v] - берем видео поток из первого входного файла (main_path)
    # scale=-2:960 - масштабируем высоту до 960, ширину авто (-2 гарантирует четность)
    # crop=1080:960 - обрезаем до 1080x960
    # setsar=1 - устанавливаем соотношение сторон пикселей 1:1
    # [top] - назначаем результат первому выходу фильтра (верхний клип)
    # [1:v] - берем видео поток из второго входного файла (loop_path)
    # scale=1080:-2, crop=1080:960, setsar=1 - то же самое для нижнего клипа
    # [bottom] - назначаем результат второму выходу фильтра (нижний клип)
    # [top][bottom]vstack - вертикально объединяем верхний и нижний клипы
    # [outv] - назначаем результат объединения на выходной видео поток
    
    ffmpeg_command = [
        "ffmpeg",
        "-i", main_path,
        "-stream_loop", "-1",  # Бесконечный цикл для второго входного файла
        "-i", loop_path,
        "-filter_complex",
        f"[0:v]scale=-2:{target_half_height},crop={target_width}:{target_half_height}:x=(iw-{target_width})/2:y=(ih-{target_half_height})/2,setsar=1[top];"
        f"[1:v]scale={target_width}:-2,crop={target_width}:{target_half_height}:x=(iw-{target_width})/2:y=(ih-{target_half_height})/2,setsar=1[bottom];"
        f"[top][bottom]vstack,format=yuv420p[outv]",
        "-map", "[outv]", # Используем обработанный видео поток
        "-map", "0:a?", # Используем аудио поток из первого файла (если есть, '?' делает его необязательным)
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:v", "3000k", # Битрейт видео
        "-r", "30", # FPS
        "-preset", "veryfast", # Пресет скорости
        "-threads", "8",
        "-crf", "25", # Качество
        "-profile:v", "main",
        "-level", "4.0",
        "-movflags", "+faststart",
        "-tune", "fastdecode",
        "-g", "30",
        "-keyint_min", "30",
        "-sc_threshold", "0",
        "-maxrate", "3000k",
        "-bufsize", "6000k",
        "-shortest",  # Ограничиваем длительность длиной первого видео
        output_path
    ]

    print("Запуск команды FFmpeg:")
    print(" ".join(ffmpeg_command))
    
    try:
        result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print("FFmpeg stdout:", result.stdout)
        print("FFmpeg stderr:", result.stderr)
        print("FFmpeg завершен успешно")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения FFmpeg:\n{e.stderr}")
        raise e
    except FileNotFoundError:
        print("Ошибка: FFmpeg не найден. Убедитесь, что FFmpeg установлен и доступен в PATH.")
        raise FileNotFoundError("FFmpeg не найден")
