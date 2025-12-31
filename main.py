import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess

IMAGE_EXTS = ('.png', '.jpg', '.jpeg')


def get_frame_files(frame_dir):
    return sorted(
        [f for f in os.listdir(frame_dir) if f.lower().endswith(IMAGE_EXTS)]
    )

# Function to rename all image files in a directory
def rename_frames(frame_dir):
    frame_dir = os.path.abspath(frame_dir)
    files = get_frame_files(frame_dir)
    if not files:
        return

    target_paths = []
    for i, filename in enumerate(files, start=1):
        _, ext = os.path.splitext(filename)
        target_paths.append(os.path.join(frame_dir, f"{i:05d}{ext}"))

    # Two-pass rename avoids collisions with existing names.
    reserved_temps = set()
    rename_plan = []
    target_set = set(target_paths)
    for i, filename in enumerate(files, start=1):
        src = os.path.join(frame_dir, filename)
        _, ext = os.path.splitext(filename)
        target = os.path.join(frame_dir, f"{i:05d}{ext}")
        temp = os.path.join(frame_dir, f"__tmp_rename_frames__{i:05d}__{ext}")
        counter = 0
        while (
            os.path.exists(temp)
            or temp in reserved_temps
            or temp in target_set
            or temp == src
            or temp == target
        ):
            counter += 1
            temp = os.path.join(
                frame_dir, f"__tmp_rename_frames__{i:05d}__{counter}{ext}"
            )
        reserved_temps.add(temp)
        rename_plan.append((src, temp, target))

    for src, temp, _ in rename_plan:
        if src != temp:
            os.rename(src, temp)

    for _, temp, target in rename_plan:
        if temp != target:
            os.rename(temp, target)

# Function to split a video into frames
def split_video(video_file, output_dir):
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    command = f'ffmpeg -i "{video_file}" "{os.path.join(output_dir, "frame_%05d.png")}"'
    subprocess.run(command, shell=True, check=True)

# Function to merge frames into a video
def merge_frames(frame_dir, output_file, frame_rate):
    # Step 1: Rename frames
    rename_frames(frame_dir)

    # Step 2: Merge renamed frames into video
    frame_dir = os.path.abspath(frame_dir)
    files = get_frame_files(frame_dir)
    if not files:
        raise ValueError("No image frames found to merge.")
    ext_set = {os.path.splitext(f)[1] for f in files}
    if len(ext_set) != 1:
        raise ValueError(
            "Frame files have mixed extensions; please keep a single format."
        )
    frame_ext = next(iter(ext_set))
    frame_pattern = os.path.join(frame_dir, f"%05d{frame_ext}")
    command = (
        f'ffmpeg -r {frame_rate} -i "{frame_pattern}" -c:v libx264 '
        f'-profile:v high -level 4.1 -pix_fmt yuv420p "{output_file}"'
    )
    subprocess.run(command, shell=True, check=True)

def transcode_video(input_file, output_file, codec):
    command = f'ffmpeg -i "{input_file}" -c:v {codec} -preset fast -c:a aac "{output_file}"'
    subprocess.run(command, shell=True, check=True)

def reverse_video(input_file, output_file):
    command = f'ffmpeg -i "{input_file}" -vf reverse -af areverse "{output_file}"'
    subprocess.run(command, shell=True, check=True)

def extract_audio(input_file, output_file):
    command = f'ffmpeg -i "{input_file}" -vn -acodec copy "{output_file}"'
    subprocess.run(command, shell=True, check=True)


