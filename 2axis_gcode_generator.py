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
        self.save_folder = ""

        # Элементы интерфейса
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="X0 (X-координата первого отверстия):").grid(row=0, column=0, sticky="w")
        self.x_first_entry = tk.Entry(self.root)
        self.x_first_entry.insert(0, str(self.x_first))
        self.x_first_entry.grid(row=0, column=1)

        tk.Label(self.root, text="dX (Расстояние между отверстиями):").grid(row=1, column=0, sticky="w")
        self.x_spacing_entry = tk.Entry(self.root)
        self.x_spacing_entry.insert(0, str(self.x_spacing))
        self.x_spacing_entry.grid(row=1, column=1)

        tk.Label(self.root, text="Hnum (Количество отверстий):").grid(row=2, column=0, sticky="w")
        self.num_holes_entry = tk.Entry(self.root)
        self.num_holes_entry.insert(0, str(self.num_holes))
        self.num_holes_entry.grid(row=2, column=1)

        tk.Label(self.root, text="Zsafe (Безопасная высота):").grid(row=3, column=0, sticky="w")
        self.safe_height_entry = tk.Entry(self.root)
        self.safe_height_entry.insert(0, str(self.z_safe))
        self.safe_height_entry.grid(row=3, column=1)

        tk.Label(self.root, text="dZ (Глубина сверления):").grid(row=4, column=0, sticky="w")
        self.drill_depth_entry = tk.Entry(self.root)
        self.drill_depth_entry.insert(0, str(self.drill_depth))
        self.drill_depth_entry.grid(row=4, column=1)

        tk.Label(self.root, text="Zmax (Максимальная высота по Z):").grid(row=5, column=0, sticky="w")
        self.z_max_entry = tk.Entry(self.root)
        self.z_max_entry.insert(0, str(self.z_max))
        self.z_max_entry.grid(row=5, column=1)

        tk.Button(self.root, text="Выбрать папку для сохранения", command=self.choose_folder).grid(row=6, column=0, columnspan=2)
        tk.Button(self.root, text="Сгенерировать G-код", command=self.generate_gcode).grid(row=7, column=0, columnspan=2)

        # Поле для редактирования G-кода
        tk.Label(self.root, text="Предпросмотр и редактирование G-кода:").grid(row=8, column=0, columnspan=2, sticky="w")
        self.gcode_text = tk.Text(self.root, height=15, width=60)
        self.gcode_text.grid(row=9, column=0, columnspan=2)

        tk.Button(self.root, text="Сохранить G-код", command=self.save_gcode).grid(row=10, column=0, columnspan=2)

    def choose_folder(self):
        self.save_folder = filedialog.askdirectory()
        if not self.save_folder:
            messagebox.showwarning("Внимание", "Папка не выбрана. Используйте текущую рабочую директорию.")

    def generate_gcode(self):
        try:
            self.x_first = float(self.x_first_entry.get())
            self.x_spacing = float(self.x_spacing_entry.get())
            self.num_holes = int(self.num_holes_entry.get())
            self.z_safe = float(self.safe_height_entry.get())
            self.drill_depth = float(self.drill_depth_entry.get())
            self.z_max = float(self.z_max_entry.get())

            if self.z_safe >= self.z_max:
                messagebox.showerror("Ошибка", "Zsafe должна быть меньше Zmax!")
                return

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
            gcode_lines.append(f"G0 X{x:.2f} Z{self.z_safe:.2f} ; Переместиться к отверстию {i + 1} безопасно")
            gcode_lines.append(f"{self.relay_pin} S1 ; Включить шпиндель")
            gcode_lines.append(f"G1 Z0.00 F100 ; Медленно подойти к поверхности детали")
            gcode_lines.append(f"G1 Z{self.drill_depth:.2f} F50 ; Просверлить отверстие на заданную глубину")
            gcode_lines.append(f"G0 Z{self.z_safe:.2f} ; Подняться на безопасную высоту")
            gcode_lines.append(f"{self.relay_pin} S0 ; Выключить шпиндель")

        gcode_lines.append(f"G0 Z{self.z_max} ; Переместиться на максимальную высоту Z")
        gcode_lines.append(f"G0 X0 ; Вернуться в X0")

        # Отображение G-кода в текстовом виджете
        self.gcode_text.delete("1.0", tk.END)
        self.gcode_text.insert(tk.END, "\n".join(gcode_lines))

    def save_gcode(self):
        gcode = self.gcode_text.get("1.0", tk.END).strip()
        if not gcode:
            messagebox.showerror("Ошибка", "G-код пуст. Сначала сгенерируйте код.")
            return

        # Генерация имени файла
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        gcode_filename = f"{timestamp}.gcode"
        txt_filename = f"{timestamp}.txt"

        if self.save_folder:
            gcode_filepath = f"{self.save_folder}/{gcode_filename}"
            txt_filepath = f"{self.save_folder}/{txt_filename}"
        else:
            gcode_filepath = gcode_filename
            txt_filepath = txt_filename

        # Сохранение файлов
        with open(gcode_filepath, "w") as gcode_file:
            gcode_file.write(gcode)

        with open(txt_filepath, "w") as txt_file:
            txt_file.write(gcode)

        messagebox.showinfo("Успех", f"Файлы сохранены:\n{gcode_filename}\n{txt_filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CNCDrillApp(root)
    root.mainloop()
