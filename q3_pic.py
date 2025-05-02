import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 中文显示支持
rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei']
rcParams['axes.unicode_minus'] = False

# 创建图
G = nx.Graph()

'''
景点热度和颜色有关：
    红色：10
    橙色：7
    黄色：5
    绿色：3
    蓝色：1
'''
# 添加节点
G.add_node("西北门", type="出入口")
G.add_node("净月广场", type="景点", heat=10)
G.add_node("荷花垂柳园", type="景点", heat=10)
G.add_node("朝夕水岸", type="景点", heat=5)
G.add_node("黑松林", type="景点", heat=1)
G.add_node("西门", type="出入口")
G.add_node("荷花池", type="景点", heat=7)
G.add_node("恐龙园", type="景点", heat=7)
G.add_node("瓦萨博物馆", type="景点", heat=7)
G.add_node("竹筏湿地公园", type="景点", heat=1)
G.add_node("月潭揽胜", type="景点", heat=1)
G.add_node("森林植物园", type="景点", heat=3)
G.add_node("大坝游船码头", type="景点", heat=10)

# 添加边（距离单位：米）
edges = [
    ("西北门", "净月广场", 200),
    ("净月广场", "朝夕水岸", 1000),
    ("朝夕水岸", "黑松林", 1100),
    ("黑松林", "荷花池", 2400),
    ("荷花池", "恐龙园", 1500),
    ("恐龙园", "瓦萨博物馆", 400),
    ("瓦萨博物馆", "竹筏湿地公园", 1600),
    ("竹筏湿地公园", "月潭揽胜", 1700),
    ("月潭揽胜", "森林植物园", 3800),
    ("森林植物园", "大坝游船码头", 400),
    ("大坝游船码头", "荷花垂柳园", 500),
    ("荷花垂柳园", "净月广场", 1000),
    ("荷花垂柳园", "朝夕水岸", 700),
    ("黑松林", "西门", 2100),
    ("荷花池", "西门", 1100)
]

for u, v, w in edges:
    G.add_edge(u, v, weight=w)

def draw_plot():
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(14, 7))

    # 边标签（权重）
    edge_labels = nx.get_edge_attributes(G, 'weight')


    # 根据热度设定颜色映射（红、橙、黄、绿、蓝）
    def heat_to_color(heat):
        if heat >= 10:
            return 'red'
        elif heat >= 7:
            return 'orange'
        elif heat >= 5:
            return 'yellow'
        elif heat >= 3:
            return 'green'
        else:
            return 'blue'

    # 节点颜色和大小（热度越高越显眼）
    node_colors = []
    node_sizes = []
    for n in G.nodes:
        ntype = G.nodes[n].get('type')
        if ntype == '出入口':
            node_colors.append('lightgray')
            node_sizes.append(1000)
        else:
            heat = G.nodes[n].get('heat', 1)
            node_colors.append(heat_to_color(heat))
            node_sizes.append(500 + heat * 50)  # 热度越高，节点越大

    # 绘图
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_labels(G, pos, font_size=9)
    nx.draw_networkx_edges(G, pos, edge_color='gray')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, label_pos=0.5)

    # 标题与美化
    plt.title("净月潭国家森林公园图模型", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('assets/jingyuetan_map.svg', format='svg', bbox_inches='tight')
    plt.close()

draw_plot()