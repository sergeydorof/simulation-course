import ctypes
import numpy as np
import time
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

lib = ctypes.CDLL('./ImitMod.dll')

lib.calculate.argtypes = [
    ctypes.c_double, # T_left
    ctypes.c_double, # T_right
    ctypes.c_double, # T_start
    ctypes.c_double, # L
    ctypes.c_double, # h
    ctypes.c_double, # tau
    ctypes.c_double, # total_time
    ctypes.POINTER(ctypes.c_double) # result
]

class App:
    def __init__(self, root):
        self.root = root
        self.root.title('Моделирование теплопроводности')

        self.frame_settings = tk.Frame(root, padx=10, pady=10)
        self.frame_settings.pack(side=tk.LEFT, fill=tk.Y)

        self.inputs = {}
        fields = [
            ('L (толщина, м):', '0.1'),
            ('h (шаг x, м):', '0.01'),
            ('tau (шаг t, с):', '0.01'),
            ('Время (с):', '2.0'),
            ('T слева (C):', '-100.0'),
            ('T справа (С):', '100.0'),
            ('T нач (С):', '20.0')
        ]

        for i, (label, default) in enumerate(fields):
            tk.Label(self.frame_settings, text=label).grid(row=i, column=0, sticky='w')
            entry = tk.Entry(self.frame_settings)
            entry.insert(0, default)
            entry.grid(row=i, column=1, pady=2)
            self.inputs[label] = entry

        self.btn_run = tk.Button(self.frame_settings, text='Расчитать',
                                 command=self.calculate, bg='lightblue')
        self.btn_run.grid(row=len(fields), columnspan=2, pady=5, sticky='we')

        self.btn_clear = tk.Button(self.frame_settings, text='Очистить',
                                   command=self.clear, bg='#ffcccb')
        self.btn_clear.grid(row=len(fields) + 1, columnspan=2, pady=5, sticky='we')

        self.lbl_info = tk.Label(self.frame_settings, text='', justify=tk.LEFT,
                                 fg='darkblue')
        self.lbl_info.grid(row=len(fields) + 2, columnspan=2, pady=10)

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('Распределение температуры')
        self.ax.set_xlabel('x (метры)')
        self.ax.set_ylabel('температура (С)')
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def calculate(self):
        try:
            L = float(self.inputs['L (толщина, м):'].get())
            h = float(self.inputs['h (шаг x, м):'].get())
            tau = float(self.inputs['tau (шаг t, с):'].get())
            total_time = float(self.inputs['Время (с):'].get())
            T_l = float(self.inputs['T слева (C):'].get())
            T_r = float(self.inputs['T справа (С):'].get())
            T_start = float(self.inputs['T нач (С):'].get())

            N = int(L / h) + 1
            result = np.zeros(2 * N, dtype=np.float64)

            start_time = time.perf_counter()
            lib.calculate(T_l, T_r, T_start, L, h, tau, total_time,
                          result.ctypes.data_as(ctypes.POINTER(ctypes.c_double)))
            end_time = time.perf_counter()
            sim_time = end_time - start_time

            x = result[0::2]
            temps = result[1::2]
            temp_center = temps[N // 2]

            self.ax.plot(x, temps, label=f'h = {h}\n tau = {tau}')
            self.ax.legend()
            self.canvas.draw()

            self.lbl_info.config(text=(
                f'Последний расчет:\n'
                f'Температура в центре: {temp_center:.4f} C\n'
                f'Время расчета: {sim_time:.6f} сек'
            ))
        except Exception as e:
            messagebox.showerror('Ошибка', f'{e}')

    def clear(self):
        self.ax.clear()
        self.ax.set_title('Распределение температуры')
        self.ax.set_xlabel('x (метры)')
        self.ax.set_ylabel('температура (С)')
        self.ax.grid(True)
        self.canvas.draw()
        self.lbl_info.config(text='График очищен')


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()