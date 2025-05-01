# 第一问
import math
from scipy.optimize import minimize
import numpy as np

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

MU = 10             # 服务率(人/小时)
C_SERVICE = 6       # 服务台数量
Wq_LIMIT = 0.25     # 排队时间限制

def Calc_Wq(lmbd):
    rho = lmbd / (C_SERVICE * MU)
    if rho >= 1 or rho <= 0:
        return float('inf')
        # 系统不稳定或数据出错
    Wq = ((lmbd / MU) ** C_SERVICE) / (math.factorial(C_SERVICE) * ((1 - rho) ** 3) * C_SERVICE * MU)
    return Wq

def Get_lambda():
    tolerance = 1e-6
    l = 0.0
    r = C_SERVICE * MU - tolerance
    lmbd = 0.0
    while r - l > tolerance:
        mid = l + (r - l) / 2
        Wq = Calc_Wq(mid)
        if Wq < Wq_LIMIT:
            l = mid
            lmbd = mid
        else:
            r = mid
    return lmbd

def Calc_N_service():
    lmbd = Get_lambda()
    N_service = lmbd * T_OPEN
    return N_service

V = 1.2             # 人群移动速度
W = 12              # 出口宽度
D_MAX = 1200        # 最远疏散路径长度
V_P = 1.5           # 户外步行速度

def Calc_t_escape():
    N_indoor = Calc_N_indoor()
    t_escape = max(N_indoor / (V * W), D_MAX / V_P)
    return t_escape

def Solve():
    # 权重
    omega1 = 0.8
    omega2 = 0.2
    N_indoor = Calc_N_indoor()
    N_service = Calc_N_service()
    N_escape = V * W * Calc_t_escape() / T_STAY_OUT

    N_upper = min(N_indoor, N_service, N_escape)

    def objective(N):
        return omega1 * abs(N[0] / N_indoor - 1) + omega2 * abs(N[0] / N_service - 1)

    # 约束：N <= N_upper
    constraints = ({
        'type': 'ineq',
        'fun': lambda N: N_upper - N[0]  # N <= N_upper
    })

    # N >= 0 约束
    bounds = [(0, N_upper)]

    # 初始猜测
    x0 = [min(N_indoor, N_service)]

    # 求解
    result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)

    # 输出结果
    if result.success:
        N_opt = result.x[0]
        print(f"最优游客容量 N = {N_opt:.2f} 人/天")
        print(f"相对误差: 室内偏差={(N_opt/N_indoor - 1):.4f}, 商服偏差={(N_opt/N_service - 1):.4f}")
    else:
        print("优化失败：", result.message)

def main():
    Solve()

if __name__ == '__main__':
    main()