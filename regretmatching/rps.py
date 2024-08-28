from regretmatching.model import RegretMatchingDecisionMaker, Expert
import numpy as np

ROCK = Expert('rock')
PAPER = Expert('paper')
SCISSORS = Expert('scissors')

RPS_EXPERTS = [ROCK, PAPER, SCISSORS]

# 这个可以理解为payoff matrix
RPS_REWARD_VECTORS = {
    ROCK:     np.asarray([0, 1, -1]),  # opponent playing ROCK
    PAPER:    np.asarray([-1, 0, 1]),  # opponent playing PAPER
    SCISSORS: np.asarray([1, -1, 0]),  # opponent playing PAPER
}

# 把RPSPlayer继承自RegretMatchingDecisionMaker这个方法
class RPSPlayer(RegretMatchingDecisionMaker):
    def __init__(self):
        # 用父类的方法快速初始化
        super(RPSPlayer, self).__init__(RPS_EXPERTS)

        # 初始化3个为0的数组，用于跟踪未来概率的累加
        self.sum_p = np.full(3, 0.)
        self.games_played = 0

    def move(self):
        # 以均匀的概率分布选择动作
        # 这是在模拟一个完全随机的对手
        return self.decision()

    def learn_from(self, opponent_move):
        # 跟踪对手的动作 - opponent_move
        reward_vector = RPS_REWARD_VECTORS[opponent_move]
        self.update_rule(reward_vector)
        self.games_played += 1
        self.sum_p += self.p

    def current_best_response(self):
        return np.round(self.sum_p / self.games_played, 4)

    def eps(self):
        # eps用来衡量收敛程度
        # eps越低，游戏越接近最优策略
        return np.max(self.regrets / self.games_played)