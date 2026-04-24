import seaborn as sns
import matplotlib.pyplot as plt
import random
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy.stats import chi2, chisquare, norm
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
from math import sqrt

def get_sample(n, mean, var):
    result = []
    for _ in range(n // 2):
        a1, a2 = random.random(), random.random()
        z0 = sqrt(-2 * math.log(a1)) * math.cos(2 * math.pi * a2)
        z1 = sqrt(-2 * math.log(a1)) * math.sin(2 * math.pi * a2)
        result.append(sqrt(var) * z0 + mean)
        result.append(sqrt(var) * z1 + mean)
    return result

class ContinRVApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Continuous Random Value')
        self.root.geometry('1000x700')

        self.build_ui()
        self.build_plot()

    def build_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.LabelFrame(main_frame, text='Params', padding=10)
        input_frame.pack(fill=tk.BOTH, pady=(0, 10))

        ttk.Label(input_frame, text='Sample size:').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.n_entry = ttk.Entry(input_frame, width=20)
        self.n_entry.grid(row=0, column=1, sticky='we', padx=5, pady=5)
        self.n_entry.insert(0, '100')

        ttk.Label(input_frame, text='Mean:').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.mean_entry = ttk.Entry(input_frame, width=50)
        self.mean_entry.grid(row=1, column=1, sticky='we', padx=5, pady=5)
        self.mean_entry.insert(0, '0')

        ttk.Label(input_frame, text='Var:').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.var_entry = ttk.Entry(input_frame, width=50)
        self.var_entry.grid(row=2, column=1, sticky='we', padx=5, pady=5)
        self.var_entry.insert(0, '1')

        generate_button = ttk.Button(input_frame, text='Generate', command=self.generate_sample)
        generate_button.grid(row=3, column=0, columnspan=2, pady=10)

        info_label = ttk.Label(
            input_frame,
            text='...',
            foreground='gray'
        )

        info_label.grid(row=4, column=0, columnspan=2, sticky='w', padx=5)

        input_frame.columnconfigure(1, weight=1)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        result_frame = ttk.LabelFrame(content_frame, text='Results', padding=10)
        result_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.result_text = tk.Text(result_frame, width=45, height=30, wrap='word', font=('Consolas', 11))
        self.result_text.pack(fill=tk.BOTH, expand=True)

        plot_frame = ttk.LabelFrame(content_frame, text='Hist', padding=10)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.plot_container = plot_frame

    def build_plot(self):
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Hist')
        self.ax.set_xlabel('Value')
        self.ax.set_ylabel('relative freq')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()

    def prepare_data(self):
        try:
            n = int(self.n_entry.get())
            if n <= 0:
                raise ValueError('sample size must be more than 0')
        except ValueError:
            raise ValueError('sample size must be more than 0')

        mean = float(self.mean_entry.get())
        var = float(self.var_entry.get())

        return n, mean, var

    def generate_sample(self):
        try:
            n, mean, var = self.prepare_data()
            sample = get_sample(n, mean, var)

            k = min(10, n // 5)

            probs = np.linspace(0, 1, k + 1)
            bins = norm.ppf(probs, loc=mean, scale=sqrt(var)) # tut
            observed, _ = np.histogram(sample, bins=bins)

            interval_probs = np.diff(norm.cdf(bins, loc=mean, scale=sqrt(var)))
            expected = n * interval_probs
            expected = expected * (n / expected.sum())

            chi_res = chisquare(f_obs=observed, f_exp=expected)
            chi_stat = float(chi_res.statistic)

            df = k - 1
            chi_crit = float(chi2.ppf(1 - 0.05, df))
            chi_result = 'Yes' if chi_stat < chi_crit else 'No'

            sample_mean = np.mean(sample)
            sample_var = np.var(sample, ddof=1)

            mean_error = f'{(abs(sample_mean - mean) / abs(mean) * 100):.2f}%'
            var_error = f'{(abs(sample_var - var) / abs(var) * 100):.2f}%'

            self.show_results(sample_mean, sample_var, mean_error, var_error,
                              chi_stat, chi_crit, chi_result)

            self.update_plot(sample, mean, var)
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def show_results(self, sample_mean, sample_var, mean_error, var_error,
                              chi_stat, chi_crit, chi_result):
        self.result_text.delete('1.0', tk.END)
        text = (
            f'Sample mean: {sample_mean:.5f} (error: {mean_error})\n'
            f'Sample var: {sample_var:.5f} (error: {var_error})\n'
        )
        if chi_crit is not None:
            text += (
                f'Chi2 stat: {chi_stat}, shi2 crit: {chi_crit}\n'
                f'Equals to theory: {chi_result}\n'
            )
        else:
            text += 'Impossible to calculate chi2\n'

        self.result_text.insert(tk.END, text)

    def update_plot(self, sample, mean, var):
        self.ax.clear()
        sample = np.asarray(sample, dtype=float)
        self.ax.hist(sample, bins='auto', density=True, alpha=0.7)
        x_min = min(sample.min(), mean - 4 * sqrt(var))
        x_max = max(sample.max(), mean + 4 * sqrt(var))
        x = np.linspace(x_min, x_max, 500)
        y = norm.pdf(x, loc=mean, scale=sqrt(var))
        self.ax.plot(x, y)
        self.ax.set_title('Hist')
        self.ax.set_xlabel('Value')
        self.ax.set_ylabel('relative freq')
        self.canvas.draw()

if __name__ == '__main__':
    root = tk.Tk()
    app = ContinRVApp(root)
    root.mainloop()