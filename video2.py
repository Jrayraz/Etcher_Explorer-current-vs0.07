import tkinter as tk
from tkinter import filedialog
from ffpyplayer.player import MediaPlayer
from PIL import Image, ImageTk
import threading
import time
import os
import psutil
import signal

class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player")
        self.root.geometry("800x600")
        self.root.configure(bg="black")
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

        self.video_frame = tk.Frame(self.root, bg="black", width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight() - 100)
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        self.video_label = tk.Label(self.video_frame, bg="black")
        self.video_label.pack(fill=tk.BOTH, expand=True)

        self.time_frame = tk.Frame(self.root)
        self.time_frame.pack(side=tk.TOP, fill=tk.X)

        self.time_lapsed_label = tk.Label(self.time_frame, text="Time Lapsed: 00:00")
        self.time_lapsed_label.pack(side=tk.LEFT)

        self.time_remaining_label = tk.Label(self.time_frame, text="Time Remaining: 00:00")
        self.time_remaining_label.pack(side=tk.RIGHT)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.load_button = tk.Button(self.control_frame, text="Load Video", command=self.load_video)
        self.load_button.grid(row=0, column=0)

        self.play_pause_button = tk.Button(self.control_frame, text="Play/Pause", command=self.play_pause)
        self.play_pause_button.grid(row=0, column=1)

        self.stop_button = tk.Button(self.control_frame, text="Stop", command=self.stop_video)
        self.stop_button.grid(row=0, column=2)

        self.repeat1_button = tk.Button(self.control_frame, text="Repeat 1", command=self.repeat1)
        self.repeat1_button.grid(row=0, column=3)

        self.repeat_all_button = tk.Button(self.control_frame, text="Repeat All", command=self.repeat_all)
        self.repeat_all_button.grid(row=0, column=4)

        self.reverse_30s_button = tk.Button(self.control_frame, text="Reverse 30s", command=self.reverse_30s)
        self.reverse_30s_button.grid(row=0, column=5)

        self.forward_30s_button = tk.Button(self.control_frame, text="Forward 30s", command=self.forward_30s)
        self.forward_30s_button.grid(row=0, column=6)

        self.reverse_1m_button = tk.Button(self.control_frame, text="Reverse 1m", command=self.reverse_1m)
        self.reverse_1m_button.grid(row=0, column=7)

        self.forward_1m_button = tk.Button(self.control_frame, text="Forward 1m", command=self.forward_1m)
        self.forward_1m_button.grid(row=0, column=8)

        self.point_a_to_b_button = tk.Button(self.control_frame, text="Point A to B", command=self.point_a_to_b)
        self.point_a_to_b_button.grid(row=0, column=9)

        self.slo_mo_button = tk.Button(self.control_frame, text="Slo Mo", command=self.slo_mo)
        self.slo_mo_button.grid(row=0, column=10)

        self.exit_button = tk.Button(self.control_frame, text="Exit", command=self.exit_app)
        self.exit_button.grid(row=0, column=11)

        self.volume_slider = tk.Scale(self.control_frame, from_=0, to=100, orient=tk.HORIZONTAL, label="Volume", command=self.set_volume)
        self.volume_slider.set(50)
        self.volume_slider.grid(row=0, column=12)

        self.video_path = None
        self.is_playing = False
        self.player = None
        self.thread = None
        self.volume = 50

        self.repeat_one = False
        self.repeat_all = False
        self.slo_mo_mode = False
        self.point_a = None
        self.point_b = None
        self.skip_time = 30  # Default skip time in seconds

        self.root.bind("<KeyPress>", self.key_press)

    def load_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if self.video_path:
            self.player = MediaPlayer(self.video_path)
            self.is_playing = True
            self.thread = threading.Thread(target=self.play_video)
            self.thread.start()

    def play_video(self):
        while self.is_playing:
            frame, val = self.player.get_frame()
            if val == 'eof':
                self.stop_video()
                if self.repeat_one:
                    self.load_video()
                elif self.repeat_all:
                    self.load_video()
                else:
                    break
            elif frame is not None:
                img, t = frame
                img = Image.frombytes('RGB', img.get_size(), img.to_bytearray()[0])
                imgtk = ImageTk.PhotoImage(image=img)
                self.root.after(0, self.update_image, imgtk)
                self.update_time_labels()
                sleep_time = 0.03 if not self.slo_mo_mode else 0.06
                time.sleep(sleep_time)

    def update_image(self, imgtk):
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

    def update_time_labels(self):
        if self.player:
            total_seconds = self.player.get_metadata()['duration']
            current_seconds = self.player.get_pts()

            time_lapsed = time.strftime("%H:%M:%S", time.gmtime(current_seconds))
            time_remaining = time.strftime("%H:%M:%S", time.gmtime(total_seconds - current_seconds))

            self.time_lapsed_label.config(text=f"Time Lapsed: {time_lapsed}")
            self.time_remaining_label.config(text=f"Time Remaining: {time_remaining}")

    def play_pause(self):
        if self.is_playing:
            self.player.set_pause(True)
        else:
            self.player.set_pause(False)
        self.is_playing = not self.is_playing

    def stop_video(self):
        self.is_playing = False
        if self.player:
            self.player.close_player()

    def set_volume(self, value):
        self.volume = int(value)
        if self.player:
            self.player.set_volume(self.volume / 100)

    def repeat1(self):
        self.repeat_one = not self.repeat_one

    def repeat_all(self):
        self.repeat_all = not self.repeat_all

    def reverse_30s(self):
        self.skip_time = 30
        self.skip_video(-self.skip_time)

    def forward_30s(self):
        self.skip_time = 30
        self.skip_video(self.skip_time)

    def reverse_1m(self):
        self.skip_time = 60
        self.skip_video(-self.skip_time)

    def forward_1m(self):
        self.skip_time = 60
        self.skip_video(self.skip_time)

    def skip_video(self, seconds):
        if self.player:
            current_pts = self.player.get_pts()
            new_pts = max(current_pts + seconds, 0)
            self.player.seek(new_pts, relative=False)

    def point_a_to_b(self):
        if self.player:
            current_pts = self.player.get_pts()
            if not self.point_a:
                self.point_a = current_pts
            elif not self.point_b:
                self.point_b = current_pts
            else:
                self.point_a = self.point_b = None

    def slo_mo(self):
        self.slo_mo_mode = not self.slo_mo_mode

    def key_press(self, event):
        if event.keysym == "Escape":
            self.exit_app()

    def exit_app(self):
        self.stop_video()
        self.root.quit()
        self.on_closing()
        
    def on_closing(self):
        # Terminate the parent terminal process
        parent_pid = psutil.Process(os.getpid()).ppid()
        os.kill(parent_pid, signal.SIGTERM)
        # Close the Tkinter window
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    player = VideoPlayer(root)
    root.mainloop()
