"""Simple script to switch logitech devices between different devices"""

import os
import time
import subprocess
import threading
import json
import sys

if sys.platform == "linux":
    import gi

    gi.require_version("Gtk", "3.0")
    gi.require_version("AppIndicator3", "0.1")
    from gi.repository import Gtk, AppIndicator3
else:
    import ctypes
    import pystray
    from PIL import Image, ImageDraw


def quit_app(icon=None, item=None) -> None:
    """Quit the application"""
    if sys.platform == "linux":
        Gtk.main_quit()
    elif sys.platform == "win32":
        icon.stop()
    os._exit(0)  # Ensure the whole script exits


def build_menu_linux():
    """Build the menu for the tray icon on Linux"""
    menu = Gtk.Menu()

    # Add a quit menu item
    quit_item = Gtk.MenuItem(label="Quit")
    quit_item.connect("activate", quit_app)
    menu.append(quit_item)

    menu.show_all()
    return menu


def create_tray_icon_linux() -> None:
    """Create the tray icon on Linux"""
    indicator = AppIndicator3.Indicator.new(
        "example-tray-icon",
        "network-transmit-receive",
        AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
    )
    indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu_linux())
    Gtk.main()


def create_tray_icon_windows() -> None:
    """Create the tray icon on Windows"""
    # Create a simple icon with pystray
    image = Image.new("RGB", (64, 64), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 64, 64), outline="white", fill="black")

    icon = pystray.Icon(
        "example-tray-icon",
        image,
        "Tray Icon",
        pystray.Menu(pystray.MenuItem("Quit", quit_app)),
    )
    icon.run()


def get_cursor_pos() -> tuple:
    """Get the current cursor position"""
    if sys.platform == "linux":
        output = os.popen("hyprctl cursorpos").read().strip()
        x_pos = int(output.split(",")[0])
        y_pos = int(output.split(",")[1])
        return x_pos, y_pos
    elif sys.platform == "win32":

        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y
    else:
        raise ValueError("Unsupported operating system")


def load_config(config_path: str = "config.json") -> dict:
    """Load the configuration file"""
    # change direcotry to the script directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)
    with open(config_path, "r") as f:
        config = json.load(f)
    return config


def main() -> None:
    """Main function"""
    # Load config file
    config = load_config()

    display_pos = config["display_pos"]
    display_height = config["display_height"]
    disable_corners = config["disable_corners"]
    devices = config["devices"]

    # Create and start the tray icon in a separate thread
    if sys.platform == "linux":
        tray_thread = threading.Thread(target=create_tray_icon_linux, daemon=True)
    elif sys.platform == "win32":
        tray_thread = threading.Thread(target=create_tray_icon_windows, daemon=True)
    else:
        raise ValueError("Unsupported operating system")
    tray_thread.start()

    run_script(
        display_pos=display_pos,
        display_height=display_height,
        disable_corners=disable_corners,
        devices=devices,
    )


def run_script(
    display_pos: int, display_height: int, disable_corners: bool, devices: dict
) -> None:
    """Run the script"""
    # change directory based on operating system and based on script directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    if sys.platform == "win32":
        os.chdir(os.path.join(script_dir, "windows"))
    else:
        os.chdir(os.path.join(script_dir, "linux"))

    prev_display_pos = -1
    while True:
        x_pos, y_pos = get_cursor_pos()

        # check if cursor is in the corner by checking the y_pos only
        if disable_corners:
            if y_pos > display_height - 20:
                time.sleep(0.1)
                continue
            elif y_pos < 20:
                time.sleep(0.1)
                continue

        if x_pos == display_pos and prev_display_pos != display_pos:
            for device in devices:
                vidpid = device["vidpid"]
                usage = device["usage"]
                usage_page = device["usage_page"]
                device_id = device["device_id"]
                to_channel = device["to_channel"] - 1  # channel number - 1
                device_number = (
                    device["device_number"] if not device["is_bluetooth"] else 1
                )
                length = 11 if device["is_bluetooth"] else 7

                # Convert toChannel to the appropriate value (e.g., 1 -> 0x01, 3 -> 0x03)
                to_channel_hex = f"0x{to_channel:02X}"
                device_number_hex = f"0x{device_number:02X}"

                # build "send-output" argument
                if device["is_bluetooth"]:
                    send_output_arg = (
                        f"0x11,{device_number_hex},{device_id[0]},{device_id[1]},{to_channel_hex},"
                        "0x00,0x00,0x00,0x00,0x00,0x00"
                    )
                else:
                    send_output_arg = (
                        f"0x10,{device_number_hex},{device_id[0]},{device_id[1]},{to_channel_hex},"
                        "0x00,0x00"
                    )

                hidapitester_cmd = [
                    "hidapitester.exe" if sys.platform == "win32" else "./hidapitester",
                    "--vidpid",
                    vidpid,
                    "--usage",
                    usage,
                    "--usagePage",
                    usage_page,
                    "--open",
                    "--length",
                    str(length),
                    "--send-output",
                    send_output_arg,
                ]

                # run 3 times because sometimes it doesn't work on the first try for some reason
                for _ in range(3):
                    subprocess.run(
                        hidapitester_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                        **(
                            {"creationflags": subprocess.CREATE_NO_WINDOW}
                            if sys.platform == "win32"
                            else {}
                        ),
                    )

        # set prev_display_pos to x_pos
        prev_display_pos = x_pos

        # sleep 100ms
        time.sleep(0.1)


if __name__ == "__main__":
    main()
