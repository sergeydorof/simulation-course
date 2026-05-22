import math
import random
import matplotlib.pyplot as plt

def exp_rv(intens):
    return - (math.log(random.random()) / intens)

t, x = 0, 0

h = float(input('Интенсивность прихода клиентов: '))
mu = float(input('Интенсивность обслуживания оператором: '))
T = int(input('Количество часов обслуживания: '))
N = 1

t_history = [0.0]
x_history = [0]

while t < T:
    tau = exp_rv(h)

    if x > 0:
        delta = exp_rv(x * mu)
    else:
        delta = float('inf')

    if tau < delta:
        if x < N:
            x += 1
        t += tau
    else:
        x -= 1
        t += delta

    t_history.append(t)
    x_history.append(x)

plt.step(t_history, x_history, where='post')
plt.xlabel('Пройденное время (ч)')
plt.ylabel('Клиентов на обслуживании')
plt.yticks([0, 1])
plt.show()