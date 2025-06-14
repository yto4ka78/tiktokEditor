import yt_dlp
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips
from moviepy.video.compositing.CompositeVideoClip import clips_array
from PIL import Image
import os
import time
import subprocess
import json
import threading


def download_video(url, output_path, on_update=None):
    cleanup_videos_folder(output_path)

    output_file = os.path.join(output_path, "video.mp4")

    ydl_opts = {
        'outtmpl': output_file,
        'format': 'bestvideo[height<=1080]+bestaudio/best',
        'merge_output_format': 'mp4',
        'overwrites': True,
        'restrictfilenames': True,
    }

    try:
        if on_update: on_update("⏬ Скачивание видео...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        if on_update:
            on_update("✅ Видео успешно скачано!")
        return output_file
    except Exception as e:
        if on_update:
            on_update(f"❌ Ошибка при скачивании: {e}")
        raise e
# def download_video(url, output_path, on_update=None):

#     cleanup_videos_folder(output_path)

#     video_path = os.path.join(output_path, "video.mp4")
#     audio_path = os.path.join(output_path, "c")
#     final_output = os.path.join(output_path, "merged.mp4")

#     # 1. Скачиваем видео
#     ydl_video_opts = {
#         'outtmpl': video_path,
#         'format': 'bestvideo[height<=1080]',
#         'overwrites': True,
#         'restrictfilenames': True
#     }

#     # 2. Скачиваем аудио
#     ydl_audio_opts = {
#         'outtmpl': audio_path,
#         'format': '140',
#         'overwrites': True,
#         'restrictfilenames': True
#     }

#     try:
#         if on_update: on_update("⏬ Скачивание видео...")
#         with yt_dlp.YoutubeDL(ydl_video_opts) as ydl:
#             ydl.download([url])
#         if on_update: on_update("🎵 Скачивание аудио...")
#         with yt_dlp.YoutubeDL(ydl_audio_opts) as ydl:
#             ydl.download([url])
#     except Exception as e:
#         if on_update: on_update(f"❌ Ошибка при скачивании: {e}")
#         print(f"❌ Ошибка при скачивании: {e}")
#         raise e

#     # 3. Объединяем через ffmpeg
#     try:
#         subprocess.run([
#             "ffmpeg",
#             "-y",  # перезапись без подтверждения
#             "-i", video_path,
#             "-i", audio_path,
#             "-c:v", "copy",
#             "-c:a", "aac",
#             "-shortest",
#             final_output
#         ], check=True)

#         os.remove(video_path)
#         os.remove(audio_path)
#         print(f"✅ Объединено в: {final_output}")
#         return final_output
#     except subprocess.CalledProcessError as e:
#         print(f"❌ Ошибка ffmpeg при объединении: {e}")
#         raise e


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
            print(f"✅ Файл {path} успешно удален")
    except Exception as e:
        print(f"Ошибка при удалении файла {path}: {e}")

def get_video_dimensions(video_path):
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "json",
            video_path
        ],
        capture_output=True, text=True
    )
    info = json.loads(result.stdout)
    width = info["streams"][0]["width"]
    height = info["streams"][0]["height"]
    return width, height


def get_padding_top(original_w, original_h, target_w=1080, target_h=1920):
    scale_factor = min(target_w / original_w, target_h / original_h)
    scaled_h = int(original_h * scale_factor)
    padding_top = int((target_h - scaled_h) / 2)
    h_mask = target_h - padding_top
    return padding_top, h_mask

def handle_prepare_and_merge_ffmpeg_diagonal_mask (main_path, loop_path, output_path, on_update):
    w, h = get_video_dimensions(main_path)
    padding_top, h_mask = get_padding_top(w, h)
    prepare_and_merge_ffmpeg_diagonal_mask(main_path, loop_path, output_path, padding_top, h_mask, on_update)

def handle_prepare_and_merge_ffmpeg_your_blur_bars (main_path, loop_path, output_path, on_update):
    w, h = get_video_dimensions(main_path)
    padding_top, h_mask = get_padding_top(w, h)
    prepare_and_merge_ffmpeg_your_blur_bars(main_path, loop_path, output_path, padding_top, h_mask, on_update)

def show_render_logs (process, on_update):
    for line in process.stdout:
        line = line.strip()
        if on_update:
            on_update(line)

    process.wait()
    if on_update:
        on_update("✅ Видео успешно обработано!")

def prepare_and_merge_ffmpeg_70_30(main_path, loop_path, output_path, on_update=None):
    target_width = 1080
    target_full_height = 1920
    target_top_height = int(target_full_height * 0.7)
    target_bottom_height = target_full_height - target_top_height  
    ffmpeg_command = [
        "ffmpeg",
        "-i", main_path,
        "-stream_loop", "-1",  # Бесконечный цикл для второго входного файла
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
        "-shortest",  # Ограничиваем длительность длиной первого видео
        output_path
    ]

    print("Запуск команды FFmpeg:")
    print(" ".join(ffmpeg_command))
    
    try:
        process = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        show_render_logs(process, on_update)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения FFmpeg:\n{e.stderr}")
        raise e
    except FileNotFoundError:
        print("Ошибка: FFmpeg не найден. Убедитесь, что FFmpeg установлен и доступен в PATH.")
        raise FileNotFoundError("FFmpeg не найден")

