import pygame
import math
from typing import List, Tuple


class RecursiveBezier:
    """递归构造Bezier曲线（De Casteljau算法）"""

    def __init__(self):
        self.control_points = []  # 原始控制点
        self.current_level = 0  # 当前递归层级
        self.ratio = 0.5  # 定比参数 t (0-1)
        self.recursive_points = []  # 所有递归点 [层级][点索引]
        self.show_construction = True  # 是否显示构造过程
        self.completed = False  # 是否构造完成
        self.final_point = None  # 最终点

        # 用于部分曲线计算的临时状态
        self.partial_curve_cache = {}  # 缓存部分曲线结果
        self.last_partial_t = -1  # 上次计算的部分t值

        # 新增：上一步功能的历史记录
        self.history = []  # 保存每一步的状态，用于支持上一步功能

        # 颜色定义 - 为每个层级定义匹配的颜色
        self.colors = {
            'control_point': (255, 255, 0),  # 黄色：原始控制点
            'control_line': (220, 220, 220, 200),  # 偏白色：控制点连线（带透明度）

            # 第一层递归
            'level1_point': (255, 100, 100),  # 红色：第一层递归点
            'level1_line': (255, 180, 180, 180),  # 浅红色：第一层连线

            # 第二层递归
            'level2_point': (100, 255, 100),  # 绿色：第二层递归点
            'level2_line': (180, 255, 180, 180),  # 浅绿色：第二层连线

            # 第三层递归
            'level3_point': (100, 100, 255),  # 蓝色：第三层递归点
            'level3_line': (180, 180, 255, 180),  # 浅蓝色：第三层连线

            # 第四层及以上递归
            'level4_point': (255, 100, 255),  # 紫色：第四层递归点
            'level4_line': (255, 180, 255, 180),  # 浅紫色：第四层连线

            # 第五层及以上递归
            'level5_point': (100, 255, 255),  # 青色：第五层递归点
            'level5_line': (180, 255, 255, 180),  # 浅青色：第五层连线

            # 最终点
            'final': (255, 255, 255),  # 白色：最终点
            'final_border': (255, 0, 0),  # 红色边框：最终点

            # 比例连线（从上一层到下一层的连线）
            'ratio_line': (255, 200, 100, 120),  # 橙色：比例连线
            'ratio_line_highlight': (255, 220, 120, 180),  # 亮橙色：高亮比例连线

            # 曲线
            'curve': (0, 255, 0)  # 绿色：最终曲线
        }

    def get_level_color(self, level: int, color_type: str = "point"):
        """根据层级获取颜色"""
        if level == 0:
            return self.colors['control_point'] if color_type == "point" else self.colors['control_line']
        elif level == 1:
            return self.colors['level1_point'] if color_type == "point" else self.colors['level1_line']
        elif level == 2:
            return self.colors['level2_point'] if color_type == "point" else self.colors['level2_line']
        elif level == 3:
            return self.colors['level3_point'] if color_type == "point" else self.colors['level3_line']
        elif level == 4:
            return self.colors['level4_point'] if color_type == "point" else self.colors['level4_line']
        else:
            return self.colors['level5_point'] if color_type == "point" else self.colors['level5_line']

    def set_control_points(self, points: List[Tuple[int, int]]):
        """设置控制点"""
        self.control_points = points.copy()
        self.reset()

    def get_ratio_point(self, p1: Tuple[int, int], p2: Tuple[int, int], t: float) -> Tuple[int, int]:
        """计算定比分点"""
        x = int(p1[0] + (p2[0] - p1[0]) * t)
        y = int(p1[1] + (p2[1] - p1[1]) * t)
        return (x, y)

    def next_step(self) -> bool:
        """进行下一步递归构造"""
        if self.completed:
            return False

        if len(self.control_points) < 2:
            return False

        print(f"执行下一步: 当前层级={self.current_level}")

        # 如果还没有开始，初始化第一层
        if len(self.recursive_points) == 0:
            self.recursive_points.append(self.control_points.copy())
            print(f"初始化第一层: {len(self.control_points)}个点")

        current_points = self.recursive_points[self.current_level]
        print(f"当前层点数量: {len(current_points)}")

        # 如果只剩一个点，构造完成
        if len(current_points) == 1:
            self.completed = True
            self.final_point = current_points[0]
            print("构造完成!")
            return True

        # 计算下一层的点
        next_points = []
        for i in range(len(current_points) - 1):
            p1 = current_points[i]
            p2 = current_points[i + 1]
            new_point = self.get_ratio_point(p1, p2, self.ratio)
            next_points.append(new_point)

        # 保存当前状态到历史记录（用于上一步功能）
        self.save_state_to_history()

        self.recursive_points.append(next_points)
        self.current_level += 1

        print(f"创建新层级 {self.current_level}: {len(next_points)}个点")

        # 检查是否完成
        if len(next_points) == 1:
            self.completed = True
            self.final_point = next_points[0]
            print("构造完成! (只剩一个点)")

        return True

    def prev_step(self) -> bool:
        """返回上一步递归构造"""
        # 如果历史记录为空或者已经是最初状态，无法返回上一步
        if not self.history or len(self.recursive_points) <= 1:
            print("已经在最初状态，无法返回上一步")
            return False

        # 从历史记录恢复上一个状态
        prev_state = self.history.pop()

        # 恢复状态
        self.recursive_points = prev_state['recursive_points']
        self.current_level = prev_state['current_level']
        self.completed = prev_state['completed']
        self.final_point = prev_state['final_point']

        # 清除部分曲线缓存
        self.partial_curve_cache.clear()

        print(f"返回上一步: 当前层级={self.current_level}, 剩余层数={len(self.recursive_points)}")

        return True

    def save_state_to_history(self):
        """保存当前状态到历史记录"""
        # 深度复制当前状态
        state = {
            'recursive_points': [layer.copy() for layer in self.recursive_points],
            'current_level': self.current_level,
            'completed': self.completed,
            'final_point': self.final_point.copy() if self.final_point else None
        }
        self.history.append(state)

    def reset(self):
        """重置构造过程"""
        self.current_level = 0
        self.recursive_points.clear()
        self.completed = False
        self.final_point = None
        self.partial_curve_cache.clear()
        self.last_partial_t = -1

        # 清空历史记录
        self.history.clear()

        if len(self.control_points) >= 2:
            self.recursive_points.append(self.control_points.copy())
            print(f"重置: 初始化{len(self.control_points)}个控制点")

    def set_ratio(self, t: float):
        """设置定比参数 t (0-1)"""
        old_ratio = self.ratio
        self.ratio = max(0.0, min(1.0, t))

        # 如果比例改变，需要重新计算所有递归点
        if abs(old_ratio - self.ratio) > 0.001 and len(self.recursive_points) > 0:
            print(f"比例改变: {old_ratio:.2f} -> {self.ratio:.2f}, 重新计算递归点")

            # 清空历史记录，因为比例改变后历史不再有效
            self.history.clear()

            # 重新计算所有递归点
            original_recursive_points = [self.control_points.copy()]
            current_points = self.control_points

            for level in range(1, len(self.recursive_points)):
                next_points = []
                for i in range(len(current_points) - 1):
                    p1 = current_points[i]
                    p2 = current_points[i + 1]
                    new_point = self.get_ratio_point(p1, p2, self.ratio)
                    next_points.append(new_point)

                original_recursive_points.append(next_points.copy())
                current_points = next_points

            self.recursive_points = original_recursive_points
            self.current_level = len(self.recursive_points) - 1

            # 更新完成状态
            if len(self.recursive_points) > 0:
                last_points = self.recursive_points[-1]
                if len(last_points) == 1:
                    self.completed = True
                    self.final_point = last_points[0]
                else:
                    self.completed = False
                    self.final_point = None

    def toggle_construction(self):
        """切换构造过程显示"""
        self.show_construction = not self.show_construction

    def draw(self, surface: pygame.Surface, scale_manager=None):
        """绘制递归构造过程"""
        if len(self.control_points) < 2:
            return

        # 应用缩放函数
        def scale_point(p):
            return scale_manager.apply_scale_to_point(p) if scale_manager else p

        def scale_points(pts):
            return scale_manager.apply_scale_to_points(pts) if scale_manager else pts

        # 绘制原始控制点和连线
        scaled_control_points = scale_points(self.control_points)

        for i in range(len(scaled_control_points) - 1):
            pygame.draw.line(surface, self.colors['control_line'],
                             scaled_control_points[i],
                             scaled_control_points[i + 1], 3)

        for point in scaled_control_points:
            pygame.draw.circle(surface, self.colors['control_point'], point, 8)
            pygame.draw.circle(surface, (0, 0, 0), point, 8, 2)

        # 如果显示构造过程
        if self.show_construction and len(self.recursive_points) > 0:
            # 绘制所有递归层
            for level in range(len(self.recursive_points)):
                points = self.recursive_points[level]

                # 关键修复：对递归点也应用缩放！
                scaled_points = scale_points(points) if scale_manager else points

                # 获取当前层的颜色
                point_color = self.get_level_color(level, "point")
                line_color = self.get_level_color(level, "line")

                # 绘制点和连线
                if level > 0:
                    prev_points = self.recursive_points[level - 1]
                    # 关键修复：对上一层的点也应用缩放！
                    scaled_prev_points = scale_points(prev_points) if scale_manager else prev_points

                    # 绘制上一层到当前层的连线
                    for i in range(len(scaled_prev_points) - 1):
                        p1 = scaled_prev_points[i]
                        p2 = scaled_prev_points[i + 1]
                        # 绘制完整的线段
                        pygame.draw.line(surface, line_color, p1, p2, 2)

                        # 如果当前层有点，绘制比例连线
                        if i < len(scaled_points):
                            current_point = scaled_points[i]
                            # 绘制从p1到当前点的比例部分
                            pygame.draw.line(surface, self.colors['ratio_line_highlight'],
                                             p1, current_point, 2)

                # 绘制当前层的点（使用缩放后的点）
                for point in scaled_points:
                    radius = 7 - level * 0.5  # 层级越高，点越小
                    radius = max(5, radius)  # 最小半径为5
                    pygame.draw.circle(surface, point_color, point, int(radius))
                    pygame.draw.circle(surface, (0, 0, 0), point, int(radius), 1)

        # 绘制最终点（也应用缩放）
        if self.final_point:
            scaled_final_point = scale_point(self.final_point)
            pygame.draw.circle(surface, self.colors['final'], scaled_final_point, 10)
            pygame.draw.circle(surface, self.colors['final_border'], scaled_final_point, 10, 3)

            # 标记最终点
            font = pygame.font.Font(None, 18)
            text = font.render(f"t={self.ratio:.2f}", True, (255, 255, 255))
            text_rect = text.get_rect()
            # 绘制文字背景
            bg_rect = pygame.Rect(
                scaled_final_point[0] + 5,
                scaled_final_point[1] - 15,
                text_rect.width + 6,
                text_rect.height + 4
            )
            pygame.draw.rect(surface, (40, 40, 60, 200), bg_rect, border_radius=3)
            pygame.draw.rect(surface, (100, 100, 120), bg_rect, 1, border_radius=3)
            surface.blit(text, (scaled_final_point[0] + 8, scaled_final_point[1] - 13))

    def get_partial_curve(self, t: float) -> List[Tuple[int, int]]:
        """获取部分Bezier曲线（0到t的部分）"""
        if len(self.control_points) < 2:
            return []

        # 检查缓存
        cache_key = f"{t:.3f}"
        if cache_key in self.partial_curve_cache:
            return self.partial_curve_cache[cache_key]

        # 保存当前状态
        original_ratio = self.ratio
        original_recursive_points = [layer.copy() for layer in self.recursive_points]
        original_current_level = self.current_level
        original_completed = self.completed
        original_final_point = self.final_point

        # 计算部分曲线
        curve_points = []

        # 对于每个t值，单独计算点
        steps = 101
        for i in range(steps):
            current_t = (t * i) / (steps - 1)

            # 使用De Casteljau算法计算当前t对应的点
            points = self.control_points.copy()
            level = 0

            while len(points) > 1:
                next_points = []
                for j in range(len(points) - 1):
                    p1 = points[j]
                    p2 = points[j + 1]
                    new_point = self.get_ratio_point(p1, p2, current_t)
                    next_points.append(new_point)
                points = next_points
                level += 1

            if points:
                curve_points.append(points[0])

        # 恢复原始状态
        self.ratio = original_ratio
        self.recursive_points = original_recursive_points
        self.current_level = original_current_level
        self.completed = original_completed
        self.final_point = original_final_point

        # 缓存结果
        self.partial_curve_cache[cache_key] = curve_points

        return curve_points

    def get_status(self) -> dict:
        """获取当前状态"""
        total_steps = max(0, len(self.control_points) - 1) if self.control_points else 0
        remaining_steps = max(0, total_steps - self.current_level)

        return {
            'control_points': len(self.control_points),
            'current_level': self.current_level,
            'total_levels': total_steps,
            'ratio': self.ratio,
            'completed': self.completed,
            'show_construction': self.show_construction,
            'remaining_steps': remaining_steps,
            'recursive_points_count': sum(len(layer) for layer in self.recursive_points),
            'can_prev_step': len(self.history) > 0  # 新增：是否可以执行上一步
        }