import pygame
import math
from typing import List, Tuple


class BezierCurve:
    def __init__(self):
        self.control_points = []  # 控制点列表
        self.curve_points = []  # 曲线上的点
        self.selected_point = -1  # 当前选中的控制点索引
        self.dragging = False  # 是否正在拖动

    def add_control_point(self, point: Tuple[int, int]) -> None:
        """添加控制点"""
        self.control_points.append(point)
        self.update_curve()

    def remove_last_control_point(self) -> None:
        """删除最后一个控制点"""
        if self.control_points:
            self.control_points.pop()
            self.update_curve()

    def clear_control_points(self) -> None:
        """清空所有控制点"""
        self.control_points.clear()
        self.curve_points.clear()

    def bernstein_polynomial(self, n: int, i: int, t: float) -> float:
        """计算Bernstein多项式值"""
        # C(n, i) * t^i * (1-t)^(n-i)
        return math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

    def calculate_bezier_point(self, t: float) -> Tuple[float, float]:
        """计算Bezier曲线在参数t处的点"""
        if len(self.control_points) < 2:
            return None

        n = len(self.control_points) - 1
        x, y = 0.0, 0.0

        for i in range(len(self.control_points)):
            basis = self.bernstein_polynomial(n, i, t)
            x += self.control_points[i][0] * basis
            y += self.control_points[i][1] * basis

        return (x, y)

    def update_curve(self, num_points: int = 100) -> None:
        """更新曲线点"""
        self.curve_points.clear()

        if len(self.control_points) < 2:
            return

        for i in range(num_points + 1):
            t = i / num_points
            point = self.calculate_bezier_point(t)
            if point:
                self.curve_points.append(point)

    def check_point_selection(self, pos: Tuple[int, int], radius: int = 10) -> bool:
        """检查是否点击到了控制点"""
        for i, point in enumerate(self.control_points):
            distance = math.sqrt((point[0] - pos[0]) ** 2 + (point[1] - pos[1]) ** 2)
            if distance <= radius:
                self.selected_point = i
                return True
        self.selected_point = -1
        return False

    def move_selected_point(self, new_pos: Tuple[int, int]) -> None:
        """移动选中的控制点"""
        if 0 <= self.selected_point < len(self.control_points):
            self.control_points[self.selected_point] = new_pos
            self.update_curve()

    def draw(self, surface: pygame.Surface, scale_manager=None):
        """绘制控制点和曲线"""
        # 绘制控制点连线 - 使用偏白色
        if len(self.control_points) > 1:
            for i in range(len(self.control_points) - 1):
                start_point = self.control_points[i]
                end_point = self.control_points[i + 1]

                # 应用缩放
                if scale_manager:
                    start_point = scale_manager.apply_scale_to_point(start_point)
                    end_point = scale_manager.apply_scale_to_point(end_point)

                pygame.draw.line(surface, (220, 220, 220),  # 偏白色
                                 start_point, end_point, 2)

        # 绘制曲线
        if len(self.curve_points) > 1:
            # 应用缩放
            if scale_manager:
                scaled_curve_points = scale_manager.apply_scale_to_points(self.curve_points)
            else:
                scaled_curve_points = self.curve_points

            pygame.draw.lines(surface, (0, 255, 0), False, scaled_curve_points, 4)

        # 绘制控制点
        for i, point in enumerate(self.control_points):
            # 应用缩放
            if scale_manager:
                scaled_point = scale_manager.apply_scale_to_point(point)
            else:
                scaled_point = point

            color = (255, 0, 0) if i == self.selected_point else (255, 255, 0)
            pygame.draw.circle(surface, color, scaled_point, 8)
            pygame.draw.circle(surface, (0, 0, 0), scaled_point, 8, 2)

            # 显示控制点编号
            font = pygame.font.Font(None, 20)
            text = font.render(str(i), True, (255, 255, 255))
            surface.blit(text, (scaled_point[0] + 10, scaled_point[1] - 10))

    def get_control_points_count(self) -> int:
        """获取控制点数量"""
        return len(self.control_points)

    def has_enough_points(self) -> bool:
        """是否有足够的点绘制曲线"""
        return len(self.control_points) >= 2