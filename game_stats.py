import json
import os
class GameStats:
    """跟踪游戏的统计信息"""

    def __init__(self,ai_game):
        """初始化统计信息"""
        self.settings=ai_game.settings
        self.reset_stats()
        self.load_high_score()

    def reset_stats(self):
        """初始化在游戏运行期间可能变化的统计信息"""
        self.ships_left=self.settings.ship_limit
        self.score=0
        self.level=1
    
    def load_high_score(self):
        """从文件加载历史最高分"""
        # 检查是否存在保存文件
        if os.path.exists("high_score.json"):
            try:
                with open("high_score.json", "r") as f:
                    self.high_score = json.load(f)  # 直接读取保存的数值
            except (json.JSONDecodeError, FileNotFoundError):
                # 如果文件损坏或不存在，使用默认值0
                self.high_score = 0
        else:
            self.high_score = 0

    def save_high_score(self):
        """将当前最高分保存到 JSON 文件"""
        filename = "high_score.json"
        with open(filename, 'w') as f:
            json.dump(self.high_score, f)  # 将数值写入文件