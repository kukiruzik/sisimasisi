import tkinter as tk
import random
import math
import time

class ShootingRange:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Тир")
        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="#16213e")
        self.canvas.pack()

        self.score = 0
        self.time_left = 30
        self.game_started = False
        self.timer_id = None
        self.target_created_at = None
        self.target_id = None
        self.target_radius = 30

        self.score_label = tk.Label(self.root, text="Очки: 0", fg="white", bg="#1a1a2e", font=("Arial", 16))
        self.score_label.pack()
        self.timer_label = tk.Label(self.root, text="Цельтесь в мишень, чтобы начать!", fg="#f5c542", bg="#1a1a2e", font=("Arial", 14))
        self.timer_label.pack()

        self.canvas.bind("<Button-1>", self.shoot)
        self.create_target()
        self.root.mainloop()

    def create_target(self):
        x = random.randint(self.target_radius, 600 - self.target_radius)
        y = random.randint(self.target_radius, 400 - self.target_radius)
        self.target_pos = (x, y)
        self.target_created_at = time.time()
        self.draw_target()

    def draw_target(self):
        self.canvas.delete("target")
        x, y = self.target_pos
        r = self.target_radius
        self.target_id = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="red", outline="white", width=2, tags="target")
        self.canvas.create_oval(x-r*0.6, y-r*0.6, x+r*0.6, y+r*0.6, fill="white", outline="", tags="target")
        self.canvas.create_oval(x-r*0.25, y-r*0.25, x+r*0.25, y+r*0.25, fill="red", outline="", tags="target")

    def shoot(self, event):
        if not self.game_started:
            self.game_started = True
            self.timer_label.config(text="Время: 30 сек")
            self.update_timer()

        if not self.target_pos:
            return

        click_x, click_y = event.x, event.y
        tx, ty = self.target_pos
        dist = math.hypot(click_x - tx, click_y - ty)

        if dist <= self.target_radius:
            # Попадание
            time_taken = time.time() - self.target_created_at
            speed_mult = 1.0 + max(0, 1.0 - time_taken)
            speed_mult = min(speed_mult, 2.0)
            accuracy_mult = 1.0 + max(0, 1.0 - dist / self.target_radius)
            points = max(1, round(speed_mult * accuracy_mult))
            self.score += points
            self.score_label.config(text=f"Очки: {self.score}")
            # Анимация попадания (мигание)
            self.canvas.itemconfig(self.target_id, fill="yellow")
            self.root.after(100, lambda: self.canvas.itemconfig(self.target_id, fill="#e94560"))
            self.create_target()
            # Показываем +очки около клика
            self.show_float_text(points, click_x, click_y)
        else:
            # Промах
            self.canvas.itemconfig(self.target_id, outline="red")
            self.root.after(150, lambda: self.canvas.itemconfig(self.target_id, outline="white"))

    def show_float_text(self, points, x, y):
        text_id = self.canvas.create_text(x, y-20, text=f"+{points}", fill="#f5c542", font=("Arial", 18, "bold"), tags="float")
        self.root.after(800, lambda: self.canvas.delete(text_id))

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Время: {self.time_left} сек")
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.end_game()

    def end_game(self):
        self.canvas.delete("target")
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.timer_label.config(text=f"Игра окончена! Ваш счёт: {self.score}")
        self.canvas.unbind("<Button-1>")
        # Можно показать таблицу лидеров (сохранить в файл)

if __name__ == "__main__":
    ShootingRange()