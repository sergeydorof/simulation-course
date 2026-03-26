import random
import statistics

def base_random(n):
    m = 2**63
    beta = 2**32 + 3
    x = beta
    result = []
    for _ in range(n):
        x = (beta * x) % m
        result.append(x / m)
    return result

base_sample = base_random(100000)
built_into_sample = [random.random() for _ in range(100000)]
print("Базовая выборка")
print(f"Среднее: {statistics.mean(base_sample)}, Дисперсия: {statistics.variance(base_sample)}")
print("\nВстроенная выборка")
print(f"Среднее: {statistics.mean(built_into_sample)}, Дисперсия: {statistics.variance(built_into_sample)}")
print("\nТеоретические значения")
print(f"Среднее: {(0 + 1) / 2}, Дисперсия: {(1 - 0)**2 / 12}")

