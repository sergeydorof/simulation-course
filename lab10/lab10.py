import random
import math
import matplotlib.pyplot as plt

def exp_rv(intens):
    return - (math.log(random.random()) / intens)

class Agent:
    def __init__(self):
        self.next_event_time = 0.0

    def get_next_event(self):
        return self.next_event_time

    def process_event(self, system):
        pass

class ClientGenerator(Agent):
    def __init__(self, h):
        super().__init__()
        self.h = h
        # Планируем приход самого первого клиента
        self.next_event_time = exp_rv(self.h)

    def process_event(self, system):
        system.total_clients += 1
        # Логика прихода клиента в систему
        if system.x < system.N:
            system.x += 1
            # Пытаемся сразу усадить клиента за свободный прибор
            system.start_service_if_possible()
        else:
            system.y += 1
            system.clients_who_waited += 1
            system.queue_timestamps.append(system.t)

        # Планируем приход СЛЕДУЮЩЕГО клиента
        self.next_event_time = system.t + exp_rv(self.h)

class Operator(Agent):
    def __init__(self, mu):
        super().__init__()
        self.mu = mu
        self.is_busy = False
        # Если прибор свободен, его событие освобождения бесконечно далеко
        self.next_event_time = float('inf')

    def start_service(self, current_time):
        self.is_busy = True
        self.next_event_time = current_time + exp_rv(self.mu)

    def process_event(self, system):
        # Прибор освободился, клиент уходит с обслуживания
        system.x -= 1

        # Проверяем, есть ли кто-то в очереди
        if system.y > 0:
            system.y -= 1
            # Не уменьшаем x, так как место тут же занял клиент из очереди
            system.x += 1
            arrival_time = system.queue_timestamps.pop(0)
            wait_time = system.t - arrival_time
            system.total_wait_time += wait_time
            # Запускаем обслуживание нового клиента на этом же приборе
            self.start_service(system.t)
        else:
            # Очередь пуста, прибор переходит в режим ожидания
            self.is_busy = False
            self.next_event_time = float('inf')

class BankSystem:
    def __init__(self, h, mu, N, num_operators):
        self.t = 0.0  # Текущее модельное время
        self.N = N  # Вместимость приборов (макс. кол-во на обслуживании)
        self.x = 0  # Клиентов на обслуживании
        self.y = 0  # Клиентов в очереди

        self.last_event_time = 0.0
        self.queue_length_time_integral = 0.0

        self.history_time = [0.0]
        self.history_queue = [0]

        self.total_clients = 0
        self.clients_who_waited = 0
        self.total_wait_time = 0
        self.queue_timestamps = []

        # Создаем агентов
        self.generator = ClientGenerator(h)
        self.operators = [Operator(mu) for _ in range(num_operators)]

        # Общий список всех агентов в среде
        self.agents = [self.generator] + self.operators

    def start_service_if_possible(self):
        # Ищем любой свободный прибор и отдаем ему клиента
        for op in self.operators:
            if not op.is_busy:
                op.start_service(self.t)
                break

    def run(self, T):
        # Главный цикл дискретно-событийного моделирования
        while self.t < T:
            # Опрашиваем всех агентов и ищем ближайшее событие
            next_agent = min(self.agents, key=lambda a: a.get_next_event())
            next_time = next_agent.get_next_event()

            if next_time >= T:
                break

            dt = next_time - self.t
            self.queue_length_time_integral += self.y * dt

            # Перепрыгиваем по времени сразу к моменту этого события
            self.t = next_time

            # Передаем управление агенту, чье событие наступило
            next_agent.process_event(self)

            self.history_time.append(self.t)
            self.history_queue.append(self.y)

        if self.t < T:
            dt = T - self.t
            self.queue_length_time_integral += self.y * dt
            self.t = T
            self.history_time.append(self.t)
            self.history_queue.append(self.y)

        self.visualize_results()

    def visualize_results(self):
        # Расчет метрик
        prob_queue = self.clients_who_waited / self.total_clients if self.total_clients > 0 else 0
        avg_wait_time = self.total_wait_time / self.total_clients if self.total_clients > 0 else 0
        avg_queue_length = self.queue_length_time_integral / self.t if self.t > 0 else 0

        # Создаем окно с двумя областями (сверху график, снизу блок текста)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [3, 1]})
        fig.suptitle("Результаты агентного моделирования СМО (Банк)", fontsize=14, fontweight='bold')

        # Отрисовка графика очереди
        ax1.step(self.history_time, self.history_queue, where='post', color='blue', linewidth=1.5,
                 label='Текущая очередь')
        ax1.fill_between(self.history_time, self.history_queue, step='post', color='blue', alpha=0.1)

        # Добавляем на график линию средней длины очереди
        ax1.axhline(y=avg_queue_length, color='red', linestyle='--', linewidth=1.5,
                    label=f'Ср. длина очереди ({avg_queue_length:.2f})')

        ax1.set_title("Динамика изменения длины очереди")
        ax1.set_xlabel("Модельное время (t), часы")
        ax1.set_ylabel("Количество человек в очереди (y)")
        ax1.grid(True, linestyle=':', alpha=0.6)
        ax1.legend(loc='upper right')

        # Вывод статистического отчета в нижнее окно
        ax2.axis('off')  # Отключаем оси для текстового блока

        stats_text = (
            f"ОБЩАЯ СТАТИСТИКА РАБОТЫ СИСТЕМЫ:\n"
            f"-------------------------------------------------------------------------\n"
            f"• Всего пришло клиентов за время симуляции: {self.total_clients} чел.\n"
            f"• Из них вынуждены были встать в очередь: {self.clients_who_waited} чел.\n"
            f"• Эмпирическая вероятность попасть в очередь: {prob_queue:.4f} ({prob_queue * 100:.2f}%)\n"
            f"• Среднее время нахождения клиента в очереди: {avg_wait_time:.4f} часа\n"
            f"• Средняя длина очереди (взвешенная по времени): {avg_queue_length:.4f} чел."
        )

        # Размещаем текст по центру нижней области
        ax2.text(0.05, 0.9, stats_text, fontsize=11, family='monospace', verticalalignment='top',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.3))

        plt.tight_layout()
        plt.show()  # Открывает статичное окно с графиком и результатами


# Запуск модели
if __name__ == "__main__":
    # Параметры системы
    H_INTENSITY = float(input('Интенсивность прихода клиентов в час: '))
    MU_INTENSITY = float(input('Интенсивность обслуживания клиентов в час: '))
    OPERATORS_COUNT = int(input('Количество операторов: '))
    MAX_SERVICING = OPERATORS_COUNT
    TOTAL_TIME = int(input("Количество часов обслуживания: "))

    bank = BankSystem(h=H_INTENSITY, mu=MU_INTENSITY, N=MAX_SERVICING, num_operators=OPERATORS_COUNT)
    bank.run(TOTAL_TIME)