from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from pytube import *
from .models import History
import os
import re

# store Downloads directory
homedir = os.path.expanduser("~")
dirs =os.path.join(homedir, "Downloads")

def home(request):
    '''Home page of YT Downloader'''
    return render(request, 'home.html')

def extract_resolution_number(resolution):
    '''Returns the numeric part of resolution and bitrate'''
    resolution_number = int(''.join(filter(str.isdigit, resolution)))
    return resolution_number
    
def video_list(request):
    '''With provided url and condition, shows the available resolutions'''
    global url, video_list
    url = request.GET.get('url')
    video_type = request.GET.get('radio')
    if video_type == 'With Audio':
        try:
            yt = YouTube(url)
            Title = yt.title
            video_list = yt.streams.filter(progressive=True)    #filter video streams of the video
            context = {'video_list': video_list, 'Title': yt.title, 'Thumbnail':yt.thumbnail_url, 'Duration':timedelta(seconds=yt.length),'Views':yt.views,'Publish_date':yt.publish_date,'Ch_name':yt.author, 'Ch_link':yt.channel_url}
            htmlfile = 'res_show.html'   
        except Exception as e:
            context = {'Exception':e, 'Title':Title}
            htmlfile = 'vid_down_error.html'
    elif video_type == 'Without Audio':
        try:
            yt = YouTube(url)
            Title = yt.title
            streams = yt.streams.filter(progressive=False, only_video=True)
            resolution_set = set()
            video_list = []
            for video in streams:   #remove duplicate resolutions and None objects
                if video.resolution is not None and video.resolution not in resolution_set:
                    resolution_set.add(video.resolution)
                    video_list.append(video)
            video_list.sort(key=lambda x: extract_resolution_number(x.resolution))  #sort the list based on resolutions
            context = {'video_list': video_list, 'Title': yt.title, 'Thumbnail':yt.thumbnail_url, 'Duration':timedelta(seconds=yt.length),'Views':yt.views,'Publish_date':yt.publish_date,'Ch_name':yt.author, 'Ch_link':yt.channel_url}
            htmlfile = 'res_show.html'   
        except Exception as e:
            context = {'Exception':e, 'Title':Title}
            htmlfile = 'vid_down_error.html'
    return render(request, htmlfile, context)

def video_download(request, resolution):
    '''Stores the url in History Database and Downloads the video of url and specified resolution'''
    global dirs, url
    try:
        if request.method == "POST":
            his_obj = History(down_link = url, down_type = 'Video')
            his_obj.save()      #store url in History Database
            yt = YouTube(url)
            Title = yt.title
            video = list(filter(lambda i: i.resolution == resolution, video_list)) #filter list which equals the resolution
            video[0].download(dirs)
            htmlfile = 'vid_down_done.html'
            context = {'Title':yt.title + " VIDEO ", 'saved_path':dirs, 'isPlaylist':False}
        else:
            context = {'Title':Title}
            htmlfile = 'vid_down_error.html'
    except Exception as e:
        context = {'Exception':e, 'Title':Title}
        htmlfile = 'vid_down_error.html'
    return render(request, htmlfile, context)

def audio_home(request):
    '''Audio home page of YT Downloader'''
    return render(request, 'audio_home.html')

def audio_list(request):
    '''With provided url, shows the available bitrate qualities'''
    global url
    url = request.GET.get('url')
    try:
        ytb = YouTube(url)
        Title = ytb.title
        bit_list = list(ytb.streams.filter(progressive=False, type="audio"))    #filter audio streams of the video
        bit_list.sort(key=lambda x: extract_resolution_number(x.abr))   #sort the list based on bitrates
        context = {'bit_list': bit_list, 'Title': ytb.title, 'Thumbnail':ytb.thumbnail_url, 'Duration':timedelta(seconds=ytb.length),'Views':ytb.views,'Publish_date':ytb.publish_date,'Ch_name':ytb.author, 'Ch_link':ytb.channel_url}
        htmlfile = 'bit_show.html'
    except Exception as e:
        context = {'Exception':e, 'Title':Title}
        htmlfile = 'vid_down_error.html'
    return render(request, htmlfile, context)

