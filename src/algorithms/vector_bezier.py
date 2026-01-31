import pygame
import math
from typing import List, Tuple
# 修复这里的导入，使用相对导入
from . import bezier_curve  # 这样导入整个模块


class VectorBezier:
    """向量表示的Bezier曲线可视化"""

    def __init__(self):
        self.control_points = []  # 控制点
        self.control_vectors = []  # 控制向量（从原点到控制点）
        self.current_vectors = []  # 当前t对应的向量
        self.origin_point = None  # 原点
        self.t_value = 0.5  # 当前参数t值
        self.colors = []  # 每个控制点的颜色
        self.vector_colors = []  # 向量的颜色
        self.show_vectors = True  # 是否显示向量
        self.show_curve = True  # 是否显示曲线
        self.vector_mode = "chained"  # "chained"首尾连接, "origin"起点都在原点

        # 预定义的颜色（最多6种）
        self.available_colors = [
            (255, 100, 100),  # 红色
            (100, 255, 100),  # 绿色
            (100, 100, 255),  # 蓝色
            (255, 255, 100),  # 黄色
            (255, 100, 255),  # 紫色
            (100, 255, 255)  # 青色
        ]

        # Bernstein基函数值
        self.bernstein_values = []
        self.normalized_vectors = []  # 归一化后的向量

    def set_control_points(self, points: List[Tuple[int, int]]):
        """设置控制点并初始化"""
        self.control_points = points.copy()

        # 自动计算原点（所有控制点的中心）
        self.calculate_origin()

        # 为每个控制点分配颜色
        self.assign_colors()

        # 计算初始控制向量
        self.calculate_control_vectors()

        # 初始化当前向量
        self.update_vectors(self.t_value)

    def calculate_origin(self):
        """计算原点（控制点的中心）"""
        if not self.control_points:
            self.origin_point = (400, 400)  # 默认原点
            return

        # 计算所有控制点的平均值
        sum_x = sum(p[0] for p in self.control_points)
        sum_y = sum(p[1] for p in self.control_points)

        self.origin_point = (
            int(sum_x / len(self.control_points)),
            int(sum_y / len(self.control_points))
        )

        # 确保原点不会太靠近边缘
        self.origin_point = (
            max(100, min(700, self.origin_point[0])),
            max(100, min(700, self.origin_point[1]))
        )

    def assign_colors(self):
        """为每个控制点分配颜色"""
        self.colors.clear()
        n = len(self.control_points)

        for i in range(n):
            color_idx = i % len(self.available_colors)
            self.colors.append(self.available_colors[color_idx])

        # 向量的颜色稍浅一些
        self.vector_colors = [
            (min(255, c[0] + 100), min(255, c[1] + 100), min(255, c[2] + 100))
            for c in self.colors
        ]

    def calculate_control_vectors(self):
        """计算从原点到控制点的向量"""
        self.control_vectors.clear()

        for point in self.control_points:
            vector = (
                point[0] - self.origin_point[0],
                point[1] - self.origin_point[1]
            )
            self.control_vectors.append(vector)

    def bernstein_polynomial(self, n: int, i: int, t: float) -> float:
        """计算Bernstein基函数值"""
        if n == 0:
            return 1.0 if i == 0 else 0.0

        # 使用math.comb计算组合数
        return math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

    def update_vectors(self, t: float):
        """根据参数t更新向量"""
        self.t_value = max(0.0, min(1.0, t))

        if len(self.control_points) < 2:
            return

        n = len(self.control_points) - 1
        self.current_vectors.clear()
        self.bernstein_values.clear()
        self.normalized_vectors.clear()

        # 计算每个基函数的值
        total_bernstein = 0.0
        for i in range(len(self.control_points)):
            b_value = self.bernstein_polynomial(n, i, self.t_value)
            self.bernstein_values.append(b_value)
            total_bernstein += b_value

        # 归一化（确保和为1）
        if total_bernstein > 0:
            self.bernstein_values = [b / total_bernstein for b in self.bernstein_values]

        # 计算当前向量（基函数值乘以原始向量）
        for i, (vector, b_value) in enumerate(zip(self.control_vectors, self.bernstein_values)):
            scaled_vector = (
                vector[0] * b_value,
                vector[1] * b_value
            )
            self.current_vectors.append(scaled_vector)

            # 计算归一化向量（用于显示）
            vector_length = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
            if vector_length > 0:
                normalized = (
                    vector[0] / vector_length * 100 * b_value,  # 乘以100放大显示
                    vector[1] / vector_length * 100 * b_value
                )
            else:
                normalized = (0, 0)
            self.normalized_vectors.append(normalized)

    def set_t(self, t: float):
        """设置参数t值"""
        self.update_vectors(t)

    def draw(self, surface: pygame.Surface, scale_manager=None):
        """绘制向量表示"""
        if not self.control_points or len(self.control_points) < 2:
            return

        # 应用缩放函数
        def scale_point(p):
            return scale_manager.apply_scale_to_point(p) if scale_manager else p

        # 缩放原点
        scaled_origin = scale_point(self.origin_point) if scale_manager else self.origin_point

        # ====== 首先绘制原始控制点和连线 ======
        # 绘制控制点连线（需要应用缩放）
        for i in range(len(self.control_points) - 1):
            p1 = scale_point(self.control_points[i])
            p2 = scale_point(self.control_points[i + 1])
            pygame.draw.line(surface, (180, 180, 180, 180), p1, p2, 2)

        # 绘制控制点（需要应用缩放）
        for i, (point, color) in enumerate(zip(self.control_points, self.colors)):
            scaled_point = scale_point(point)
            pygame.draw.circle(surface, color, scaled_point, 8)
            pygame.draw.circle(surface, (0, 0, 0), scaled_point, 8, 2)

            # 绘制控制点编号
            point_font = pygame.font.Font(None, 18)
            point_text = point_font.render(str(i), True, (255, 255, 255))
            surface.blit(point_text, (scaled_point[0] + 12, scaled_point[1] - 10))

        # ====== 绘制原点和原始向量连线 ======
        # 绘制原点
        pygame.draw.circle(surface, (255, 255, 255), scaled_origin, 10)
        pygame.draw.circle(surface, (0, 0, 0), scaled_origin, 10, 2)

        # 绘制原点标记
        font = pygame.font.Font(None, 16)
        origin_text = font.render("O", True, (255, 255, 255))
        surface.blit(origin_text, (scaled_origin[0] + 12, scaled_origin[1] - 8))

        if self.show_vectors:
            # 绘制从原点到控制点的原始向量（虚线）
            for i, (point, color, vector) in enumerate(zip(self.control_points, self.colors, self.control_vectors)):
                # 计算缩放后的终点
                scaled_point = scale_point(point)

                # 绘制原始向量（虚线）- 使用缩放后的坐标
                self.draw_dashed_line(surface, (200, 200, 200, 150),
                                      scaled_origin, scaled_point, 1)

        # ====== 绘制当前向量（根据模式选择） ======
        if self.current_vectors and self.show_vectors:
            # 创建缩放后的控制向量
            scaled_control_vectors = []
            for vector in self.control_vectors:
                # 计算缩放后的向量终点
                end_x = self.origin_point[0] + vector[0]
                end_y = self.origin_point[1] + vector[1]
                scaled_end = scale_point((end_x, end_y))

                # 计算缩放后的向量
                scaled_vector = (
                    scaled_end[0] - scaled_origin[0],
                    scaled_end[1] - scaled_origin[1]
                )
                scaled_control_vectors.append(scaled_vector)

            # 创建缩放后的当前向量
            scaled_current_vectors = []
            for vector in self.current_vectors:
                # 计算缩放后的向量终点
                end_x = self.origin_point[0] + vector[0]
                end_y = self.origin_point[1] + vector[1]
                scaled_end = scale_point((end_x, end_y))

                # 计算缩放后的向量
                scaled_vector = (
                    scaled_end[0] - scaled_origin[0],
                    scaled_end[1] - scaled_origin[1]
                )
                scaled_current_vectors.append(scaled_vector)

            if self.vector_mode == "chained":
                # 模式1：首尾连接
                self.draw_chained_vectors(surface, scaled_origin, scaled_current_vectors)
            else:
                # 模式2：所有向量起点都在原点
                self.draw_origin_vectors(surface, scaled_origin, scaled_current_vectors)

        # ====== 绘制曲线 ======
        if self.show_curve:
            # 绘制部分Bezier曲线（从t=0到当前t值），使用颜色混合
            curve_points = self.draw_bezier_curve(surface, scale_manager)

            # 在曲线终点添加标记（如果有点）
            if curve_points:
                end_point = curve_points[-1]

                # 绘制终点标记（和递归模式一样的黄色圆点带红色边框）
                pygame.draw.circle(surface, (255, 255, 0), end_point, 6)
                pygame.draw.circle(surface, (255, 0, 0), end_point, 6, 2)

                # 标记t值
                t_font = pygame.font.Font(None, 18)
                t_text = t_font.render(f"t={self.t_value:.2f}", True, (255, 255, 255))
                text_rect = t_text.get_rect()

                # 绘制文字背景（和递归模式一样的样式）
                bg_rect = pygame.Rect(
                    end_point[0] + 5,
                    end_point[1] - 15,
                    text_rect.width + 6,
                    text_rect.height + 4
                )
                pygame.draw.rect(surface, (40, 40, 60, 200), bg_rect, border_radius=3)
                pygame.draw.rect(surface, (100, 100, 120), bg_rect, 1, border_radius=3)
                surface.blit(t_text, (end_point[0] + 8, end_point[1] - 13))

    def draw_chained_vectors(self, surface: pygame.Surface, origin, scaled_vectors):
        """绘制首尾连接的向量（使用缩放后的坐标）"""
        current_end = origin

        for i, (vector, color) in enumerate(zip(scaled_vectors, self.vector_colors)):
            next_end = (
                current_end[0] + vector[0],
                current_end[1] + vector[1]
            )

            # 绘制向量线段
            pygame.draw.line(surface, color, current_end, next_end, 3)

            # 绘制向量箭头
            self.draw_arrow(surface, color, current_end, next_end)

            # 绘制向量标签
            vector_font = pygame.font.Font(None, 14)
            if self.bernstein_values and i < len(self.bernstein_values):
                label = f"B{i}={self.bernstein_values[i]:.2f}"
            else:
                label = f"V{i}"
            label_text = vector_font.render(label, True, color)
            label_x = (current_end[0] + next_end[0]) // 2
            label_y = (current_end[1] + next_end[1]) // 2 - 15
            surface.blit(label_text, (label_x, label_y))

            current_end = next_end

    def draw_origin_vectors(self, surface: pygame.Surface, origin, scaled_vectors):
        """绘制所有向量起点都在原点（使用缩放后的坐标）"""
        for i, (vector, color) in enumerate(zip(scaled_vectors, self.vector_colors)):
            end_point = (
                origin[0] + vector[0],
                origin[1] + vector[1]
            )

            # 绘制向量线段
            pygame.draw.line(surface, color, origin, end_point, 3)

            # 绘制向量箭头
            self.draw_arrow(surface, color, origin, end_point)

            # 绘制向量标签
            vector_font = pygame.font.Font(None, 14)
            if self.bernstein_values and i < len(self.bernstein_values):
                label = f"B{i}={self.bernstein_values[i]:.2f}"
            else:
                label = f"V{i}"
            label_text = vector_font.render(label, True, color)
            label_x = (origin[0] + end_point[0]) // 2
            label_y = (origin[1] + end_point[1]) // 2 - 15
            surface.blit(label_text, (label_x, label_y))

    def draw_bezier_curve(self, surface: pygame.Surface, scale_manager=None):
        """绘制部分Bezier曲线（从t=0到当前t值），使用颜色混合"""
        if len(self.control_points) < 2:
            return []

        # 应用缩放函数
        def scale_point(p):
            return scale_manager.apply_scale_to_point(p) if scale_manager else p

        # 计算部分曲线上的点（从t=0到self.t_value）
        curve_points = []
        colors = []  # 存储每个曲线点的颜色
        steps = 50  # 采样点数量

        for step in range(steps + 1):
            # 计算当前t值（从0到self.t_value）
            t = (step / steps) * self.t_value

            n = len(self.control_points) - 1
            x, y = 0.0, 0.0

            # 计算当前t对应的颜色（控制点颜色的线性组合）
            r_total, g_total, b_total = 0.0, 0.0, 0.0

            # 使用Bernstein多项式计算曲线点和颜色
            for i in range(len(self.control_points)):
                b = self.bernstein_polynomial(n, i, t)
                x += self.control_points[i][0] * b
                y += self.control_points[i][1] * b

                # 累加颜色成分，权重为Bernstein基函数值
                if i < len(self.colors):
                    r_total += self.colors[i][0] * b
                    g_total += self.colors[i][1] * b
                    b_total += self.colors[i][2] * b

            curve_points.append((int(x), int(y)))

            # 确保颜色值在0-255范围内
            r = max(0, min(255, int(r_total)))
            g = max(0, min(255, int(g_total)))
            b = max(0, min(255, int(b_total)))
            colors.append((r, g, b))

        # 对曲线点应用缩放
        if scale_manager:
            scaled_curve_points = []
            for point in curve_points:
                scaled_curve_points.append(scale_point(point))
        else:
            scaled_curve_points = curve_points

        # 绘制部分曲线（使用颜色混合）
        if len(scaled_curve_points) > 1:
            # 绘制渐变颜色的线段
            for i in range(len(scaled_curve_points) - 1):
                start_point = scaled_curve_points[i]
                end_point = scaled_curve_points[i + 1]
                start_color = colors[i]
                end_color = colors[i + 1]

                # 对每个线段使用中间颜色（取两个端点的平均值）
                mid_color = (
                    (start_color[0] + end_color[0]) // 2,
                    (start_color[1] + end_color[1]) // 2,
                    (start_color[2] + end_color[2]) // 2
                )

                pygame.draw.line(surface, mid_color, start_point, end_point, 5)

                # 也可以绘制更平滑的渐变，但需要更多代码
                # 这里简化处理，使用线段中点的颜色

        # 返回曲线点，方便在外部绘制标记
        return scaled_curve_points

    def draw_dashed_line(self, surface, color, start, end, width=1, dash_length=10):
        """绘制虚线"""
        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1
        distance = max(1, math.sqrt(dx * dx + dy * dy))
        dx = dx / distance
        dy = dy / distance

        # 绘制虚线
        for i in range(0, int(distance), dash_length * 2):
            start_i = (x1 + dx * i, y1 + dy * i)
            end_i = (x1 + dx * min(i + dash_length, distance),
                     y1 + dy * min(i + dash_length, distance))
            pygame.draw.line(surface, color, start_i, end_i, width)

    def draw_arrow(self, surface, color, start, end, arrow_size=10):
        """绘制箭头"""
        # 计算箭头方向
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        # 只有当线段足够长时才绘制箭头
        length = math.sqrt(dx * dx + dy * dy)
        if length < arrow_size * 2:
            return

        # 计算箭头位置（在线段末端）
        arrow_pos = (
            end[0] - dx / length * arrow_size,
            end[1] - dy / length * arrow_size
        )

        # 计算箭头两侧的点
        angle = math.atan2(dy, dx)

        left_angle = angle + math.pi * 0.75
        right_angle = angle - math.pi * 0.75

        left_point = (
            arrow_pos[0] + math.cos(left_angle) * arrow_size,
            arrow_pos[1] + math.sin(left_angle) * arrow_size
        )

        right_point = (
            arrow_pos[0] + math.cos(right_angle) * arrow_size,
            arrow_pos[1] + math.sin(right_angle) * arrow_size
        )

        # 绘制箭头
        pygame.draw.polygon(surface, color, [end, left_point, right_point])

    def get_status(self):
        """获取当前状态"""
        return {
            'num_points': len(self.control_points),
            't_value': self.t_value,
            'origin': self.origin_point,
            'show_vectors': self.show_vectors,
            'show_curve': self.show_curve,
            'bernstein_values': self.bernstein_values.copy() if self.bernstein_values else []
        }

    # 添加切换向量模式的方法
    def toggle_vector_mode(self):
        """切换向量显示模式"""
        if self.vector_mode == "chained":
            self.vector_mode = "origin"
        else:
            self.vector_mode = "chained"
        return self.vector_mode

    def get_vector_mode_text(self):
        """获取向量模式文本"""
        if self.vector_mode == "chained":
            return "首尾连接"
        else:
            return "起点在原点"