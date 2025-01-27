
import tkinter as tk
from tkinter import filedialog, Scrollbar, Canvas, Listbox
from PIL import Image, ImageTk, ImageEnhance, ImageOps, ImageFilter, ImageDraw
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox

class PhotoEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Editor")
        self.root.geometry("1200x800")

        # Set up the canvas and scrollbars
        self.canvas = Canvas(root, bg='grey')
        self.canvas.grid(row=0, column=0, columnspan=10, sticky='nsew')

        self.h_scroll = Scrollbar(root, orient='horizontal', command=self.canvas.xview)
        self.h_scroll.grid(row=1, column=0, columnspan=10, sticky='ew')
        self.v_scroll = Scrollbar(root, orient='vertical', command=self.canvas.yview)
        self.v_scroll.grid(row=0, column=10, sticky='ns')

        self.canvas.config(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        # Buttons row 1
        self.load_btn = tk.Button(root, text="Load Photo", command=self.load_photo)
        self.load_btn.grid(row=2, column=0)
        self.rotate_btn = tk.Button(root, text="Rotate", command=self.rotate_photo)
        self.rotate_btn.grid(row=2, column=1)
        self.crop_btn = tk.Button(root, text="Crop", command=self.crop_photo)
        self.crop_btn.grid(row=2, column=2)
        self.zoom_in_btn = tk.Button(root, text="+", command=self.zoom_in)
        self.zoom_in_btn.grid(row=2, column=3)
        self.zoom_out_btn = tk.Button(root, text="-", command=self.zoom_out)
        self.zoom_out_btn.grid(row=2, column=4)
        self.color_btn = tk.Button(root, text="Color", command=self.color_adjust)
        self.color_btn.grid(row=2, column=5)
        self.effects_btn = tk.Button(root, text="Effects", command=self.effects_adjust)
        self.effects_btn.grid(row=2, column=6)
        self.negative_btn = tk.Button(root, text="Negative", command=self.negative_effect)
        self.negative_btn.grid(row=2, column=7)

        # Buttons row 2
        self.undo_btn = tk.Button(root, text="Undo", command=self.undo)
        self.undo_btn.grid(row=3, column=0)
        self.redo_btn = tk.Button(root, text="Redo", command=self.redo)
        self.redo_btn.grid(row=3, column=1)
        self.reset_btn = tk.Button(root, text="Reset", command=self.reset_photo)
        self.reset_btn.grid(row=3, column=2)
        self.save_btn = tk.Button(root, text="Save", command=self.save_photo)
        self.save_btn.grid(row=3, column=3)
        self.add_text_btn = tk.Button(root, text="Add Text", command=self.add_text)
        self.add_text_btn.grid(row=3, column=4)
        self.add_watermark_btn = tk.Button(root, text="Add Watermark", command=self.add_watermark)
        self.add_watermark_btn.grid(row=3, column=5)
        self.shape_btn = tk.Button(root, text="Shape", command=self.draw_shape)
        self.shape_btn.grid(row=3, column=6)
        self.brush_btn = tk.Button(root, text="Brush", command=self.draw_brush)
        self.brush_btn.grid(row=3, column=7)

        # Buttons row 3
        self.white_balance_btn = tk.Button(root, text="White Balance", command=self.adjust_white_balance)
        self.white_balance_btn.grid(row=4, column=0)
        self.noise_reduction_btn = tk.Button(root, text="Noise Reduction", command=self.reduce_noise)
        self.noise_reduction_btn.grid(row=4, column=1)
        self.batch_btn = tk.Button(root, text="Batch Process", command=self.batch_process)
        self.batch_btn.grid(row=4, column=2)
        self.guides_btn = tk.Button(root, text="Guides & Grids", command=self.toggle_guides)
        self.guides_btn.grid(row=4, column=3)
        self.metadata_btn = tk.Button(root, text="Metadata", command=self.view_metadata)
        self.metadata_btn.grid(row=4, column=4)
        self.layer_mask_btn = tk.Button(root, text="Layer Mask", command=self.add_layer_mask)
        self.layer_mask_btn.grid(row=4, column=5)
        self.clone_btn = tk.Button(root, text="Clone Tool", command=self.clone_tool)
        self.clone_btn.grid(row=4, column=6)
        self.healing_brush_btn = tk.Button(root, text="Healing Brush", command=self.healing_brush)
        self.healing_brush_btn.grid(row=4, column=7)

        # Buttons row 4
        self.perspective_btn = tk.Button(root, text="Perspective Correction", command=self.perspective_correction)
        self.perspective_btn.grid(row=5, column=0)
        self.merge_btn = tk.Button(root, text="Merge Photos", command=self.merge_photos)
        self.merge_btn.grid(row=5, column=1)
        self.geotag_btn = tk.Button(root, text="Geotagging", command=self.add_geotag)
        self.geotag_btn.grid(row=5, column=2)
        self.clip_btn = tk.Button(root, text="Clip", command=self.clip_photo)
        self.clip_btn.grid(row=5, column=3)
        self.opacity_btn = tk.Button(root, text="Opacity", command=self.adjust_opacity)
        self.opacity_btn.grid(row=5, column=4)

        # History Panel
        self.history_panel = Listbox(root)
        self.history_panel.grid(row=0, column=11, rowspan=6, sticky='ns')

        # Initialize additional variables
        self.photo = None
        self.image = None
        self.layers = []
        self.undo_stack = []
        self.redo_stack = []
        self.show_guides = False

        # Bind shortcuts
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())

    def add_to_history(self, action):
        self.history_panel.insert(tk.END, action)
        self.history_panel.yview(tk.END)

    def load_photo(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)

    def display_image(self, image):
        self.canvas.delete("all")

        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.photo, anchor='nw')
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.add_to_history("Displayed image")

        if self.show_guides:
            self.redraw_guides_and_grids()

    def rotate_photo(self):
        if self.image:
            self.image = self.image.rotate(90, expand=True)
            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)
            self.add_to_history("Rotated photo")

    def zoom_in(self):
        if self.image:
            self.image = self.image.resize((int(self.image.width * 1.2), int(self.image.height * 1.2)))
            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)
            self.add_to_history("Zoomed in")

    def zoom_out(self):
        if self.image:
            self.image = self.image.resize((int(self.image.width * 0.8), int(self.image.height * 0.8)))
            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)
            self.add_to_history("Zoomed out")

    def crop_photo(self):
        if self.image:
            self.canvas.bind("<Button-1>", self.start_crop)
            self.canvas.bind("<B1-Motion>", self.perform_crop)
            self.canvas.bind("<ButtonRelease-1>", self.end_crop)

    def start_crop(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y

    def perform_crop(self, event):
        self.crop_end_x = event.x
        self.crop_end_y = event.y

        self.display_image(self.image)
        self.canvas.create_rectangle(self.crop_start_x, self.crop_start_y, self.crop_end_x, self.crop_end_y, outline="red")

    def end_crop(self, event):
        if self.image:
            left = min(self.crop_start_x, self.crop_end_x)
            top = min(self.crop_start_y, self.crop_end_y)
            right = max(self.crop_start_x, self.crop_end_x)
            bottom = max(self.crop_start_y, self.crop_end_y)
            self.image = self.image.crop((left, top, right, bottom))
            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            self.add_to_history("Cropped photo")

    def save_photo(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            image_to_save = self.image.convert("RGB")
            image_to_save.save(file_path)
            self.add_to_history("Saved photo")

    def color_adjust(self):
        if self.image:
            top = tk.Toplevel(self.root)
            top.title("Color Adjustment")

            self.red_scale = tk.Scale(top, from_=-100, to=100, orient='horizontal', label="Red")
            self.red_scale.pack()

            self.green_scale = tk.Scale(top, from_=-100, to=100, orient='horizontal', label="Green")
            self.green_scale.pack()

            self.blue_scale = tk.Scale(top, from_=-100, to=100, orient='horizontal', label="Blue")
            self.blue_scale.pack()

            apply_btn = tk.Button(top, text="Apply", command=self.apply_color_adjust)
            apply_btn.pack()

    def apply_color_adjust(self):
        red = self.red_scale.get()
        green = self.green_scale.get()
        blue = self.blue_scale.get()

        # + Adjust color vibrancy
        r, g, b = self.image.split()
        r = r.point(lambda p: p * (1 + red / 100.0))
        g = g.point(lambda p: p * (1 + green / 100.0))
        b = b.point(lambda p: p * (1 + blue / 100.0))
        self.image = Image.merge("RGB", (r, g, b))

        self.undo_stack.append(self.image.copy())
        self.display_image(self.image)
        self.add_to_history("Adjusted colors")


    def effects_adjust(self):
        if self.image:
            top = tk.Toplevel(self.root)
            top.title("Effects Adjustment")

            self.brightness_scale = tk.Scale(top, from_=-100, to=100, orient='horizontal', label="Brightness")
            self.brightness_scale.pack()

            self.contrast_scale = tk.Scale(top, from_=-100, to=100, orient='horizontal', label="Contrast")
            self.contrast_scale.pack()

            apply_btn = tk.Button(top, text="Apply", command=self.apply_effects_adjust)
            apply_btn.pack()

    def apply_effects_adjust(self):
        brightness = self.brightness_scale.get()
        contrast = self.contrast_scale.get()

        # Apply effects adjustment logic
        enhancer = ImageEnhance.Brightness(self.image)
        self.image = enhancer.enhance(1 + brightness / 100.0)
        enhancer = ImageEnhance.Contrast(self.image)
        self.image = enhancer.enhance(1 + contrast / 100.0)
        self.undo_stack.append(self.image.copy())
        self.display_image(self.image)
        self.add_to_history("Adjusted effects")

    def negative_effect(self):
        if self.image:
            image_to_invert = self.image.convert("RGB")
            self.image = ImageOps.invert(image_to_invert)
            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)
            self.add_to_history("Applied negative effect")

    def undo(self):
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            self.image = self.undo_stack[-1].copy()
            self.display_image(self.image)
            self.add_to_history("Undid action")

    def redo(self):
        if self.redo_stack:
            self.image = self.redo_stack.pop()
            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)
            self.add_to_history("Redid action")

    def reset_photo(self):
        if self.undo_stack:
            self.image = self.undo_stack[0].copy()
            self.undo_stack = [self.image.copy()]
            self.redo_stack.clear()
            self.display_image(self.image)
            self.add_to_history("Reset photo")

    def add_text(self):
        if self.image:
            text = simpledialog.askstring("Input", "Enter text:")
            if text:
                self.text_to_add = text
                self.canvas.bind("<Button-1>", self.start_text_box)
                self.canvas.bind("<B1-Motion>", self.perform_text_box)
                self.canvas.bind("<ButtonRelease-1>", self.end_text_box)

    def start_text_box(self, event):
        self.text_start_x = event.x
        self.text_start_y = event.y

    def perform_text_box(self, event):
        self.text_end_x = event.x
        self.text_end_y = event.y

        self.display_image(self.image)
        self.canvas.create_rectangle(self.text_start_x, self.text_start_y, self.text_end_x, self.text_end_y, outline="red")

    def end_text_box(self, event):
        if self.image:
            left = min(self.text_start_x, self.text_end_x)
            top = min(self.text_start_y, self.text_end_y)
            right = max(self.text_start_x, self.text_end_x)
            bottom = max(self.text_start_y, self.text_end_y)

            draw = ImageDraw.Draw(self.image)
            text_position = ((left + right) // 2, (top + bottom) // 2)
            draw.text(text_position, self.text_to_add, fill="white")
            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)

            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            self.add_to_history("Added text/watermark")

    def add_watermark(self):
        if self.image:
            watermark = simpledialog.askstring("Input", "Enter watermark:")
            if watermark:
                width, height = self.image.size
                draw = ImageDraw.Draw(self.image)
                text_bbox = draw.textbbox((0, 0), watermark)  # + Corrected to use textbbox
                text_position = (width - text_bbox[2], height - text_bbox[3])  # + Adjusted positioning
                draw.text(text_position, watermark, fill=(255, 255, 255, 128))  # + Added watermark with transparency
                self.undo_stack.append(self.image.copy())
                self.display_image(self.image)
                self.add_to_history("Added watermark")

    def update_canvas(self):
        self.display_image(self.image)
        for layer_type, layer_data in self.layers:
            if layer_type == "text":
                self.canvas.create_text(100, 100, text=layer_data, fill="white", font=("Helvetica", 20))
            elif layer_type == "watermark":
                self.canvas.create_text(300, 300, text=layer_data, fill="grey", font=("Helvetica", 15), anchor='se')

    def draw_shape(self):
        if self.image:
            shape_type = simpledialog.askstring("Input", "Enter shape (rectangle, oval):")  # + Open a menu for shape selection
            if shape_type:
                self.shape_type = shape_type
                self.canvas.bind("<Button-1>", self.add_shape)

    def add_shape(self, event):
        if self.shape_type == "rectangle":
            self.canvas.create_rectangle(event.x, event.y, event.x+50, event.y+50, outline="white", width=3)
        elif self.shape_type == "oval":
            self.canvas.create_oval(event.x, event.y, event.x+50, event.y+50, outline="white", width=3)
        self.add_to_history(f"Added {self.shape_type}")
        self.canvas.unbind("<Button-1>")

    def draw_brush(self):
        if self.image:
            self.canvas.bind("<B1-Motion>", self.paint)
            self.add_to_history("Used brush tool")

    def paint(self, event):
        x, y = event.x, event.y
        self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="black", outline="black")

    def adjust_white_balance(self):
        if self.image:
            enhancer = ImageEnhance.Color(self.image)
            self.image = enhancer.enhance(1.5)  # Adjust this value as needed
            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)
            self.add_to_history("Adjusted white balance")

    def reduce_noise(self):
        if self.image:
            self.image = self.image.filter(ImageFilter.SMOOTH_MORE)
            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)
            self.add_to_history("Reduced noise")

    def batch_process(self):
        file_paths = filedialog.askopenfilenames()
        for file_path in file_paths:
            img = Image.open(file_path)
            # Apply a specific set of edits to each image
            img = img.rotate(90, expand=True)
            img.save(file_path.replace(".", "_edited."))
        messagebox.showinfo("Batch Process", "Batch processing completed.")
        self.add_to_history("Batch processed photos")

    def toggle_guides(self):
        self.show_guides = not self.show_guides
        self.redraw_guides_and_grids()

    def redraw_guides_and_grids(self):
        self.canvas.delete('grid_line')
        if self.show_guides:
            for i in range(0, self.image.width, 100):
                self.canvas.create_line([(i, 0), (i, self.image.height)], fill='red', tags='grid_line', width=1)
            for i in range(0, self.image.height, 100):
                self.canvas.create_line([(0, i), (self.image.width, i)], fill='red', tags='grid_line', width=1)

    def view_metadata(self):
        if self.image:
            metadata = self.image.getexif()  # + Corrected 'getexif'
            metadata_text = "\n".join([f"{k}: {v}" for k, v in metadata.items()]) if metadata else "No metadata found"
            top = tk.Toplevel(self.root)
            top.title("Metadata Viewer")
            text_box = tk.Text(top)
            text_box.insert(tk.END, metadata_text)
            text_box.pack()
            self.add_to_history("Viewed metadata")

    def add_layer_mask(self):
        if self.image:
            self.layers.append(("mask", self.image.copy()))
            self.update_canvas()
            self.add_to_history("Added layer mask")

    def clone_tool(self):
        if self.image:
            self.canvas.bind("<B1-Motion>", self.clone_paint)
            self.add_to_history("Used clone tool")

    def clone_paint(self, event):
        x, y = event.x, event.y
        self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="white", outline="white")

    def healing_brush(self):
        if self.image:
            self.canvas.bind("<B1-Motion>", self.heal_paint)
            self.add_to_history("Used healing brush tool")

    def heal_paint(self, event):
        x, y = event.x, event.y
        self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="grey", outline="grey")

    def perspective_correction(self):
        if self.image:
            # Apply perspective correction logic
            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)
            self.add_to_history("Corrected perspective")

    def merge_photos(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:  # + Added check for empty file_paths
            images = [Image.open(fp) for fp in file_paths]
            widths, heights = zip(*(img.size for img in images))
            total_width, max_height = sum(widths), max(heights)
            merged_image = Image.new('RGB', (total_width, max_height))
            x_offset = 0
            for img in images:
                merged_image.paste(img, (x_offset, 0))
                x_offset += img.width
            self.image = merged_image
            self.display_image(self.image)
            self.add_to_history("Merged photos")

    def add_geotag(self):
        if self.image:
            top = tk.Toplevel(self.root)
            top.title("Geotagging")

            self.zip_code = tk.StringVar()

            zip_label = tk.Label(top, text="Enter ZIP Code:")
            zip_label.pack()
            zip_entry = tk.Entry(top, textvariable=self.zip_code)
            zip_entry.pack()

            apply_btn = tk.Button(top, text="Apply", command=self.apply_geotag)
            apply_btn.pack()

    def apply_geotag(self):
        zip_code = self.zip_code.get()
        if zip_code:
            # Add geotag to metadata (for demonstration purposes, we'll just add text overlay)
            width, height = self.image.size
            draw = ImageDraw.Draw(self.image)
            text_position = (10, height - 20)
            draw.text(text_position, f"ZIP Code: {zip_code}", fill="white")

            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)
            self.add_to_history("Added geotag")

    def clip_photo(self):
        if self.image:
            self.clipping = True
            self.points = []
            self.canvas.bind("<Button-1>", self.add_clip_point)
            self.add_to_history("Started clipping")

    def add_clip_point(self, event):
        if self.clipping:
            self.points.append((event.x, event.y))
            self.canvas.create_oval(event.x-2, event.y-2, event.x+2, event.y+2, fill="red")
            if len(self.points) > 2 and self.distance(self.points[0], self.points[-1]) < 10:  # + When points form a closed shape
                self.apply_clip()

    def apply_clip(self):
        if self.image:
            self.clipping = False
            self.canvas.unbind("<Button-1>")
            mask = Image.new('L', self.image.size, 0)
            ImageDraw.Draw(mask).polygon(self.points, outline=1, fill=1)
            mask = mask.filter(ImageFilter.GaussianBlur(3))
            self.image = Image.composite(self.image, Image.new('RGB', self.image.size), mask)
            self.undo_stack.append(self.image.copy())
            self.display_image(self.image)
            self.add_to_history("Applied clipping")

    def distance(self, point1, point2):
        return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5  # + Utility function to measure distance

    def adjust_opacity(self):
        if self.image:
            top = tk.Toplevel(self.root)
            top.title("Opacity Adjustment")

            self.opacity_scale = tk.Scale(top, from_=0, to=100, orient='horizontal', label="Opacity")
            self.opacity_scale.pack()

            apply_btn = tk.Button(top, text="Apply", command=self.apply_opacity_adjust)
            apply_btn.pack()

    def apply_opacity_adjust(self):
        opacity = self.opacity_scale.get() / 100.0  # + Changed to a fraction
        self.image = self.image.convert("RGBA")
        alpha = self.image.split()[3]
        alpha = alpha.point(lambda p: p * opacity)
        self.image.putalpha(alpha)
        self.undo_stack.append(self.image.copy())
        self.display_image(self.image)
        self.add_to_history("Adjusted opacity")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoEditor(root)
    root.mainloop()
