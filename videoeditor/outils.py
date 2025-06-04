import yt_dlp
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import clips_array
from PIL import Image
import os
import time
import subprocess

def download_video(url, output_path):

    cleanup_videos_folder(output_path)

    video_path = os.path.join(output_path, "video.mp4")
    audio_path = os.path.join(output_path, "с")
    final_output = os.path.join(output_path, "merged.mp4")

    # 1. Скачиваем видео
    ydl_video_opts = {
        'outtmpl': video_path,
        'format': '136',
        'overwrites': True,
        'restrictfilenames': True
    }

    # 2. Скачиваем аудио
    ydl_audio_opts = {
        'outtmpl': audio_path,
        'format': '140',
        'overwrites': True,
        'restrictfilenames': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_video_opts) as ydl:
            ydl.download([url])
        with yt_dlp.YoutubeDL(ydl_audio_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"❌ Ошибка при скачивании: {e}")
        raise e

    # 3. Объединяем через ffmpeg
    try:
        subprocess.run([
            "ffmpeg",
            "-y",  # перезапись без подтверждения
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            final_output
        ], check=True)

        os.remove(video_path)
        os.remove(audio_path)
        print(f"✅ Объединено в: {final_output}")
        return final_output
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка ffmpeg при объединении: {e}")
        raise e


def cleanup_videos_folder(folder_path="videos"):
    print("🧹 Очистка папки перед скачиванием...")
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"🗑️ Удалён: {file_path}")
        except Exception as e:
            print(f"❌ Не удалось удалить {file_path}: {e}")
    print("✨ Очистка завершена")

def delete_video(path):
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"Файл {path} успешно удален")
    except Exception as e:
        print(f"Ошибка при удалении файла {path}: {e}")

