from django.http import HttpResponse
from django.shortcuts import render

import yt_dlp as youtube_dl
import re 
import os
import shutil
from django.conf import settings
from mutagen.mp3 import MP3, EasyMP3
from mutagen.id3 import ID3, APIC, error
from bing_image_downloader import downloader

#todo: fix / 

class YTObject:
   def __init__(self, url=None, title=None, artist=None, album_arts=[]):
      self.YDL_OPTS = {
          'outtmpl': 'static/tbd/%(title)s [%(id)s].%(ext)s',
          'format': 'bestaudio/best',
          'postprocessors': [{
              'key': 'FFmpegExtractAudio',
              'preferredcodec': 'mp3',
              'preferredquality': '192',
          }],
        }
      self.url = url
      self.title = title
      self.artist = artist
      self.orig_title = title
      self.album_arts = album_arts
      
YTO = YTObject()
static_path = os.path.join(settings.BASE_DIR, 'static/tbd')

def download_mp3_file(audio_file_path, title, artist):
  file = open(audio_file_path, "rb").read() 
  response = HttpResponse(file)
  response['Content-Disposition'] = f'attachment; filename="{title} - {artist}.mp3"'
  return response

def download_album_art(title, artist, n = 1):
  search_query = f'{title} by {artist} original album cover'
  downloader.download(search_query,
                      limit=n, output_dir='static/tbd',
                      adult_filter_off=True, force_replace=False,
                      timeout=60)
  image_file_path = f'static/tbd/{search_query}/'
  filenames = next(os.walk(image_file_path), (None, None, []))[2]
  return [f'tbd/{search_query}/' + f for f in filenames]

def edit_audio_meta(audio_file_path, title, artist, image_number):
  image_path = f'static/{YTO.album_arts[image_number]}'
  audio = MP3(audio_file_path, ID3=ID3)
  try:
      audio.add_tags()
  except error:
      print('Error in editing tags')
      pass

  audio.tags.add(
      APIC(
          encoding=3,
          mime='image/jpeg',
          type=3,
          desc='Cover',
          data=open(image_path, 'rb').read()
      )
  )
  audio.save()
  audio = EasyMP3(audio_file_path)
  audio['title'] = title
  audio['artist'] = artist
  audio.save()

def download_audio(yt_url, title, artist, image_number):
  with youtube_dl.YoutubeDL(YTO.YDL_OPTS) as ydl:
    file_id = get_vid_id(yt_url)
    audio_file_path = f'static/tbd/{YTO.orig_title} [{file_id}].mp3'
    ydl.download([yt_url])

  edit_audio_meta(audio_file_path, title, artist, image_number)
  return download_mp3_file(audio_file_path, title, artist)

def get_title(title):
    title = title.replace('/', '⧸')
    orig_title = title
    t = title.split(" - ")
    title = t[1] if len(t) == 2 else title
    t_artist = t[0] if len(t) == 2 else None
    title = re.sub("[\(\[].*?[\)\]]", "", title)  
    return orig_title, title , t_artist

def get_vid_id(url):
   return url.split("watch?v=")[1]

def index(request):
  if request.method == 'POST':
        if os.path.exists(static_path):
           shutil.rmtree(static_path)
        YTO.url = request.POST.get('yt_url', '')
        with youtube_dl.YoutubeDL(YTO.YDL_OPTS) as ydl:
          info_dict = ydl.extract_info(YTO.url, download=False)
          YTO.orig_title, title, t_artist = get_title(info_dict['title'])
          if not t_artist:
            artist = info_dict['artist'] if 'artist' in info_dict else info_dict['channel']
          else:
            artist = t_artist
          YTO.album_arts = download_album_art(title, artist,3)
          return render(request, 'main.html', 
                        {'orig_title': YTO.orig_title, 
                         'yt_title': title, 
                         'yt_artist' : artist,
                         'album_arts' : YTO.album_arts,
                         'album_arts_len' : [n for n in range(len(YTO.album_arts))]})
  return render(request, 'main.html')

def yt_dl(request):
  if request.method == 'POST':
        image_number = request.POST.get('image_number')
        YTO.title = request.POST.get('title')
        YTO.artist = request.POST.get('artist')
        response = download_audio(YTO.url, YTO.title, YTO.artist, int(image_number))
  return response
