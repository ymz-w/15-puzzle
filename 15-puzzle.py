"""
数字华容道4*4 解法
"""
from random import randint, choice
from time import time
from typing import Tuple

class Puzzle:
    """
    4*4 数字华容道 (15-Puzzle)
    状态用二维列表表示,空格为 0.
    内部 id 由 16 个 4-bit 数字拼接成 64 位整数,用于快速哈希和判等.
    """
    DIRECTIONS = ["U", "D", "L", "R"]
    REVERSE_MAP = {"U": "D", "D": "U", "R": "L", "L": "R"}

    def __init__(self, l: list, if_verify: bool = True, i0: tuple = None, origin: str = "") -> None:
        self.l = self._verify(l) if if_verify else l
        self.i0 = i0 or self._search_for_0(self.l)   # 0 空格坐标 (y, x)
        self.origin = origin                         # 到达该状态的移动序列,如 "UUDL"
        self.id = self._get_id()
    
    def __hash__(self) -> int:
        return self.id

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Puzzle) and other.id == self.id

    def __getitem__(self, index):
        if isinstance(index, tuple) and len(index) == 2:
            return self.l[index[0]][index[1]]
        elif isinstance(index, int):
            return self.l[index]
        raise ValueError("索引格式错误")

    def __setitem__(self, index, value):
        if isinstance(index, tuple) and len(index) == 2 and isinstance(value, int):
            self.l[index[0]][index[1]] = value
        elif isinstance(index, int) and isinstance(value, list):
            self.l[index] = value
        else:
            raise ValueError("索引或值格式错误")

    @staticmethod
    def _verify(l: list):
        if not isinstance(l, list) or len(l) != 4:
            raise ValueError("状态必须是 4x4 的二维列表")
        flat = []
        for i, row in enumerate(l):
            if not isinstance(row, list) or len(row) != 4:
                raise ValueError("状态必须是 4x4 的二维列表")
            flat.extend(row)
        if sorted(flat) != list(range(16)):
            raise ValueError("状态必须包含数字 0~15 各一个")
        return l

    @staticmethod
    def _search_for_0(l: list):
        for y, row in enumerate(l):
            for x, val in enumerate(row):
                if val == 0:
                    return (y, x)

    def copy(self) -> "Puzzle":
        """深拷贝状态,用于生成后继"""
        new_l = [row[:] for row in self.l]
        return Puzzle(l=new_l, if_verify=False, i0=self.i0, origin=self.origin)

    def _get_id(self) -> int:
        """将二维布局编码为一个 64 位整数:每 4 bit 存放一个数字"""
        flat = [num for row in self.l for num in row]
        hex_str = "".join(hex(num)[-1] for num in flat)
        return int(hex_str, 16)

    @classmethod
    def create_by_id(cls, id: int) -> "Puzzle":
        """从整数 id 还原 Puzzle 对象"""
        hex_str = hex(id)[2:].zfill(16)       # 保证 16 位十六进制
        digits = [int(ch, 16) for ch in hex_str]
        l = [digits[i:i+4] for i in range(0, 13, 4)]
        return cls(l, if_verify=False)

    @classmethod
    def create_by_random(cls, resolvable=None) -> "Puzzle":
        """随机生成一个初始状态"""
        one = cls._create_by_random()
        if resolvable is None: return one
        if resolvable ^ one.is_solvable():
            one = one.rotate()
        #while (one.is_solvable() ^ resolvable):
        #    one = cls._create_by_random()
        return one

    @classmethod
    def _create_by_random(cls):
        pool = list(range(16))
        l = [[None] * 4 for _ in range(4)]
        for y in range(4):
            for x in range(4):
                idx = randint(0, len(pool) - 1)
                l[y][x] = pool.pop(idx)
        return cls(l, if_verify=False)

    @classmethod
    def create_by_step_count(cls, step:int, clear_origin:bool=False, resolvable=True) -> "Puzzle":
        """依据步数从终点进行随机生成地图, 但可能因为过于随机 比最简路径大得多"""
        if resolvable is None:
            resolvable = bool(randint(0, 1))
        p = Puzzle([
            [ 1, 2, 3, 4],
            [ 5, 6, 7, 8],
            [ 9,10,11,12],
            [13,14,15, 0]
        ]) if resolvable else Puzzle([
            [4, 8,12, 0],
            [3, 7,11,15],
            [2, 6,10,14],
            [1, 5, 9,13]
        ])
        for _ in range(step):
            p = choice(p.move_for_directions())
        p.origin = "" if clear_origin else p.reverse_origin(p.origin) 
        return p

    def pprint(self):
        print("=" * 12)
        for row in self.l:
            for e in row:
                print(f"{e:02d}", end=" ")
            print()
        print("=" * 12)

    @staticmethod
    def reverse_origin(origin: str) -> str:
        """将移动序列反转(用于双向搜索拼接路径)"""
        return "".join(Puzzle.REVERSE_MAP[d] for d in origin[::-1])

    def search_for(self, element:int) -> Tuple[int, int]:
        for yi, yl in enumerate(self.l):
            for xi, e in enumerate(yl):
                if e==element: return (yi, xi)

    def _move_i0(self, target: tuple):
        """交换空格与目标位置的数字,并更新空格坐标"""
        self[self.i0], self[target] = self[target], self[self.i0]
        self.i0 = target

    def _get_direction_pos(self, direction:str):
        if direction=="U":
            v = self.i0[0] - 1
            return (v, self.i0[1]) if v >= 0 else False
        elif direction== "D":
            v = self.i0[0] + 1
            return (v, self.i0[1]) if v <= 3 else False
        elif direction== "L":
            v = self.i0[1] - 1
            return (self.i0[0], v) if v >= 0 else False
        elif direction== "R":
            v = self.i0[1] + 1
            return (self.i0[0], v) if v <= 3 else False
        else:
            raise ValueError("非法方向")
        
        ''' # python 3.10
        match direction:
            case "U":
                v = self.i0[0] - 1
                return (v, self.i0[1]) if v >= 0 else False
            case "D":
                v = self.i0[0] + 1
                return (v, self.i0[1]) if v <= 3 else False
            case "L":
                v = self.i0[1] - 1
                return (self.i0[0], v) if v >= 0 else False
            case "R":
                v = self.i0[1] + 1
                return (self.i0[0], v) if v <= 3 else False
            case _:
                raise ValueError("非法方向")
        '''

    def _move(self, direction: str) -> "Puzzle":
        """朝指定方向移动,返回新状态(移动失败返回 None)"""
        new = self.copy()
        pos = self._get_direction_pos(direction)
        if pos:
            new._move_i0(pos)
            new.origin += direction
            new.id = new._get_id()          # ★ 移动后必须更新 id
            return new
        return None

    def up(self)    -> "Puzzle": return self._move("U")
    def down(self)  -> "Puzzle": return self._move("D")
    def left(self)  -> "Puzzle": return self._move("L")
    def right(self) -> "Puzzle": return self._move("R")

    def move_for_directions(self, allow_turn_back:bool=False):
        """返回所有合法移动的后继状态列表"""
        result = []
        ds = self.DIRECTIONS
        if allow_turn_back and self.origin:
            ds.remove(self.REVERSE_MAP[self.origin[-1]])
        for d in ds:
            moved = self._move(d)
            if moved:
                result.append(moved)
        return result

    def move_by_path(self, path:str) -> "Puzzle":
        p = self.copy()
        for d in path:
            p = p._move(d)
        return p

    def is_solvable(self) -> bool:
        """
        判断当前状态是否可解(以标准目标状态为基准)
        对于 4x4 棋盘:逆序数 + 空格顶部行号(1~4) 为偶数则可解
        """
        flat = [num for row in self.l for num in row if num != 0]
        inversions = 0
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                if flat[i] > flat[j]:
                    inversions += 1
        row_of_zero = self.i0[0] + 1      # 顶部行号,1~4
        return (inversions + row_of_zero) % 2 == 0

    def rotate(self) -> "Puzzle":
        """顺时针旋转 可以改变可解性"""
        newl = [[self[3-x, y] for x in range(4)] for y in range(4)]
        return Puzzle(newl, False)

