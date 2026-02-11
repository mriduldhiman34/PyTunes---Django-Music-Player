from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, FileResponse
from .forms import login2
import yt_dlp
import tempfile
from ytmusicapi import YTMusic
import os
import random
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize YTMusic with OAuth
YT_PATH = os.path.join(os.path.dirname(__file__), '../browser.json')
try:
    ytmusic = YTMusic(YT_PATH)
    logger.info("YTMusic initialized successfully with OAuth")
except Exception as e:
    logger.error(f"Failed to initialize YTMusic: {str(e)}")
    ytmusic = None

def index(request):
    """Home screen with random song suggestions."""
    try:
        if not ytmusic:
            raise Exception("YTMusic not initialized")
        # Fetch songs from a broad category
        results = ytmusic.search("popular music", filter='songs', limit=50)
        
        # Format the results
        formatted_results = [{
            'title': item['title'],
            'artist': item['artists'][0]['name'] if item.get('artists') else 'Unknown',
            'videoId': item['videoId'],
            'duration': item.get('duration', 'Unknown'),
            'thumbnail': item['thumbnails'][-1]['url'] if item.get('thumbnails') else None
        } for item in results]
        
        # Shuffle and pick 10 random songs
        random.shuffle(formatted_results)
        suggested_songs = formatted_results[:10]
        
        logger.info("Suggested songs fetched successfully")
        return render(request, "index.html", {'suggested_songs': suggested_songs})
    except Exception as e:
        logger.error(f"Error in index view: {str(e)}")
        return render(request, "index.html", {'error': f"Could not load suggestions: {str(e)}"})

def search(request):
    """Search for songs on YouTube Music."""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'results': []})
    
    try:
        if not ytmusic:
            raise Exception("YTMusic not initialized")
        results = ytmusic.search(query, filter='songs', limit=10)
        formatted_results = [{
            'title': item['title'],
            'artist': item['artists'][0]['name'] if item.get('artists') else 'Unknown',
            'videoId': item['videoId'],
            'duration': item.get('duration', 'Unknown'),
            'thumbnail': item['thumbnails'][-1]['url'] if item.get('thumbnails') else None
        } for item in results]
        logger.debug(f"Search results for '{query}': {len(formatted_results)} songs found")
        return JsonResponse({'results': formatted_results})
    except Exception as e:
        logger.error(f"Error in search view: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def get_stream(request):
    """Fetch a playable audio stream URL for a given video ID."""
    video_id = request.GET.get('id')
    if not video_id:
        return JsonResponse({'error': 'No video ID provided'}, status=400)

    try:
        # Try ytmusicapi with OAuth first
        if ytmusic:
            logger.debug(f"Fetching stream for video ID {video_id} with ytmusicapi")
            song_data = ytmusic.get_song(video_id)
            streaming_data = song_data.get('streamingData', {})
            audio_formats = streaming_data.get('adaptiveFormats', [])
            
            audio_url = None
            for fmt in audio_formats:
                mime_type = fmt.get('mimeType', '')
                if 'audio/mp4' in mime_type or 'audio/mpeg' in mime_type:
                    audio_url = fmt.get('url')
                    break
            
            if audio_url:
                # Verify URL accessibility
                response = requests.head(audio_url, allow_redirects=True)
                if response.status_code == 200:
                    logger.info(f"Valid stream URL from ytmusicapi: {audio_url}")
                    return JsonResponse({
                        'url': audio_url,
                        'title': song_data.get('videoDetails', {}).get('title', 'Unknown Title'),
                        'artist': song_data.get('videoDetails', {}).get('author', 'Unknown Artist'),
                        'album_art': song_data.get('videoDetails', {}).get('thumbnail', {}).get('thumbnails', [{}])[-1].get('url'),
                        'duration': song_data.get('videoDetails', {}).get('lengthSeconds')
                    })
                else:
                    logger.warning(f"ytmusicapi URL inaccessible: {response.status_code}")

        # Fallback to yt_dlp
        logger.debug(f"Falling back to yt_dlp for video ID {video_id}")
        ydl_opts = {
            'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio',  # Prioritize MP3/M4A
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            audio_url = info.get('url') or info.get('formats', [{}])[0].get('url')

        if not audio_url:
            logger.error("No audio stream found")
            return JsonResponse({'error': 'No audio stream found'}, status=404)

        # Verify URL accessibility
        response = requests.head(audio_url, allow_redirects=True)
        if response.status_code != 200:
            logger.error(f"Stream URL inaccessible: {response.status_code}")
            return JsonResponse({'error': 'Stream URL not accessible'}, status=500)

        logger.info(f"Valid stream URL from yt_dlp: {audio_url}")
        return JsonResponse({
            'url': audio_url,
            'title': info.get('title', 'Unknown Title'),
            'artist': info.get('uploader', 'Unknown Artist'),
            'album_art': info.get('thumbnail'),
            'duration': info.get('duration')
        })

    except Exception as e:
        logger.error(f"Error in get_stream: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def get_lyrics(request):
    """Fetch lyrics for a given video ID."""
    video_id = request.GET.get('id')
    if not video_id:
        return JsonResponse({'error': 'No video ID provided'}, status=400)

    try:
        if not ytmusic:
            raise Exception("YTMusic not initialized")
        watch_data = ytmusic.get_watch_playlist(videoId=video_id)
        lyrics_id = watch_data.get('lyrics')
        if lyrics_id:
            lyrics_data = ytmusic.get_lyrics(lyrics_id)
            logger.debug(f"Lyrics fetched for video ID {video_id}")
            return JsonResponse({'lyrics': lyrics_data.get('lyrics', 'Lyrics not available')})
        logger.debug(f"No lyrics found for video ID {video_id}")
        return JsonResponse({'lyrics': 'Lyrics not available'})
    except Exception as e:
        logger.error(f"Error in get_lyrics: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def download_song(request):
    video_id = request.GET.get('id')
    title = request.GET.get('title', 'Unknown Title')
    artist = request.GET.get('artist', 'Unknown Artist')

    if not video_id:
        return HttpResponse('No video ID provided!', status=400)

    # Fetch stream URL (same endpoint used for playback)
    response = requests.get(f"http://127.0.0.1:8000/get_stream/?id={video_id}")
    if response.status_code != 200 or 'url' not in response.json():
        return HttpResponse('Error fetching stream URL!', status=500)

    stream_url = response.json()['url']

    # Get the audio file content
    audio_response = requests.get(stream_url, stream=True)
    if audio_response.status_code != 200:
        return HttpResponse('Error downloading audio!', status=500)

    # Format filename as "Song Name - Artist Name.mp3"
    sanitized_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).rstrip()
    sanitized_artist = "".join(c for c in artist if c.isalnum() or c in (" ", "-", "_")).rstrip()
    filename = f"{sanitized_title} - {sanitized_artist}.mp3"

    # Create response with audio file
    response = FileResponse(audio_response.raw, content_type='audio/mp3')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def signup(request):
    """Handle user signup."""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'signup.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully!")
        return redirect('user_login')

    return render(request, 'signup.html')

def user_login(request):
    """Handle user login."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password!")
            return render(request, 'user_login.html')

    return render(request, 'user_login.html')

def login2_view(request):
    """Render login2 page with form."""
    form = login2()
    return render(request, "login2.html", context={"form": form})

def layout(request):
    """Render layout page."""
    return render(request, "layout.html")

def hero(request):
    """Render hero page."""
    return render(request, 'hero.html')

def contact(request):
    """Render contact page."""
    return render(request, 'contact.html')
