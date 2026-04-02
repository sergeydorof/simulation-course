import random
import tkinter as tk

class App:
    def __init__(self, root):
        self.prob = 0.3

        self.root = root
        self.root.title("Да / Нет")

        self.run_btn = tk.Button(self.root, text="Зарандомить", command=self.calculate)
        self.run_btn.pack(padx=20, pady=10)

        self.display = tk.Text(self.root, height=10, width=45)
        self.display.pack(padx=20, pady=10)

        self.display.config(state=tk.DISABLED)

    def calculate(self):
        result = ["Да", "blue"] if random.random() < self.prob else ["Нет", "red"]
        self.display.config(state=tk.NORMAL)
        self.display.delete('1.0', tk.END)
        self.display.insert(tk.END, result[0])
        self.display.config(fg=result[1], state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()