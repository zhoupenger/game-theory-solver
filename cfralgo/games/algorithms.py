from common.constants import A
from common.utils import init_sigma, init_empty_node_maps

# 这个是CFR算法的基类，包含了一些核心的共用的方法
class CounterfactualRegretMinimizationBase:

    def __init__(self, root, chance_sampling = False):
        self.root = root
        # 初始化sigma策略表(概率)-当前策略
        self.sigma = init_sigma(root)
        # 初始化累计收益/遗憾
        self.cumulative_regrets = init_empty_node_maps(root)
        # 初始化sigma策略的累计概率 -> 用于计算纳什均衡策略
        self.cumulative_sigma = init_empty_node_maps(root)
        # 初始化纳什均衡策略
        self.nash_equilibrium = init_empty_node_maps(root)
        # 是否使用chance_sampling方法
        self.chance_sampling = chance_sampling

    def _update_sigma(self, i):
        # 传入i信息集
        # 首先计算所有累积遗憾值（cumulative regrets）中大于0的元素的和（rgrt_sum）
        rgrt_sum = sum(filter(lambda x : x > 0, self.cumulative_regrets[i].values()))
        # 对于这个玩家在信息集i下的每一个可能动作a，更新策略sigma中对应的元素
        for a in self.cumulative_regrets[i]:
            # 最基本的遗憾匹配算法
            # 每一个行动的regret去除所有regrets
            self.sigma[i][a] = max(self.cumulative_regrets[i][a], 0.) / rgrt_sum if rgrt_sum > 0 else 1. / len(self.cumulative_regrets[i].keys())

    def compute_nash_equilibrium(self):
        # self-play完后，可以使用这个方法来计算纳什均衡策略
        self.__compute_ne_rec(self.root)

    def __compute_ne_rec(self, node):
        # 到达终止节点结束
        if node.is_terminal():
            return
        
        # 先找出当前节点所处的information set
        i = node.inf_set()

        # 如果节点是chance节点
        if node.is_chance():
            # nash均衡策略在chance节点均匀分布
            self.nash_equilibrium[i] = {a:node.chance_prob() for a in node.actions}
        else:
        # 如果节点不是chance node
            # 按照cumulative_sigma比例来分配->nash_equilibrium
            sigma_sum = sum(self.cumulative_sigma[i].values()) # 当前信息集的概率总和
            self.nash_equilibrium[i] = {a: self.cumulative_sigma[i][a] / sigma_sum for a in node.actions} # 每一个动作累积概率/信息集的概率总和
        
        # 递归的方法去子节点
        for k in node.children:
            self.__compute_ne_rec(node.children[k])
    
    # 把新的regret更新到cumulative_regrets表中
    def _cumulate_cfr_regret(self, information_set, action, regret):
        self.cumulative_regrets[information_set][action] += regret

    # 把新的sigma策略概率集更新到cumulative_sigma表中
    def _cumulate_sigma(self, information_set, action, prob):
        self.cumulative_sigma[information_set][action] += prob

    def run(self, iterations):
        # 这部分需要具体实现
        raise NotImplementedError("Please implement run method")

    def value_of_the_game(self):
        # 从chance node开始计算游戏路径价值
        # v_i(\sigma,h)=\sum_{z\in Z,h\sqsubset z}\pi_{-i}^\sigma(h)\pi^\sigma(h,z)u_i(z)
        return self.__value_of_the_game_state_recursive(self.root)

    def _cfr_utility_recursive(self, state, reach_a, reach_b):
        children_states_utilities = {}
        if state.is_terminal():
            # 如果是终止节点，则把比赛结果返回
            return state.evaluation()
        if state.is_chance():
            if self.chance_sampling:
                # 开启chance_sampling会随机选择一个事件而非全部计算
                return self._cfr_utility_recursive(state.sample_one(), reach_a, reach_b)
            else:
                # 不开启chance_sampling我们会考虑chance node的所有可能情况
                chance_outcomes = {state.play(action) for action in state.actions}
                return state.chance_prob() * sum([self._cfr_utility_recursive(outcome, reach_a, reach_b) for outcome in chance_outcomes])
        
  
        value = 0. # 虚拟价值
        for action in state.actions:
            # 更新玩家1和玩家2到达下一节点的概率
            child_reach_a = reach_a * (self.sigma[state.inf_set()][action] if state.to_move == A else 1)
            child_reach_b = reach_b * (self.sigma[state.inf_set()][action] if state.to_move == -A else 1)
            
            # v[i][a] = CFR(ha)
            child_state_utility = self._cfr_utility_recursive(state.play(action), child_reach_a, child_reach_b)
            # v[i] = v[i] + v[i][a]*P(a)
            value +=  self.sigma[state.inf_set()][action] * child_state_utility
            
            # 记录子状态效用值
            children_states_utilities[action] = child_state_utility

        # 计算并累积两位玩家的反事实遗憾值（regrets），并据此更新他们的策略。
        # 在一个节点里，玩家A和玩家B所面临的情况是不同的
        # (对手到达的概率，玩家到达的概率)
        (cfr_reach, reach) = (reach_b, reach_a) if state.to_move == A else (reach_a, reach_b)
        for action in state.actions:
            # 计算遗憾值
            
            # r[i][a] = r[i][a] + Pi(对手) * (v[i][a]-v[i])
            # 这个地方遗憾值是从玩家A的视角来计算的，所以通过to_move来进行调整
            action_cfr_regret = state.to_move * cfr_reach * (children_states_utilities[action] - value)

            self._cumulate_cfr_regret(state.inf_set(), action, action_cfr_regret)
            # s[i][a] = s[i][a] + Pi(玩家) * P(a) 
            self._cumulate_sigma(state.inf_set(), action, reach * self.sigma[state.inf_set()][action])

        if self.chance_sampling:
            # 如果选择chance_sampling
            # 我们可以更新sigma策略
            self._update_sigma(state.inf_set())
        return value

    def __value_of_the_game_state_recursive(self, node):
        # 把tree从上到下遍历
        value = 0.
        if node.is_terminal():
            # 找到了终止节点
            # 把比赛结果返回
            return node.evaluation()
        
        # 遍历node的路径
        for action in node.actions:
            # 评估一个节点的价值
            # 查找当前信息集在纳什均衡策略下对应的行动概率
            # 然后用这个概率乘以采取该行动后新游戏状态的价值
            value +=  self.nash_equilibrium[node.inf_set()][action] * self.__value_of_the_game_state_recursive(node.play(action))
        return value

# 纯粹的CFR算法，不进行chance_sampling
class VanillaCFR(CounterfactualRegretMinimizationBase):

    def __init__(self, root):
        super().__init__(root = root, chance_sampling = False)

    def run(self, iterations = 1):
        for _ in range(0, iterations):
            self._cfr_utility_recursive(self.root, 1, 1)

            # 这里需要一个递归的方法来更新sigma策略，因为是便利了所有情况
            self.__update_sigma_recursively(self.root)

    def __update_sigma_recursively(self, node):
        # 到达终止节点结束
        if node.is_terminal():
            return
        # 忽略chance node
        if not node.is_chance():
            self._update_sigma(node.inf_set())
        # 递归player node
        for k in node.children:
            self.__update_sigma_recursively(node.children[k])

class ChanceSamplingCFR(CounterfactualRegretMinimizationBase):

    def __init__(self, root):
        super().__init__(root = root, chance_sampling = True)

    # 选择ChanceSamplingCFR方法
    def run(self, iterations = 1):
        for _ in range(0, iterations):
            self._cfr_utility_recursive(self.root, 1, 1)
