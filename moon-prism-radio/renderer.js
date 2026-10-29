// Browser-preview fallback for the Electron preload bridge.
if (!window.widget) {
  let memoryPins = null;
  let memoryGif = null;

  window.widget = {
    resize() {},
    pin() {},
    minimize() {},
    open: (url) => window.open(url),
    close() {},
    loadPins: async () => memoryPins,
    savePins: async (value) => {
      memoryPins = value;
      return true;
    },
    loadGif: async () => memoryGif,
    saveGif: async (value) => {
      memoryGif = value;
      return true;
    },
    clearGif: async () => {
      memoryGif = null;
      return true;
    }
  };
}

const $ = (id) => document.getElementById(id);
const player = $('player');
const status = $('status');

let pins = [
  {
    name: 'Pokmn <3',
    url: 'https://soundcloud.com/david-imasuen-999087366/nostalgic-pokemon-music'
  },
  {
    name: 'Lana',
    url: 'https://soundcloud.com/lesly-arellano-320948469/born-to-die-lana-del-rey-full'
  },
  {
    name: 'Marina',
    url: 'https://soundcloud.com/marinadiamandis/sets/electra-heart-platinum-blonde'
  },
  null
];

let nowPlaying = null;
let currentIndex = -1;
let editingIndex = null;
let playing = false;
let repeat = false;
let lastExternalUrl = null;
let currentTime = 0;
let duration = null;

// Drawers
function openDrawer(id) {
  document.querySelectorAll('.drawer').forEach((drawer) => {
    const shouldOpen = drawer.id === id && !drawer.classList.contains('show');
    drawer.classList.toggle('show', shouldOpen);
  });
}

document.querySelectorAll('[data-drawer]').forEach((button) => {
  button.addEventListener('click', () => openDrawer(button.dataset.drawer));
});

document.querySelectorAll('.drawer-close').forEach((button) => {
  button.addEventListener('click', () => button.parentElement.classList.remove('show'));
});

// Link parsing and embedded players
function parseLink(raw) {
  let url;

  try {
    url = new URL(raw.trim());
  } catch {
    return null;
  }

  const host = url.hostname.replace(/^(www\.|m\.|music\.)/, '');

  if (host === 'youtu.be' || host === 'youtube.com') {
    let id = host === 'youtu.be'
      ? url.pathname.split('/')[1]
      : url.searchParams.get('v');

    if (!id && /\/(shorts|embed|live)\//.test(url.pathname)) {
      id = url.pathname.split('/')[2];
    }

    const list = url.searchParams.get('list');
    if (!id && !list) return null;

    const source = id
      ? `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&enablejsapi=1${list ? `&list=${encodeURIComponent(list)}` : ''}`
      : `https://www.youtube-nocookie.com/embed/videoseries?list=${encodeURIComponent(list)}&autoplay=1&enablejsapi=1`;

    return {
      type: 'yt',
      watch: url.href,
      src: source
    };
  }

  if (host === 'soundcloud.com' || host === 'on.soundcloud.com') {
    const params = new URLSearchParams({
      url: url.href,
      auto_play: 'true',
      hide_related: 'true',
      show_comments: 'false',
      show_user: 'true'
    });

    return {
      type: 'sc',
      watch: url.href,
      src: `https://w.soundcloud.com/player/?${params}`
    };
  }

  return null;
}

function deriveName(raw) {
  try {
    return decodeURIComponent(new URL(raw).pathname.split('/').filter(Boolean).pop())
      .replace(/[-_]+/g, ' ')
      .slice(0, 28);
  } catch {
    return 'now playing';
  }
}

function formatTime(seconds) {
  if (!Number.isFinite(seconds)) return '--:--';
  const minutes = Math.floor(seconds / 60);
  const remainder = String(Math.floor(seconds % 60)).padStart(2, '0');
  return `${minutes}:${remainder}`;
}

function sendYouTubeCommand(func, args = []) {
  const iframe = player.querySelector('iframe');
  if (!iframe) return;

  iframe.contentWindow.postMessage(
    JSON.stringify({ event: 'command', func, args }),
    '*'
  );
}

function loadTrack(raw, name, index = -1) {
  const value = (raw || $('link').value).trim();
  const parsed = parseLink(value);
  $('fallback').className = 'fallback';

  if (!parsed) {
    status.textContent = 'that link does not look like YouTube or SoundCloud';
    return;
  }

  nowPlaying = {
    name: name || deriveName(value),
    url: value,
    type: parsed.type
  };
  currentIndex = index;
  currentTime = 0;
  duration = null;

  $('trackTitle').textContent = nowPlaying.name;
  $('artist').textContent = parsed.type === 'yt' ? 'YouTube' : 'SoundCloud';
  status.textContent = `playing from ${$('artist').textContent}`;
  lastExternalUrl = parsed.watch;
  player.innerHTML = `<iframe allow="autoplay; encrypted-media" src="${parsed.src}"></iframe>`;

  playing = false;
  updatePlayButton();
  setProgress(0, null);

  if (parsed.type === 'yt') {
    initializeYouTube();
  } else {
    initializeSoundCloud();
  }
}

