import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import font
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import ttk  # Import ttk for the progress bar
from PIL import Image, ImageTk
import threading  # Import threading for background tasks
import time  # For tracking elapsed time
from . import video_helpers  # Import video_helpers
import re
from moviepy import (VideoFileClip, concatenate_videoclips)
import random
import subprocess
import platform
import traceback
import pygame  # Import pygame for audio playback

class VideoUI:
    def __init__(self):
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

        # Play the startup sound
        self.play_startup_sound()

        self.root = TkinterDnD.Tk()
        self.root.title("SpeedyCollab Plus")
        self.root.geometry("850x900")
        self.root.resizable(False, False)  # Disable resizing
        self.root.configure(bg="dark green")  # Set background color to dark green
        # Define a bigger font size for everything
        self.default_font = font.Font(family="Helvetica", size=12)

        # Create a main frame for the UI
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side="left", fill="both", expand=True)

        # Create a frame for progress info
        self.progress_frame = ttk.Frame(self.root, width=400)
        self.progress_frame.pack(side="right", fill="y")

        # Create a scrollable frame inside the main frame
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.selected_file = None
        self.create_widgets()

    def play_startup_sound(self):
        """Play the startup sound."""
        project_root = os.path.dirname(os.path.abspath(__file__))  # Get the directory of ui.py
        assets_folder = os.path.join(project_root, '..', 'assets')  # Go up one level and into 'assets'
        sound_path = os.path.join(assets_folder, 'startup.ogg')  # Path to the startup sound

        if os.path.exists(sound_path):
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
        else:
            print("Startup sound file not found:", sound_path)

    def play_finish_sound(self):
        """Play the finish sound."""
        project_root = os.path.dirname(os.path.abspath(__file__))  # Get the directory of ui.py
        assets_folder = os.path.join(project_root, '..', 'assets')  # Go up one level and into 'assets'
        sound_path = os.path.join(assets_folder, 'finish.ogg')  # Path to the finish sound

        if os.path.exists(sound_path):
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
        else:
            print("Finish sound file not found:", sound_path)

    def create_widgets(self):
        # Load the PNG image
        project_root = os.path.dirname(os.path.abspath(__file__))  # Get the directory of ui.py
        assets_folder = os.path.join(project_root, '..', 'assets')  # Go up one level and into 'assets'

        # Now construct the full path to the logo.png
        logo_path = os.path.join(assets_folder, 'SpeedyCollabLogo.png')
        self.image = Image.open(logo_path)  # Corrected path
        self.image = self.image.resize((150, 150))  # Resize the image to fit the UI
        self.image_tk = ImageTk.PhotoImage(self.image)

        # Label to show the image (on the left side)
        self.image_label = tk.Label(self.scrollable_frame, image=self.image_tk)
        self.image_label.pack(pady=10)

        # Button to select a video file
        self.select_button = tk.Button(
            self.scrollable_frame,
            text="Select Video File",
            font=self.default_font,
            command=self.browse_file,
            bg="green",  # Set background color to green
            fg="white"   # Set text color to white for better contrast
        )
        self.select_button.pack(pady=10)

        # Label to show selected file
        self.file_label = tk.Label(self.scrollable_frame, text="No file selected", font=self.default_font, wraplength=500)
        self.file_label.pack(pady=10)

        # Font settings group
        font_settings_frame = ttk.LabelFrame(self.scrollable_frame, text="Font Settings", padding=10)
        font_settings_frame.pack(fill="x", pady=10)

        # Dropdown for font color selection
        self.text_color_label = tk.Label(font_settings_frame, text="Select Number Font Color:", font=self.default_font)
        self.text_color_label.pack(pady=5)

        self.text_color_var = tk.StringVar(font_settings_frame)
        self.text_color_var.set("Red")  # default value

        self.color_options = ["Red", "White", "Blue", "Pink", "Yellow", "Orange", "Green", "Purple", "Random"]
        self.text_color_menu = tk.OptionMenu(font_settings_frame, self.text_color_var, *self.color_options)
        self.text_color_menu.config(font=self.default_font)
        self.text_color_menu.pack(pady=5)

        # Dropdown for font selection
        self.font_label = tk.Label(font_settings_frame, text="Select Font:", font=self.default_font)
        self.font_label.pack(pady=5)

        fonts_dir = "C:/Windows/Fonts"
        supported_formats = [".ttf", ".otf", ".woff", ".woff2"]
        available_fonts = [f.split(".")[0] for f in os.listdir(fonts_dir) if any(f.endswith(ext) for ext in supported_formats)]

        self.font_var = tk.StringVar(font_settings_frame)
        self.font_var.set("arial")  # Default font

        self.font_menu = tk.OptionMenu(font_settings_frame, self.font_var, *available_fonts)
        self.font_menu.config(font=self.default_font)
        self.font_menu.pack(pady=5)

        # Slider for font size adjustment
        self.font_size_label = tk.Label(font_settings_frame, text="Adjust Font Size:", font=self.default_font)
        self.font_size_label.pack(pady=5)

        self.font_size_var = tk.IntVar(value=150)  # Default font size
        self.font_size_slider = tk.Scale(
            font_settings_frame,
            from_=50,  # Minimum font size
            to=300,    # Maximum font size
            orient="horizontal",
            variable=self.font_size_var,
            font=self.default_font
        )
        self.font_size_slider.pack(pady=10)

        # Number settings group
        number_settings_frame = ttk.LabelFrame(self.scrollable_frame, text="Number Settings", padding=10)
        number_settings_frame.pack(fill="x", pady=10)

        # Label for Starting Number
        self.starting_number_label = tk.Label(number_settings_frame, text="Enter the Starting Number:", font=self.default_font)
        self.starting_number_label.pack(pady=5)

        # Entry for Starting Number
        validate_starting_number_command = self.root.register(self.validate_starting_number)
        self.starting_number_entry = tk.Entry(number_settings_frame, font=self.default_font, validate="key",
                                              validatecommand=(validate_starting_number_command, '%P'))
        self.starting_number_entry.pack(pady=10)
        self.starting_number_entry.insert(0, "1")  # Default value for starting number

        # Label for number of iterations input
        self.number_label = tk.Label(number_settings_frame, text="Enter the number of iterations (1-99999):",
                                     font=self.default_font)
        self.number_label.pack(pady=5)

        # Entry for user to input a number
        validate_command = self.root.register(self.only_digits)
        self.number_entry = tk.Entry(number_settings_frame, font=self.default_font, validate="key",
                                     validatecommand=(validate_command, '%P'))
        self.number_entry.pack(pady=10)
        self.number_entry.insert(0, "72")  # Default value for number of iterations

        # Label for output file name input
        self.output_filename_label = tk.Label(number_settings_frame, text="Enter the output file name:", font=self.default_font)
        self.output_filename_label.pack(pady=5)

        # Entry for output file name
        output_name_validate_command = self.root.register(self.validate_output_filename)
        self.output_filename_entry = tk.Entry(number_settings_frame, font=self.default_font, validate="key",
                                              validatecommand=(output_name_validate_command, '%P'))
        self.output_filename_entry.pack(pady=10)
        self.output_filename_entry.insert(0, "output_video.mp4")  # Default value for output file name

        # Button to start the task
        self.validate_button = tk.Button(
            number_settings_frame,
            text="Submit Number",
            font=self.default_font,
            command=self.start_task,
            bg="green",  # Set background color to green
            fg="white"   # Set text color to white for better contrast
        )
        self.validate_button.pack(pady=10)

        # Progress-related elements in the progress frame
        self.progress = ttk.Progressbar(self.progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)
        self.progress['value'] = 0
        self.progress["maximum"] = 100  # Max value for progress (set to 100 for percentage)

        # Label to display progress percentage
        self.progress_percentage_label = tk.Label(self.progress_frame, text="0%", font=self.default_font)
        self.progress_percentage_label.pack(pady=5)

        # Label to show elapsed time
        self.time_label = tk.Label(self.progress_frame, text="Elapsed Time: 00:00:00", font=self.default_font)
        self.time_label.pack(pady=10)

        # Setup drag and drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

        self.show_folder_button = tk.Button(
            self.progress_frame,
            text="Show Video Location Folder",
            font=self.default_font,
            command=self.open_output_folder,
            bg="green",  # Set background color to green
            fg="white"   # Set text color to white for better contrast
        )
        self.show_folder_button.pack(pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv")])
        if file_path:
            self.set_selected_file(file_path)

    def set_selected_file(self, file_path):
        self.selected_file = file_path
        self.file_label.config(text=f"Selected: {file_path}")

    def open_output_folder(self):

        full_path = os.path.abspath(self.final_output_path)
        print(full_path)
        print(self.final_output_path)
        if platform.system() == "Windows":
            subprocess.run(['explorer', '/select,', full_path])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', '-R', full_path])
        else:
            print("Unsupported OS")

    def validate_number(self):
        value = self.number_entry.get()
        try:
            num = int(value)
            if 1 <= num <= 99999:
                messagebox.showinfo("Valid Number", f"Accepted number: {num}")
            else:
                messagebox.showerror("Invalid Number", "Number must be between 1 and 99999.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer.")

    def only_digits(self, new_value):
        if new_value == "":
            self.number_entry.config(bg="white")
            return True

        if new_value.isdigit():
            num = int(new_value)
            if 1 <= num <= 99999:
                self.number_entry.config(bg="white")
            else:
                self.number_entry.config(bg="#ffcccc")
            return True
        else:
            return False

    def validate_starting_number(self, new_value):
        # Allow empty input (before the user starts typing)
        if new_value == "":
            return True

        # Check if the value is a whole number
        if new_value.isdigit():
            return True
        else:
            return False

    def validate_output_filename(self, new_value):
        # Check if the new value contains only valid characters (alphanumeric, -, ., and _)
        if new_value == "":
            return True  # Allow empty input (before the user starts typing)

        # Regex for alphanumeric characters, hyphens, periods, and underscores
        pattern = r'^[a-zA-Z0-9.-_]*$'
        if re.match(pattern, new_value):
            return True  # Valid input
        else:
            self.output_filename_entry.config(bg="#ffcccc")  # Highlight invalid input
            return False  # Reject invalid input

    def on_drop(self, event):
        file_path = event.data.strip('{}')
        if file_path:
            self.set_selected_file(file_path)

    def start_task(self):
        """Start the long-running task in a separate thread"""
        # Disable the submit button immediately when the task starts
        self.validate_button.config(state="disabled")

        # Reset progress bar
        self.progress['value'] = 0
        self.progress.pack()  # Make sure it's visible

        # Record the start time
        self.start_time = time.time()

        # Start the task in a background thread to keep the UI responsive
        threading.Thread(target=self.run_task).start()

    def run_task(self):
        """Run the three-step task: Set up, Iterations, Clean up"""
        try:
            # Set up (done once)
            input_file_path = self.selected_file
            file_directory = os.path.dirname(input_file_path)
            current_dir = os.path.dirname(os.path.abspath(__file__))

            self.final_output_path = os.path.join(file_directory, self.output_filename_entry.get())
            temp_folder = os.path.join(current_dir, 'tmp')

            os.makedirs(temp_folder, exist_ok=True)

            initial_clip = VideoFileClip(input_file_path)
            files = [initial_clip]
            stub_files_list = []
            files_cap_limit = 150

            starting_number = int(self.starting_number_entry.get()) if self.starting_number_entry.get() else 1
            version_number = starting_number - 1

            # Get the number from the text box (this is the number of iterations)
            max_iterations = int(self.number_entry.get())

            # Set the maximum value of the progress bar
            self.progress["maximum"] = max_iterations

            # Iterations (done multiple times)
            for i in range(max_iterations):
                version_number += 1
                temp_output_file = os.path.join(temp_folder, f"ex_{i}.mp4")

                # Call the helper function for each iteration
                sped_up_clip_file = video_helpers.double_and_concat(initial_clip, temp_output_file)

                sped_up_clip = VideoFileClip(sped_up_clip_file)
                self.text_color = self.text_color_var.get()

                if self.text_color.lower() == 'random':
                    valid_colors = [c for c in self.color_options if c.lower() != "random"]
                    self.text_color = random.choice(valid_colors)
                clip_with_number = video_helpers.put_text_on_video(
                    sped_up_clip,
                    text_to_write=f"{version_number}",
                    font_size=self.font_size_var.get(),  # Use the selected font size
                    color=self.text_color,
                    font=self.font_var.get()  # Pass the selected font
                )
                if len(files) == files_cap_limit:
                    print(f"Hit files cap limit on loop: {i}")
                    stub_clip = concatenate_videoclips(files)
                    mini_stub_path = os.path.join(temp_folder, f"stub_{i}.mp4")
                    stub_clip.write_videofile(mini_stub_path)
                    stub_clip.close()
                    while files:
                        mini = files.pop()
                        mini.close()

                    read_stub_clip = VideoFileClip(mini_stub_path)
                    stub_files_list.append(read_stub_clip)

                files.append(clip_with_number)

                initial_clip = clip_with_number

                # Update progress bar value
                self.progress['value'] = i + 1

                # Update the elapsed time every second
                self.update_elapsed_time()
                self.update_progress(i, max_iterations)

                # Force UI to update progress bar
                self.root.update_idletasks()

            final_clip = concatenate_videoclips(stub_files_list + files)

            final_clip.write_videofile(self.final_output_path)
            final_clip.close()

            # Task complete, update the progress bar
            self.progress['value'] = max_iterations
            self.validate_button.config(state="normal")
            self.show_folder_button.pack(pady=10)

            # Play the finish sound
            self.play_finish_sound()

            messagebox.showinfo("Task Complete", "Speed video has been created!")

        except ValueError as e:
            messagebox.showerror("Invalid Input", f"{e}")
            tb = traceback.extract_tb(sys.exc_info()[2])
            for filename, lineno, func, text in tb:
                print(f"Error in {filename}, line {lineno}, in {func}")
                print(f"    {text}")

    def update_elapsed_time(self):
        """Update the elapsed time label"""
        elapsed_seconds = int(time.time() - self.start_time)
        hours = elapsed_seconds // 3600
        minutes = (elapsed_seconds % 3600) // 60
        seconds = elapsed_seconds % 60
        self.time_label.config(text=f"Elapsed Time: {hours:02}:{minutes:02}:{seconds:02}")

    def update_progress(self, current_value, max_value):
        # Update progress bar value
        self.progress['value'] = current_value

        # Calculate the percentage and update the label
        percentage = (current_value / max_value) * 100
        self.progress_percentage_label.config(text=f"{int(percentage)}%")

    def run(self):
        self.root.mainloop()
