import random
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.patches as patches
import collections
import pandas as pd

Q = [[-0.35, 0.2, 0.1, 0.05],
     [0.15, -0.35, 0.15, 0.05],
     [0.05, 0.15, -0.35, 0.15],
     [0.05, 0.1, 0.2, -0.35]]

def generate_drv(probs):
     a = random.random()
     k = 0
     while True:
          a -= probs[k]
          if a > 0:
               k += 1
          else:
               result = k
               break
     return result

def model_state(i, t):
     tau = math.log(random.random()) / Q[i][i]
     t += tau
     probs = [- Q[i][j] / Q[i][i] if i != j else 0 for j in range(4)]
     i = generate_drv(probs)
     return i, t

def generate_chain(N):
     i, t = 0, 0
     result = [(i, t)]
     while t < N:
          i, t = model_state(i, t)
          result.append((i, t))
     return result

def get_empiric():
     completed_days = range(1, N + 1)
     states_at_daily_intervals = []

     for day in completed_days:
          idx = max([i for i, t in enumerate(times) if t <= day])
          states_at_daily_intervals.append(states[idx])

     counter = collections.Counter(states_at_daily_intervals)
     total_days = len(states_at_daily_intervals)
     empiric = {state: count / total_days for state, count in counter.items()}
     empiric_df = pd.DataFrame(list(empiric.items()), columns=['Номер состояния', 'Эмп вероятность'])
     empiric_df = empiric_df.sort_values(by='Номер состояния').reset_index(drop=True)
     return empiric_df

def get_theory():
     Qnp = np.array(Q)
     n = Qnp.shape[0]

     # pi * Q = 0 -> Q.T * pi.T = 0
     M = Qnp.copy().T
     M[-1, :] = 1

     b = np.zeros(n)
     b[-1] = 1

     pi = np.linalg.solve(M, b)

     theory_df = pd.DataFrame({
          'Номер состояния': range(len(pi)),
          'Теоретич вероятность': pi
     })

     return theory_df

N = 60
history = generate_chain(N)

states_map = {0: 'Ясно', 1: 'Облачно', 2: 'Дождь', 3: 'Гроза'}
states, times = zip(*history)
colors_map = {
     0: "#FFD700",
     1: "#D3D3D3",
     2: "#1E90FF",
     3: "#4B0082"
}

empiric_df = get_empiric()
theory_df = get_theory()

empiric_df.to_csv(
     'empiric.csv',
     sep=';',
     encoding='utf-8-sig',
     index=False,
     decimal=','
)

theory_df.to_csv(
     'theory.csv',
     sep=';',
     encoding='utf-8-sig',
     index=False,
     decimal=','
)

fig, ax = plt.subplots(figsize=(10, 4))
ax.set_xlim(0, N)
ax.set_ylim(-0.5, 3.5)
ax.set_yticks([0, 1, 2, 3])
ax.set_yticklabels([states_map[0], states_map[1], states_map[2], states_map[3]])
ax.set_xlabel("Время (дни)")
ax.grid(True, linestyle='--', alpha=0.6)

time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes,
                    fontsize=12, fontweight='bold', verticalalignment='top')

bg_rect = patches.Rectangle((0, 0), 1, 1,
                            transform=ax.transAxes, zorder=-1, alpha=0.5)
ax.add_patch(bg_rect)

line, = ax.plot([], [], lw=2, color='blue', drawstyle='steps-post')
point, = ax.plot([], [], 'ro')

daily_points, = ax.plot([], [], 'd', color='cyan', markeredgecolor='black',
                        markersize=5, label='Состояние в конце дня', zorder=4)

def init():
     line.set_data([], [])
     point.set_data([], [])
     time_text.set_text('')
     daily_points.set_data([], [])
     bg_rect.set_facecolor('white')
     return line, point, daily_points, time_text, bg_rect

def update(frame):
     past_events = [i for i, t in enumerate(times) if t <= frame]
     if past_events:
         idx = past_events[-1]
         current_state = states[idx]
         plot_times = list(times[:idx + 1]) + [frame]
         plot_states = list(states[:idx + 1]) + [current_state]
         line.set_data(plot_times, plot_states)
         point.set_data([frame], [current_state])

         completed_days = np.arange(1, int(frame) + 1)
         day_states = []

         for day in completed_days:
             state_at_end_of_date = states[max(
                   [i for i, t in enumerate(times) if t <= day]
              )]
             day_states.append(state_at_end_of_date)

         daily_points.set_data(completed_days, day_states)
     bg_rect.set_facecolor(colors_map[current_state])
     time_text.set_text(f'Время: {frame:.2f} дн')
     return line, point, daily_points, time_text, bg_rect

ani = FuncAnimation(
     fig, update,
     frames=np.linspace(0, N, 1500),
     init_func=init,
     blit=True, interval=5, repeat=False
)

plt.legend(loc='lower right')
plt.show()
