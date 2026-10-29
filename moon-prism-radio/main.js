const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const fs = require('fs');

// Let the embedded players start without a click inside the iframe
app.commandLine.appendSwitch('autoplay-policy', 'no-user-gesture-required');

let win;

// ---- tiny on-disk store for pinned links (survives restarts) ----
const storePath = path.join(app.getPath('userData'), 'pins.json');

function readPins() {
  try { return JSON.parse(fs.readFileSync(storePath, 'utf8')); }
  catch { return null; }
}
function writePins(pins) {
  try { fs.writeFileSync(storePath, JSON.stringify(pins, null, 2)); return true; }
  catch { return false; }
}

// ---- scene gif storage (survives restarts) ----
// We copy the user's chosen gif into userData and hand the renderer a data URL.
const gifPath = path.join(app.getPath('userData'), 'scene.gif');

function readGif() {
  try {
    const buf = fs.readFileSync(gifPath);
    return 'data:image/gif;base64,' + buf.toString('base64');
  } catch { return null; }
}
function writeGif(dataUrl) {
  try {
    // dataUrl looks like data:image/gif;base64,XXXX (or png/webp — all fine in <img>)
    const comma = dataUrl.indexOf(',');
    const b64 = comma >= 0 ? dataUrl.slice(comma + 1) : dataUrl;
    fs.writeFileSync(gifPath, Buffer.from(b64, 'base64'));
    return true;
  } catch { return false; }
}
function clearGif() {
  try { fs.unlinkSync(gifPath); } catch {}
  return true;
}

function createWindow() {
  win = new BrowserWindow({
    width: 505,
    height: 184,
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    hasShadow: false,
    skipTaskbar: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.loadFile('index.html');

  // YouTube embeds want a Referer (avoids Error 153 from a local file).
  win.webContents.session.webRequest.onBeforeSendHeaders(
    { urls: ['*://*.youtube.com/*', '*://*.youtube-nocookie.com/*', '*://*.googlevideo.com/*'] },
    (details, callback) => {
      details.requestHeaders['Referer'] = 'https://www.youtube.com/';
      details.requestHeaders['Origin'] = 'https://www.youtube.com';
      callback({ requestHeaders: details.requestHeaders });
    }
  );

  // Float above full-screen apps too (handy while studying)
  win.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  win.setAlwaysOnTop(true, 'floating');

  // Keep external links out of the widget window
  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

// ---- IPC ----
ipcMain.on('widget:resize', (_e, height) => {
  if (!win) return;
  const [w] = win.getSize();
  win.setSize(w, Math.round(height), true);
});

ipcMain.on('widget:pin', (_e, pinned) => {
  if (!win) return;
  win.setAlwaysOnTop(pinned, 'floating');
});

ipcMain.on('widget:minimize', () => {
  if (win) win.minimize();
});

ipcMain.on('widget:open', (_e, url) => shell.openExternal(url));

ipcMain.on('widget:close', () => app.quit());

ipcMain.handle('pins:load', () => readPins());
ipcMain.handle('pins:save', (_e, pins) => writePins(pins));

ipcMain.handle('gif:load', () => readGif());
ipcMain.handle('gif:save', (_e, dataUrl) => writeGif(dataUrl));
ipcMain.handle('gif:clear', () => clearGif());

app.whenReady().then(createWindow);

app.on('window-all-closed', () => app.quit());