def audio_download(request, abr):
    '''Stores the url in History Database and Downloads the audio of video from url'''
    global url, dirs
    try:
        if request.method == "POST":
            his_obj = History(down_link = url, down_type = 'Audio')     
            his_obj.save()      #store url in History Database
            yt = YouTube(url)
            Title = yt.title
            yt.streams.filter(abr=abr, progressive=False, type="audio").first().download(dirs)
            htmlfile = 'vid_down_done.html'
            context = {'Title':yt.title + " AUDIO ", 'saved_path':dirs, 'isPlaylist':False}
        else:
            htmlfile = 'vid_down_error.html'
            context = {'Title':Title}
    except Exception as e:
        context = {'Exception':e, 'Title':Title}
        htmlfile = 'vid_down_error.html'
    return render(request, htmlfile, context)

def remove_spl_title(title):
    # Remove invalid characters from the Playlist title
    return re.sub(r'[<>:"/\\|?*]', '', title)

def playlist_home(request):
    '''Playlist page of YT Downloader'''
    return render(request, 'playlist_home.html')

def playlist_download(request):
    '''Stores url in History Database and downloads the entire Playlist in Video / Audio formats'''
    global dirs
    url = request.GET.get('url')
    his_obj = History(down_link = url, down_type = 'Playlist')
    his_obj.save()  #store url in History Database
    video_or_audio = request.GET.get('radio')
    res_or_bit = request.GET.get('radio2')
    playlist_obj = Playlist(url);
    playlist_dir = os.path.join(dirs, remove_spl_title(playlist_obj.title))
    os.makedirs(playlist_dir, exist_ok=True) 
    content = []
    try:
        if request.method == 'GET':
            if video_or_audio == 'Video':
                for yt in playlist_obj.videos:
                    try:
                        yt.streams.filter(resolution=res_or_bit[:4], progressive=True).first().download(playlist_dir)
                        content.append(yt.title + " Video Downloaded")
                    except Exception as e:
                        content.append(str(e) + " So skipped")
            elif video_or_audio == 'Audio':    
                for yt in playlist_obj.videos:
                    try:
                        yt.streams.filter(abr=res_or_bit[5:], progressive=False).first().download(playlist_dir)
                        content.append(yt.title + " Audio Downloaded")
                    except Exception as e:
                        content.append(str(e) + " So skipped")
            htmlfile = 'vid_down_done.html'
            context = {'content':content, 'Title':playlist_obj.title, 'Ch_name':playlist_obj.owner, 'Ch_link':playlist_obj.owner_url,'saved_path':playlist_dir, 'isPlaylist':True}
        else:
            htmlfile = 'vid_down_error.html'
            context = {}
    except Exception as e:
        context = {'Exception':e, 'Title':playlist_obj.title}
        htmlfile = 'vid_down_error.html'
    return render(request, htmlfile, context)

def search(request):
    '''Retrieves the YouTube results for given prompt and uses Pagination Technique '''
    try:
        stmt = request.GET.get('search')
        if stmt is not None:
            stmt = stmt.strip()
            search_obj = Search(stmt)
            video_list = list(search_obj.results)
            #Pagination is a technique to show the results in subsets(pages) and move between pages
            paginator = Paginator(video_list, per_page=10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)  #gets page object with page number which consists the entire results

            context = {'page_obj': page_obj}
            htmlfile = 'search_results.html'
        else:
            context = {}
            htmlfile = 'search_results.html'
    except Exception as e:
        context = {'Exception': e}
        htmlfile = 'vid_down_error.html'

    # Include the search prompt in the pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    pagination_query_params = query_params.urlencode()  #converts the dictionary into a URL-encoded string representation.

    context['pagination_query_params'] = pagination_query_params
    return render(request, htmlfile, context)

def view_history(request):
    '''Deletes Yesterday's history and Shows the Present day's Downloading History'''
    try:
        #Deleting yesterday's history
        current_date = timezone.now().date()
        yesterday = current_date - timedelta(days=1)
        History.objects.filter(down_time__day=yesterday.day, down_time__lt=current_date).delete()
        #Fetching present day's history
        history_today = History.objects.filter(down_time__gte=current_date).order_by('-down_time')
        history_list = list(history_today)

        #Pagination technique
        paginator = Paginator(history_list, per_page=10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'page_obj': page_obj}
        htmlfile = 'history.html'
    except Exception as e:
        context = {'Exception': e}
        htmlfile = 'vid_down_error.html'
    return render(request, htmlfile, context)