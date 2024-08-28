from common.constants import CHECK, BET, CALL, FOLD, A, CHANCE, RESULTS_MAP
import random

# 父类GameStateBase，定义了游戏状态的基本属性（这个状态包括chance node和player node）
class GameStateBase:

    def __init__(self, parent, to_move, actions):
        # 无论是什么节点，都包含parent父节点，to_move当前玩家，actions合规动作集这几个基本属性
        # 其实每一个node都有children子节点，但是这部分需要单独实现
        # 一个节点的children应该是一个字典，key为动作，value为下一个节点的实例
        self.parent = parent
        self.to_move = to_move
        self.actions = actions

    # 每个节点都可以通过合法动作到子节点
    def play(self, action):
        # 执行一个动作action，返回这个动作指向的下一个节点实例
        return self.children[action]
    
    # 判断当前节点是否为chance节点
    def is_chance(self):
        return self.to_move == CHANCE

    def inf_set(self):
        # inforamtion set
        raise NotImplementedError("Please implement information_set method")

# 定义游戏的chance节点
# chance节点和玩家节点都是继承自GameStateBase方法
class KuhnRootChanceGameState(GameStateBase):

    # chance节点的acions其实就是发牌(例如KQ, KJ等等)
    def __init__(self, actions):
        # chance节点当前不需要玩家做决策，所以to_move定义为CHANCE
        super().__init__(parent = None, to_move = CHANCE, actions = actions)
        
        # children为一个字典，key为actions(也就是双方的牌型），value为下一级玩家节点的实例
        # 当前节点self作为parent，to_move指向玩家A，cards传入action_hisotry作为该节点两个玩家的牌型，合法行动为[BET, CHECK]
        self.children = {
            cards: KuhnPlayerMoveGameState(
                self, A, [],  cards, [BET, CHECK]
            ) for cards in self.actions
        }

        # 每个节点的概率
        self._chance_prob = 1. / len(self.children)

    def is_terminal(self):
        return False

    def inf_set(self):
        # chance节点为根节点
        return "."

    def chance_prob(self):
        return self._chance_prob

    def sample_one(self):
        # 随机挑选一个玩家节点
        return random.choice(list(self.children.values()))

# 定义玩家节点
class KuhnPlayerMoveGameState(GameStateBase):

    def __init__(self, parent, to_move, actions_history, cards, actions):
        # 传入parent节点，to_move，actions_history，cards，actions
        super().__init__(parent = parent, to_move = to_move, actions = actions)

        self.actions_history = actions_history
        self.cards = cards
        # 把下一级的节点通过self.children加进来
        # A玩家的下一级节点，to_move指向B玩家，actions_history需要加上当前动作，
        # 下一级节点的合法行动为__get_actions_in_next_round（例如玩家A假如BET时，下一级节点的合法行动为[CALL, FOLD]）
        self.children = {
            a : KuhnPlayerMoveGameState(
                self,
                -to_move,
                self.actions_history + [a],
                cards,
                self.__get_actions_in_next_round(a)
            ) for a in self.actions
        }

        # 自己的牌
        public_card = self.cards[0] if self.to_move == A else self.cards[1]
        self._information_set = ".{0}.{1}".format(public_card, ".".join(self.actions_history))

    # 这里同时限制无限递归
    def __get_actions_in_next_round(self, a):
        if len(self.actions_history) == 0 and a == BET:
            return [FOLD, CALL]
        elif len(self.actions_history) == 0 and a == CHECK:
            return [BET, CHECK]
        elif self.actions_history[-1] == CHECK and a == BET:
            return [CALL, FOLD]
        elif a == CALL or a == FOLD or (self.actions_history[-1] == CHECK and a == CHECK):
            return []

    def inf_set(self):
        # 输出信息集
        return self._information_set

    def is_terminal(self):
        # 是否为终止节点- terminal node
        return self.actions == []

    def evaluation(self):
        # 如果还没到终止节点，则无法进行评估
        # 到达终止节点，根据历史动作可以对最终结果进行评估
        if self.is_terminal() == False:
            raise RuntimeError("trying to evaluate non-terminal node")

        # 两个check则show down
        if self.actions_history[-1] == CHECK and self.actions_history[-2] == CHECK:
            # 只有一个ante
            return RESULTS_MAP[self.cards] * 1 # only ante is won/lost

        if self.actions_history[-2] == BET and self.actions_history[-1] == CALL:
            # 牌面会有两个ante
            return RESULTS_MAP[self.cards] * 2

        if self.actions_history[-2] == BET and self.actions_history[-1] == FOLD:
            # 牌面只有一个ante
            return self.to_move * 1