function initializeYouTube() {
  const iframe = player.querySelector('iframe');
  if (!iframe) return;

  iframe.addEventListener('load', () => {
    iframe.contentWindow.postMessage(JSON.stringify({
      event: 'listening',
      id: 'moon-prism-radio',
      channel: 'widget'
    }), '*');
  });
}

function initializeSoundCloud() {
  // SoundCloud announces readiness by message. Registering from the iframe's
  // load event is too early, so setup is completed in the message handler.
}

function sendSoundCloud(method, value) {
  const iframe = player.querySelector('iframe');
  if (!iframe) return;

  iframe.contentWindow.postMessage(JSON.stringify({ method, value }), '*');
}

window.addEventListener('message', (event) => {
  const iframe = player.querySelector('iframe');
  if (!iframe || event.source !== iframe.contentWindow) return;

  let data;

  try {
    data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
  } catch {
    return;
  }

  if (data?.event === 'infoDelivery' && data.info) {
    if (Number.isFinite(data.info.currentTime)) {
      setProgress(data.info.currentTime, null);
    }
    if (Number.isFinite(data.info.duration)) {
      setProgress(null, data.info.duration);
    }
    if (data.info.videoData?.title) {
      $('trackTitle').textContent = data.info.videoData.title;
      $('artist').textContent = data.info.videoData.author || 'YouTube';
    }
  }

  if (data?.event === 'onStateChange') {
    const state = data.info;
    if (state === 1) {
      playing = true;
      updatePlayButton();
    } else if (state === 2) {
      playing = false;
      updatePlayButton();
    } else if (state === 0) {
      playing = false;
      updatePlayButton();
      trackEnded();
    }
  }

  if (data?.event === 'onError' && (data.info === 101 || data.info === 150)) {
    showFallback();
  }
  if (data?.method === 'ready' && nowPlaying?.type === 'sc') {
    sendSoundCloud('addEventListener', 'playProgress');
    sendSoundCloud('addEventListener', 'finish');
    sendSoundCloud('addEventListener', 'pause');
    sendSoundCloud('addEventListener', 'play');
    sendSoundCloud('getDuration');
    sendSoundCloud('getCurrentSound');
  }
  if (data?.method === 'playProgress' && data.value) {
    setProgress(data.value.currentPosition / 1000, null);
  }
  if (data?.method === 'finish') {
    trackEnded();
  }
  if (data?.method === 'play') {
    playing = true;
    updatePlayButton();
  }
  if (data?.method === 'pause') {
    playing = false;
    updatePlayButton();
  }
  if (data?.method === 'getDuration') {
    const seconds = Number.isFinite(data.value) ? data.value / 1000 : null;
    setProgress(null, seconds);
  }
  if (data?.method === 'getCurrentSound' && data.value) {
    if (data.value.title) {
      $('trackTitle').textContent = data.value.title;
    }
    if (data.value.user?.username) {
      $('artist').textContent = data.value.user.username;
    }
  }
});

// Progress and transport controls
function setProgress(newTime, newDuration) {
  if (newTime !== null) currentTime = newTime;
  if (newDuration !== null) duration = newDuration;

  $('elapsed').textContent = formatTime(currentTime);
  $('duration').textContent = formatTime(duration);

  const fraction = duration
    ? Math.max(0, Math.min(1, currentTime / duration))
    : 0;

  $('progressFill').style.width = `${fraction * 100}%`;
  $('progressKnob').style.left = `${fraction * 100}%`;
}

function updatePlayButton() {
  $('pauseBtn').classList.toggle('is-playing', playing);
}

function togglePlay() {
  if (!nowPlaying) return;

  if (nowPlaying.type === 'yt') {
    sendYouTubeCommand(playing ? 'pauseVideo' : 'playVideo');
  } else {
    const iframe = player.querySelector('iframe');
    iframe?.contentWindow.postMessage(
      JSON.stringify({ method: playing ? 'pause' : 'play' }),
      '*'
    );
  }

  // Provider play/pause events update the button once the command succeeds.
}

function populatedPins() {
  return pins
    .map((pin, index) => pin && { ...pin, index })
    .filter(Boolean);
}

function stepTrack(direction, shuffle = false) {
  const available = populatedPins();
  if (!available.length) return;

  let position = available.findIndex((pin) => pin.index === currentIndex);
  position = shuffle
    ? Math.floor(Math.random() * available.length)
    : (position + direction + available.length) % available.length;

  const selected = available[position];
  loadTrack(selected.url, selected.name, selected.index);
}

