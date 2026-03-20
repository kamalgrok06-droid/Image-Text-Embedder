import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
import threading

class ImageTextEmbedder:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Text Embedder - Batch Processor")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.image_files = []
        self.output_folder = ""
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File selection
        ttk.Label(main_frame, text="Select Images:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Button(main_frame, text="Add Images", command=self.add_images).grid(row=0, column=1, padx=5)
        ttk.Button(main_frame, text="Clear List", command=self.clear_images).grid(row=0, column=2, padx=5)
        
        self.file_listbox = tk.Listbox(main_frame, height=6)
        self.file_listbox.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=1, column=3, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Output folder
        ttk.Label(main_frame, text="Output Folder:").grid(row=2, column=0, sticky=tk.W, pady=(20,5))
        self.output_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_var, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.select_output_folder).grid(row=2, column=2)
        
        # Text settings frame
        text_frame = ttk.LabelFrame(main_frame, text="Text Overlay Settings", padding="10")
        text_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Text content
        ttk.Label(text_frame, text="Text to Embed:").grid(row=0, column=0, sticky=tk.W)
        self.text_var = tk.StringVar(value="Your Text Here")
        ttk.Entry(text_frame, textvariable=self.text_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        
        # Font size
        ttk.Label(text_frame, text="Font Size:").grid(row=1, column=0, sticky=tk.W)
        self.font_size_var = tk.IntVar(value=48)
        font_size_spin = ttk.Spinbox(text_frame, from_=12, to=200, textvariable=self.font_size_var, width=10)
        font_size_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Text color
        ttk.Label(text_frame, text="Text Color:").grid(row=2, column=0, sticky=tk.W)
        self.color_var = tk.StringVar(value="#FFFFFF")
        ttk.Entry(text_frame, textvariable=self.color_var, width=12).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(text_frame, text="Color Picker", command=self.color_picker).grid(row=2, column=2, padx=5)
        
        # Position
        ttk.Label(text_frame, text="Position:").grid(row=3, column=0, sticky=tk.W)
        self.position_var = tk.StringVar(value="bottom")
        position_combo = ttk.Combobox(text_frame, textvariable=self.position_var, 
                                    values=["top-left", "top-right", "bottom-left", "bottom-right", "center"], 
                                    state="readonly", width=12)
        position_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Background
        self.bg_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(text_frame, text="Add Background Box", variable=self.bg_var).grid(row=4, column=0, columnspan=2, sticky=tk.W)
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="Process All Images", command=self.start_processing)
        self.process_btn.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=6, column=0, columnspan=3)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def add_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp")]
        )
        for file in files:
            if file not in self.image_files:
                self.image_files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
    
    def clear_images(self):
        self.image_files.clear()
        self.file_listbox.delete(0, tk.END)
    
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_var.set(folder)
            self.output_folder = folder
    
    def color_picker(self):
        color_window = tk.Toplevel(self.root)
        color_window.title("Pick Color")
        color_window.geometry("300x300")
        
        canvas = tk.Canvas(color_window, width=280, height=200, bg="white")
        canvas.pack(pady=10)
        
        def update_color(event):
            x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
            color_hex = "#{:02x}{:02x}{:02x}".format(int(x/1.4), int(y/1.4), 255-int(y/1.4))
            self.color_var.set(color_hex)
            canvas.config(bg=color_hex)
        
        canvas.bind("<Button-1>", update_color)
    
    def get_position_xy(self, img_width, img_height, position):
        positions = {
            "top-left": (20, 20),
            "top-right": (img_width - 200, 20),
            "bottom-left": (20, img_height - 80),
            "bottom-right": (img_width - 200, img_height - 80),
            "center": (img_width // 2 - 100, img_height // 2 - 40)
        }
        return positions.get(position, (20, img_height - 80))
    
    def process_images(self):
        if not self.image_files or not self.output_folder:
            messagebox.showerror("Error", "Please select images and output folder!")
            return
        
        try:
            total = len(self.image_files)
            self.progress['maximum'] = total
            self.progress['value'] = 0
            
            for i, img_path in enumerate(self.image_files):
                self.status_label.config(text=f"Processing: {os.path.basename(img_path)} ({i+1}/{total})")
                self.root.update()
                
                # Open image
                with Image.open(img_path) as img:
                    # Convert to RGBA if not already
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    draw = ImageDraw.Draw(img)
                    
                    try:
                        # Try to use custom font, fallback to default
                        font = ImageFont.truetype("arial.ttf", self.font_size_var.get())
                    except:
                        font = ImageFont.load_default()
                    
                    # Text settings
                    text = self.text_var.get()
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    # Get position
                    img_width, img_height = img.size
                    x, y = self.get_position_xy(img_width, img_height, self.position_var.get())
                    
                    # Center text if needed
                    if self.position_var.get() == "center":
                        x -= text_width // 2
                        y -= text_height // 2
                    
                    # Draw background if enabled
                    if self.bg_var.get():
                        bg_padding = 10
                        draw.rectangle(
                            [x - bg_padding, y - bg_padding, 
                             x + text_width + bg_padding, y + text_height + bg_padding],
                            fill=(0, 0, 0, 128)
                        )
                    
                    # Draw text
                    color = tuple(int(self.color_var.get()[i:i+2], 16) for i in (1, 3, 5)) + (255,)
                    draw.text((x, y), text, font=font, fill=color)
                
                # Save processed image
                filename = os.path.splitext(os.path.basename(img_path))[0] + "_text.png"
                output_path = os.path.join(self.output_folder, filename)
                img.save(output_path, "PNG")
                
                self.progress['value'] = i + 1
                self.root.update()
            
            self.status_label.config(text=f"Completed! Processed {total} images.")
            messagebox.showinfo("Success", f"Successfully processed {total} images!\nOutput: {self.output_folder}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
        finally:
            self.process_btn.config(state='normal')
    
    def start_processing(self):
        if not self.image_files or not self.output_folder:
            messagebox.showerror("Error", "Please select images and output folder!")
            return
        
        self.process_btn.config(state='disabled')
        thread = threading.Thread(target=self.process_images)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = ImageTextEmbedder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
