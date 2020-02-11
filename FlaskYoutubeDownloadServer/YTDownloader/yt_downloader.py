from __future__ import unicode_literals

import os
import re
import shutil
from zipfile import ZipFile
import subprocess

import youtube_dl
import colorama

colorama.init()


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        print(f"{Colors.WARNING}Warning: '{msg}'{Colors.ENDC}")

    def error(self, msg):
        print(f"{Colors.FAIL}ERROR: '{msg}'{Colors.ENDC}")


file = "YTDownloader/downloadList.txt"
regex_for_zip = r"\\|\/|\:|\*|\?|\"|\<|\>|\|"
audio_format = 'mp3'


def my_hook(d):
    if d['status'] == 'finished':
        print(f'{Colors.OKGREEN}Fertig heruntergeladen!\n{Colors.ENDC}'
              f'{Colors.OKBLUE}Start der Konvertierung zu {audio_format} . . .{Colors.ENDC}')


def download_video(url):
    ydl_opts = {
        'writethumbnail': True,
        'format': 'bestaudio/best',
        'outtmpl': './tmp/%(title)s.%(ext)s',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': '192'
            },
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'},
        ],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = re.sub(regex_for_zip, "_", info_dict.get('title', None))
            print(f"{Colors.BOLD}Starte den Download des Videos:{Colors.ENDC}\n{video_title}\nURL: {url}")
            ydl.download([url])
        print(
            f"{Colors.OKGREEN}Das Video '{video_title}' wurde erfolgreich heruntergeladen und zu {audio_format} konvertiert{Colors.ENDC}")
    except youtube_dl.utils.DownloadError:
        print(f"{Colors.FAIL}Das Video, mit der URL: {url}\nkonnte nicht heruntergeladen werden.{Colors.ENDC}")

    # move_to_download_folder(video_title + '-' + video_id)
    print('\n')


def execute_download():
    try:
        with open(file, 'r+') as txt:
            for line in txt:
                download_video(line)
                print('----------------------------------------------------------------------')
        print(f'{Colors.OKGREEN}ALLES ERLEDIGT!{Colors.ENDC}')
        delete_file(file)
    except FileNotFoundError as msg:
        print(f'{Colors.FAIL}ERROR: {msg}{Colors.ENDC}\n')


def execute_json_download(url_list):
    try:
        for url in url_list:
            download_video(url)
            print('----------------------------------------------------------------------')
        print(f'{Colors.OKGREEN}ALLES ERLEDIGT!{Colors.ENDC}')
    except FileNotFoundError as msg:
        print(f'{Colors.FAIL}ERROR: {msg}{Colors.ENDC}\n')


def create_download_list(with_value, content=None):
    print(f"{Colors.WARNING}Erstelle '{file}'.{Colors.ENDC}")
    f = open(file, "w+")

    if with_value:
        for line in content.split(','):
            f.write(line + '\n')

    f.close()


def delete_file(filename):
    try:
        print(f'{Colors.WARNING}Die Datei "{filename}" wird gelöscht!{Colors.ENDC}')
        os.remove(filename)
    except FileNotFoundError as msg:
        print(f'{Colors.FAIL}Die Datei "{filename}" konnte nicht geloescht werden\nERROR: {msg}{Colors.ENDC}')





# Nicht mehr notwendig

def download_video_with_command_line(url):
    try:
        subprocess.run(['youtube-dl', '--extract-audio',
                        '--audio-format',
                        'mp3',
                        '--output',
                        './tmp/%(title)s.%(ext)s',
                        '--embed-thumbnail',
                        '--add-metadata',
                        url])
        print(
            f"{Colors.OKGREEN}Das Video wurde erfolgreich heruntergeladen und zu {audio_format} konvertiert{Colors.ENDC}")
    except:
        print(f"{Colors.FAIL}Die URL:\n{url}\nkonnte nicht heruntergeladen werden.{Colors.ENDC}")


def move_to_download_folder(filename):
    try:
        shutil.move(f'{filename}.{audio_format}', f'tmp/{filename}.{audio_format}')
        print(f"Die Datei {filename}.{audio_format} wurde in tmp verschoben")
    except FileNotFoundError as msg:
        print(f'{Colors.FAIL}Die Datei "{filename}" konnte nicht verschoben werden\nERROR: {msg}{Colors.ENDC}')


def folder_to_zip(foldername):
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(foldername):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

            # returning all file paths

    print(f'{Colors.WARNING}Folgende Lieder werden gezipped:{Colors.ENDC}')
    for file_name in file_paths:
        print(file_name)

        # writing files to a zipfile
    with ZipFile('downloaded_songs.zip', 'w') as zip:
        # writing each file one by one
        for file in file_paths:
            zip.write(file)

    print(f'{Colors.OKGREEN}Alle Dateien wurden erfolgreich gezipped!{Colors.ENDC}')

    for file_name in file_paths:
        delete_file(file_name)
