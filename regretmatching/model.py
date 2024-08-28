import numpy as np

class Expert:
    def __init__(self, id):
        self.id = id


class RegretMatchingDecisionMaker:

    def __init__(self, experts):
        self.n = len(experts)
        # experts列表
        # experts可以理解为动作集
        self.experts = experts
        # 玩家积累的期望值（行动概率或者叫策略与payoff matrix的点积）        
        self.expected_reward = 0.
        # 动作expert期望的累加 - (xx, xx, xx, xx)
        self.experts_rewards = np.zeros(self.n)
        # regrets为每一个动作的期望-实际期望的差值
        self.regrets = np.zeros(self.n)
        # 生成均匀的概率分布，这个概率分布会在之后进行更新
        self.p = np.full(self.n, 1. / self.n)

    def decision(self):
        # 从experts列表中随机选择一个动作
        # experts列表中的动作的概率分布由self.p决定
        expert = np.random.choice(self.experts, 1,  p=self.p)
        return expert[0]

    def update_rule(self, rewards_vector):
        # 在知道对手的动作后，我们需要获取我们面临这个动作时的payoff matrix

        # self.p 是我们当前的策略，它描述了我们选择每个行动的概率
        # rewards_vector是对于每个可能的行动，我们期望得到的奖励或者支付
        # 通过计算这两者的点积，得到的结果即为我们预期的奖励
        self.expected_reward += np.dot(self.p, rewards_vector)

        # 每个动作的期望进行累加更新
        self.experts_rewards += rewards_vector

        # regret = u(s_i',s_{-i})-u(a)，每个动作的效用-执行动作的效用
        # 完全执行一个expert，我们获得的奖励与我们实际获得的奖励之间的差值
        self.regrets = self.experts_rewards - self.expected_reward
        self._update_p()

    def _update_p(self):
        # 基于当前的遗憾来更新策略向量 self.p

        # 计算regrets总和
        sum_w = np.sum([self._w(i) for i in np.arange(self.n)])

        if sum_w <= 0:
            # 均匀分布
            self.p = np.full(self.n, 1. / self.n)
        else:
            # 每个expert新的概率值为其遗憾值与所有专家遗憾总和的比例
            self.p = np.asarray(
                [self._w(i) / sum_w for i in np.arange(self.n)]
            )

    def _w(self, i):
        # 返回第i个expert的regret值（必须是大于0的）
        return max(0, self.regrets[i])