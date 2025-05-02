import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib import rcParams

# 设置全局字体为支持中文的字体
rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei']
rcParams['axes.unicode_minus'] = False

os.makedirs('assets', exist_ok=True)

def draw_plot(N_upper=8228.571428571428, N_opt=6582.857142276136,
              N_indoor=8228.571428571428, N_outdoor=278260.8695652174,
              N_service=12396.10149718569, N_escape=10017.391304347826):
    N_range = np.linspace(2000, 12000, 500)

    # 定义各分段函数参数
    params = [
        (0.8, 1.25, -2.5, 3),      # 室内
        (0.6, 1.67, -1.25, 1.75),  # 户外
        (0.7, 1.43, -1.67, 2.17),  # 服务
        (0.5, 2.0, -1.0, 1.5)      # 疏散
    ]
    labels = ['室内容量', '户外容量', '服务容量', '疏散容量']
    colors = ['#ffa600', '#bc5090', '#003f5c', '#665191']  # 调和色板
    weights = [0.5, 0.25, 0.2, 0.05]
    N_vals = [N_indoor, N_outdoor, N_service, N_escape]

    plt.figure(figsize=(12, 7))

    # 绘制四个约束函数
    for i in range(4):
        p, k1, k2, b = params[i]
        y = np.piecewise(N_range/N_vals[i],
                         [N_range/N_vals[i] <= p, N_range/N_vals[i] > p],
                         [lambda x: k1*x, lambda x: k2*x + b])
        plt.plot(N_range, y, lw=2.2, label=labels[i], color=colors[i])

    # 计算目标函数
    def objective(N):
        total = 0
        for i in range(4):
            p, k1, k2, b = params[i]
            y = np.piecewise(N/N_vals[i],
                             [N/N_vals[i] <= p, N/N_vals[i] > p],
                             [lambda x: k1*x, lambda x: k2*x + b])
            total += y * weights[i]
        return total

    objective_values = [objective(n) for n in N_range]
    plt.plot(N_range, objective_values, color='#003f5c', lw=3.5, label='目标函数', linestyle='-')

    # 标注垂线
    plt.axvline(N_upper, color='red', linestyle='--', alpha=0.7)
    plt.axvline(N_opt, color='green', linestyle='dashdot', alpha=0.7)
    plt.text(N_upper + 100, max(objective_values)*0.8, f'N_upper={N_upper:.0f}', color='red', fontsize=10,
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'))
    plt.text(N_opt + 100, max(objective_values)*0.6, f'最优值={N_opt:.0f}', color='green', fontsize=10,
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='green'))

    # 设置标题和标签
    plt.title('游客承载能力评估函数图', fontsize=16)
    plt.xlabel('游客数量 N (人)', fontsize=14)
    plt.ylabel('函数值', fontsize=14)

    # 图例外移右侧
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('assets/functions.svg', format='svg', bbox_inches='tight')
    plt.close()

# 执行绘图
draw_plot()
