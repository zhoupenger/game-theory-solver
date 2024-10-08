KQ = "KQ"; KJ = "KJ"; QK = "QK"; QJ = "QJ"; JK = "JK"; JQ = "JQ"
# 定义的是发牌的各种可能性
CARDS_DEALINGS = [KQ, KJ, QK, QJ, JK, JQ]

CHANCE = "CHANCE"

CHECK = "CHECK"
CALL = "CALL"
FOLD = "FOLD"
BET = "BET"

ANNOUNCE = "ANNOUNCE"
DUDO = "DUDO"
DUDO_RESULT_MAP = {}
DUDO_RESULT_MAP[0] = [2]
DUDO_RESULT_MAP[1] = [3]
DUDO_RESULT_MAP[2] = [4]
DUDO_RESULT_MAP[3] = [5]
DUDO_RESULT_MAP[4] = [6]
DUDO_RESULT_MAP[5] = [1]
DUDO_RESULT_MAP[6] = [2, 2]
DUDO_RESULT_MAP[7] = [3, 3]
DUDO_RESULT_MAP[8] = [4, 4]
DUDO_RESULT_MAP[9] = [5, 5]
DUDO_RESULT_MAP[10] = [6, 6]
DUDO_RESULT_MAP[11] = [1, 1]

RESULTS_MAP = {}
# 定义的是发牌各种可能性下输赢的结果
RESULTS_MAP[QK] = -1
RESULTS_MAP[JK] = -1
RESULTS_MAP[JQ] = -1
RESULTS_MAP[KQ] = 1
RESULTS_MAP[KJ] = 1
RESULTS_MAP[QJ] = 1

# 定义玩家决策的顺序
A = 1
B = -A
