# Advanced Professional Version with Requested Features

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import os
import threading

class ImageTextEmbedder:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Image Text Processor")
        self.root.geometry("800x650")

        self.image_files = []
        self.output_folder = ""
        self.processed_images = []  # store previews before saving

        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Button(frame, text="Select Input Folder", command=self.select_input_folder).pack(pady=5)

        ttk.Label(frame, text="Output Folder").pack(anchor="w")
        self.output_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.output_var).pack(fill="x")
        ttk.Button(frame, text="Browse Output", command=self.select_output).pack(pady=5)

        settings = ttk.LabelFrame(frame, text="Text Settings", padding=10)
        settings.pack(fill="x", pady=10)

        ttk.Label(settings, text="Font Size").grid(row=0, column=0)
        self.font_size = tk.IntVar(value=40)
        ttk.Spinbox(settings, from_=10, to=200, textvariable=self.font_size).grid(row=0, column=1)

        ttk.Label(settings, text="Position").grid(row=1, column=0)
        self.position = tk.StringVar(value="bottom-right")
        ttk.Combobox(settings, textvariable=self.position,
                     values=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
                     state="readonly").grid(row=1, column=1)

        ttk.Button(frame, text="Process Images", command=self.start_processing).pack(pady=10)

        self.preview_frame = ttk.Frame(frame)
        self.preview_frame.pack(fill="both", expand=True)

        self.save_btn = ttk.Button(frame, text="Save All Images", command=self.save_all, state="disabled")
        self.save_btn.pack(pady=10)

    def select_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.image_files = [os.path.join(folder, f) for f in os.listdir(folder)
                                if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
            messagebox.showinfo("Loaded", f"{len(self.image_files)} images loaded")

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.output_var.set(folder)

    def get_font(self, size):
        try:
            return ImageFont.truetype("Aptos.ttf", size)
        except:
            return ImageFont.load_default()

    def auto_text_color(self, img, x, y, w, h):
        crop = img.crop((x, y, x+w, y+h)).convert("RGB")
        pixels = list(crop.getdata())
        avg = tuple(sum(c[i] for c in pixels)//len(pixels) for i in range(3))

        brightness = sum(avg)/3
        return (0,0,0,255) if brightness > 127 else (255,255,255,255)

    def calculate_position(self, img_w, img_h, text_w, text_h):
        margin = 20
        pos = self.position.get()

        if pos == "top-left":
            return margin, margin
        if pos == "top-right":
            return img_w - text_w - margin, margin
        if pos == "bottom-left":
            return margin, img_h - text_h - margin
        if pos == "bottom-right":
            return img_w - text_w - margin, img_h - text_h - margin
        return (img_w - text_w)//2, (img_h - text_h)//2

    def process_images(self):
        self.processed_images.clear()

        for path in self.image_files:
            img = Image.open(path).convert("RGBA")
            draw = ImageDraw.Draw(img)

            font = self.get_font(self.font_size.get())

            text = os.path.splitext(os.path.basename(path))[0]

            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]

            x, y = self.calculate_position(img.width, img.height, tw, th)

            color = self.auto_text_color(img, x, y, tw, th)

            draw.rectangle([x-10, y-10, x+tw+10, y+th+10], fill=(0,0,0,120))
            draw.text((x, y), text, fill=color, font=font)

            self.processed_images.append((img.copy(), path))

        self.show_preview()

    def show_preview(self):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        for i, (img, _) in enumerate(self.processed_images[:6]):
            preview = img.resize((150,150))
            tk_img = tk.PhotoImage(preview)
            lbl = ttk.Label(self.preview_frame, image=tk_img)
            lbl.image = tk_img
            lbl.grid(row=i//3, column=i%3, padx=5, pady=5)

        self.save_btn.config(state="normal")

    def save_all(self):
        for img, path in self.processed_images:
            name = os.path.splitext(os.path.basename(path))[0]
            out = os.path.join(self.output_folder, f"{name}.png")
            img.save(out)

        messagebox.showinfo("Saved", "All images saved successfully")

    def start_processing(self):
        if not self.image_files or not self.output_folder:
            messagebox.showerror("Error", "Select input and output folders")
            return

        threading.Thread(target=self.process_images, daemon=True).start()


def main():
    root = tk.Tk()
    app = ImageTextEmbedder(root)
    root.mainloop()


if __name__ == "__main__":
    main()
