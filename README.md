# Restim

Restim is a realtime e-stim signal generator for multi-electrode setups.

Refer to the [wiki](https://github.com/diglet48/restim/wiki) for help.

## Supported hardware

* Stereostim (three-phase only) and other audio-based devices (Mk312, 2B, ...)
* FOC-Stim
* NeoDK (coming soon)

## Main features

* Control e-stim signals with funscript or user interface.
* Synchronize e-stim with video or games.
* Calibrate signal for your preferred electrode configuration.

## Installation

### Windows
download the latest release package: https://github.com/diglet48/restim/releases

### Linux 
make sure python 3.10 or newer is installed on your system.  
Download the Restim source code, and execute `run.sh`

### Mac
Grab the latest `.dmg` from [Releases][releases] —
`Restim-arm64.dmg` for Apple Silicon (M1+) or `Restim-x86_64.dmg`
for Intel. Open the DMG and drag Restim.app to Applications.

**First launch** — macOS will block the app because it's not signed
with an Apple Developer ID. Pick one of:

*Option A — System Settings (no terminal required):*

1. Double-click Restim in Applications. You'll get a dialog saying
   it can't be opened or was blocked — dismiss it.
2. Open **System Settings → Privacy & Security**, scroll down to
   the Security section. You'll see a message about Restim being
   blocked, with an **Open Anyway** button. Click it.
3. Confirm with Touch ID or your password, then click **Open** in
   the final dialog.

*Option B — one-line terminal command:*

Open Terminal and paste:

```sh
xattr -dr com.apple.quarantine /Applications/Restim.app
```

Then double-click the app normally. This removes the "downloaded
from the internet" flag that triggers Gatekeeper; it does not
disable Gatekeeper system-wide or require sudo.

Subsequent launches are normal double-clicks either way.

> Older guides mention a "right-click → Open" shortcut. That path
> was removed in macOS Sequoia (15) for apps without a Developer ID
> signature; use one of the options above instead.

[releases]: https://github.com/diglet48/restim/releases

### Development:
install PyCharm and python 3.10 or newer.
Open Settings, python interpreter, and configure a new venv.
Navigate to requirements.txt and install the dependencies. Then run restim.py.