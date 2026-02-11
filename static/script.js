// Player State
let isPlaying = false;
let currentTrackIndex = -1;
let queue = [];
const prefetchedURLs = {};

// DOM Elements
const audio = document.getElementById('audioElement');
const playButton = document.getElementById('playButton');
const progressBar = document.getElementById('progressBar');
const volumeSlider = document.getElementById('volumeSlider');
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const queueList = document.getElementById('queueList');
const currentTimeDisplay = document.getElementById('currentTime');
const durationDisplay = document.getElementById('duration');
const searchToggle = document.getElementById('searchToggle');
const searchContainer = document.getElementById('searchContainer');
const queueToggle = document.getElementById('queueToggle');
const queueSidebar = document.getElementById('queueSidebar');
const profileBtn = document.getElementById('profileBtn');
const profileMenu = document.getElementById('profileMenu');
const caretIcon = document.getElementById('caretIcon');
const lyricsContainer = document.getElementById('lyricsContainer');
const closeLyrics = document.getElementById('closeLyrics');

// Event Listeners
document.getElementById('lyricsToggle').addEventListener('click', () => {
  lyricsContainer.style.display = lyricsContainer.style.display === 'block' ? 'none' : 'block';
});
playButton.addEventListener('click', togglePlay);
volumeSlider.addEventListener('input', updateVolume);
audio.addEventListener('timeupdate', updateProgress);
document.getElementById('progressContainer').addEventListener('click', seekAudio);
document.getElementById('nextButton').addEventListener('click', playNext);
document.getElementById('prevButton').addEventListener('click', playPrevious);
document.getElementById('downloadButton').addEventListener('click', downloadSong);
queueList.addEventListener('click', handleQueueItemClick);
searchInput.addEventListener('input', handleSearchInput);
audio.addEventListener("ended", () => playNext());
searchToggle.addEventListener('click', () => {
  searchContainer.style.display = searchContainer.style.display === 'block' ? 'none' : 'block';
});
queueToggle.addEventListener('click', () => {
  queueSidebar.style.display = queueSidebar.style.display === 'block' ? 'none' : 'block';
});
profileBtn.addEventListener('click', () => {
  const visibility = profileMenu.style.visibility === 'visible' ? 'hidden' : 'visible';
  profileMenu.style.visibility = visibility;
  caretIcon.className = `fa fa-caret-${visibility === 'hidden' ? 'down' : 'up'}`;
});
closeLyrics.addEventListener('click', () => {
  lyricsContainer.style.display = 'none';
});

// Suggested Songs Playback
document.querySelectorAll('.activity-info').forEach(item => {
  item.addEventListener('click', () => {
    const videoId = item.getAttribute('data-video-id');
    const track = {
      title: item.querySelector('.song-info .track-name').textContent,
      artist: item.querySelector('.song-info .artist-name').textContent,
      videoId: videoId,
      thumbnail: item.querySelector('.img-div img').src
    };
    addToQueue(track);
    playSong(videoId);
  });
});

// Player Controls
function togglePlay() {
  if (audio.paused) {
    audio.play();
    isPlaying = true;
  } else {
    audio.pause();
    isPlaying = false;
  }
  updatePlayButton();
}

function updatePlayButton() {
  playButton.querySelector('i').className = audio.paused ? 'bx bx-play' : 'bx bx-pause';
}

function updateVolume() {
  const volume = volumeSlider.value;
  audio.volume = volume;
  updateVolumeIcon(volume);
}

function updateVolumeIcon(volume) {
  const volumeIcon = document.getElementById('volumeIcon');
  volumeIcon.className = volume == 0
    ? 'bx bx-volume-mute'
    : volume <= 0.5
      ? 'bx bx-volume-low'
      : 'bx bx-volume-full';
}

function updateProgress() {
  const progress = (audio.currentTime / audio.duration) * 100 || 0;
  progressBar.style.width = `${progress}%`;
  currentTimeDisplay.textContent = formatDuration(audio.currentTime);
  durationDisplay.textContent = formatDuration(audio.duration || 0);
}

function seekAudio(e) {
  const rect = e.target.getBoundingClientRect();
  const pos = (e.clientX - rect.left) / rect.width;
  audio.currentTime = pos * audio.duration;
}

// Queue Management
function addToQueue(track) {
  queue.push(track);
  prefetchSong(track.videoId);
  renderQueue();
  if (currentTrackIndex === -1) {
    currentTrackIndex = 0;
    playSong(queue[currentTrackIndex].videoId);
  }
}