class Explorer:
    """
    搜索器:使用 BFS 或双向 BFS 寻找从初始状态到目标状态的最短路径.
    """
    # 两个目标状态:AIM_ID1 为标准答案,AIM_ID0 为不可解类的"伪答案"
    AIM_ID0 = Puzzle([
        [4, 8,12, 0],
        [3, 7,11,15],
        [2, 6,10,14],
        [1, 5, 9,13]
    ]).id

    AIM_ID1 = Puzzle([
        [ 1, 2, 3, 4],
        [ 5, 6, 7, 8],
        [ 9,10,11,12],
        [13,14,15, 0]
    ]).id

    AIM_IDS = [AIM_ID0, AIM_ID1]

    def __init__(self, starting: Puzzle):
        starting.origin = ""
        self.st = starting # 务必copy
    
    #region BFS
    @staticmethod
    def _bar(id_to_path, current) -> str:
        return f"All: {len(id_to_path):>10_d} ; New: {len(current):>5_d}"

    def explore_BFS0(self):
        """单向 BFS(内存不友好,仅用于演示)"""
        id_to_path = {self.st.id: ""}
        current_layer = [self.st.copy()]
        path_to_aim = []

        steps = 0
        while not path_to_aim:
            print(f"{steps:3d} ", self._bar(id_to_path, current_layer))
            steps += 1

            # 生成下一层所有状态(去重)
            next_objs = set()
            for obj in current_layer:
                for succ in obj.move_for_directions():
                    next_objs.add(succ)

            # 检查是否遇到目标,并更新已知路径
            new_id_to_path = {}
            new_layer = []
            for obj in next_objs:
                if obj.id in Explorer.AIM_IDS:
                    path_to_aim.append(obj.origin)

                if obj.id in id_to_path:
                    # 如果找到了更短的到达路径,更新记录并重新扩展该状态
                    if len(obj.origin) < len(id_to_path[obj.id]):
                        id_to_path[obj.id] = obj.origin
                        new_layer.append(obj)
                else:
                    new_id_to_path[obj.id] = obj.origin
                    new_layer.append(obj)

            id_to_path.update(new_id_to_path)
            current_layer = new_layer
            # input("回车继续(:")   # 调试用

        print(path_to_aim)

    def explore_BFS(self):
        """单向 BFS(内存优化版,逐层更新)"""
        id_to_path = {self.st.id: ""}
        new_id_to_path = {self.st.id: ""}

        path_to_aim = []
        steps = 0
        while True:
            print(f"{steps:3d} ", self._bar(id_to_path, new_id_to_path))
            steps += 1

            # 当前层若包含目标,直接结束
            for pid in new_id_to_path:
                if pid in Explorer.AIM_IDS:
                    path_to_aim.append(new_id_to_path[pid])
            if path_to_aim:
                break

            next_id_to_path = {}
            for pid in new_id_to_path:
                p = Puzzle.create_by_id(pid)
                p.origin = new_id_to_path[pid]
                for succ in p.move_for_directions():
                    if succ.id in next_id_to_path:
                        next_id_to_path[succ.id] = min(
                            (succ.origin, next_id_to_path[succ.id]), key=len)
                    else:
                        next_id_to_path[succ.id] = succ.origin

            # 将新发现的节点合并到全局记录,并准备下一层
            new_id_to_path.clear()
            for nid, path in next_id_to_path.items():
                if nid in id_to_path:
                    id_to_path[nid] = min((path, id_to_path[nid]), key=len)
                else:
                    id_to_path[nid] = path
                    new_id_to_path[nid] = path

        print(path_to_aim)

    def explore_BFS2(self):
        """双向 BFS(内存优化版),找到所有最短路径"""
        aim_id = self.AIM_IDS[self.st.is_solvable()]

        forward_visited = {self.st.id: ""}
        forward_layer = {self.st.id: ""}
        backward_visited = {aim_id: ""}
        backward_layer = {aim_id: ""}

        path_to_aim = []
        steps = 0
        while True:
            print(f"{steps:3d} F: {self._bar(forward_visited, forward_layer)} ; "
                f"B: {self._bar(backward_visited, backward_layer)}")
            steps += 1

            common = set(forward_visited.keys()) & set(backward_visited.keys())
            if common:
                # 收集所有相遇点的拼接路径
                all_paths = []
                for cid in common:
                    path = forward_visited[cid] + Puzzle.reverse_origin(backward_visited[cid])
                    all_paths.append(path)

                # 保留所有长度最短的路径(理论上此时都相等,但保留保险逻辑)
                if all_paths:
                    min_len = min(len(p) for p in all_paths)
                    path_to_aim = [p for p in all_paths if len(p) == min_len]
                    break

            # 生成下一层前向
            next_forward = {}
            for pid in forward_layer:
                p = Puzzle.create_by_id(pid)
                p.origin = forward_layer[pid]
                for succ in p.move_for_directions():
                    if succ.id in next_forward:
                        next_forward[succ.id] = min((succ.origin, next_forward[succ.id]), key=len)
                    else:
                        next_forward[succ.id] = succ.origin

            # 生成下一层后向
            next_backward = {}
            for pid in backward_layer:
                p = Puzzle.create_by_id(pid)
                p.origin = backward_layer[pid]
                for succ in p.move_for_directions():
                    if succ.id in next_backward:
                        next_backward[succ.id] = min((succ.origin, next_backward[succ.id]), key=len)
                    else:
                        next_backward[succ.id] = succ.origin

            forward_layer.clear()
            for nid, path in next_forward.items():
                if nid in forward_visited:
                    forward_visited[nid] = min((path, forward_visited[nid]), key=len)
                else:
                    forward_visited[nid] = path
                    forward_layer[nid] = path

            backward_layer.clear()
            for nid, path in next_backward.items():
                if nid in backward_visited:
                    backward_visited[nid] = min((path, backward_visited[nid]), key=len)
                else:
                    backward_visited[nid] = path
                    backward_layer[nid] = path

        # 输出所有最短路径
        print(f"找到 {len(path_to_aim)} 个最短解,长度 {len(path_to_aim[0])}:")
        for i, p in enumerate(path_to_aim):
            print(f"  [{i}] {p}")
        return path_to_aim

    #endregion

    #region A*
    @staticmethod
    def _get_target_pos(p: Puzzle):
        l = p.l
        target_pos = {}
        for yi, yl in enumerate(l):
            for xi, e in enumerate(yl):
                target_pos[e] = (yi, xi)
        return target_pos

    @staticmethod
    def _swap_4bits(state: int, p1: int, p2: int) -> int:
        """交换 64 位 state 中两个 4-bit 块 (p1,p2 为 0~15 的位置索引)"""
        if p1 == p2:
            return state
        shift1 = (15 - p1) * 4
        shift2 = (15 - p2) * 4
        val1 = (state >> shift1) & 0xF
        val2 = (state >> shift2) & 0xF
        # 清除两位
        state &= ~((0xF << shift1) | (0xF << shift2))
        # 放入交换后的值
        state |= (val1 << shift2) | (val2 << shift1)
        return state

    @staticmethod
    def _get_successors(state: int, blank_yx: tuple):
        """输入当前状态整数和空格坐标 (y,x),返回可达的 (新状态, 新空格坐标, 方向字符) 列表"""
        y, x = blank_yx
        successors = []
        if y > 0:   # UP
            ny, nx = y-1, x
            new_state = Explorer._swap_4bits(state, y*4 + x, ny*4 + nx)
            successors.append((new_state, (ny, nx), 'U'))
        if y < 3:   # DOWN
            ny, nx = y+1, x
            new_state = Explorer._swap_4bits(state, y*4 + x, ny*4 + nx)
            successors.append((new_state, (ny, nx), 'D'))
        if x > 0:   # LEFT
            ny, nx = y, x-1
            new_state = Explorer._swap_4bits(state, y*4 + x, ny*4 + nx)
            successors.append((new_state, (ny, nx), 'L'))
        if x < 3:   # RIGHT
            ny, nx = y, x+1
            new_state = Explorer._swap_4bits(state, y*4 + x, ny*4 + nx)
            successors.append((new_state, (ny, nx), 'R'))
        return successors

    @staticmethod
    def _heuristic(state: int, target_pos: dict) -> int:
        """计算曼哈顿距离 + 线性冲突的启发式值(目标位置由 target_pos 给出)。
        如果 target_pos 缺少某些数字，则这些数字不计入距离和冲突。
        """
        # 1. 解析当前每个数字的位置
        pos = {}  # digit -> (row, col)
        for i in range(16):
            shift = (15 - i) * 4
            digit = (state >> shift) & 0xF
            if digit != 0:
                pos[digit] = (i // 4, i % 4)

        # 2. 曼哈顿距离（仅计算有目标位置的数字）
        manhattan = 0
        for digit, (cr, cc) in pos.items():
            if digit in target_pos:
                tr, tc = target_pos[digit]
                manhattan += abs(cr - tr) + abs(cc - tc)
            # else 忽略

        # 3. 线性冲突（只考虑有目标位置的数字）
        conflict = 0
        # 行冲突
        for row in range(4):
            tiles = []
            for digit, (cr, cc) in pos.items():
                if digit in target_pos:      # 新增保护，防止 KeyError
                    tr, tc = target_pos[digit]
                    if tr == row and cr == row:
                        tiles.append((cc, tc, digit))
            tiles.sort()
            for i in range(len(tiles)):
                for j in range(i + 1, len(tiles)):
                    if tiles[i][1] > tiles[j][1]:   # 目标列顺序冲突
                        conflict += 1
        # 列冲突
        for col in range(4):
            tiles = []
            for digit, (cr, cc) in pos.items():
                if digit in target_pos:      # 新增保护
                    tr, tc = target_pos[digit]
                    if tc == col and cc == col:
                        tiles.append((cr, tr, digit))
            tiles.sort()
            for i in range(len(tiles)):
                for j in range(i + 1, len(tiles)):
                    if tiles[i][1] > tiles[j][1]:   # 目标行顺序冲突
                        conflict += 1

        return manhattan + 2 * conflict

    @staticmethod
    def _ida_search(state: int, blank: tuple, g: int, bound: int,
                    path: list, target: int, target_pos: dict,
                    is_partial: bool = False) -> Tuple[bool, int]:
        f = g + Explorer._heuristic(state, target_pos)
        if f > bound:
            return False, f

        # 终止条件：完整目标 或 部分目标
        if is_partial:
            # 检查 target_pos 中所有数字是否都在目标位置
            if Explorer._is_partial_goal(state, target_pos):
                return True, 0
        else:
            if state == target:
                return True, 0

        min_exceed = float('inf')
        last_move = path[-1] if path else ''
        reverse = {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}
        for new_state, new_blank, move in Explorer._get_successors(state, blank):
            if move == reverse.get(last_move, ''):
                continue
            path.append(move)
            found, res = Explorer._ida_search(new_state, new_blank, g + 1, bound,
                                            path, target, target_pos, is_partial)
            if found:
                return True, 0
            if res < min_exceed:
                min_exceed = res
            path.pop()
        return False, min_exceed

    @staticmethod
    def _is_partial_goal(state: int, target_pos: dict) -> bool:
        """检查 state 中 target_pos 指定的所有数字是否都在目标位置"""
        for digit, (tr, tc) in target_pos.items():
            idx = tr * 4 + tc
            shift = (15 - idx) * 4
            if ((state >> shift) & 0xF) != digit:
                return False
        return True

    @classmethod
    def _explore_ida_star_with_target_pos(cls, st: Puzzle, target_pos: dict,
                                        should_print: bool = False):
        """IDA* 求解部分目标位置（如只要求1,2,3复位）"""
        start_id = st.id
        start_blank = st.i0
        bound = cls._heuristic(start_id, target_pos)
        path = []

        if should_print:
            print("开始 IDA* 搜索（部分目标）...")
        while True:
            if should_print:
                print(f"当前阈值: {bound}")
            found, res = cls._ida_search(start_id, start_blank, 0, bound,
                                        path, None, target_pos, is_partial=True)
            if found:
                break
            if res == float('inf'):
                if should_print:
                    print("无解!")
                return None
            bound = res

        solution = "".join(path)
        if should_print:
            print(f"求解成功!步数: {len(solution)}, 路径: {solution}")
        return solution

    def explore_ida_star(self):
        """IDA* 直接解"""
        return self._explore_ida_star(
                self.st.copy(),
                Puzzle.create_by_id(self.AIM_IDS[self.st.is_solvable()]),
                True
            )
    
    @classmethod
    def _explore_ida_star(cls, st:Puzzle, ed:Puzzle, should_print:bool=False):
        """IDA* 搜索(曼哈顿+线性冲突),平衡简单与效率; 起始到目标"""
        aim_id = ed.id
        target_pos = cls._get_target_pos(ed)

        start_id = st.id
        start_blank = st.i0

        # 初始阈值
        bound = cls._heuristic(start_id, target_pos)
        path = []   # 当前移动路径

        should_print and print("开始 IDA* 搜索...")
        while True:
            should_print and print(f"当前阈值: {bound}")
            found, res = cls._ida_search(start_id, start_blank, 0, bound,
                                          path, aim_id, target_pos)
            if found:
                break
            if res == float('inf'):
                should_print and print("无解!")
                return None
            bound = res   # 增加阈值继续

        solution = "".join(path)
        should_print and print(f"求解成功!步数: {len(solution)}, 路径: {solution}")
        return solution


    #endregion

    #region 硬编码 NOTE：不可取，十分难设计！
    def explore_HC(self):
        """硬编码寻路"""
        st = self.st
        
    
    @staticmethod
    def _move_by_hard_code(p:Puzzle, line:int):
        if line < 2:
            p = Puzzle._move_by_hard_code1_0(p, 1)
            p = Puzzle._move_by_hard_code1_0(p, 2)

    @staticmethod
    def _move_by_hard_code0_0(p:Puzzle, d0_pos:Tuple[int, int]):
        if d0_pos[0] >= 0:
            for _ in range(d0_pos[0]):  p = p._move("U")
        else:
            for _ in range(-d0_pos[0]): p = p._move("D")
        if d0_pos[1] >= 0:
            for _ in range(d0_pos[1]):  p = p._move("L")
        else:
            for _ in range(-d0_pos[1]): p = p._move("R")
        if not p: raise # 不应该的错误?
        return p

    @classmethod
    def _move_by_hard_code0_1(cls, p:Puzzle, e_pos:int, de_pos:Tuple[int, int]):
        if sum(abs(x) for x in de_pos)!=1: raise ValueError("不允许一次移动多步或不移动")
        oneaim_pos = (e_pos[0]-de_pos[0], e_pos[1]-de_pos[1])
        d0_pos = (p.i0[0]-oneaim_pos[0], p.i0[1]-oneaim_pos[1])
        return cls._move_by_hard_code0_0(p, d0_pos), oneaim_pos

    @classmethod
    def _move_by_hard_code1_0(cls, p:Puzzle, element:int):
        aim_pos = ((element-1)//4, element%4-1)
        e_pos = p.search_for(element+1)
        d_pos = (e_pos[0]-aim_pos[0], e_pos[1]-aim_pos[1])
        i = 1 if d_pos[0]>=0 else -1
        for _ in range(abs(d_pos[0])):
            p, e_pos = cls._move_by_hard_code0_1(p, e_pos, (i, 0))
        i = 1 if d_pos[1]>=0 else -1
        for _ in range(abs(d_pos[1])):
            p, e_pos = cls._move_by_hard_code0_1(p, e_pos, (0, i))
        return p

    @staticmethod
    def _move_by_hard_code1_1(p:Puzzle, line:int):
        ...

    @staticmethod
    def _move_by_hard_code1():
        ...


    #endregion
    
    @classmethod
    def explore_ida_star_to_samplify(cls, p:Puzzle, path:str):
        # A*剪枝, 魔法数字多 
        pp = p.copy()
        dnum = 0
        dx = 5
        length = 25
        n = 0
        print("A*剪枝")
        while dnum<5:
            n += 1
            print(f"\n{n}轮")
            
            pp = p.copy()
            plist = [(pp:=pp.move_by_path(path[:dx])).copy()] if dx!=0 else []
            ll = [dx] if dx!=0 else []

            for i in range(dx, len(path), length):
                plist.append(
                        (pp:=pp.move_by_path(path[i:i+length])).copy()
                    )
                ll.append(len(path[i:i+length]))

            if path[i+length:]:
                plist.append(pp.move_by_path(path[i+length:]))
                ll.append(len(path[i:i+length]))

            pst = p.copy()
            newpath = []
            with Timer(f"{n}轮"):
                for i, ped in enumerate(plist):
                    with Timer(f"  {i+1} {ll[i]}"):
                        newpath.append(cls._explore_ida_star(pst, ped))
                        pst = ped
            newpath = "".join(newpath)
            dlen = len(path) - len(newpath)
            print(-dlen, len(newpath), newpath)
            path = newpath
            dx = (dx+3) % length
            if dlen==0:
                dnum += 1
                length += 8
                length = min(length, int(len(path)/1.8))
                dx = (dx+3) % length
            else:
                dnum = max(0, dnum-1)
                length = max(10, length-3)
                dx = dx % length

        return path

    def explore_broad_ida_star(self):
        print("泛A*")
        paths = []
        p = self.st.copy()
        tp = {1:(0,0)}
        with Timer("1"):
            paths.append(self._explore_ida_star_with_target_pos(p, tp))
            p = p.move_by_path(paths[-1])
        
        tp[2] = (0,1)
        with Timer("2"):
            paths.append(self._explore_ida_star_with_target_pos(p, tp))
            p = p.move_by_path(paths[-1])

        tp[3] = (0,2)
        tp[4] = (0,3)
        with Timer("3 4"):
            paths.append(self._explore_ida_star_with_target_pos(p, tp))
            p = p.move_by_path(paths[-1])    

        tp[5] = (1,0)
        tp[6] = (1,1)
        with Timer("5 6"):
            paths.append(self._explore_ida_star_with_target_pos(p, tp))
            p = p.move_by_path(paths[-1])
        
        tp[7] = (1,2)
        tp[8] = (1,3)
        with Timer("7 8"):
            paths.append(self._explore_ida_star_with_target_pos(p, tp))
            p = p.move_by_path(paths[-1])
        
        tp[9] = (3,0)
        tp[10] = (2,0)
        with Timer("9 10"):
            paths.append(self._explore_ida_star_with_target_pos(p, tp))
            p = p.move_by_path(paths[-1])
        
        tp[9] = (2,0)
        tp[10] = (2,1)
        tp[11] = (2,2)
        tp[12] = (2,3)
        tp[13] = (3,0)
        tp[14] = (3,1)
        tp[15] = (3,2)
        with Timer("..."):
            paths.append(self._explore_ida_star_with_target_pos(p, tp))
            p = p.move_by_path(paths[-1])
        path = "".join(paths)
        #p.pprint()
        #print(len(path), path)

        return path

    #region 存表 NOTE: 未来考虑
    @classmethod
    def _generate_broad_ida_star_table(cls): # 生成泛A*表格
        # NOTE: 短时间完不成
        ...

    #endregion

    def explore_HP(self):
        """分层寻路HierarchicalPathfinding, 泛A*+剪枝A*"""

        with Timer("泛A*"):
            path = self.explore_broad_ida_star()
        print(len(path), path)
        with Timer("剪枝A*"):
            path = e.explore_ida_star_to_samplify(e.st, path)
        print(len(path), path)

        return path


class Timer:
    def __init__(self, taskname:str|None=""):
        self.taskname = taskname
        if taskname:
            self.taskname += " "

    def __enter__(self):
        self.start = time()
        self.end: float
        self.time: float = None

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time()
        self.time = self.end - self.start
        if self.taskname is not None:
            print(f"{self.taskname}共用时 {self.time:.2f}s")
        
        return False  # 不抑制异常


if __name__ == "__main__":
    # 示例:一个可解的初始状态

    Puzzle([ 
        [ 2, 0, 9,14],
        [13, 5, 4, 7],
        [11,10,12, 6],
        [ 1, 3,15, 8]
    ]) # 712.91s 51 DDDLUURRURDDDLUUULDDDLURRUULDLDRRDLUURRULLLDRRRDLDR

    k = Puzzle([ 
        [ 2, 0, 9,14],
        [13, 5, 4, 7],
        [11,10,12, 6],
        [ 1, 3,15, 8]
    ])
    
    #k = Puzzle.create_by_random(True)
    print(k.id)
    k.pprint()
    #print(k.search_for(5))
    #print("可解性:", k.is_solvable())
    e = Explorer(k)
    
    with Timer("HP"):
        path = e.explore_HP()

    print(k.id, len(path), path)

    while 1:
        input() # 避免直接打开导致程序关闭
