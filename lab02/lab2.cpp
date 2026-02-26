#include "pch.h"
#include <vector>

using namespace std;

extern "C" {
	__declspec(dllexport) void calculate(
		double T_left,
		double T_right,
		double T_start,
		double L,
		double h,
		double tau,
		double total_time,
		double* result
	) {
		// константы для стали
		const double rho = 7800, c = 460, lambda = 46;

		// количество шагов по времени и пространству
		int N = static_cast<int>(L / h) + 1;
		int steps = static_cast<int>(total_time / tau);

		vector<double> T(N, T_start);
		vector<double> T_next(N);
		T[0] = T_left;
		T[N - 1] = T_right;

		double A = lambda / (h * h);
		double C = A;
		double B = 2.0 * lambda / (h * h) + (rho * c) / tau;

		vector<double> alpha(N);
		vector<double> beta(N);

		for (int step = 0; step < steps; ++step) {
			// прямая прогонка
			alpha[1] = 0;
			beta[1] = T_left;
			for (int i = 1; i < N - 1; ++i) {
				double Fi = -(rho * c / tau) * T[i];
				double den = B - C * alpha[i];
				alpha[i + 1] = A / den;
				beta[i + 1] = (C * beta[i] - Fi) / den;
			}

			//обратная прогонка
			T_next[N - 1] = T_right;
			for (int i = N - 2; i >= 0; --i) {
				T_next[i] = alpha[i + 1] * T_next[i + 1] + beta[i + 1];
			}
			T = T_next;
		}

		for (int i = 0; i < N; ++i) {
			result[2 * i] = i * h;
			result[2 * i + 1] = T[i];
		}
	}
}