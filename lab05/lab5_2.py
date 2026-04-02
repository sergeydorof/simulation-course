import random
import tkinter as tk

class App:
    def __init__(self, root):
        self.probs = [0.05, 0.05, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2]

        self.root = root
        self.root.title("Да / Нет")

        self.run_btn = tk.Button(self.root, text="Зарандомить", command=self.calculate)
        self.run_btn.pack(padx=20, pady=10)

        self.display = tk.Text(self.root, height=10, width=45)
        self.display.pack(padx=20, pady=10)

        self.display.config(state=tk.DISABLED)

    def calculate(self):
        events = [['один', 'red'], ['два', 'orange'], ['три', 'yellow'], ['четыре', 'green'],
                  ['пять', 'cyan'], ['шесть', 'blue'], ['семь', 'purple'], ['восемь', 'magenta']]
        result = []
        a = random.random()
        k = 0
        while True:
            a -= self.probs[k]
            if a > 0:
                k += 1
            else:
                result = events[k]
                break

        self.display.config(state=tk.NORMAL)
        self.display.delete('1.0', tk.END)
        self.display.insert(tk.END, result[0])
        self.display.config(fg=result[1], state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()