import ctypes
import json
import tkinter as tk
from pathlib import Path


# Keep all app paths relative to this file so the batch file can be run from anywhere.
APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "animation_config.json"

# Tkinter's transparent-color mode removes pixels matching this exact color.
DEFAULT_TRANSPARENT = "#010203"

# Tkinter can load these formats without extra packages.
IMAGE_EXTENSIONS = {".gif", ".png", ".ppm", ".pgm"}


# Windows style flags used only for optional click-through mode.
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020


def load_config():
    """Read the user-editable JSON config, or use defaults if it is missing."""
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_asset(value):
    """Turn the config's animation path into an absolute local path."""
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = APP_DIR / path
    return path


def first_animation_in_folder(folder):
    """Find a usable dropped file when the exact config path is wrong or missing."""
    if not folder.exists() or not folder.is_dir():
        return None
    candidates = [
        path for path in sorted(folder.iterdir())
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return candidates[0] if candidates else None


def sniff_image_type(path):
    """Detect the real image type because downloaded files often have wrong extensions."""
    try:
        with path.open("rb") as handle:
            header = handle.read(16)
    except OSError:
        return ""
    if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
        return "gif"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    return path.suffix.lower().lstrip(".")


class BorderlessAnimationPlayer:
    def __init__(self):
        # Config controls the animation source, size, transparency, and window behavior.
        self.config = load_config()
        self.transparent = self.config.get("transparent_color", DEFAULT_TRANSPARENT)
        self.scale = float(self.config.get("scale", 1.0))
        self.screen_percent = self.config.get("screen_percent")
        self.delay = int(self.config.get("frame_delay_ms", 80))
        self.frames = []
        self.frame_index = 0
        self.paused = False
        self.drag = None

        # Create a borderless Tk window. The transparent color makes the background vanish.
        self.root = tk.Tk()
        self.root.title("Borderless Animation Player")
        self.root.overrideredirect(True)
        self.root.configure(bg=self.transparent)
        self.root.wm_attributes("-transparentcolor", self.transparent)
        self.root.wm_attributes("-topmost", bool(self.config.get("always_on_top", True)))

        # The label is the whole visible widget: each animation frame is swapped into it.
        self.label = tk.Label(self.root, bg=self.transparent, bd=0, highlightthickness=0)
        self.label.pack()

        # Right-click menu for runtime controls without editing config.
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Pause / resume", command=self.toggle_pause)
        self.menu.add_command(label="Reload animation", command=self.reload)
        self.menu.add_separator()
        self.menu.add_command(label="25% of screen", command=lambda: self.set_screen_percent(25))
        self.menu.add_command(label="20% of screen", command=lambda: self.set_screen_percent(20))
        self.menu.add_command(label="15% of screen", command=lambda: self.set_screen_percent(15))
        self.menu.add_command(label="10% of screen", command=lambda: self.set_screen_percent(10))
        self.menu.add_command(label="5% of screen", command=lambda: self.set_screen_percent(5))
        self.menu.add_separator()
        self.menu.add_command(label="Original size", command=lambda: self.set_scale(1.0))
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.root.destroy)

        # Keyboard and mouse controls. Dragging is disabled when click-through is enabled.
        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.bind("<space>", lambda _event: self.toggle_pause())
        self.label.bind("<ButtonPress-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.move_drag)
        self.label.bind("<ButtonRelease-1>", self.stop_drag)
        self.label.bind("<Button-3>", self.show_menu)

        self.reload()
        self.apply_click_through()

    def apply_click_through(self):
        """Let mouse clicks pass through the widget to the window underneath."""
        if not self.config.get("click_through", False):
            return
        self.root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)

    def reload(self):
        """Re-read config and reload the animation without restarting the app."""
        self.config = load_config()
        self.transparent = self.config.get("transparent_color", DEFAULT_TRANSPARENT)
        self.scale = float(self.config.get("scale", self.scale))
        self.screen_percent = self.config.get("screen_percent", self.screen_percent)
        self.delay = int(self.config.get("frame_delay_ms", self.delay))
        self.root.configure(bg=self.transparent)
        self.label.configure(bg=self.transparent)
        self.root.wm_attributes("-transparentcolor", self.transparent)
        self.root.wm_attributes("-topmost", bool(self.config.get("always_on_top", True)))

        # Prefer the configured path; fall back to the first dropped animation file.
        asset = resolve_asset(self.config.get("animation"))
        if not asset or not asset.exists():
            asset = first_animation_in_folder(APP_DIR / "animations")
        self.frames = self.load_frames(asset)
        self.frame_index = 0

        x = int(self.config.get("start_x", self.root.winfo_x()))
        y = int(self.config.get("start_y", self.root.winfo_y()))
        if self.frames:
            self.resize_window(x, y)
            self.show_current_frame()
        else:
            self.show_missing_animation(x, y)

    def load_frames(self, asset):
        """Load a GIF, still image, or folder of frame images into Tk PhotoImages."""
        if not asset:
            return []
        if asset.is_dir():
            files = sorted(path for path in asset.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS)
            return [tk.PhotoImage(file=str(path)) for path in files]
        image_type = sniff_image_type(asset)
        if image_type == "gif":
            return self.load_gif(asset)
        if image_type in {"png", "ppm", "pgm"} and asset.exists():
            return [tk.PhotoImage(file=str(asset))]
        if asset.suffix.lower() in IMAGE_EXTENSIONS and asset.exists():
            return [tk.PhotoImage(file=str(asset))]
        return []

    def load_gif(self, path):
        """Read every frame from an animated GIF until Tk reports no more frames."""
        frames = []
        index = 0
        while True:
            try:
                frames.append(tk.PhotoImage(file=str(path), format=f"gif -index {index}"))
                index += 1
            except tk.TclError:
                break
        return frames

    def scaled_frame(self, frame):
        """Return a display-sized frame using Tk's built-in integer scaling."""
        target_scale = self.effective_scale(frame)
        if abs(target_scale - 1) < 0.01:
            return frame

        # Tkinter scaling is integer based. For shrink sizes, subsampling is the reliable path.
        if target_scale < 1:
            subsample_by = max(1, round(1 / target_scale))
            return frame.subsample(subsample_by, subsample_by)

        zoom_by = max(1, round(target_scale))
        return frame.zoom(zoom_by, zoom_by)

    def effective_scale(self, frame):
        """Calculate scale from screen_percent first, then fall back to raw scale."""
        if self.screen_percent:
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            target = min(screen_w, screen_h) * (float(self.screen_percent) / 100)
            largest_side = max(frame.width(), frame.height(), 1)
            return max(0.03, target / largest_side)
        return self.scale

    def resize_window(self, x=None, y=None):
        """Resize the borderless window to exactly fit the current animation frame."""
        frame = self.scaled_frame(self.frames[0])
        self.current_scaled = frame
        width = frame.width()
        height = frame.height()
        if x is None:
            x = self.root.winfo_x()
        if y is None:
            y = self.root.winfo_y()
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def show_current_frame(self):
        """Display one frame, advance the index, then schedule the next frame."""
        if not self.frames:
            return
        frame = self.scaled_frame(self.frames[self.frame_index])
        self.current_scaled = frame
        self.label.configure(image=frame, text="")
        self.root.geometry(f"{frame.width()}x{frame.height()}+{self.root.winfo_x()}+{self.root.winfo_y()}")
        if not self.paused:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.root.after(self.delay, self.show_current_frame)

    def show_missing_animation(self, x, y):
        """Show a small help message when no usable animation file can be found."""
        self.label.configure(
            image="",
            text="Drop a GIF into animations\\diane.gif\nor edit animation_config.json",
            fg="#f4f7f7",
            bg="#1b242b",
            font=("Segoe UI", 11, "bold"),
            padx=18,
            pady=14,
        )
        self.root.geometry(f"320x92+{x}+{y}")

    def set_scale(self, value):
        """Use the source asset's original size multiplied by a raw scale value."""
        self.scale = value
        self.screen_percent = None
        if self.frames:
            self.resize_window()
            self.show_current_frame()

    def set_screen_percent(self, value):
        """Resize the widget relative to the smaller side of the user's screen."""
        self.screen_percent = value
        if self.frames:
            self.resize_window()
            self.show_current_frame()

    def toggle_pause(self):
        """Pause or resume frame advancement."""
        self.paused = not self.paused

    def start_drag(self, event):
        """Remember the pointer and window positions when dragging starts."""
        if self.config.get("click_through", False):
            return
        self.drag = (event.x_root, event.y_root, self.root.winfo_x(), self.root.winfo_y())

    def move_drag(self, event):
        """Move the borderless window while the left mouse button is held."""
        if not self.drag:
            return
        sx, sy, wx, wy = self.drag
        self.root.geometry(f"+{wx + event.x_root - sx}+{wy + event.y_root - sy}")

    def stop_drag(self, _event):
        """Clear drag state when the mouse button is released."""
        self.drag = None

    def show_menu(self, event):
        """Open the right-click menu unless click-through mode disables interaction."""
        if self.config.get("click_through", False):
            return
        self.menu.tk_popup(event.x_root, event.y_root)

    def run(self):
        """Start Tk's event loop."""
        self.root.mainloop()


if __name__ == "__main__":
    BorderlessAnimationPlayer().run()
