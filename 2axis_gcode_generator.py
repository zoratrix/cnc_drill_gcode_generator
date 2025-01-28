import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

class CNCDrillApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор G-кода для сверлильного станка")

        # Параметры по умолчанию
        self.x_first = 0
        self.x_spacing = 10
        self.num_holes = 5
        self.z_safe = 15
        self.safe_height = 30
        self.drill_depth = -5
        self.z_max = 25
        self.relay_pin = "M3"

        # Элементы интерфейса
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="X-координата первого отверстия:").grid(row=0, column=0, sticky="w")
        self.x_first_entry = tk.Entry(self.root)
        self.x_first_entry.insert(0, str(self.x_first))
        self.x_first_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Расстояние между отверстиями:").grid(row=1, column=0, sticky="w")
        self.x_spacing_entry = tk.Entry(self.root)
        self.x_spacing_entry.insert(0, str(self.x_spacing))
        self.x_spacing_entry.grid(row=1, column=1)

        tk.Label(self.root, text="Количество отверстий:").grid(row=2, column=0, sticky="w")
        self.num_holes_entry = tk.Entry(self.root)
        self.num_holes_entry.insert(0, str(self.num_holes))
        self.num_holes_entry.grid(row=2, column=1)

        tk.Label(self.root, text="Безопасная высота для переходов (Z safe):").grid(row=3, column=0, sticky="w")
        self.safe_height_entry = tk.Entry(self.root)
        self.safe_height_entry.insert(0, str(self.safe_height))
        self.safe_height_entry.grid(row=3, column=1)

        tk.Label(self.root, text="Глубина сверления (отрицательное значение):").grid(row=4, column=0, sticky="w")
        self.drill_depth_entry = tk.Entry(self.root)
        self.drill_depth_entry.insert(0, str(self.drill_depth))
        self.drill_depth_entry.grid(row=4, column=1)

        tk.Label(self.root, text="Максимальная высота по Z:").grid(row=5, column=0, sticky="w")
        self.z_max_entry = tk.Entry(self.root)
        self.z_max_entry.insert(0, str(self.z_max))
        self.z_max_entry.grid(row=5, column=1)

        tk.Button(self.root, text="Сгенерировать G-код", command=self.generate_gcode).grid(row=6, column=0, columnspan=2)

    def generate_gcode(self):
        try:
            self.x_first = float(self.x_first_entry.get())
            self.x_spacing = float(self.x_spacing_entry.get())
            self.num_holes = int(self.num_holes_entry.get())
            self.safe_height = float(self.safe_height_entry.get())
            self.drill_depth = float(self.drill_depth_entry.get())
            self.z_max = float(self.z_max_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Пожалуйста, введите корректные числовые значения.")
            return

        gcode_lines = [
            "G21 ; Установить единицы измерения в миллиметрах",
            "G17 ; Выбрать плоскость XY",
            f"G90 ; Абсолютное позиционирование",
            f"G0 Z{self.z_max} ; Переместиться на максимальную высоту Z",
        ]

        for i in range(self.num_holes):
            x = self.x_first + i * self.x_spacing
            gcode_lines.append(f"G0 X{x:.2f} Z{self.safe_height:.2f} ; Переместиться к отверстию {i + 1} безопасно")
            gcode_lines.append(f"{self.relay_pin} S1 ; Включить шпиндель")
            gcode_lines.append(f"G1 Z0.00 F100 ; Медленно подойти к поверхности детали")
            gcode_lines.append(f"G1 Z{self.drill_depth:.2f} F50 ; Просверлить отверстие на заданную глубину")
            gcode_lines.append(f"G0 Z{self.safe_height:.2f} ; Подняться на безопасную высоту")
            gcode_lines.append(f"{self.relay_pin} S0 ; Выключить шпиндель")

        gcode_lines.append(f"G0 Z{self.z_max} ; Переместиться на максимальную высоту Z")
        gcode_lines.append(f"G0 X0 ; Вернуться в X0")

        # Генерация имени файла на основе текущей даты и времени
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        gcode_filename = f"gcode_{timestamp}.gcode"
        txt_filename = f"gcode_{timestamp}.txt"

        # Сохранение G-кода в файлы
        with open(gcode_filename, "w") as gcode_file:
            gcode_file.write("\n".join(gcode_lines))

        with open(txt_filename, "w") as txt_file:
            txt_file.write("\n".join(gcode_lines))

        messagebox.showinfo("Успех", f"Файлы сохранены:\n{gcode_filename}\n{txt_filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CNCDrillApp(root)
    root.mainloop()