def prepare_and_merge_ffmpeg_50_50(main_path, loop_path, output_path, on_update=None):
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
        process = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        show_render_logs(process, on_update)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения FFmpeg:\n{e.stderr}")
        if on_update:
            on_update("❌ Ошибка монтажа, но видео смонтировано!")
        raise e

def prepare_and_merge_ffmpeg_30_70(main_path, loop_path, output_path, on_update=None):
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
        process = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        show_render_logs(process, on_update)
    except subprocess.CalledProcessError as e:
        if on_update:
            on_update("❌ Ошибка монтажа, но видео смонтировано!")
        raise e

def prepare_and_merge_ffmpeg_youTube_blur_bars(main_path, output_path, on_update=None):
    ffmpeg_command = [
        "ffmpeg",
        "-i", main_path,
        "-filter_complex",
        (
            "[0:v]split=2[bg][fg];"
            "[bg]scale=1080:1920,boxblur=20:1[blurred];"
            "[fg]scale=-1:ih*min(1080/iw\\,1920/ih),setsar=1[main];"
            "[blurred][main]overlay=(W-w)/2:(H-h)/2:format=auto[outv]"
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
        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        show_render_logs(process, on_update)

    except subprocess.CalledProcessError as e:
        if on_update:
            on_update("❌ Ошибка монтажа, но видео смонтировано!")
        print("❌ FFmpeg завершился с ошибкой:")
        print(e.stderr)
        raise e

def prepare_and_merge_ffmpeg_your_blur_bars(main_path, loop_path, output_path, padding_top, h_mask, on_update=None):
    ffmpeg_command = [
        "ffmpeg",
        "-i", main_path,
        "-stream_loop", "-1",
        "-i", loop_path,
        "-filter_complex",
        (
            f"""
            [1:v]scale=1080:1920,boxblur=20:1[blurred];
            color=black:s=3000x3000:d=15[mask_base1];
            [mask_base1]drawbox=x=0:y=1500:w=3000:h=10:color=white@1.0:t=fill,
            rotate=-0.523599:ow=1080:oh=1920:c=black,
            scale=1080:1920[mask1];
            [0:v]scale=iw*min(1080/iw\\,1920/ih):ih*min(1080/iw\\,1920/ih),setsar=1[scaled];
            [scaled]pad=1080:1920:(1080-in_w)/2:(1920-in_h)/2[main];
            color=black:s=1080x1920:d=15[mask_base2];
            [mask_base2]drawbox=x=0:y={padding_top}:w={h_mask}:h=760:color=white@1.0:t=fill[mask2];
            [mask1][mask2]blend=all_mode=lighten[mask_combined];
            [mask_combined]fps=30,setpts=PTS-STARTPTS,format=gray[alpha_mask];
            [main][alpha_mask]alphamerge[main_with_alpha];
            [blurred][main_with_alpha]overlay=0:0,format=yuv420p[outv]
            """
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
        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        show_render_logs(process, on_update)
    except subprocess.CalledProcessError as e:
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print("⚠️ FFmpeg завершился с ошибкой, но файл создан успешно.")
            print("Ошибка FFmpeg:\n", e.stderr)
            return  # или return output_path, если нужно вернуть путь
        else:
            print("❌ FFmpeg завершился с ошибкой и файл не создан.")
            print(e.stderr)
            raise e

def prepare_and_merge_ffmpeg_diagonal_mask(main_path, loop_path, output_path, padding_top, h_mask, on_update=None):
    ffmpeg_command = [
        "ffmpeg",
        "-i", main_path,
        "-stream_loop", "-1",
        "-i", loop_path,
        "-filter_complex",
        (
            f"""
            [1:v]scale=1080:1920,boxblur=20:1[blurred];
            [0:v]scale=iw*min(1080/iw\,1920/ih):ih*min(1080/iw\,1920/ih),setsar=1[scaled];
            [scaled]pad=1080:1920:(1080-in_w)/2:(1920-in_h)/2[main];
            color=black:s=3000x3000:d=5[mask_base1];
            [mask_base1]drawbox=x=0:y=1500:w=3000:h=5:color=white@1.0:t=fill,
            rotate=-1:ow=1080:oh=1920:c=black,
            scale=1080:1920[mask1];
            color=black:s=3000x3000:d=5[mask_base2];
            [mask_base2]drawbox=x=0:y=2100:w=3000:h=5:color=white@1.0:t=fill,
            rotate=-0.009:ow=1080:oh=1920:c=black,
            scale=1080:1920[mask2];
            [mask1][mask2]blend=all_mode=lighten[combined_mask];
            [combined_mask]fps=30,setpts=PTS-STARTPTS,format=gray[alpha_mask];
            [blurred][alpha_mask]alphamerge[main_with_alpha];
            [main][main_with_alpha]overlay=0:0[with_alpha];
            [with_alpha]format=yuv420p[outv]
            """
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
        "-threads", "4", 
        "-max_muxing_queue_size", "1024",
        "-max_interleave_delta", "0",
        "-shortest",
        output_path
    ]

    try:
        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        show_render_logs(process, on_update)

    except subprocess.CalledProcessError as e:
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            if on_update:
                on_update("❌ Ошибка монтажа, но видео смонтировано!")
            print("⚠️ FFmpeg завершился с ошибкой, но файл создан успешно.")
            print("Ошибка FFmpeg:\n", e.stderr)
            return  # или return output_path, если нужно вернуть путь
        else:
            if on_update:
                on_update("❌ Ошибка монтажа")
            print("❌ FFmpeg завершился с ошибкой и файл не создан.")
            print(e.stderr)
            raise e