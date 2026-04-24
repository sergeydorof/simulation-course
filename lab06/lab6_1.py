import seaborn as sns
import matplotlib.pyplot as plt
import random
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy.stats import chi2, chisquare
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def parse_number_list(text: str):
    tokens = text.replace(';', ' ').split()
    if not tokens:
        raise ValueError('List is empty')
    try:
        return [float(token.replace(',', '.')) for token in tokens]
    except ValueError:
        raise ValueError("Can't read numbers")

def get_sample(n, vals, probs):
    result = []
    for _ in range(n):
        a = random.random()
        k = 0
        while True:
            a -= probs[k]
            if a > 0:
                k += 1
            else:
                result.append(vals[k])
                break
    return result

class DiscreteRVApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Discrete Random Value')
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

        ttk.Label(input_frame, text='Values (from space):').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.vals_entry = ttk.Entry(input_frame, width=50)
        self.vals_entry.grid(row=1, column=1, sticky='we', padx=5, pady=5)
        self.vals_entry.insert(0, '1 2 3 4 5')

        ttk.Label(input_frame, text='Probs (from space):').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.probs_entry = ttk.Entry(input_frame, width=50)
        self.probs_entry.grid(row=2, column=1, sticky='we', padx=5, pady=5)
        self.probs_entry.insert(0, '1 2 3 4 5')

        generate_button = ttk.Button(input_frame, text='Generate', command=self.generate_sample)
        generate_button.grid(row=3, column=0, columnspan=2, pady=10)

        info_label = ttk.Label(
            input_frame,
            text='final prob for i val = entered prob for i / sum of entered probs',
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

        vals = parse_number_list(self.vals_entry.get())
        probs = parse_number_list(self.probs_entry.get())

        if len(vals) != len(probs):
            raise ValueError('Count of probs and vals is not equals')
        if len(vals) < 5:
            raise ValueError('Minimum 5 values')
        if len(set(vals)) != len(vals):
            raise ValueError('Vals must be different')

        probs = np.array(probs, dtype=float)
        vals = np.array(vals, dtype=float)

        prob_sum = probs.sum()
        probs = probs / prob_sum

        order = np.argsort(vals)
        vals = vals[order]
        probs = probs[order]

        self.vals_entry.delete(0, tk.END)
        self.vals_entry.insert(0, ' '.join(f'{x:g}' for x in vals))

        self.probs_entry.delete(0, tk.END)
        self.probs_entry.insert(0, ' '.join(f'{p:.4f}' for p in probs))

        return n, vals, probs, prob_sum

    def generate_sample(self):
        try:
            n, vals, probs, prob_sum = self.prepare_data()
            sample = get_sample(n, vals, probs)

            observed_counts = np.array([(sample == x).sum() for x in vals], dtype=float)
            observed_freqs = observed_counts / n
            expected_counts = n * probs

            positive_mask = expected_counts > 0
            obs = observed_counts[positive_mask]
            exp = expected_counts[positive_mask]

            df = len(obs) - 1

            if df > 0:
                chi_result_obj = chisquare(f_obs=obs, f_exp=exp)
                chi_stat = float(chi_result_obj.statistic)
                chi_crit = chi2.ppf(1 - 0.05, df)
                chi_result = 'Yes' if chi_stat < chi_crit else 'No'
            else:
                chi_stat = None
                chi_crit = None
                chi_result = 'Impossible to calculate'

            theory_mean = np.sum(vals * probs)
            theory_var = np.sum((vals - theory_mean)**2 * probs)

            sample_mean = np.mean(sample)
            sample_var = np.var(sample, ddof=1)

            mean_error = f'{(abs(sample_mean - theory_mean) / abs(theory_mean) * 100):.2f}%'
            var_error = f'{(abs(sample_var - theory_var) / abs(theory_var) * 100):.2f}%'

            self.show_results(theory_mean, theory_var,
                              sample_mean, sample_var, mean_error, var_error,
                              chi_stat, chi_crit, chi_result)

            self.update_plot(vals, observed_freqs)
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def show_results(self, theory_mean, theory_var,
                              sample_mean, sample_var, mean_error, var_error,
                              chi_stat, chi_crit, chi_result):
        self.result_text.delete('1.0', tk.END)
        text = (
            f'Theory mean: {theory_mean:.5f}, sample mean: {sample_mean:.5f} (error: {mean_error})\n'
            f'Theory var: {theory_var:.5f}, sample var: {sample_var:.5f} (error: {var_error})\n'
        )
        if chi_crit is not None:
            text += (
                f'Chi2 stat: {chi_stat}, shi2 crit: {chi_crit}\n'
                f'Equals to theory: {chi_result}\n'
            )
        else:
            text += 'Impossible to calculate chi2\n'

        self.result_text.insert(tk.END, text)

    def update_plot(self, vals, observed_freqs):
        self.ax.clear()
        self.ax.bar(vals, observed_freqs)
        self.ax.set_title('Hist')
        self.ax.set_xlabel('Value')
        self.ax.set_ylabel('relative freq')
        self.canvas.draw()

if __name__ == '__main__':
    root = tk.Tk()
    app = DiscreteRVApp(root)
    root.mainloop()