def prepare_and_merge_ffmpeg_70_30(main_path, loop_path, output_path):
    target_width = 1080
    target_full_height = 1920
    target_top_height = int(target_full_height * 0.7)  # 70% от полной высоты (1344)
    target_bottom_height = target_full_height - target_top_height  # 30% от полной высоты (576)
    
    # Команда FFmpeg для масштабирования, обрезки/добавления полей и объединения
    # Фильтр complex_filter объяснение:
    # [0:v] - берем видео поток из первого входного файла (main_path)
    # scale=-2:1344 - масштабируем высоту до 1344, ширину авто (-2 гарантирует четность)
    # crop=1080:1344 - обрезаем до 1080x1344
    # setsar=1 - устанавливаем соотношение сторон пикселей 1:1
    # [top] - назначаем результат первому выходу фильтра (верхний клип)
    # [1:v] - берем видео поток из второго входного файла (loop_path)
    # scale=1080:-2, crop=1080:576, setsar=1 - то же самое для нижнего клипа
    # [bottom] - назначаем результат второму выходу фильтра (нижний клип)
    # [top][bottom]vstack - вертикально объединяем верхний и нижний клипы
    # [outv] - назначаем результат объединения на выходной видео поток
    
    ffmpeg_command = [
        "ffmpeg",
        "-i", main_path,
        "-stream_loop", "-1",  # Бесконечный цикл для второго входного файла
        "-i", loop_path,
        "-filter_complex",
        f"[0:v]scale=-2:{target_top_height},crop={target_width}:{target_top_height}:x=(iw-{target_width})/2:y=(ih-{target_top_height})/2,setsar=1[top];"
        f"[1:v]scale={target_width}:-2,crop={target_width}:{target_bottom_height}:x=(iw-{target_width})/2:y=(ih-{target_bottom_height})/2,setsar=1[bottom];"
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

def prepare_and_merge_ffmpeg_50_50(main_path, loop_path, output_path):
    target_width = 1080
    target_full_height = 1920
    target_half_height = target_full_height // 2  # 50% от полной высоты (960)
    
    ffmpeg_command = [
        "ffmpeg",
        "-i", main_path,
        "-stream_loop", "-1",
        "-i", loop_path,
        "-filter_complex",
        f"[0:v]scale=-2:{target_half_height},crop={target_width}:{target_half_height}:x=(iw-{target_width})/2:y=(ih-{target_half_height})/2,setsar=1[top];"
        f"[1:v]scale={target_width}:-2,crop={target_width}:{target_half_height}:x=(iw-{target_width})/2:y=(ih-{target_half_height})/2,setsar=1[bottom];"
        f"[top][bottom]vstack,format=yuv420p[outv]",
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:v", "3000k",
        "-r", "30",
        "-preset", "veryfast",
        "-threads", "8",
        "-crf", "25",
        "-profile:v", "main",
        "-level", "4.0",
        "-movflags", "+faststart",
        "-tune", "fastdecode",
        "-g", "30",
        "-keyint_min", "30",
        "-sc_threshold", "0",
        "-maxrate", "3000k",
        "-bufsize", "6000k",
        "-shortest",
        output_path
    ]

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

def prepare_and_merge_ffmpeg_30_70(main_path, loop_path, output_path):
    target_width = 1080
    target_full_height = 1920
    target_top_height = int(target_full_height * 0.3)  # 30% от полной высоты (576)
    target_bottom_height = target_full_height - target_top_height  # 70% от полной высоты (1344)
    
    ffmpeg_command = [
        "ffmpeg",
        "-i", main_path,
        "-stream_loop", "-1",
        "-i", loop_path,
        "-filter_complex",
        f"[0:v]scale=-2:{target_top_height},crop={target_width}:{target_top_height}:x=(iw-{target_width})/2:y=(ih-{target_top_height})/2,setsar=1[top];"
        f"[1:v]scale={target_width}:-2,crop={target_width}:{target_bottom_height}:x=(iw-{target_width})/2:y=(ih-{target_bottom_height})/2,setsar=1[bottom];"
        f"[top][bottom]vstack,format=yuv420p[outv]",
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:v", "3000k",
        "-r", "30",
        "-preset", "veryfast",
        "-threads", "8",
        "-crf", "25",
        "-profile:v", "main",
        "-level", "4.0",
        "-movflags", "+faststart",
        "-tune", "fastdecode",
        "-g", "30",
        "-keyint_min", "30",
        "-sc_threshold", "0",
        "-maxrate", "3000k",
        "-bufsize", "6000k",
        "-shortest",
        output_path
    ]

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

def prepare_and_merge_ffmpeg_blur_bars(main_path, output_path):
    ffmpeg_command = [
        "ffmpeg",
        "-i", main_path,
        "-filter_complex",
        (
            "[0:v]split=2[bg][fg];"
            "[bg]scale=1080:1920,boxblur=20:1[blurred];"
            "[fg]scale=iw*min(1080/iw\\,1920/ih):ih*min(1080/iw\\,1920/ih),setsar=1[main];"
            "[blurred][main]overlay=(W-w)/2:(H-h)/2,format=yuv420p[outv]"
        ),
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:v", "3500k",
        "-r", "30",
        "-preset", "veryfast",
        "-crf", "23",
        "-profile:v", "high",
        "-level", "4.0",
        "-movflags", "+faststart",
        "-shortest",
        output_path
    ]

    try:
        result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print("✅ Видео успешно обработано!")
        print("FFmpeg stdout:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("❌ FFmpeg завершился с ошибкой:")
        print(e.stderr)
        raise e

def prepare_and_merge_ffmpeg_diagonal_mask(main_path, loop_path, output_path):
    ffmpeg_command = [
        "ffmpeg",
        "-i", main_path,
        "-stream_loop", "-1",
        "-i", loop_path,
        "-filter_complex",
        (
            "[1:v]scale=1080:1920,boxblur=20:1[blurred_bg];"
            "color=white@1.0:s=1080x1920:r=30:d=15[white];"
            "[white]drawbox=x=0:y=960:w=1080:h=10:color=black@1.0:t=fill,"
            "rotate=0.785398:ow=rotw(0):oh=roth(0):c=white@1.0[mask_raw];"
            "[mask_raw]fps=30,trim=duration=14,setpts=PTS-STARTPTS[mask_trimmed];"
            "[0:v]scale=iw*min(1080/iw\\,1920/ih):ih*min(1080/iw\\,1920/ih),setsar=1[main];"
            "[mask_trimmed][main]scale2ref[mask_scaled][main2];"
            "[main2][mask_scaled]alphamerge[main_masked];"
            "[blurred_bg][main_masked]overlay=(W-w)/2:(H-h)/2,format=yuv420p[outv]"
        ),
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:v", "3500k",
        "-r", "30",
        "-preset", "veryfast",
        "-crf", "23",
        "-profile:v", "high",
        "-level", "4.0",
        "-movflags", "+faststart",
        "-threads", "4",  # Ограничиваем количество потоков
        "-max_muxing_queue_size", "1024",  # Увеличиваем размер очереди мультиплексирования
        "-max_interleave_delta", "0",  # Отключаем интерливинг
        "-shortest",
        output_path
    ]

    try:
        result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print("✅ Видео успешно обработано!")
    except subprocess.CalledProcessError as e:
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print("⚠️ FFmpeg завершился с ошибкой, но файл создан успешно.")
            print("Ошибка FFmpeg:\n", e.stderr)
            return  # или return output_path, если нужно вернуть путь
        else:
            print("❌ FFmpeg завершился с ошибкой и файл не создан.")
            print(e.stderr)
            raise e
