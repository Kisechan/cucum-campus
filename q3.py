import networkx as nx
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpInteger, value
import matplotlib.pyplot as plt
from matplotlib import rcParams
# 中文显示支持
rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei']
rcParams['axes.unicode_minus'] = False

# 创建图
G = nx.Graph()

# 添加节点
nodes = [
    ("西北门", {"type": "出入口", "heat": 10, "danger": 4}),
    ("净月广场", {"type": "景点", "heat": 10, "danger": 2}),
    ("荷花垂柳园", {"type": "景点", "heat": 10, "danger": 5}),
    ("朝夕水岸", {"type": "景点", "heat": 5, "danger": 7}),
    ("黑松林", {"type": "景点", "heat": 1, "danger": 4}),
    ("西门", {"type": "出入口", "heat": 3, "danger": 2}),
    ("荷花池", {"type": "景点", "heat": 7, "danger": 4}),
    ("恐龙园", {"type": "景点", "heat": 7, "danger": 3}),
    ("瓦萨博物馆", {"type": "景点", "heat": 7, "danger": 1}),
    ("竹筏湿地公园", {"type": "景点", "heat": 1, "danger": 4}),
    ("月潭揽胜", {"type": "景点", "heat": 1, "danger": 5}),
    ("森林植物园", {"type": "景点", "heat": 3, "danger": 4}),
    ("大坝游船码头", {"type": "景点", "heat": 10, "danger": 9})
]
G.add_nodes_from(nodes)

# 添加边
edges = [
    ("西北门", "净月广场", {"weight": 200, "danger": 1}),
    ("净月广场", "朝夕水岸", {"weight": 1000, "danger": 5}),
    ("朝夕水岸", "黑松林", {"weight": 1100, "danger": 5}),
    ("黑松林", "荷花池", {"weight": 2400, "danger": 4}),
    ("荷花池", "恐龙园", {"weight": 1500, "danger": 2}),
    ("恐龙园", "瓦萨博物馆", {"weight": 400, "danger": 1}),
    ("瓦萨博物馆", "竹筏湿地公园", {"weight": 1600, "danger": 2}),
    ("竹筏湿地公园", "月潭揽胜", {"weight": 1700, "danger": 3}),
    ("月潭揽胜", "森林植物园", {"weight": 3800, "danger": 4}),
    ("森林植物园", "大坝游船码头", {"weight": 400, "danger": 1}),
    ("大坝游船码头", "荷花垂柳园", {"weight": 500, "danger": 6}),
    ("荷花垂柳园", "净月广场", {"weight": 1000, "danger": 3}),
    ("荷花垂柳园", "朝夕水岸", {"weight": 700, "danger": 4}),
    ("黑松林", "西门", {"weight": 2100, "danger": 2}),
    ("荷花池", "西门", {"weight": 1100, "danger": 2})
]
G.add_edges_from(edges)

# 参数设置
params = {
    "r_guide": 300,       # 引导服务半径(m)
    "r_emergency": 500,   # 应急服务半径(m)
    "rho_guide": 50,      # 引导服务效率(人/小时)
    "rho_emergency": 20,  # 应急服务效率(事件/小时)
    "rho_consult": 30,    # 咨询服务效率(人/小时)
    "lambda": 0.1         # 风险权重系数
}

# 创建问题实例
prob = LpProblem("Volunteer_Allocation", LpMinimize)

# 定义决策变量
# 节点志愿者变量
x_guide = {node: LpVariable(f"x_guide_{node}", lowBound=0, cat=LpInteger) for node in G.nodes()}
x_consult = {node: LpVariable(f"x_consult_{node}", lowBound=0, cat=LpInteger) for node in G.nodes()}
x_emergency = {node: LpVariable(f"x_emergency_{node}", lowBound=0, cat=LpInteger) for node in G.nodes()}

# 边志愿者变量
y_guide = {edge: LpVariable(f"y_guide_{edge[0]}_{edge[1]}", lowBound=0, cat=LpInteger) for edge in G.edges()}
y_emergency = {edge: LpVariable(f"y_emergency_{edge[0]}_{edge[1]}", lowBound=0, cat=LpInteger) for edge in G.edges()}

# 目标函数
risk_term = lpSum(
    G.nodes[node]['danger'] * G.nodes[node]['heat'] * (1 - 0.05 * x_emergency[node])  # 风险随志愿者递减
    for node in G.nodes()
) + lpSum(
    G.edges[edge]['danger'] * (G.nodes[edge[0]]['heat'] + G.nodes[edge[1]]['heat']) / 2 * (1 - 0.05 * y_emergency[edge])
    for edge in G.edges()
)

prob += lpSum(x_guide.values()) + lpSum(x_consult.values()) + lpSum(x_emergency.values()) + \
        lpSum(y_guide.values()) + lpSum(y_emergency.values()) + params['lambda'] * risk_term

