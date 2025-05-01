# 第一问
import math
from scipy.optimize import minimize
import numpy as np
import matplotlib.pyplot as plt

C_MAX = [800, 600, 400] # 展馆最大瞬时容量/人
T_OPEN = 8              # 开放时间/小时
T_STAY = 1.75           # 平均驻留时间/小时

A_EFF = 400000          # 有效浏览面积/平方米
S_MIN = 10              # 舒适度阈值/(平方米/人)
T_STAY_OUT = 1.15       # 户外平均驻留时间

def Calc_N_indoor():
    N_indoor = 0
    for c_i in C_MAX:
        N_indoor += T_OPEN / T_STAY * c_i
    return N_indoor

def Calc_N_outdoor():
    N_outdoor = A_EFF / S_MIN * T_OPEN / T_STAY_OUT
    return N_outdoor

# 三类服务点：休息点，商服点，医疗点
MU = [320, 200, 40]             # 服务率(人/小时)
C_SERVICE = [12, 6, 3]          # 服务台数量
P_SERVICE = [0.3, 0.1, 0.01]    # 服务点游客比例
Wq_LIMIT = 0.30                 # 排队时间限制(小时)


# 计算单类商服点的 λ
def Calc_lambda_max(mu, c):
    def Calc_Wq(lmbd):
        rho = lmbd / (c * mu)
        if rho >= 1 or rho <= 0:
            return float('inf')  # 系统不稳定

        # 计算 P0
        sum_p0 = 0
        for k in range(c):
            term = (lmbd/mu)**k / math.factorial(k)
            sum_p0 += term

        # 最后一项的分母 (1 - rho) 避免除以零
        last_term = (lmbd/mu)**c / (math.factorial(c) * (1 - rho))
        P0 = 1 / (sum_p0 + last_term)

        # 计算 Wq
        Wq = ( (lmbd/mu)**c ) / (math.factorial(c) * (1 - rho)**2 ) * P0 / (c * mu)
        return Wq

    # 二分法搜索满足 Wq ≤ Wq_LIMIT 的最大 lambda
    tolerance = 1e-6
    left, right = 0, c * mu - tolerance  # 确保 rho < 1
    best_lambda = 0

    while right - left > tolerance:
        mid = (left + right) / 2
        current_Wq = Calc_Wq(mid)
        if current_Wq <= Wq_LIMIT:
            best_lambda = mid
            left = mid
        else:
            right = mid

    return best_lambda

# 日服务能力
def Calc_N_service():
    N_service_list = [(Calc_lambda_max(mu, c) / p) for mu, c, p in zip(MU, C_SERVICE, P_SERVICE)]

    weights = np.array(C_SERVICE) / sum(C_SERVICE)

    # 取三种服务点的加权平均返回
    return np.sum(np.array(N_service_list) * weights)


V = 1.2             # 人群移动速度
W = 12              # 出口宽度
D_MAX = 1200        # 最远疏散路径长度
V_P = 1.5           # 户外步行速度

def Calc_t_escape():
    N_indoor = Calc_N_indoor()
    t_escape = max(N_indoor / (V * W), D_MAX / V_P)
    return t_escape

def Solve():
    N_outdoor = Calc_N_outdoor()
    N_indoor = Calc_N_indoor()
    N_service = Calc_N_service()
    N_escape = V * W * Calc_t_escape() / T_STAY_OUT

    print(f'N_indoor: {N_indoor:.2f}人, N_outdoor: {N_outdoor:.2f}人, N_service: {N_service:.2f}人, N_escape: {N_escape:.2f}人')

    N_upper = min(N_indoor, N_outdoor, N_service, N_escape)

    def objective(N_array):
        N = N_array[0]  # 从数组中取出标量

        params = [
            (0.8, 1.25, -2.5, 3),
            (0.6, 1.67, -1.25, 1.75),
            (0.7, 1.43, -1.67, 2.17),
            (0.5, 2, -1, 1.5)
        ]

        def N_func(N, p, k1, k2, b):
            return np.piecewise(N,
                                [
                                    (N <= p),
                                    (p < N)
                                ],
                                [
                                    lambda N: k1 * N,
                                    lambda N: k2 * N + b,
                                ]
                                )

        weights = [0.5, 0.25, 0.2, 0.05]
        N_vals = [N_indoor, N_outdoor, N_service, N_escape]

        value = 0
        for i in range(4):
            value += float(N_func(N / N_vals[i], *params[i])) * weights[i]

        return -value


    # 约束，取空值
    constraints = ()

    # 0 <= N <= N_upper 约束
    # 这个边界的优先级更高
    bounds = [
        (0, N_upper),
    ]

    # 初始猜测
    x0 = [N_upper/2]

    # 求解
    result = minimize(objective, x0, method='Powell', bounds=bounds, constraints=constraints)

    # 输出结果
    if result.success:
        N_opt = result.x[0]
        print(f"最优游客容量 N = {N_opt:.2f} 人/天")
    else:
        print("优化失败：", result.message)

    def draw_objective():
        N_test = np.linspace(0, 15000, 300)
        obj_values = [objective([n]) for n in N_test]
        plt.figure(figsize=(10, 6))
        plt.plot(N_test, obj_values, label="Objective Function", color='blue')
        plt.axvline(x=N_upper, color='red', linestyle='--', label=f'N_upper = {N_upper:.1f}')
        plt.xlabel("N")
        plt.ylabel("Objective")
        plt.grid(True)
        plt.legend()
        plt.show()

    draw_objective()

def main():
    Solve()

if __name__ == '__main__':
    main()