import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class CNCDrillApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CNC G-code Generator")

        # Параметры реле и координат
        self.relay_pin = tk.StringVar(value="M3")  # Команда для включения реле
        self.x_max = tk.DoubleVar(value=200.0)
        self.x_min = tk.DoubleVar(value=0.0)
        self.z_max = tk.DoubleVar(value=100.0)
        self.z_min = tk.DoubleVar(value=0.0)
        self.z_safe = tk.DoubleVar(value=15.0)  # Высота безопасного запуска
        self.safe_height = tk.DoubleVar(value=30.0)  # Безопасная высота для перемещений между отверстиями

        # Ввод параметров
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Количество отверстий").grid(row=0, column=0)
        self.num_holes = tk.Entry(self.root)
        self.num_holes.grid(row=0, column=1)

        tk.Label(self.root, text="Координата X первого отверстия").grid(row=1, column=0)
        self.x_start = tk.Entry(self.root)
        self.x_start.grid(row=1, column=1)

        tk.Label(self.root, text="Расстояние между отверстиями").grid(row=2, column=0)
        self.hole_spacing = tk.Entry(self.root)
        self.hole_spacing.grid(row=2, column=1)

        tk.Label(self.root, text="Глубина сверления (Za)").grid(row=3, column=0)
        self.z_depth = tk.Entry(self.root)
        self.z_depth.grid(row=3, column=1)

        tk.Label(self.root, text="Xmax").grid(row=4, column=0)
        self.x_max_entry = tk.Entry(self.root, textvariable=self.x_max)
        self.x_max_entry.grid(row=4, column=1)

        tk.Label(self.root, text="Xmin").grid(row=5, column=0)
        self.x_min_entry = tk.Entry(self.root, textvariable=self.x_min)
        self.x_min_entry.grid(row=5, column=1)

        tk.Label(self.root, text="Zmax").grid(row=6, column=0)
        self.z_max_entry = tk.Entry(self.root, textvariable=self.z_max)
        self.z_max_entry.grid(row=6, column=1)

        tk.Label(self.root, text="Zmin").grid(row=7, column=0)
        self.z_min_entry = tk.Entry(self.root, textvariable=self.z_min)
        self.z_min_entry.grid(row=7, column=1)

        tk.Label(self.root, text="Реле для шпинделя").grid(row=8, column=0)
        self.relay_entry = tk.Entry(self.root, textvariable=self.relay_pin)
        self.relay_entry.grid(row=8, column=1)

        tk.Label(self.root, text="Высота безопасного запуска Zsafe").grid(row=9, column=0)
        self.z_safe_entry = tk.Entry(self.root, textvariable=self.z_safe)
        self.z_safe_entry.grid(row=9, column=1)

        tk.Label(self.root, text="Безопасная высота для перемещений (Safe Height)").grid(row=10, column=0)
        self.safe_height_entry = tk.Entry(self.root, textvariable=self.safe_height)
        self.safe_height_entry.grid(row=10, column=1)

        # Предварительный просмотр и генерация G-кода
        self.preview_button = tk.Button(self.root, text="Предпросмотр G-кода", command=self.preview_gcode)
        self.preview_button.grid(row=11, column=0, columnspan=2)

        self.generate_button = tk.Button(self.root, text="Сохранить G-код", command=self.save_gcode)
        self.generate_button.grid(row=12, column=0, columnspan=2)

        # Текстовое поле для предпросмотра
        self.gcode_preview = scrolledtext.ScrolledText(self.root, width=50, height=15)
        self.gcode_preview.grid(row=13, column=0, columnspan=2)

    def generate_gcode(self):
        try:
            # Получаем данные от пользователя
            num_holes = int(self.num_holes.get())
            x_start = float(self.x_start.get())
            hole_spacing = float(self.hole_spacing.get())
            z_depth = float(self.z_depth.get())

            # Генерация G-кода
            gcode = []
            gcode.append(f"G21 ; Устанавливаем мм")
            gcode.append(f"G90 ; Абсолютное программирование")
            gcode.append(f"G0 Z{self.z_max.get()} ; Поднимаем шпиндель в верхнее положение для начала")

            for i in range(num_holes):
                x_pos = x_start + i * hole_spacing
                if x_pos > self.x_max.get() or x_pos < self.x_min.get():
                    messagebox.showerror("Ошибка", "Координата X выходит за пределы!")
                    return
                gcode.append(f"G0 X{x_pos} Z{self.safe_height.get()} ; Перемещаемся к отверстию {i + 1}")
                gcode.append(f"G0 Z{self.z_safe.get()} ; Опускаемся на безопасную высоту перед запуском сверления")
                gcode.append(f"{self.relay_pin.get()} ; Включаем реле для шпинделя")
                gcode.append(f"G4 P0.5 ; Задержка 0.5 секунд для включения шпинделя")
                gcode.append(f"G0 Z0 ; Опускаемся к поверхности детали (Z0)")
                gcode.append(f"G1 Z{-z_depth} F100 ; Опускаемся для сверления на глубину Za")
                gcode.append(f"G4 P1 ; Задержка 1 секунда для завершения сверления")
                gcode.append(f"G0 Z{self.z_safe.get()} ; Поднимаемся на безопасную высоту после сверления")
                gcode.append(f"M5 ; Выключаем реле для шпинделя")
                gcode.append(f"G0 Z{self.safe_height.get()} ; Поднимаемся на безопасную высоту для перемещения")

            gcode.append(f"G0 X0 Z{self.z_max.get()} ; Возвращаемся в начальное положение")
            gcode.append("M30 ; Завершение программы")

            return "\n".join(gcode)

        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные значения!")
            return ""

    def preview_gcode(self):
        # Отображаем G-код в текстовом поле предпросмотра
        gcode = self.generate_gcode()
        if gcode:
            self.gcode_preview.delete(1.0, tk.END)
            self.gcode_preview.insert(tk.END, gcode)

    def save_gcode(self):
        # Сохранение G-кода в файл
        gcode = self.generate_gcode()
        if gcode:
            file_path = filedialog.asksaveasfilename(defaultextension=".gcode", filetypes=[("G-code files", "*.gcode")])
            if file_path:
                with open(file_path, "w") as file:
                    file.write(gcode)
                messagebox.showinfo("Успех", "G-код успешно сохранен!")

if __name__ == "__main__":
    root = tk.Tk()
    app = CNCDrillApp(root)
    root.mainloop()