# 约束条件
for node in G.nodes():
    # 节点引导需求约束
    prob += x_guide[node] >= (G.degree(node) * G.nodes[node]['heat']) / params['rho_guide']

    # 节点咨询需求约束
    # 假设咨询需求为人流量的 30%
    prob += x_consult[node] >= 0.3 * G.nodes[node]['heat']

    # 节点应急需求约束
    prob += x_emergency[node] >= (G.nodes[node]['danger'] * G.nodes[node]['heat']) / 10

for edge in G.edges():
    # 计算边的游客流动速率
    f_ij = (G.nodes[edge[0]]['heat'] + G.nodes[edge[1]]['heat']) / (2 * G.edges[edge]['weight'])

    # 边引导需求约束
    prob += y_guide[edge] >= (f_ij * G.edges[edge]['weight']) / (params['r_guide'] * params['rho_guide'])

    # 边应急需求约束
    prob += y_emergency[edge] >= (G.edges[edge]['danger'] * f_ij) / 5

# 服务半径覆盖约束
for node in G.nodes():
    # 获取在服务半径内的其他节点
    neighbors_in_radius = [
        n for n in G.nodes()
        if n != node and nx.shortest_path_length(G, source=node, target=n, weight='weight') <= params['r_emergency']
    ]

    # 应急服务覆盖约束
    prob += x_emergency[node] + lpSum(x_emergency[n] for n in neighbors_in_radius) >= G.nodes[node]['heat'] * 0.1

# 求解问题
prob.solve()

# 输出结果
print("优化状态:", prob.status)
print(f'目标函数值为: {value(prob.objective):.1f}')

# 收集结果
results = {
    'nodes': {},
    'edges': {}
}

for node in G.nodes():
    results['nodes'][node] = {
        'guide': value(x_guide[node]),
        'consult': value(x_consult[node]),
        'emergency': value(x_emergency[node])
    }

for edge in G.edges():
    results['edges'][edge] = {
        'guide': value(y_guide[edge]),
        'emergency': value(y_emergency[edge])
    }

# 输出结果
sum_num = 0
print("\n节点志愿者分配:")
for node, alloc in results['nodes'].items():
    print(f"{node}: \t引导={alloc['guide']} \t咨询={alloc['consult']} \t应急={alloc['emergency']}")
    sum_num += alloc['guide'] + alloc['consult'] + alloc['emergency']

print("\n道路志愿者分配:")
for edge, alloc in results['edges'].items():
    print(f"{edge[0]}--{edge[1]}: \t引导={alloc['guide']} \t应急={alloc['emergency']}")
    sum_num += alloc['guide'] + alloc['emergency']

print(f"\n志愿者总数: {sum_num:.1f} 人")

def draw_plot():
    # 创建可视化图形
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, seed=42, k=0.15)  # 设置节点布局

    # 1. 绘制节点和边的基础图
    nx.draw_networkx_edges(G, pos, alpha=0.3, width=1.5)

    # 2. 绘制节点（按志愿者总数设置大小和颜色）
    node_sizes = [100 + 350*(results['nodes'][n]['guide'] + results['nodes'][n]['consult'] + results['nodes'][n]['emergency'])
                  for n in G.nodes()]
    node_colors = [results['nodes'][n]['emergency'] for n in G.nodes()]  # 用应急志愿者数量作为颜色指标

    nodes = nx.draw_networkx_nodes(
        G, pos, node_size=node_sizes,
        node_color=node_colors,
        cmap='YlOrRd', alpha=0.8
    )

    # 3. 添加节点标签（显示三类志愿者数量）
    node_labels = {
        n: f"{n}\nG:{results['nodes'][n]['guide']} C:{results['nodes'][n]['consult']} E:{results['nodes'][n]['emergency']}"
        for n in G.nodes()
    }
    nx.draw_networkx_labels(
        G, pos, labels=node_labels,
        font_size=8, font_color='black',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.3')
    )

    # 4. 添加边标签（显示两类志愿者数量）
    edge_labels = {
        e: f"G:{results['edges'][e]['guide']} E:{results['edges'][e]['emergency']}"
        for e in G.edges()
    }
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels,
        font_size=7, font_color='blue',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
    )

    # 5. 添加图例和颜色条
    plt.colorbar(nodes, label='应急志愿者数量', shrink=0.8)
    plt.title("净月潭国家森林公园志愿者分配方案\n(节点大小表示总志愿者需求，颜色表示应急志愿者数量)", fontsize=12)

    # 6. 添加说明文本
    plt.figtext(0.5, 0.05,
                "G:引导志愿者数量  C:咨询志愿者数量  E:应急志愿者数量",
                ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})

    plt.axis('off')
    plt.tight_layout()
    plt.savefig('assets/jingyuetan_volunteers.svg', format='svg', bbox_inches='tight')
    plt.close()