def main():
    root = tk.Tk()
    root.title("FFmpeg GUI")
    root.geometry("500x500")

    # Function to split video to frames
    def split_video_to_frames():
        video_file = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4;*.avi;*.mkv"), ("All Files", "*.*")]
        )
        if not video_file:
            messagebox.showwarning("No File Selected", "Please select a video file.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Directory for Frames")
        if not output_dir:
            messagebox.showwarning("No Directory Selected", "Please select an output directory.")
            return

        try:
            split_video(video_file, output_dir)
            messagebox.showinfo("Success", f"Frames saved to: {output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to split video: {e}")

    # Function to merge frames into video
    def merge_frames_to_video():
        frame_dir = filedialog.askdirectory(title="Select Directory Containing Frames")
        if not frame_dir:
            messagebox.showwarning("No Directory Selected", "Please select a frame directory.")
            return

        output_file = filedialog.asksaveasfilename(
            title="Save Video File As",
            defaultextension=".mp4",
            filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")]
        )
        if not output_file:
            messagebox.showwarning("No Output File", "Please specify the output video file.")
            return

        try:
            frame_rate = int(fps_input.get())
            if frame_rate <= 0:
                raise ValueError("Frame rate must be a positive integer.")
            # Merge frames into video after renaming
            merge_frames(frame_dir, output_file, frame_rate)
            messagebox.showinfo("Success", f"Video saved to: {output_file}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge frames: {e}")
        
    def transcode_video_ui():
        input_file = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4;*.avi;*.mkv;*.mov"), ("All Files", "*.*")]
        )
        if not input_file:
            messagebox.showwarning("No File Selected", "Please select a video file.")
            return
        
        output_file = filedialog.asksaveasfilename(
            title="Save Transcoded Video As",
            defaultextension=".mp4",
            filetypes=[("MP4", "*.mp4"), ("AVI", "*.avi"), ("MKV", "*.mkv"), ("MOV", "*.mov")]
        )
        if not output_file:
            messagebox.showwarning("No Output File", "Please specify the output video file.")
            return
        
        codec = "libx264" if output_file.endswith(".mp4") else "libxvid" if output_file.endswith(".avi") else "libx265"
        
        try:
            transcode_video(input_file, output_file, codec)
            messagebox.showinfo("Success", f"Transcoded video saved to: {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to transcode video: {e}")

    def reverse_video_ui():
        input_file = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4;*.avi;*.mkv;*.mov"), ("All Files", "*.*")]
        )
        if not input_file:
            messagebox.showwarning("No File Selected", "Please select a video file.")
            return
        
        output_file = filedialog.asksaveasfilename(
            title="Save Reversed Video As",
            defaultextension=".mp4",
            filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")]
        )
        if not output_file:
            messagebox.showwarning("No Output File", "Please specify the output video file.")
            return
        
        try:
            reverse_video(input_file, output_file)
            messagebox.showinfo("Success", f"Reversed video saved to: {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reverse video: {e}")
    
    def extract_audio_ui():
        input_file = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4;*.avi;*.mkv;*.mov"), ("All Files", "*.*")]
        )
        if not input_file:
            messagebox.showwarning("No File Selected", "Please select a video file.")
            return

        output_file = filedialog.asksaveasfilename(
            title="Save Audio File As",
            defaultextension=".m4a",
            filetypes=[("M4A Audio", "*.m4a"), ("MP3 Audio", "*.mp3"), ("All Files", "*.*")]
        )
        if not output_file:
            messagebox.showwarning("No Output File", "Please specify the output audio file.")
            return

        try:
            extract_audio(input_file, output_file)
            messagebox.showinfo("Success", f"Audio extracted to: {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract audio: {e}")




    # UI Elements
    label = ttk.Label(root, text="FFmpeg GUI", font=("Arial", 16))
    label.pack(pady=10)

    split_button = ttk.Button(root, text="Split Video to Frames", command=split_video_to_frames)
    split_button.pack(pady=10)

    merge_button = ttk.Button(root, text="Merge Frames to Video", command=merge_frames_to_video)
    merge_button.pack(pady=10)

    fps_label = ttk.Label(root, text="Frame Rate:")
    fps_label.pack(pady=5)

    fps_input = ttk.Entry(root)
    fps_input.pack(pady=5)
    fps_input.insert(0, "30")  # Default frame rate
    
    transcode_button = ttk.Button(root, text="Transcode Video", command=transcode_video_ui)
    transcode_button.pack(pady=10)

    reverse_button = ttk.Button(root, text="Reverse Video", command=reverse_video_ui)
    reverse_button.pack(pady=10)

    extract_audio_button = ttk.Button(root, text="Extract Audio", command=extract_audio_ui)
    extract_audio_button.pack(pady=10)


    root.mainloop()

if __name__ == "__main__":
    main()

