# 对sigma进行初始化，参数为node（从chance节点root开始）
# 以递归的方法更新output，它代表每个信息集下的sigma(合法动作的概率集)
# output是一个字典，key为每一个节点的information set，值为一个子字典
# 子字典的key为合法动作(例如CHECK，FOLD），值为对应action的概率（也就是策略sigma）
'''
{
'.K.': {'BET': 0.5, 'CHECK': 0.5},
'.Q.BET': {'FOLD': 0.5, 'CALL': 0.5},
...
}
'''
def init_sigma(node, output = None):
    output = dict()
    def init_sigma_recursive(node):
        # 初始化就按照action做均匀分配就行
        output[node.inf_set()] = {action: 1. / len(node.actions) for action in node.actions}
        for k in node.children:
            init_sigma_recursive(node.children[k])
    init_sigma_recursive(node)
    return output

# 这里是对统计表的初始化
# 类似的，每一个字典的key为information set，值为合法行动的累计值集合
'''
{
'.K.': {'BET': 0.0, 'CHECK': 0.0},
'.Q.BET': {'FOLD': 0.0, 'CALL': 0.0},
...
}
'''
def init_empty_node_maps(node, output = None):
    output = dict()
    def init_empty_node_maps_recursive(node):
        output[node.inf_set()] = {action: 0. for action in node.actions}
        for k in node.children:
            init_empty_node_maps_recursive(node.children[k])
    init_empty_node_maps_recursive(node)
    return output
