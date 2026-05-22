import math
import random
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.distributions.empirical_distribution import ECDF

t = 0
h = float(input('Введите интенсивность: '))
T = int(input('Введите общее время моделирования (часы): '))
result = []
count_rv = [0] * T
hour = 1

while t < T:
    t += (- (math.log(random.random()) / h))

    if t > hour:
        hour += int(t - hour + 1)

    if t < T:
        result.append(t)
        count_rv[hour - 1] += 1

ecdf = ECDF(count_rv)
plt.step(ecdf.x, ecdf.y, where='post')
plt.title(f'Эмпирическое распределение\nСреднее: теоретическое - {h}, выборочное - {np.mean(count_rv):.3f}\nДисперсия: теоретическая - {h}, выборочная - {np.var(count_rv, ddof=1):.3f}')
plt.tight_layout()
plt.show()