function trackEnded() {
  if (repeat && nowPlaying) {
    loadTrack(nowPlaying.url, nowPlaying.name, currentIndex);
  } else {
    stepTrack(1);
  }
}

function showFallback() {
  player.innerHTML = '';
  playing = false;
  updatePlayButton();
  $('fallback').className = 'fallback show';
}

$('pauseBtn').addEventListener('click', togglePlay);
$('previous').addEventListener('click', () => stepTrack(-1));
$('next').addEventListener('click', () => stepTrack(1));
$('shuffle').addEventListener('click', () => stepTrack(1, true));
$('repeat').addEventListener('click', () => {
  repeat = !repeat;
  $('repeat').classList.toggle('active', repeat);
});

$('progressBar').addEventListener('click', (event) => {
  if (!duration) return;

  const seconds = event.offsetX / event.currentTarget.clientWidth * duration;
  if (nowPlaying?.type === 'yt') {
    sendYouTubeCommand('seekTo', [seconds, true]);
  } else {
    player.querySelector('iframe')?.contentWindow.postMessage(
      JSON.stringify({ method: 'seekTo', value: seconds * 1000 }),
      '*'
    );
  }
  setProgress(seconds, null);
});

// Persisted pinned links
async function loadPins() {
  const saved = await window.widget.loadPins();
  if (Array.isArray(saved)) pins = saved;
  while (pins.length < 4) pins.push(null);
  renderPins();
}

function persistPins() {
  window.widget.savePins(pins);
}

function renderPins() {
  $('pins').innerHTML = '';

  pins.forEach((pin, index) => {
    const button = document.createElement('button');
    button.className = 'chip';
    button.textContent = pin ? pin.name : '+ add';
    button.addEventListener('click', () => {
      if (pin) {
        loadTrack(pin.url, pin.name, index);
      } else {
        editPin(index);
      }
    });

    if (pin) {
      const remove = document.createElement('span');
      remove.className = 'x';
      remove.textContent = ' ×';
      remove.addEventListener('click', (event) => {
        event.stopPropagation();
        pins[index] = null;
        persistPins();
        renderPins();
      });
      button.append(remove);
      button.addEventListener('contextmenu', (event) => {
        event.preventDefault();
        editPin(index);
      });
    }

    $('pins').append(button);
  });
}

function editPin(index) {
  editingIndex = index;
  $('editName').value = pins[index]?.name || nowPlaying?.name || '';
  $('editUrl').value = pins[index]?.url || nowPlaying?.url || '';
  $('editor').className = 'editor show';
}

$('editSave').addEventListener('click', () => {
  if (editingIndex === null) return;

  const url = $('editUrl').value.trim();
  if (url) {
    pins[editingIndex] = {
      name: $('editName').value.trim() || 'favorite',
      url
    };
  }

  persistPins();
  renderPins();
  $('editor').className = 'editor';
  editingIndex = null;
});

$('editCancel').addEventListener('click', () => {
  $('editor').className = 'editor';
});

$('heart').addEventListener('click', () => {
  if (!nowPlaying) return;

  let index = pins.findIndex((pin) => !pin);
  if (index < 0) index = pins.length;
  pins[index] = { name: nowPlaying.name, url: nowPlaying.url };
  persistPins();
  renderPins();
  $('heart').textContent = '♥';
});

// General window and link controls
$('play').addEventListener('click', () => loadTrack());
$('link').addEventListener('keydown', (event) => {
  if (event.key === 'Enter') loadTrack();
});
$('openExternal').addEventListener('click', () => {
  if (lastExternalUrl) window.widget.open(lastExternalUrl);
});
$('pin').addEventListener('change', (event) => {
  window.widget.pin(event.target.checked);
});
$('maximize').addEventListener('click', () => {
  $('pin').checked = !$('pin').checked;
  window.widget.pin($('pin').checked);
});
$('minimize').addEventListener('click', () => window.widget.minimize());
$('close').addEventListener('click', () => window.widget.close());

// Custom scene image
function showGif(data) {
  if (data) {
    $('sceneGif').src = data;
    $('scene').classList.add('has-gif');
  } else {
    $('sceneGif').removeAttribute('src');
    $('scene').classList.remove('has-gif');
  }
}

$('gifBtn').addEventListener('click', () => $('gifFile').click());
$('gifFile').addEventListener('change', () => {
  const file = $('gifFile').files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.addEventListener('load', async () => {
    showGif(reader.result);
    await window.widget.saveGif(reader.result);
  });
  reader.readAsDataURL(file);
  $('gifFile').value = '';
});

$('clearGif').addEventListener('click', async () => {
  showGif(null);
  await window.widget.clearGif();
});

$('scene').addEventListener('contextmenu', (event) => {
  event.preventDefault();
  $('clearGif').click();
});

window.widget.loadGif().then(showGif).catch(() => {});
loadPins();
window.widget.resize(184);
