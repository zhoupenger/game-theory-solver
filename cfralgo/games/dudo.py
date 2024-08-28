from common.constants import ANNOUNCE, DUDO, CHANCE, A, B, DUDO_RESULT_MAP
import random
import itertools

# 父类GameStateBase，定义了游戏状态的基本属性（这个状态包括chance node和player node）
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
class DudoRootChanceGameState(GameStateBase):

    # chance节点的acions其实就是扔色子，可以指定一个色子数量进行博弈(玩家1有6个, 玩家2有5个)
    def __init__(self, actions):
        
        # 把[num1, num2]作为actions传入就行
        actions = self.__roll_dice_combinations(actions)

        # chance节点当前不需要玩家做决策，所以to_move定义为CHANCE
        super().__init__(parent = None, to_move = CHANCE, actions = actions)
        
        # children为一个字典，key为actions(也就是双方的牌型），value为下一级玩家节点的实例
        # 当前节点self作为parent，to_move指向玩家A，dices传入action_hisotry作为该节点两个玩家的色子结果，合法行动为[BET, CHECK]
        self.children = {
            dices: DudoPlayerMoveGameState(
                self, A, [],  dices, [0]
            ) for dices in self.actions
        }

        # 每个节点的概率
        self._chance_prob = 1. / len(self.children)
    
    def __roll_dice_combinations(self, dice_num):
        # 生成玩家1的所有骰子可能结果
        player1_dice_outcomes = list(itertools.product(range(1, 7), repeat=dice_num[0]))
        # 生成玩家2的所有骰子可能结果
        player2_dice_outcomes = list(itertools.product(range(1, 7), repeat=dice_num[1]))
    
        # 生成玩家1和玩家2骰子的所有组合
        all_combinations = list(itertools.product(player1_dice_outcomes, player2_dice_outcomes))
    
        # 转换组合格式，方便区分玩家1和玩家2的骰子
        formatted_combinations = [
            (("player1", player1_dice), ("player2", player2_dice)) 
            for player1_dice, player2_dice in all_combinations
        ]
    
        return formatted_combinations

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
class DudoPlayerMoveGameState(GameStateBase):

    def __init__(self, parent, to_move, actions_history, dices, actions):
        # 传入parent节点，to_move，actions_history，cards，actions
        super().__init__(parent = parent, to_move = to_move, actions = actions)

        self.actions_history = actions_history
        self.dices = dices
        # 把下一级的节点通过self.children加进来
        # A玩家的下一级节点，to_move指向B玩家，actions_history需要加上当前动作，
        # 下一级节点的合法行动为__get_actions_in_next_round（例如玩家A假如BET时，下一级节点的合法行动为[CALL, FOLD]）
        self.children = {
            a : DudoPlayerMoveGameState(
                self,
                -to_move,
                self.actions_history + [str(a)],
                dices,
                self.__get_actions_in_next_round(a)
            ) for a in self.actions
        }

        # 自己的牌
        public_dices = self.dices[0][1] if self.to_move == A else self.dices[1][1]
        self._information_set = ".{0}.{1}".format(public_dices, ".".join(self.actions_history))

    def __get_actions_in_next_round(self, a):
        # 返回大于行动强度a小于12的合法行动
        action = []

        if a == DUDO:
            return []
        else:
            for i in range(a+1, 12):
                action.append(i)
            action.append(DUDO)
        
        return action

    def inf_set(self):
        # 输出信息集
        return self._information_set

    def is_terminal(self):
        # 是否为终止节点- terminal node
        return self.actions == []

    def evaluation(self):
        return 0
    
    def evaluation(self):
        # 如果还没到终止节点，则无法进行评估
        # 到达终止节点，根据历史动作可以对最终结果进行评估
        if self.is_terminal() == False:
            raise RuntimeError("trying to evaluate non-terminal node")
        
        player1_dice_list = []
        player2_dice_list = []
        player1_dice_list.append(self.dices[0][1][0])
        player2_dice_list.append(self.dices[1][1][0])
        
        #player1_dices = self.dices[0][1][0] # 比如说5
        #player2_dices = self.dices[1][1][0]

        level = int(self.actions_history[-2])

        dudo_list = DUDO_RESULT_MAP[level] # [2]
        declared_dice_value = dudo_list[0] # 数字2
        declared_dice_count = len(dudo_list) # 数字1，代表1个2

        actual_dice_count = player1_dice_list.count(declared_dice_value) + player2_dice_list.count(declared_dice_value)

        # 根据实际数量判定是否dudo成功：实际数量小于声明数量，则dudo成功，否则失败
        if actual_dice_count < declared_dice_count:
            return 1
        else:
            return -1