import numpy as np
from regretmatching.model import RegretMatchingDecisionMaker, Expert

def generate_combinations(S, N):
    # 对于N个战场，S个士兵，返回所有可能的分配方案。（包括0的情况）
    if N == 1:
        return [[S]]
    else:
        combinations = []
        for i in range(S+1):
            for rest in generate_combinations(S-i, N-1):
                combinations.append([i] + rest)
        return combinations

# 这里的expert代表的是战场分配方案
# 因此在继承Expert的方法的同时，还需要实现方案的表示
class BattleFieldExpert(Expert):
    def __init__(self, id, distribution):
        super().__init__(id)
        # 每个BattleFieldExpert都有一个特定的士兵分配方式
        self.distribution = distribution
    

class ColonelBlottoPlayer(RegretMatchingDecisionMaker):
    def __init__(self, S, N):
        # 首先要获取可能的分配方案
        all_possible_distributions = generate_combinations(S, N)
        # 然后将这些方案转换成BattleFieldExpert对象
        all_experts = [BattleFieldExpert(i, dist) for i, dist in enumerate(all_possible_distributions)]
        
        # 把构造的experts方法列表传入父类的构造函数
        super(ColonelBlottoPlayer, self).__init__(all_experts)

        # p是一个tuple，表示每个expert/action的概率
        # (action_p1, action_p2, ..., action_pN)
        self.sum_p = np.zeros(len(self.experts))
        self.games_played = 0

        # 战场数量
        self.N = N
    
    def move(self):
        # 返回行动
        return self.decision()

    def learn_from(self, opponent_distribution):
        # 计算payoff matrix
        # 如果多个战场胜利奖励为1，平局为0，失败为-1
        rewards_vector = self.calculate_rewords_vector(opponent_distribution)
        self.update_rule(rewards_vector)
        self.games_played += 1
        self.sum_p += self.p

    def calculate_rewords_vector(self, opponent_distribution):
        # 对手也是根据experts列表来选择行动
        rewards_vector = np.zeros(len(self.experts))

        # 遍历自己的experts列表，计算与opponent_distribution对应的奖励
        for i, expert in enumerate(self.experts):
            # 先循环每一个方案
            # 再循环每一个方案里的每一个战场
            # 如果说战场胜利的总数比对手多，则奖励1，平局为0，失败为-1
            win_count = sum(1 for j in range(self.N) if expert.distribution[j] > opponent_distribution.distribution[j])
            lost_count = sum(1 for j in range(self.N) if expert.distribution[j] < opponent_distribution.distribution[j])

            # 计算奖励
            if win_count > lost_count:
                rewards_vector[i] = 1
            elif win_count == lost_count:
                rewards_vector[i] = 0
            else:
                rewards_vector[i] = -1

        return rewards_vector

    def current_best_response(self):
        # 返回的是当前最优的分配方案而不仅仅是一个概率
        return np.round(self.sum_p / self.games_played, 4)
        #best_response_index = np.argmax(self.sum_p / self.games_played)
        #return self.experts[best_response_index].distribution

    def eps(self):
        return np.max(self.regrets / self.games_played)