function renderQueue() {
  queueList.innerHTML = queue.map((track, index) => `
    <li class="queue-item" data-index="${index}">
      ${track.title} - ${track.artist}
    </li>
  `).join('');
}

function handleQueueItemClick(e) {
  if (e.target.classList.contains('queue-item')) {
    currentTrackIndex = parseInt(e.target.dataset.index);
    playSong(queue[currentTrackIndex].videoId);
  }
}

// Search Functionality
async function handleSearchInput(e) {
  const query = e.target.value.trim();
  if (query.length > 2) {
    const results = await searchSongs(query);
    showSearchResults(results);
  } else {
    searchResults.innerHTML = '';
  }
}

async function searchSongs(query) {
  try {
    const response = await fetch(`/search/?q=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error('Search failed');
    const data = await response.json();
    return data.results || [];
  } catch (error) {
    console.error('Search error:', error);
    return [];
  }
}

function showSearchResults(results) {
  searchResults.innerHTML = results.map(track => `
    <div class="search-item" data-id="${track.videoId}">
      <img src="${track.thumbnail}" alt="${track.title}">
      <div>
        <div>${track.title}</div>
        <div class="artist">${track.artist}</div>
      </div>
    </div>
  `).join('');
  document.querySelectorAll('.search-item').forEach(item => {
    item.addEventListener('click', () => {
      const track = {
        title: item.querySelector('div > div:first-child').textContent,
        artist: item.querySelector('.artist').textContent,
        videoId: item.dataset.id,
        thumbnail: item.querySelector('img').src
      };
      addToQueue(track);
      searchInput.value = '';
      searchResults.innerHTML = '';
      searchContainer.style.display = 'none';
    });
  });
}

// Playback Functions
let isFetching = false;
async function playSong(videoId) {
  if (isFetching) return;
  isFetching = true;
  try {
    const track = queue.find(t => t.videoId === videoId);
    if (!track) throw new Error("Track not found in queue");

    document.getElementById('songTitle').textContent = track.title || "Unknown Title";
    document.getElementById('artist').textContent = track.artist || "Unknown Artist";
    document.getElementById('albumArt').src = track.thumbnail || "{% static 'default-cover.jpg' %}";

    let url = prefetchedURLs[videoId];
    if (!url) {
      const response = await fetch(`/get_stream/?id=${videoId}`);
      if (!response.ok) throw new Error('Failed to fetch stream URL');
      const data = await response.json();
      if (data.error) throw new Error(data.error);
      url = data.url;
      prefetchedURLs[videoId] = url;
    }

    audio.src = url;
    await audio.play();
    isPlaying = true;
    updatePlayButton();
    fetchLyrics(videoId, false);
  } catch (error) {
    console.error("Error in playSong:", error);
    alert(`Error: ${error.message}`);
  } finally {
    isFetching = false;
  }
}

// Lyrics Functions
async function fetchLyrics(videoId, showImmediately = true) {
  try {
    const response = await fetch(`/get_lyrics/?id=${videoId}`);
    const data = await response.json();
    document.getElementById('lyricsText').textContent = data.lyrics || "Lyrics not available";
    if (showImmediately) {
      lyricsContainer.style.display = 'block';
    }
  } catch (error) {
    console.error('Error fetching lyrics:', error);
  }
}

// Download Function
function downloadSong() {
  if (currentTrackIndex >= 0) {
    const track = queue[currentTrackIndex];
    const videoId = track.videoId;
    const title = encodeURIComponent(track.title);
    const artist = encodeURIComponent(track.artist);
    window.location.href = `/download_song/?id=${videoId}&title=${title}&artist=${artist}`;
  } else {
    alert("No song selected to download!");
  }
}

// Navigation Functions
function playNext() {
  if (currentTrackIndex < queue.length - 1) {
    currentTrackIndex++;
    playSong(queue[currentTrackIndex].videoId);
  }
}

function playPrevious() {
  if (currentTrackIndex > 0) {
    currentTrackIndex--;
    playSong(queue[currentTrackIndex].videoId);
  }
}

// Helper Function: Format Time in MM:SS
function formatDuration(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00';
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

async function prefetchSong(videoId) {
  if (prefetchedURLs[videoId]) return;
  try {
    const response = await fetch(`/get_stream/?id=${videoId}`);
    const data = await response.json();
    if (data.url) prefetchedURLs[videoId] = data.url;
  } catch (error) {
    console.error('Error prefetching song:', error);
  }
}

audio.addEventListener('play', () => {
  if (queue.length > currentTrackIndex + 1) {
    prefetchSong(queue[currentTrackIndex + 1].videoId);
  }
});
