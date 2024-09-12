# logitech device switch

This tool is to switch logitech devices between two computers when hitting the border of the screen. It works in linux in combination with [Hyprland](https://hyprland.org/) and in Windows.

I mainly wrote this so I don't have to switch my keyboard and mouse manually between my two computers at work. It may work for you or it may not. [Hyprland](https://hyprland.org/) makes it easy to grab the global mouse position which is usually not that easy using wayland as far as I know.

## Install

Download [hidapitester](https://github.com/todbot/hidapitester) and put it into the `linux` or `windows` subdirectory. This is where the script searches for it.

The rest of the installation is platform dependent.

## Linux

You need to install the following packages:

```bash
sudo pacman -S libappindicator-gtk3 python-gobject
```

`hidapitester` needs access to the USB devices. Therefore you need to add a udev rule. Copy the file `linux/42-logitech-unify.rules` to `/etc/udev/rules.d/`:

```bash
sudo cp linux/42-logitech-unify.rules /etc/udev/rules.d/
```

It is using the group `plugdev`. You may need to create the group and add your user to it:

```bash
sudo groupadd plugdev
sudo usermod -aG plugdev $USER
```

You may need to log out and log in again for the changes to take effect.

Reload the udev rules:

```bash
sudo udevadm control --reload-rules
```

Create a virtual environment and install the requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install PyGObject
```

The last step is to edit and copy the file `linux/LogitechDeviceSwitch.desktop` to `~/.local/share/applications/`:

```bash
cp linux/LogitechDeviceSwitch.desktop ~/.local/share/applications/
```

Make sure to edit the `Exec` line to point to the correct paths.

## Windows

In Windows it is a bit easier. Just install the virutaenv and the requirements:

```cmd
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pystray
```

There is a script called `logitech_device_switch_win_background.vbs` which is able to start the tool in background. You can create a shortcut to this script and put it into the start menu by copying it to `%appdata%\Microsoft\Windows\Start Menu\Programs`.

## Configuration

Copy the file `config.json.example` to `config.json`. The file must be in the same directory as the script.

The script contains the following configuration options:

* *display_pos* - The position of the border of the screen you want to touch to switch the devices. For the left border it will be 0, for the right border it will be the width of the screen minus one. E.g. 5119 if you use 2 2560x1440 monitors.
* *display_height* - The height of the display. It is used by the next option to get the correct positions of the corners.
* *disable_corners* - If set to true the script will not switch the devices when the mouse is in the corners of the screen.
* *devices* - The array of Logitech devices to switch. The options for each device are explained below.

The options for each device are:

* *vidpid* - The vendor and product id of the device. For the logitech unifying receiver it should be `046d:c52b`.
* *usage* - The usage of the device. For the logitech unifying receiver it is always `0x0001`.
* *usage_page* - The usage page of the device. For the logitech unifying receiver it is always `0xFF00`.
* *device_id* - I called it device ID but I don't know what it is but it needs to be correct.
* *device_number* - The number of the device connected to the unifying receiver. The first connected device will be 1, the second 2 and so on.
* *to_channel* - The channel you want to switch to.
* *is_bluetooth* - If the device is connected via bluetooth set this to true.

Finding out the correct values for *vidpid*, *usage*, *usage_page* is easy. Just go into the subdirectory of your platform and run the `hidapitester --list-detail`. It will list all connected devices with the correct values.

Here is an example output for the unifying receiver:

```bash
046D/C52B: Logitech - USB Receiver
  vendorId:      0x046D
  productId:     0xC52B
  usagePage:     0xFF00
  usage:         0x0001
  serial_number:  
  interface:     2 
  path: /dev/hidraw0
```

It will be different but self-explanatory for bluetooth devices. Make sure to set *is_bluetooth* to true if the device is connected via bluetooth.

The more complicated part is to find out the correct values for *device_id* and *device_number*. You can use `solaar` to find out the correct values. Open `solaar` with debug output enabled:

```bash
solaar -ddd
```

The first thing you will see is the device list. Out of the order of the devices you can set the correct value for *device_number*. The top device will be 1, the second 2 and so on.

Then select a device and unlock the last option _Change Host_. Change the host to another device and you will see the correct value for *device_id* in the debug output. It will look like this:

```bash
DEBUG [AsyncUI] logitech_receiver.base: (20) <= w[11 01 0A1E 02000000000000000000000000000000]
```

In this case the *device_id* is `0A1E`. So within the config write:

```json
"device_id": [
    "0x0a",
    "0x1e"
]
```

Repeat this for all devices you want to switch and finalize the configuration.

## Usage

Once everything is configured you can start the script. Either use the desktop file in linux or the shortcut in windows. The tool will create a tray icon which you can use to quit the tool.

## Special thanks

I used the explanation of the [input-switcher](https://github.com/marcelhoffs/input-switcher) repository as base for this repository. I also copied the file `linux/42-logitech-unify.rules` from there.
