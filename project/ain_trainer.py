import tkinter as tk
from tkinter import messagebox
import random

# Декоратор для логирования вызовов методов
def log_call(func):
    # Логирует имя вызываемого метода
    def wrapper(*args, **kwargs):
        print(f"Вызван метод: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# Декоратор, проверяющий, активна ли игра
def game_active_required(func):
    # Перед выполнением метода проверяет активна ли игра
    def wrapper(self, *args, **kwargs):
        if not self.game_active:
            print("Игра не активна, действие проигнорировано")
            return
        return func(self, *args, **kwargs)
    return wrapper

# Рекурсивная функция для бонуса комбо
def combo_bonus(combo):
    if combo <= 1:
        return 0
    return (combo - 1) + combo_bonus(combo - 1)

# Базовый класс для игр (содержит общее поле title)
class Game:
    def __init__(self, title):
        self.title = title

# Основной класс Aim Trainer
class AimTrainer(Game):
    def __init__(self):
        # Вызов конструктора базового класса
        super().__init__("Aim Trainer")
        
        # Создание главного окна приложения
        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.geometry("800x600")
        
        # Словарь конфигурации игры
        self.config = {
            "canvas_width": 800, # ширина поля в пикселях
            "canvas_height": 500, # высота поля в пикселях
            "initial_time": 30, # начальное время игры
            "initial_target_size": 40, # начальный диаметр мишени
            "min_target_size": 20, # минимальный диаметр мишени
            "bg_color": "white", # цвет фона холста
            "target_color": "red" # цвет мишени
        }
        
        # Атрибуты состояния игры
        self.score = 0 # текущий счёт
        self.combo = 0 # текущее комбо
        self.time_left = self.config["initial_time"] # оставшееся время
        self.game_active = False # игра активна или нет
        self.target_id = None # идентификатор мишени
        self.target_size = self.config["initial_target_size"] # текущий размер мишени
        
        # Загрузка рекорда из файла
        self.high_score = self.load_high_score()
        
        # Построение графического интерфейса
        self.create_widgets()
        
        # Запуск главного цикла обработки событий tkinter
        self.root.mainloop()
    
    def load_high_score(self):
        # Загружает рекорд из файла highscore.txt. При ошибках возвращает 0.
        high_score_file = "highscore.txt"
        try:
            with open(high_score_file, "r") as f:
                return int(f.read().strip())
        except FileNotFoundError:
            # Файл отсутствует – рекорд равен 0
            return 0
        except ValueError:
            # Файл содержит не число – рекорд равен 0
            return 0
    
    def save_high_score(self):
        # Сохраняет текущий рекорд в файл highscore.txt
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except IOError as e:
            print(f"Ошибка при сохранении рекорда: {e}")
    
    def create_widgets(self):
        # Создаёт все элементы интерфейса
        # Верхняя панель с информацией
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10)
        
        # Метка для отображения счёта
        self.score_label = tk.Label(info_frame, text=f"Счёт: {self.score}", font=("Arial", 16))
        self.score_label.pack(side="left", padx=20)
        
        # Метка для отображения оставшегося времени
        self.time_label = tk.Label(info_frame, text=f"Время: {self.time_left}", font=("Arial", 16))
        self.time_label.pack(side="left", padx=20)
        
        # Метка для отображения рекорда
        self.high_label = tk.Label(info_frame, text=f"Рекорд: {self.high_score}", font=("Arial", 12))
        self.high_label.pack(side="left", padx=20)
        
        # Кнопка запуска игры
        self.start_btn = tk.Button(info_frame, text="Start Game", font=("Arial", 12))
        self.start_btn.config(command=lambda: self.start_game())
        self.start_btn.pack(side="left", padx=20)
        
        # Поле для мишени
        self.canvas = tk.Canvas(self.root,
                                width=self.config["canvas_width"],
                                height=self.config["canvas_height"],
                                bg=self.config["bg_color"])
        self.canvas.pack(pady=10)
        
        # Привязка события нажатия левой кнопки мыши к обработчику
        self.canvas.bind("<Button-1>", self.check_hit)
        
        # Заставка
        self.message_id = self.canvas.create_text(
            self.config["canvas_width"] // 2,
            self.config["canvas_height"] // 2,
            text="Нажмите Start Game",
            font=("Arial", 24),
            fill="gray"
        )
    
    @log_call
    def start_game(self):
        # Запускает новую игру: сбрасывает счёт, время, размер мишени и активирует игру
        self.game_active = True
        self.score = 0
        self.time_left = self.config["initial_time"]
        self.target_size = self.config["initial_target_size"]
        self.update_score_display()
        self.update_time_display()
        
        # Удаляет текст-заставку
        self.canvas.delete(self.message_id)
        # Удаляет старую мишень, если она существует
        if self.target_id:
            self.canvas.delete(self.target_id)
        # Создаёт первую мишень
        self.create_target()
        # Запускает таймер
        self.update_timer()
    
    def update_score_display(self):
        # Обновляет счёт
        self.score_label.config(text=f"Счёт: {self.score}")
    
    def update_time_display(self):
        # Обновляет время
        self.time_label.config(text=f"Время: {self.time_left}")
    
    def create_target(self):
        # Создаёт новую мишень в случайной позиции
        # Вычисляет допустимые границы, чтобы мишень помистилась
        max_x = self.config["canvas_width"] - self.target_size // 2
        min_x = self.target_size // 2
        max_y = self.config["canvas_height"] - self.target_size // 2
        min_y = self.target_size // 2
        x = random.randint(min_x, max_x)  # случайная X-координата центра
        y = random.randint(min_y, max_y)  # случайная Y-координата центра
        
        # Координаты углов хитбокса
        x1 = x - self.target_size // 2
        y1 = y - self.target_size // 2
        x2 = x + self.target_size // 2
        y2 = y + self.target_size // 2
        
        # Рисует мишень
        self.target_id = self.canvas.create_oval(x1, y1, x2, y2,
                                                 fill=self.config["target_color"],
                                                 outline="black")
    
    # Обработчик события нажатия кнопки мыши
    def check_hit(self, event):
        # Проверяет, активна ли игра, и существует ли мишень
        if not self.game_active:
            return
        if not self.target_id:
            return
        
        # Получает хитбокс
        bbox = self.canvas.bbox(self.target_id)
        if bbox:
            x1, y1, x2, y2 = bbox
            # Проверяет, попал ли клик внутрь хитбокса
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                # Попадание: увеличивает счёт и обновляет метку
                self.score += 1
                self.update_score_display()
                
                # Уменьшает размер мишени
                if self.target_size > self.config["min_target_size"]:
                    self.target_size -= 2
                 
                # Перемещает мишень в новое место
                self.canvas.delete(self.target_id)
                self.create_target()

        # Увеличивает комбо с каждым попаданием
        self.combo += 1
        bonus = combo_bonus(self.combo)
        self.score += 1 + bonus
        self.update_score_display()

    
    def update_timer(self):
        # Управляет обратным отсчётом времени
        if not self.game_active:
            return
        if self.time_left > 0:
            self.time_left -= 1
            self.update_time_display()
            # Запланировать следующий вызов через 1 секунду
            self.root.after(1000, self.update_timer)
        else:
            self.end_game()
    
    def end_game(self):
        # Завершает игру, отображает результат и обновляет рекорд
        self.game_active = False
        if self.target_id:
            self.canvas.delete(self.target_id)
            self.target_id = None
        
        # Проверяет, установлен ли новый рекорд
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            self.high_label.config(text=f"Рекорд: {self.high_score}")
            messagebox.showinfo("Новый рекорд!", f"Вы установили рекорд – {self.score} очков!")
        else:
            messagebox.showinfo("Игра окончена", f"Ваш счёт: {self.score}")
        
        # Показывает заставку с результатом игры
        self.message_id = self.canvas.create_text(
            self.config["canvas_width"] // 2,
            self.config["canvas_height"] // 2,
            text=f"Игра окончена! Счёт: {self.score}\nНажмите Start Game",
            font=("Arial", 18),
            fill="gray"
        )

# Запуск игры
if __name__ == "__main__":
    game = AimTrainer()