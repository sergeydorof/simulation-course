from dataclasses import dataclass
from distutils.command.check import check

import numpy as np
import random
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import ttk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Симулятор пожара")
        self.grid_map = None
        self.grid_states = None
        self.heatmap = None
        self.cols = ['gray', '#00b6ff', 'orangered', '#00ff64', '#00e156', '#00d04f']
        self.cmap = ListedColormap(self.cols)
        self.labels = {0: 'Сгоревший участок',
          1: 'Река',
          2: 'Огонь',
          3: 'М дерево',
          4: 'Дерево',
          5: 'Б дерево'}
        self.legend_patches = [mpatches.Patch(color=self.cols[i], label=self.labels[i]) for i in self.labels]

        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Label(self.controls_frame, text='Размер сетки (N x N):').pack(side=tk.LEFT)
        self.map_size_var = tk.StringVar(value='30')
        self.map_size_entry = tk.Entry(self.controls_frame, textvariable=self.map_size_var, width=5)
        self.map_size_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(self.controls_frame, text='Вероятность загореться м дерева:').pack(side=tk.LEFT)
        self.s_prob_var = tk.StringVar(value='0.3')
        self.s_prob_entry = tk.Entry(self.controls_frame, textvariable=self.s_prob_var, width=5)
        self.s_prob_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(self.controls_frame, text='Вероятность загореться дерева:').pack(side=tk.LEFT)
        self.prob_var = tk.StringVar(value='0.2')
        self.prob_entry = tk.Entry(self.controls_frame, textvariable=self.prob_var, width=5)
        self.prob_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(self.controls_frame, text='Вероятнгсть загореться б дерева:').pack(side=tk.LEFT)
        self.b_prob_var = tk.StringVar(value='0.1')
        self.b_prob_entry = tk.Entry(self.controls_frame, textvariable=self.b_prob_var, width=5)
        self.b_prob_entry.pack(side=tk.LEFT, padx=5)

        self.wind = ['Нет', 'Лево', 'Верх', 'Право', 'Низ']
        self.current_wind = 'Нет'
        tk.Label(self.controls_frame, text="Ветер:").pack(side=tk.LEFT)
        self.combo = ttk.Combobox(self.controls_frame, values=self.wind, state='readonly')
        self.combo.current(0)
        self.combo.pack(side=tk.LEFT, padx=5)
        self.combo.bind('<<ComboboxSelected>>', self.change_wind)

        self.fig = Figure(figsize=(8, 8), dpi=100, tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.upd_btn = tk.Button(self.controls_frame, text='Генерить карту', command=self.generate_grid_map)
        self.upd_btn.pack(side=tk.LEFT, padx=10)

        self.fire_btn = tk.Button(self.controls_frame, text='ПОДЖЕЧЬ', command=self.start_fire_grid_map)
        self.fire_btn.pack(side=tk.LEFT, padx=10)

    def change_wind(self, event):
        self.current_wind = self.combo.get()

    def start_fire_grid_map(self):
        n = int(self.map_size_var.get())
        ri = random.randint(0, n - 1)
        rj = random.randint(0, n - 1)

        while self.grid_map[ri, rj].current_state == 1:
            ri = random.randint(0, n - 1)
            rj = random.randint(0, n - 1)

        if self.grid_map[ri, rj].current_state == 3:
            self.grid_map[ri, rj].fire_health = 1
        elif self.grid_map[ri, rj].current_state == 4:
            self.grid_map[ri, rj].fire_health = 2
        else:
            self.grid_map[ri, rj].fire_health = 3

        self.grid_map[ri, rj].current_state = 2
        self.grid_states = generate_states(self.grid_map, n)
        self.update_heatmap()

    def update_heatmap(self):
        self.heatmap.collections[0].set_array(self.grid_states.ravel())
        self.canvas.draw_idle()

        if 2 in self.grid_states:
            self.root.after(500, self.fire_tick_map)

    def fire_tick_map(self):
        n = int(self.map_size_var.get())
        s_prob = float(self.s_prob_var.get())
        prob = float(self.prob_var.get())
        b_prob = float(self.b_prob_var.get())
        self.grid_map = fire_tick(self.grid_map, n, s_prob, prob, b_prob, self.current_wind)
        self.grid_states = generate_states(self.grid_map, n)
        self.update_heatmap()

    def generate_grid_map(self):
        n = int(self.map_size_var.get())
        self.grid_map = generate_map(n)
        self.grid_states = generate_states(self.grid_map, n)
        self.draw_heatmap()

    def draw_heatmap(self):
        self.ax.clear()
        self.heatmap = sns.heatmap(self.grid_states, ax=self.ax, cmap=self.cmap, annot=False, cbar=False, vmin=0, vmax=5, square=True,
                    xticklabels=False, yticklabels=False)
        self.ax.legend(handles=self.legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left')
        self.fig.subplots_adjust(right=0.75)
        self.fig.tight_layout()
        self.canvas.draw()


@dataclass
class Cell:
    # 0 - сгорела, 1 - вода, 2 - огонь, 3 - мал дерево, 4 - дерево, 5 - бол дерево
    current_state: int = 0
    new_state: int = 0
    fire_health: int = 0

def generate_map(gsize):
    gmap = np.array([[Cell() for _ in range(gsize)] for _ in range(gsize)], dtype=object)
    i = 0
    j = random.randint(0, gsize-1)
    last_operation = 0 # -1 - лево, 1 - право, 0 - низ
    gmap[i, j].current_state = 1

    while True:
        if last_operation == 0:
            last_operation = random.randint(-1, 1)
            if last_operation == 0:
                i += 1
            try:
                if j + last_operation == -1:
                    raise IndexError
                gmap[i, j + last_operation].current_state = 1
                j += last_operation
            except IndexError:
                last_operation *= -1
                gmap[i, j + last_operation].current_state = 1
                j += last_operation
        else:
            last_operation = random.randint(min(0, last_operation), max(0, last_operation))
            if last_operation == 0:
                i += 1
            try:
                if j + last_operation == -1:
                    raise IndexError
                gmap[i, j + last_operation].current_state = 1
                j += last_operation
            except IndexError:
                last_operation = 0
                i += 1
                gmap[i, j + last_operation].current_state = 1
        if i == gsize - 1:
            break

    for i in range(gsize):
        for j in range(gsize):
            if gmap[i, j].current_state != 1:
                r = random.random()
                if r <= 0.15:
                    gmap[i, j].current_state = 5
                elif 0.15 < r <= 0.45:
                    gmap[i, j].current_state = 4
                elif r > 0.45:
                    gmap[i, j].current_state = 3
    return gmap

def generate_states(gmap, gsize):
    states = np.zeros((gsize, gsize), dtype=int)
    for i in range(gsize):
        for j in range(gsize):
            states[i, j] = gmap[i, j].current_state
    return states

def check_fire(cell):
    if cell.fire_health > 0:
        cell.fire_health -= 1
        cell.new_state = 2
    else:
        cell.new_state = 0
    return cell

def check_forest(gmap, gsize, cell, i, j, s_prob, prob, b_prob, wind):
    f_prob = 0
    f_health = 0
    i_checks = []
    j_checks = []
    boost_horizontal = dict()
    boost_vertical = dict()

    if cell.current_state == 3:
        f_prob = s_prob
        f_health = 0
    elif cell.current_state == 4:
        f_prob = prob
        f_health = 1
    else:
        f_prob = b_prob
        f_health = 2

    if i == 0:
        i_checks = [0, 1, 2]
    elif i == 1:
        i_checks = [-1, 0, 1, 2]
    elif i == gsize-1:
        i_checks = [-2, -1, 0]
    elif i == gsize-2:
        i_checks = [-2, -1, 0, 1]
    else:
        i_checks = [-2, -1, 0, 1, 2]

    if j == 0:
        j_checks = [0, 1, 2]
    elif j == 1:
        j_checks = [-1, 0, 1, 2]
    elif j == gsize-1:
        j_checks = [-2, -1, 0]
    elif j == gsize-2:
        j_checks = [-2, -1, 0, 1]
    else:
        j_checks = [-2, -1, 0, 1, 2]

    if wind == 'Лево':
        i_checks = [item for item in i_checks if item not in [-2, 2]]
        j_checks = [item for item in j_checks if item not in [-2]]
        boost_horizontal = {-1: 0.5, 0: 1, 1: 2, 2: 1}
        boost_vertical = {-1: 0, 0: 0, 1: 0}
    elif wind == 'Право':
        i_checks = [item for item in i_checks if item not in [-2, 2]]
        j_checks = [item for item in j_checks if item not in [2]]
        boost_horizontal = {-2: 1, -1: 2, 0: 1, 1: 0.5}
        boost_vertical = {-1: 0, 0: 0, 1: 0}
    elif wind == 'Верх':
        i_checks = [item for item in i_checks if item not in [-2]]
        j_checks = [item for item in j_checks if item not in [-2, 2]]
        boost_horizontal = {-1: 0, 0: 0, 1: 0}
        boost_vertical = {-1: 0.5, 0: 1, 1: 2, 2: 1}
    elif wind == 'Низ':
        i_checks = [item for item in i_checks if item not in [2]]
        j_checks = [item for item in j_checks if item not in [-2, 2]]
        boost_horizontal = {-1: 0, 0: 0, 1: 0}
        boost_vertical = {-2: 1, -1: 2, 0: 1, 1: 0.5}
    else:
        i_checks = [item for item in i_checks if item not in [-2, 2]]
        j_checks = [item for item in j_checks if item not in [-2, 2]]
        boost_horizontal = {-1: 1, 0: 1, 1: 1}
        boost_vertical = {-1: 0, 0: 0, 1: 0}

    for i_check in i_checks:
        for j_check in j_checks:
            if not (i_check == 0 and j_check == 0):
                if gmap[i + i_check, j + j_check].current_state == 2:
                    if random.random() <= (f_prob * (boost_horizontal[j_check] + boost_vertical[i_check])):
                        cell.new_state = 2
                        cell.fire_health = f_health
                        return cell

    cell.new_state = cell.current_state
    return cell

def fire_tick(gmap, gsize, s_prob, prob, b_prob, wind):
    for i in range(gsize):
        for j in range(gsize):
            if gmap[i, j].current_state == 2:
                gmap[i, j] = check_fire(gmap[i, j])
            elif gmap[i, j].current_state in [3, 4, 5]:
                gmap[i, j] = check_forest(gmap, gsize, gmap[i, j], i, j, s_prob, prob, b_prob, wind)
            else:
                gmap[i, j].new_state = gmap[i, j].current_state

    for i in range(gsize):
        for j in range(gsize):
            gmap[i, j].current_state = gmap[i, j].new_state

    return gmap

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()