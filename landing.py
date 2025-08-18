import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw

class ContinentalQuestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Continental Quest")
        self.root.state("zoomed")  # Fullscreen

        # Load and prepare background as a big sphere
        self.original_bg = Image.open("galaxy.jpg").resize((2200, 2200))  # larger than screen
        self.original_bg = self.make_circle(self.original_bg)
        self.angle = 0
        self.bg_photo = ImageTk.PhotoImage(self.original_bg)

        # Canvas for rotating sphere background
        self.canvas = tk.Canvas(self.root, width=1920, height=1080, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.bg_item = self.canvas.create_image(960, 540, image=self.bg_photo)

        # Title (center aligned)
        self.title = self.canvas.create_text(
            960, 150,
            text="🌍 Continental Quest 🌍",
            font=("Comic Sans MS", 56, "bold"),
            fill="cyan",
            anchor="center"   # ensures text is centered
        )

        # Fancy buttons
        self.start_btn = tk.Button(self.root, text="▶ Start Game", font=("Arial", 24, "bold"),
                                   bg="#1e90ff", fg="white", relief="flat",
                                   activebackground="#63b3ed", activeforeground="white",
                                   command=self.start_game)
        self.points_btn = tk.Button(self.root, text="⭐ View Points", font=("Arial", 24, "bold"),
                                    bg="#38a169", fg="white", relief="flat",
                                    activebackground="#68d391", activeforeground="white",
                                    command=self.view_points)
        self.exit_btn = tk.Button(self.root, text="❌ Exit", font=("Arial", 24, "bold"),
                                  bg="#e53e3e", fg="white", relief="flat",
                                  activebackground="#fc8181", activeforeground="white",
                                  command=self.root.quit)

        # Place buttons on canvas
        self.start_btn_window = self.canvas.create_window(960, 350, window=self.start_btn, width=300, height=70)
        self.points_btn_window = self.canvas.create_window(960, 470, window=self.points_btn, width=300, height=70)
        self.exit_btn_window = self.canvas.create_window(960, 590, window=self.exit_btn, width=300, height=70)

        # Start background animation
        self.rotate_background()

        # Title glow effect
        self.glow_colors = ["cyan", "deepskyblue", "dodgerblue", "aqua"]
        self.color_index = 0
        self.animate_title()

    def make_circle(self, img):
        """Mask the image into a circle (sphere look)"""
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
        result = img.copy()
        result.putalpha(mask)
        return result

    def rotate_background(self):
        """Rotate circular background faster"""
        self.angle += 1.0  # increased speed
        rotated = self.original_bg.rotate(self.angle, resample=Image.BICUBIC)
        self.bg_photo = ImageTk.PhotoImage(rotated)
        self.canvas.itemconfig(self.bg_item, image=self.bg_photo)
        self.root.after(50, self.rotate_background)

    def animate_title(self):
        """Make title glow with changing colors"""
        self.canvas.itemconfig(self.title, fill=self.glow_colors[self.color_index])
        self.color_index = (self.color_index + 1) % len(self.glow_colors)
        self.root.after(500, self.animate_title)

    # ----------- Transition Animation -------------
    def start_game(self):
        """Start game with cinematic zoom + warp effect"""
        self.transition_overlay = tk.Canvas(self.root, width=self.root.winfo_width(),
                                            height=self.root.winfo_height(), bg="black", highlightthickness=0)
        self.transition_overlay.place(x=0, y=0)

        # Load galaxy image for zoom
        self.trans_bg = self.original_bg.resize((2200, 2200))
        self.trans_angle = 0
        self.zoom_scale = 1.0
        self.transition_step()

    def transition_step(self):
        """Animate zoom + warp speed"""
        w, h = self.root.winfo_width(), self.root.winfo_height()
        
        # Zoom in by scaling image
        self.zoom_scale += 0.1
        zoomed = self.trans_bg.resize((int(self.trans_bg.width * self.zoom_scale),
                                       int(self.trans_bg.height * self.zoom_scale)))
        rotated = zoomed.rotate(self.trans_angle, resample=Image.BICUBIC)
        self.trans_photo = ImageTk.PhotoImage(rotated)
        
        # Show zoomed background
        self.transition_overlay.delete("all")  # clear previous frame
        self.transition_overlay.create_image(w//2, h//2, image=self.trans_photo)

        # Light streaks
        for i in range(20):
            x = w//2 + (i-10)*40
            self.transition_overlay.create_line(x, 0, x, h, fill="white", width=2)

        self.trans_angle += 5

        if self.zoom_scale < 3.0:
            self.root.after(50, self.transition_step)
        else:
            # Remove overlay and show globe
            self.transition_overlay.destroy()
            messagebox.showinfo("Globe", "Now the globe appears! (replace with actual globe app here)")

    def view_points(self):
        messagebox.showinfo("Points", "Your current points: 0")


# Run
if __name__ == "__main__":
    root = tk.Tk()
    app = ContinentalQuestApp(root)
    root.mainloop()
