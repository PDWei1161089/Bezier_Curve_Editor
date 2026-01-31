"""
dynamic_bezier.py
Bezier曲线动力学分析模块
绘制速度、加速度、急动度向量
"""

import pygame
import math
import os
from typing import List, Tuple


class DynamicBezier:
    """Bezier曲线动力学分析"""

    def __init__(self):
        self.control_points = []  # 控制点
        self.t_value = 0.5  # 当前参数t值
        self.colors = []  # 每个控制点的颜色

        # 导数向量显示控制
        self.show_velocity = True
        self.show_acceleration = False
        self.show_jerk = False

        # 新增：三个子窗口的数据
        self.show_vector_windows = True  # 是否显示向量窗口

        # 存储完整向量轨迹数据（存储完整的导数向量曲线）
        self.full_velocity_data = []   # 完整的速度向量数据
        self.full_acceleration_data = []  # 完整的加速度向量数据
        self.full_jerk_data = []       # 完整的急动度向量数据

        # 当前t对应的向量值
        self.current_velocity = (0, 0, 0)
        self.current_acceleration = (0, 0, 0)
        self.current_jerk = (0, 0, 0)

        # 子窗口配置 - 改为2x2布局
        self.window_width = 350  # 稍微加宽以适应2x2布局
        self.window_height = 200
        self.window_spacing = 15  # 减小间距以适应2x2

        # 子窗口位置（动态计算）
        self.window_positions = []

        # 完整向量数据点数
        self.full_data_points = 100

        # 子窗口显示控制
        self.show_velocity_window = True
        self.show_acceleration_window = True
        self.show_jerk_window = True

        # 曲率圆相关
        self.show_curvature_circle = False
        self.curvature_radius_history = []  # 存储曲率半径历史
        self.curvature_color_positive = (255, 100, 100, 200)  # 正半径颜色（红色）
        self.curvature_color_negative = (100, 100, 255, 200)  # 负半径颜色（蓝色）

        # 曲率窗口配置
        self.show_curvature_window = True
        self.curvature_window_width = 350
        self.curvature_window_height = 200

        # 完整曲率数据（t从0到1）
        self.full_curvature_data = []

        # 当前曲率值
        self.current_curvature = 0
        self.current_curvature_radius = 0
        self.current_curvature_center = (0, 0)

        # 预定义的颜色
        self.available_colors = [
            (255, 100, 100),  # 红色
            (100, 255, 100),  # 绿色
            (100, 100, 255),  # 蓝色
            (255, 255, 100),  # 黄色
            (255, 100, 255),  # 紫色
            (100, 255, 255)  # 青色
        ]

        # 导数向量颜色
        self.velocity_color = (0, 255, 0)      # 绿色 - 速度
        self.acceleration_color = (255, 255, 0)  # 黄色 - 加速度
        self.jerk_color = (255, 0, 0)         # 红色 - 急动度

        # 向量缩放因子（用于可视化）
        self.velocity_scale = 1.0
        self.acceleration_scale = 0.5
        self.jerk_scale = 0.25

        # 中文字体（需要从主程序传入或使用系统字体）
        self.chinese_font = None
        self.initialize_chinese_font()

        # 新增：曲率圆绘制的最大半径（用于缩放显示）
        self.max_curvature_radius_display = 500

    def initialize_chinese_font(self):
        """初始化中文字体"""
        try:
            # 尝试加载常见的中文字体
            font_paths = [
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
                "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
                "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑粗体
                "/System/Library/Fonts/PingFang.ttc",  # macOS 苹方
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux 文泉驿
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    self.chinese_font = pygame.font.Font(font_path, 14)
                    print(f"成功加载中文字体: {font_path}")
                    return

            # 如果找不到系统字体，使用默认字体（可能无法显示中文）
            self.chinese_font = pygame.font.Font(None, 14)
            print("警告：未找到中文字体，使用默认字体")

        except Exception as e:
            print(f"字体加载失败: {e}")
            self.chinese_font = pygame.font.Font(None, 14)

    def set_control_points(self, points: List[Tuple[int, int]]):
        """设置控制点并初始化"""
        self.control_points = points.copy()
        self.assign_colors()
        # 当控制点变化时，重新计算完整的导数向量曲线
        self.calculate_full_vector_data()
        # 初始化当前向量值
        self.update_current_vectors()

    def calculate_full_vector_data(self):
        """计算完整的导数向量曲线（t从0到1）"""
        self.full_velocity_data = []
        self.full_acceleration_data = []
        self.full_jerk_data = []
        self.full_curvature_data = []

        steps = self.full_data_points

        for i in range(steps + 1):
            t = i / steps

            # 计算速度向量
            v = self.calculate_velocity(t)
            v_length = math.sqrt(v[0] ** 2 + v[1] ** 2)
            self.full_velocity_data.append((v[0], v[1], v_length))

            # 计算加速度向量（如果控制点足够）
            if len(self.control_points) >= 3:
                a = self.calculate_acceleration(t)
                a_length = math.sqrt(a[0] ** 2 + a[1] ** 2)
                self.full_acceleration_data.append((a[0], a[1], a_length))
            else:
                self.full_acceleration_data.append((0, 0, 0))

            # 计算急动度向量（如果控制点足够）
            if len(self.control_points) >= 4:
                j = self.calculate_jerk(t)
                j_length = math.sqrt(j[0] ** 2 + j[1] ** 2)
                self.full_jerk_data.append((j[0], j[1], j_length))
            else:
                self.full_jerk_data.append((0, 0, 0))

            # 新增：计算曲率数据
            curvature = self.calculate_curvature(t)
            curvature_radius = self.calculate_curvature_radius(t)
            self.full_curvature_data.append((t, curvature, curvature_radius))

    def assign_colors(self):
        """为每个控制点分配颜色"""
        self.colors.clear()
        n = len(self.control_points)

        for i in range(n):
            color_idx = i % len(self.available_colors)
            self.colors.append(self.available_colors[color_idx])

    def bernstein_polynomial(self, n: int, i: int, t: float) -> float:
        """计算Bernstein基函数值"""
        if n == 0:
            return 1.0 if i == 0 else 0.0
        if i < 0 or i > n:  # 边界检查
            return 0.0
        return math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

    def bernstein_derivative(self, n: int, i: int, t: float, order: int = 1) -> float:
        """计算Bernstein基函数的导数"""
        if order == 0:
            return self.bernstein_polynomial(n, i, t)
        elif order == 1:
            if n == 0:
                return 0.0
            # 修正：处理边界条件
            term1 = self.bernstein_polynomial(n-1, i-1, t) if i-1 >= 0 else 0.0
            term2 = self.bernstein_polynomial(n-1, i, t) if i <= n-1 else 0.0
            return n * (term1 - term2)
        elif order == 2:
            if n < 2:
                return 0.0
            # 修正：处理边界条件
            term1 = self.bernstein_polynomial(n-2, i-2, t) if i-2 >= 0 else 0.0
            term2 = self.bernstein_polynomial(n-2, i-1, t) if i-1 >= 0 and i-1 <= n-2 else 0.0
            term3 = self.bernstein_polynomial(n-2, i, t) if i <= n-2 else 0.0
            return n * (n-1) * (term1 - 2 * term2 + term3)
        elif order == 3:
            if n < 3:
                return 0.0
            # 修正：处理边界条件
            term1 = self.bernstein_polynomial(n-3, i-3, t) if i-3 >= 0 else 0.0
            term2 = self.bernstein_polynomial(n-3, i-2, t) if i-2 >= 0 and i-2 <= n-3 else 0.0
            term3 = self.bernstein_polynomial(n-3, i-1, t) if i-1 >= 0 and i-1 <= n-3 else 0.0
            term4 = self.bernstein_polynomial(n-3, i, t) if i <= n-3 else 0.0
            return n * (n-1) * (n-2) * (term1 - 3 * term2 + 3 * term3 - term4)
        return 0.0

    def calculate_point(self, t: float) -> Tuple[float, float]:
        """计算曲线在参数t处的点"""
        if len(self.control_points) < 2:
            return (0, 0)

        n = len(self.control_points) - 1
        x, y = 0.0, 0.0

        for i in range(len(self.control_points)):
            b = self.bernstein_polynomial(n, i, t)
            x += self.control_points[i][0] * b
            y += self.control_points[i][1] * b

        return (x, y)

    def calculate_velocity(self, t: float) -> Tuple[float, float]:
        """计算速度向量（一阶导数）"""
        if len(self.control_points) < 2:
            return (0, 0)

        n = len(self.control_points) - 1
        vx, vy = 0.0, 0.0

        for i in range(len(self.control_points)):
            db = self.bernstein_derivative(n, i, t, 1)
            vx += self.control_points[i][0] * db
            vy += self.control_points[i][1] * db

        return (vx, vy)

    def calculate_acceleration(self, t: float) -> Tuple[float, float]:
        """计算加速度向量（二阶导数）"""
        if len(self.control_points) < 3:
            return (0, 0)

        n = len(self.control_points) - 1
        ax, ay = 0.0, 0.0

        for i in range(len(self.control_points)):
            d2b = self.bernstein_derivative(n, i, t, 2)
            ax += self.control_points[i][0] * d2b
            ay += self.control_points[i][1] * d2b

        return (ax, ay)

    def calculate_jerk(self, t: float) -> Tuple[float, float]:
        """计算急动度向量（三阶导数）"""
        if len(self.control_points) < 4:
            return (0, 0)

        n = len(self.control_points) - 1
        jx, jy = 0.0, 0.0

        for i in range(len(self.control_points)):
            d3b = self.bernstein_derivative(n, i, t, 3)
            jx += self.control_points[i][0] * d3b
            jy += self.control_points[i][1] * d3b

        return (jx, jy)

    def update_current_vectors(self):
        """更新当前t对应的向量值"""
        vx, vy = self.calculate_velocity(self.t_value)
        v_length = math.sqrt(vx ** 2 + vy ** 2)
        self.current_velocity = (vx, vy, v_length)

        if len(self.control_points) >= 3:
            ax, ay = self.calculate_acceleration(self.t_value)
            a_length = math.sqrt(ax ** 2 + ay ** 2)
            self.current_acceleration = (ax, ay, a_length)
        else:
            self.current_acceleration = (0, 0, 0)

        if len(self.control_points) >= 4:
            jx, jy = self.calculate_jerk(self.t_value)
            j_length = math.sqrt(jx ** 2 + jy ** 2)
            self.current_jerk = (jx, jy, j_length)
        else:
            self.current_jerk = (0, 0, 0)

    def set_t(self, t: float):
        """设置参数t值"""
        self.t_value = max(0.0, min(1.0, t))
        # 更新当前向量值
        self.update_current_vectors()
        # 更新当前曲率值
        self.update_current_curvature()

    def update_current_curvature(self):
        """更新当前t对应的曲率值"""
        self.current_curvature = self.calculate_curvature(self.t_value)
        self.current_curvature_radius = self.calculate_curvature_radius(self.t_value)
        self.current_curvature_center = self.calculate_curvature_center(self.t_value)

    def draw(self, surface: pygame.Surface, scale_manager=None, font=None):
        """绘制动力学分析（兼容原有调用方式）"""
        if len(self.control_points) < 2:
            return

        # 计算当前t对应的曲线点
        current_point = self.calculate_point(self.t_value)

        # 绘制控制点和连线
        self.draw_control_points(surface, scale_manager)

        # 绘制完整曲线（从0到t的曲线段）
        self.draw_current_curve_segment(surface, scale_manager)

        # 绘制当前点
        if scale_manager:
            scaled_point = scale_manager.apply_scale_to_point(current_point)
        else:
            scaled_point = current_point

        pygame.draw.circle(surface, (255, 255, 0), scaled_point, 6)
        pygame.draw.circle(surface, (255, 0, 0), scaled_point, 6, 2)

        # 绘制速度向量（如果启用）
        if self.show_velocity:
            velocity = self.calculate_velocity(self.t_value)
            if velocity != (0, 0):
                self.draw_vector(surface, scaled_point, velocity,
                                 self.velocity_color, "速度", 2.0, scale_manager, font)

        # 绘制加速度向量（如果启用且有足够控制点）
        if self.show_acceleration and len(self.control_points) >= 3:
            acceleration = self.calculate_acceleration(self.t_value)
            if acceleration != (0, 0):
                self.draw_vector(surface, scaled_point, acceleration,
                                 self.acceleration_color, "加速度", 1.5, scale_manager, font)

        # 绘制急动度向量（如果启用且有足够控制点）
        if self.show_jerk and len(self.control_points) >= 4:
            jerk = self.calculate_jerk(self.t_value)
            if jerk != (0, 0):
                self.draw_vector(surface, scaled_point, jerk,
                                 self.jerk_color, "急动度", 1.0, scale_manager, font)

        # 绘制曲率圆（在绘制向量之后）
        if self.show_curvature_circle and len(self.control_points) >= 3:
            self.draw_curvature_circle(surface, scale_manager)

        # 绘制t值标签
        self.draw_t_label(surface, scaled_point, font)

        # 绘制向量轨迹窗口（显示完整向量曲线）
        self.draw_vector_windows(surface)

    def draw_control_points(self, surface: pygame.Surface, scale_manager=None):
        """绘制控制点和连线"""
        # 应用缩放函数
        def scale_point(p):
            return scale_manager.apply_scale_to_point(p) if scale_manager else p

        # 绘制控制点连线
        if len(self.control_points) > 1:
            for i in range(len(self.control_points) - 1):
                p1 = scale_point(self.control_points[i])
                p2 = scale_point(self.control_points[i + 1])
                pygame.draw.line(surface, (180, 180, 180, 180), p1, p2, 2)

        # 绘制控制点
        for i, (point, color) in enumerate(zip(self.control_points, self.colors)):
            scaled_point = scale_point(point)
            pygame.draw.circle(surface, color, scaled_point, 8)
            pygame.draw.circle(surface, (0, 0, 0), scaled_point, 8, 2)

            # 绘制控制点编号（英文数字可以正常显示）
            point_font = pygame.font.Font(None, 18)
            point_text = point_font.render(str(i), True, (255, 255, 255))
            surface.blit(point_text, (scaled_point[0] + 12, scaled_point[1] - 10))

    def draw_current_curve_segment(self, surface: pygame.Surface, scale_manager=None):
        """绘制从t=0到当前t值的曲线段"""
        if len(self.control_points) < 2:
            return

        # 应用缩放函数
        def scale_point(p):
            return scale_manager.apply_scale_to_point(p) if scale_manager else p

        # 计算从t=0到当前t值的曲线点
        curve_points = []
        steps = 50

        for step in range(steps + 1):
            t = step / steps * self.t_value  # 只计算到当前t值
            point = self.calculate_point(t)
            curve_points.append(point)

        # 绘制已走过的曲线段
        if len(curve_points) > 1:
            # 应用缩放
            scaled_points = []
            for point in curve_points:
                scaled_points.append(scale_point(point))

            # 使用渐变颜色绘制
            for i in range(len(scaled_points) - 1):
                # 计算当前段的颜色（基于t值）
                segment_t = i / (len(scaled_points) - 2)
                r = int(100 * segment_t)
                g = int(200 * (1 - segment_t) + 100 * segment_t)
                b = int(255 * (1 - segment_t))
                color = (r, g, b)

                pygame.draw.line(surface, color, scaled_points[i], scaled_points[i+1], 4)

    def draw_vector(self, surface: pygame.Surface, start_point, vector, color,
                    label, scale_factor, scale_manager=None, font=None):
        """绘制向量（归一化显示）"""
        # 计算向量长度
        length = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
        if length == 0:
            return

        # 归一化向量（保持方向，长度为scale_factor）
        normalized_x = vector[0] / length * scale_factor * 50
        normalized_y = vector[1] / length * scale_factor * 50

        # 计算向量终点
        end_x = start_point[0] + normalized_x
        end_y = start_point[1] + normalized_y
        end_point = (int(end_x), int(end_y))

        # 绘制向量线段
        pygame.draw.line(surface, color, start_point, end_point, 3)

        # 绘制向量箭头
        arrow_length = math.sqrt((end_x - start_point[0]) ** 2 + (end_y - start_point[1]) ** 2)
        if arrow_length > 20:
            self.draw_arrow(surface, color, start_point, end_point)
        else:
            # 如果箭头太短，在终点绘制一个点代替
            pygame.draw.circle(surface, color, end_point, 4)

        # 绘制向量标签（不绘制长度条）
        self.draw_vector_label(surface, start_point, end_point, color, label, length, font)

        return length

    def draw_arrow(self, surface, color, start, end, arrow_size=12):
        """绘制漂亮的箭头"""
        # 计算向量方向和长度
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        length = math.sqrt(dx * dx + dy * dy)

        # 如果向量太短，绘制小圆点代替
        if length < 15:
            pygame.draw.circle(surface, color, end, 5)
            return

        # 归一化方向向量
        if length > 0:
            unit_x = dx / length
            unit_y = dy / length
        else:
            return

        # 计算垂直向量（用于箭头宽度）
        perp_x = -unit_y
        perp_y = unit_x

        # 箭头三角形的位置（终点位置）
        # 箭头尖端稍微向内，避免与线段重叠
        tip_distance = 10  # 箭头尖端距离终点的距离
        tip_x = end[0] - unit_x * tip_distance
        tip_y = end[1] - unit_y * tip_distance

        # 箭头底边的两个点
        base_width = 8  # 箭头底边宽度
        left_base_x = tip_x + perp_x * base_width
        left_base_y = tip_y + perp_y * base_width

        right_base_x = tip_x - perp_x * base_width
        right_base_y = tip_y - perp_y * base_width

        # 绘制箭头三角形
        arrow_points = [
            end,  # 箭头尖端（线段终点）
            (int(left_base_x), int(left_base_y)),  # 左侧底点
            (int(right_base_x), int(right_base_y))  # 右侧底点
        ]

        pygame.draw.polygon(surface, color, arrow_points)

        # 确保箭头与线段平滑连接
        # 绘制一个小线段连接箭头三角形底边中点与线段
        base_mid_x = (left_base_x + right_base_x) / 2
        base_mid_y = (left_base_y + right_base_y) / 2

        # 计算连接点的位置（稍微向外一点）
        connect_x = base_mid_x + unit_x * 2
        connect_y = base_mid_y + unit_y * 2

        pygame.draw.line(surface, color,
                         (int(connect_x), int(connect_y)),
                         (int(tip_x), int(tip_y)), 2)

    def draw_vector_label(self, surface, start_point, end_point, color, label, length, font=None):
        """绘制向量标签（无长度条）"""
        # 使用传入的字体或默认字体
        if font is None:
            vector_font = pygame.font.Font(None, 14)
        else:
            vector_font = font

        # 标签文本
        label_text = f"{label}: {length:.2f}"
        label_surf = vector_font.render(label_text, True, color)

        # 计算标签位置（向量中点上方）
        label_x = (start_point[0] + end_point[0]) // 2
        label_y = (start_point[1] + end_point[1]) // 2 - 15

        # 绘制标签背景
        bg_rect = pygame.Rect(
            label_x - 5, label_y - 2,
            label_surf.get_width() + 10, label_surf.get_height() + 4
        )
        pygame.draw.rect(surface, (40, 40, 60, 200), bg_rect, border_radius=3)
        pygame.draw.rect(surface, color, bg_rect, 1, border_radius=3)

        surface.blit(label_surf, (label_x, label_y))

    def draw_t_label(self, surface: pygame.Surface, point, font=None):
        """绘制t值标签"""
        if font is None:
            t_font = pygame.font.Font(None, 18)
        else:
            t_font = font

        t_text = t_font.render(f"t={self.t_value:.2f}", True, (255, 255, 255))
        text_rect = t_text.get_rect()

        # 绘制文字背景
        bg_rect = pygame.Rect(
            point[0] + 5,
            point[1] - 15,
            text_rect.width + 6,
            text_rect.height + 4
        )
        pygame.draw.rect(surface, (40, 40, 60, 200), bg_rect, border_radius=3)
        pygame.draw.rect(surface, (100, 100, 120), bg_rect, 1, border_radius=3)
        surface.blit(t_text, (point[0] + 8, point[1] - 13))

    def get_status(self):
        """获取当前状态"""
        velocity = self.calculate_velocity(self.t_value)
        acceleration = self.calculate_acceleration(self.t_value)
        jerk = self.calculate_jerk(self.t_value)

        velocity_len = math.sqrt(velocity[0]**2 + velocity[1]**2)
        acceleration_len = math.sqrt(acceleration[0]**2 + acceleration[1]**2)
        jerk_len = math.sqrt(jerk[0]**2 + jerk[1]**2)

        return {
            'num_points': len(self.control_points),
            't_value': self.t_value,
            'show_velocity': self.show_velocity,
            'show_acceleration': self.show_acceleration,
            'show_jerk': self.show_jerk,
            'velocity_length': velocity_len,
            'acceleration_length': acceleration_len,
            'jerk_length': jerk_len
        }

    def toggle_velocity(self):
        """切换速度向量显示"""
        self.show_velocity = not self.show_velocity
        return self.show_velocity

    def toggle_acceleration(self):
        """切换加速度向量显示"""
        self.show_acceleration = not self.show_acceleration
        return self.show_acceleration

    def toggle_jerk(self):
        """切换急动度向量显示"""
        self.show_jerk = not self.show_jerk
        return self.show_jerk

    def draw_vector_window(self, surface, rect, title, vector_data, current_vector, color):
        """绘制单个向量轨迹窗口（显示完整向量曲线）"""
        # 绘制窗口背景
        pygame.draw.rect(surface, (40, 40, 60, 230), rect, border_radius=8)
        pygame.draw.rect(surface, (100, 100, 150), rect, 2, border_radius=8)

        # 绘制标题（使用中文字体）
        if self.chinese_font:
            title_font = pygame.font.Font(self.chinese_font.path, 16) if hasattr(self.chinese_font, 'path') else self.chinese_font
        else:
            title_font = pygame.font.Font(None, 16)

        title_text = title_font.render(title, True, (255, 255, 255))
        surface.blit(title_text, (rect.x + 10, rect.y + 8))

        # 绘制关闭按钮（小x）
        close_rect = pygame.Rect(rect.right - 25, rect.y + 5, 20, 20)
        pygame.draw.rect(surface, (200, 80, 80), close_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 120, 120), close_rect, 1, border_radius=4)

        # 绘制x符号
        center_x = close_rect.x + close_rect.width // 2
        center_y = close_rect.y + close_rect.height // 2
        line_length = 6
        pygame.draw.line(surface, (255, 255, 255),
                         (center_x - line_length, center_y - line_length),
                         (center_x + line_length, center_y + line_length), 2)
        pygame.draw.line(surface, (255, 255, 255),
                         (center_x + line_length, center_y - line_length),
                         (center_x - line_length, center_y + line_length), 2)

        # 计算绘图区域
        plot_rect = pygame.Rect(
            rect.x + 10,
            rect.y + 35,
            rect.width - 20,
            rect.height - 45
        )

        # 绘制绘图区域背景
        pygame.draw.rect(surface, (30, 30, 40), plot_rect)
        pygame.draw.rect(surface, (80, 80, 100), plot_rect, 1)

        # 绘制坐标轴（原点在中心） - 使用与主窗口相同的坐标系（Y轴向下为正）
        center_x = plot_rect.x + plot_rect.width // 2
        center_y = plot_rect.y + plot_rect.height // 2

        # x轴（向右为正）
        pygame.draw.line(surface, (150, 150, 150),
                         (plot_rect.x, center_y),
                         (plot_rect.right, center_y), 1)

        # y轴（向下为正，与主窗口一致）
        pygame.draw.line(surface, (150, 150, 150),
                         (center_x, plot_rect.y),
                         (center_x, plot_rect.bottom), 1)

        # 绘制坐标原点标记
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), 3)

        # 绘制完整的向量轨迹曲线（t从0到1）
        if len(vector_data) > 1:
            points = []

            # 找到最大向量长度用于缩放
            max_length = 0
            for vx, vy, length in vector_data:
                current_length = math.sqrt(vx ** 2 + vy ** 2)
                if current_length > max_length:
                    max_length = current_length

            if max_length == 0:
                max_length = 1.0  # 避免除零

            # 计算缩放因子（使用绘图区域大小的80%）
            scale_factor = min(plot_rect.width, plot_rect.height) * 0.4 / max_length

            # 绘制完整的向量轨迹 - 重要：使用与主窗口相同的坐标系
            for i, (vx, vy, length) in enumerate(vector_data):
                # 映射到绘图区域，使用与主窗口相同的坐标系（Y轴向下为正）
                # 注意：这里不需要对vy取负，因为我们要保持与主窗口相同的方向
                point_x = center_x + vx * scale_factor
                point_y = center_y + vy * scale_factor  # 注意：这里是 +vy，不是 -vy
                points.append((int(point_x), int(point_y)))

            # 绘制完整的轨迹线
            if len(points) > 1:
                pygame.draw.lines(surface, color, False, points, 2)

            # 绘制当前t对应的点
            if current_vector and len(vector_data) > 0:
                # 计算当前t对应的索引
                current_index = int(self.t_value * len(vector_data))
                current_index = min(current_index, len(vector_data) - 1)

                vx, vy, length = vector_data[current_index]
                point_x = center_x + vx * scale_factor
                point_y = center_y + vy * scale_factor  # 注意：这里是 +vy，保持相同坐标系
                current_point = (int(point_x), int(point_y))

                # 绘制当前点（大一些，更醒目）
                pygame.draw.circle(surface, (255, 255, 255), current_point, 6)
                pygame.draw.circle(surface, color, current_point, 6, 2)

                # 绘制从原点到当前点的向量
                pygame.draw.line(surface, color, (center_x, center_y), current_point, 2)

                # 绘制向量箭头
                self.draw_small_arrow(surface, color, (center_x, center_y), current_point, 6)

                # 标记t值位置
                if 0 <= current_index < len(points):
                    t_point = points[current_index]
                    # 绘制一个小的标记
                    pygame.draw.circle(surface, (255, 200, 100), t_point, 3)

                    # 绘制t值标签（英文数字可以正常显示）
                    label_font = pygame.font.Font(None, 12)
                    t_label = label_font.render(f"t={self.t_value:.2f}", True, (255, 200, 100))
                    label_rect = t_label.get_rect(center=(t_point[0], t_point[1] - 15))
                    surface.blit(t_label, label_rect)

        # 绘制刻度标签
        label_font = pygame.font.Font(None, 12)

        # x轴标签
        x_label = label_font.render("X", True, (200, 200, 200))
        surface.blit(x_label, (plot_rect.right - 15, center_y - 15))

        # y轴标签（向下为正）
        y_label = label_font.render("Y", True, (200, 200, 200))
        surface.blit(y_label, (center_x + 5, plot_rect.bottom - 15))  # Y标签在底部

        # 显示当前向量信息
        if current_vector:
            current_vx, current_vy, current_length = current_vector
            info_font = pygame.font.Font(None, 14)

            # 向量分量
            comp_text = f"({current_vx:.1f}, {current_vy:.1f})"
            comp_surf = info_font.render(comp_text, True, color)
            surface.blit(comp_surf, (rect.x + 10, rect.bottom - 45))

            # 向量长度
            length_text = f"长度: {current_length:.2f}"
            # 尝试使用中文字体显示"长度"
            if self.chinese_font:
                length_font = pygame.font.Font(self.chinese_font.path, 14) if hasattr(self.chinese_font, 'path') else self.chinese_font
                length_surf = length_font.render(length_text, True, color)
            else:
                length_surf = info_font.render(length_text, True, color)
            surface.blit(length_surf, (rect.x + 10, rect.bottom - 25))

            # 显示t值
            t_text = f"t={self.t_value:.2f}"
            t_surf = info_font.render(t_text, True, (200, 200, 200))
            surface.blit(t_surf, (rect.x + 10, rect.bottom - 65))

    def draw_small_arrow(self, surface, color, start, end, arrow_size=6):
        """绘制小箭头（用于向量窗口）"""
        # 计算向量方向
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        length = math.sqrt(dx * dx + dy * dy)
        if length < 10:  # 太短不绘制箭头
            return

        # 归一化
        if length > 0:
            dx = dx / length
            dy = dy / length

        # 箭头尖端位置（稍微向内）
        tip_x = end[0] - dx * arrow_size * 0.7
        tip_y = end[1] - dy * arrow_size * 0.7

        # 计算垂直方向
        perp_x = -dy * arrow_size * 0.4
        perp_y = dx * arrow_size * 0.4

        # 箭头三角形
        points = [
            end,  # 尖端
            (int(tip_x + perp_x), int(tip_y + perp_y)),  # 左侧
            (int(tip_x - perp_x), int(tip_y - perp_y))  # 右侧
        ]

        pygame.draw.polygon(surface, color, points)

    def draw_vector_windows(self, main_surface, offset_x=0, offset_y=0):
        """绘制四个向量轨迹窗口（显示完整向量曲线）- 改为2x2布局"""
        if not self.show_vector_windows:
            return

        # 计算窗口位置 - 使用2x2布局
        screen_width = main_surface.get_width()
        screen_height = main_surface.get_height()

        # 计算每行每列的位置
        start_x = screen_width - self.window_width * 2 - self.window_spacing * 2
        start_y = offset_y if offset_y > 0 else 80

        self.window_positions = []
        window_count = 0

        # 定义四个窗口的位置（2x2网格）
        window_positions_2x2 = [
            (start_x, start_y),  # 左上：速度
            (start_x + self.window_width + self.window_spacing, start_y),  # 右上：加速度
            (start_x, start_y + self.window_height + self.window_spacing),  # 左下：急动度
            (start_x + self.window_width + self.window_spacing, start_y + self.window_height + self.window_spacing)  # 右下：曲率
        ]

        # 绘制速度向量窗口（左上）
        if self.show_velocity_window and len(self.full_velocity_data) > 0:
            pos_x, pos_y = window_positions_2x2[0]
            window_rect = pygame.Rect(pos_x, pos_y, self.window_width, self.window_height)
            self.draw_vector_window(main_surface, window_rect,
                                    "速度向量轨迹(X)",
                                    self.full_velocity_data,
                                    self.current_velocity,
                                    self.velocity_color)
            self.window_positions.append(('velocity', window_rect))
            window_count += 1

        # 绘制加速度向量窗口（右上）
        if (self.show_acceleration_window and len(self.full_acceleration_data) > 0
                and len(self.control_points) >= 3):
            pos_x, pos_y = window_positions_2x2[1]
            window_rect = pygame.Rect(pos_x, pos_y, self.window_width, self.window_height)
            self.draw_vector_window(main_surface, window_rect,
                                    "加速度向量轨迹(D)",
                                    self.full_acceleration_data,
                                    self.current_acceleration,
                                    self.acceleration_color)
            self.window_positions.append(('acceleration', window_rect))
            window_count += 1

        # 绘制急动度向量窗口（左下）
        if (self.show_jerk_window and len(self.full_jerk_data) > 0
                and len(self.control_points) >= 4):
            pos_x, pos_y = window_positions_2x2[2]
            window_rect = pygame.Rect(pos_x, pos_y, self.window_width, self.window_height)
            self.draw_vector_window(main_surface, window_rect,
                                    "急动度向量轨迹(K)",
                                    self.full_jerk_data,
                                    self.current_jerk,
                                    self.jerk_color)
            self.window_positions.append(('jerk', window_rect))
            window_count += 1

        # 绘制曲率窗口（右下）
        if self.show_curvature_window and len(self.full_curvature_data) > 0:
            pos_x, pos_y = window_positions_2x2[3]
            window_rect = pygame.Rect(pos_x, pos_y, self.window_width, self.window_height)
            self.draw_curvature_window(main_surface, window_rect)
            self.window_positions.append(('curvature', window_rect))
            window_count += 1

        # 如果没有显示任何窗口，关闭向量窗口显示
        if window_count == 0:
            self.show_vector_windows = False

    def toggle_vector_windows(self):
        """切换向量窗口显示"""
        self.show_vector_windows = not self.show_vector_windows
        return self.show_vector_windows

    def toggle_velocity_window(self):
        """切换速度向量窗口显示"""
        self.show_velocity_window = not self.show_velocity_window
        return self.show_velocity_window

    def toggle_acceleration_window(self):
        """切换加速度向量窗口显示"""
        self.show_acceleration_window = not self.show_acceleration_window
        return self.show_acceleration_window

    def toggle_jerk_window(self):
        """切换急动度向量窗口显示"""
        self.show_jerk_window = not self.show_jerk_window
        return self.show_jerk_window

    def clear_vector_history(self):
        """清空向量历史数据（重置完整向量数据）"""
        self.full_velocity_data = []
        self.full_acceleration_data = []
        self.full_jerk_data = []
        self.calculate_full_vector_data()

    def calculate_curvature(self, t: float) -> float:
        """计算曲率"""
        if len(self.control_points) < 3:
            return 0.0

        # 计算一阶导数（速度）
        vx, vy = self.calculate_velocity(t)

        # 计算二阶导数（加速度）
        ax, ay = self.calculate_acceleration(t)

        # 计算速度的模长
        v_len = math.sqrt(vx ** 2 + vy ** 2)
        if v_len == 0:
            return 0.0

        # 计算曲率公式: κ = |v×a| / |v|^3
        # 二维叉积: v×a = vx*ay - vy*ax
        cross_product = vx * ay - vy * ax
        curvature = abs(cross_product) / (v_len ** 3)

        # 确定符号（曲率方向） - 叉积的正负决定曲线的弯曲方向
        sign = 1 if cross_product >= 0 else -1

        return curvature * sign

    def calculate_curvature_radius(self, t: float) -> float:
        """计算曲率半径"""
        curvature = self.calculate_curvature(t)

        # 检查curvature是否为0、NaN或无穷大
        if curvature == 0 or math.isnan(curvature) or math.isinf(curvature):
            # 返回一个大的数值而不是NaN
            return 10000.0  # 使用一个大数表示无穷大

        try:
            radius = 1.0 / abs(curvature)
        except ZeroDivisionError:
            return 10000.0

        # 检查radius是否为NaN或无穷大
        if math.isnan(radius) or math.isinf(radius):
            return 10000.0

        # 保留符号信息
        if curvature < 0:
            radius = -radius

        return radius

    def calculate_curvature_center(self, t: float) -> Tuple[float, float]:
        """计算曲率中心 - 关键修复：确保圆心在曲线内侧"""
        if len(self.control_points) < 3:
            return (0, 0)

        # 计算曲线点
        point = self.calculate_point(t)

        # 计算速度向量（单位切向量）
        vx, vy = self.calculate_velocity(t)
        v_len = math.sqrt(vx ** 2 + vy ** 2)
        if v_len == 0:
            return point

        # 单位切向量
        tx = vx / v_len
        ty = vy / v_len

        # 计算加速度向量
        ax, ay = self.calculate_acceleration(t)

        # 计算加速度的法向分量（指向曲线内侧）
        # 切向分量
        a_tangent = (ax * tx + ay * ty) * tx, (ax * tx + ay * ty) * ty

        # 法向分量
        a_normal = (ax - a_tangent[0]), (ay - a_tangent[1])

        a_normal_len = math.sqrt(a_normal[0]**2 + a_normal[1]**2)

        if a_normal_len > 0:
            # 单位法向量（指向曲线的内侧/凹侧）
            nx = a_normal[0] / a_normal_len
            ny = a_normal[1] / a_normal_len
        else:
            # 如果法向加速度为0，使用垂直向量
            nx = -ty
            ny = tx

        # 计算曲率半径（绝对值）
        radius = abs(self.calculate_curvature_radius(t))

        # 如果半径太大，限制显示范围
        if radius > self.max_curvature_radius_display:
            radius = self.max_curvature_radius_display
        elif radius < 5:  # 最小半径限制
            radius = 5

        # 关键：曲率中心应该在曲线的内侧（法向量方向）
        # 根据曲率的符号调整方向
        curvature = self.calculate_curvature(t)

        # 曲率中心：从切点沿法向量方向偏移半径距离
        # 注意：法向量nx, ny已经指向曲线内侧
        center_x = point[0] + nx * radius
        center_y = point[1] + ny * radius

        return (center_x, center_y)

    def draw_curvature_circle(self, surface: pygame.Surface, scale_manager=None):
        """绘制曲率圆 - 只绘制边框，圆心在曲线内侧"""
        if not self.show_curvature_circle or len(self.control_points) < 3:
            return

        # 总是绘制曲率圆，无论半径多大
        # 应用缩放函数
        def scale_point(p):
            return scale_manager.apply_scale_to_point(p) if scale_manager else p

        # 计算当前点在曲线上的位置
        current_point = self.calculate_point(self.t_value)
        scaled_current_point = scale_point(current_point)

        # 计算曲率中心（现在应该在内侧）
        center = self.current_curvature_center
        scaled_center = scale_point(center)

        # 计算实际半径
        dx = scaled_current_point[0] - scaled_center[0]
        dy = scaled_current_point[1] - scaled_center[1]
        actual_radius = math.sqrt(dx * dx + dy * dy)

        # 如果实际半径为0，不绘制
        if actual_radius == 0:
            return

        # 选择颜色
        if self.current_curvature_radius > 0:
            base_color = self.curvature_color_positive
        else:
            base_color = self.curvature_color_negative

        # 只绘制边框，不填充 - 使用pygame.draw.circle直接绘制边框
        pygame.draw.circle(surface, base_color,
                          (int(scaled_center[0]), int(scaled_center[1])),
                          int(actual_radius), 2)  # 线宽为2

        # 绘制圆心
        pygame.draw.circle(surface, (255, 255, 255),
                          (int(scaled_center[0]), int(scaled_center[1])), 6)
        pygame.draw.circle(surface, (0, 0, 0),
                          (int(scaled_center[0]), int(scaled_center[1])), 6, 1)

        # 绘制半径线
        pygame.draw.line(surface, (255, 255, 255, 200),
                        (int(scaled_center[0]), int(scaled_center[1])),
                        scaled_current_point, 2)

        # 验证相切条件：检查半径是否垂直于切线
        vx, vy = self.calculate_velocity(self.t_value)
        v_len = math.sqrt(vx ** 2 + vy ** 2)
        if v_len > 0:
            # 切线方向
            tx = vx / v_len
            ty = vy / v_len

            # 半径方向（从圆心指向切点）
            rx = (scaled_current_point[0] - scaled_center[0]) / actual_radius
            ry = (scaled_current_point[1] - scaled_center[1]) / actual_radius

            # 计算点积（应该接近0，表示垂直）
            dot_product = tx * rx + ty * ry
            # print(f"切线·半径点积: {dot_product:.6f}")  # 调试用

        # 绘制半径标签
        self.draw_radius_label(surface, (int(scaled_center[0]), int(scaled_center[1])),
                              scaled_current_point)

    def draw_gradient_circle(self, surface, center, radius, base_color):
        """绘制渐变颜色的圆"""
        if radius <= 0:
            return

        # 创建临时surface绘制渐变
        circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        # 获取基础颜色分量
        r, g, b, a = base_color

        # 绘制多个同心圆实现渐变效果
        for r_radius in range(radius, 0, -1):
            # 计算当前半径的颜色强度
            intensity = r_radius / radius

            # 计算当前透明度
            current_alpha = int(a * intensity)

            # 绘制圆环
            if current_alpha > 0:
                # 注意：这里需要创建带透明度的颜色
                current_color = (r, g, b, current_alpha)

                # 由于pygame.draw.circle不支持RGBA颜色，我们需要使用特殊方法
                # 方法1：使用pygame.gfxdraw（如果可用）
                # 方法2：绘制实心圆然后blit

                # 这里使用简单方法：绘制实心圆到临时surface
                temp_surface = pygame.Surface((r_radius * 2, r_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, current_color,
                                   (r_radius, r_radius), r_radius)

                # 计算位置
                pos_x = radius - r_radius
                pos_y = radius - r_radius
                circle_surface.blit(temp_surface, (pos_x, pos_y))

        # 绘制到主surface
        surface.blit(circle_surface, (center[0] - radius, center[1] - radius))

    def draw_radius_label(self, surface, center, point):
        """绘制半径标签"""
        # 使用中文字体
        if self.chinese_font:
            radius_font = pygame.font.Font(self.chinese_font.path, 14) if hasattr(self.chinese_font, 'path') else self.chinese_font
        else:
            radius_font = pygame.font.Font(None, 14)

        # 显示实际半径值
        actual_radius = math.sqrt((center[0] - point[0])**2 + (center[1] - point[1])**2)
        radius_text = f"半径: {actual_radius:.1f}"
        radius_surf = radius_font.render(radius_text, True, (255, 255, 255))

        # 计算标签位置（半径中点）
        label_x = (center[0] + point[0]) // 2
        label_y = (center[1] + point[1]) // 2

        # 绘制背景
        bg_rect = pygame.Rect(
            label_x - 5, label_y - 10,
            radius_surf.get_width() + 10, radius_surf.get_height() + 4
        )
        pygame.draw.rect(surface, (40, 40, 60, 200), bg_rect, border_radius=3)
        pygame.draw.rect(surface, (100, 100, 120), bg_rect, 1, border_radius=3)

        surface.blit(radius_surf, (label_x, label_y - 8))

    def draw_curvature_window(self, surface, rect):
        """绘制曲率半径变化窗口 - 修复中文显示"""
        # 绘制窗口背景
        pygame.draw.rect(surface, (40, 40, 60, 230), rect, border_radius=8)
        pygame.draw.rect(surface, (100, 100, 150), rect, 2, border_radius=8)

        # 绘制标题 - 使用中文字体
        if self.chinese_font:
            title_font = pygame.font.Font(self.chinese_font.path, 18) if hasattr(self.chinese_font,
                                                                                 'path') else self.chinese_font
        else:
            title_font = pygame.font.Font(None, 18)

        title_text = title_font.render("曲率半径变化(L)", True, (255, 255, 255))
        surface.blit(title_text, (rect.x + 10, rect.y + 8))

        # 绘制关闭按钮（小x）
        close_rect = pygame.Rect(rect.right - 25, rect.y + 5, 20, 20)
        pygame.draw.rect(surface, (200, 80, 80), close_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 120, 120), close_rect, 1, border_radius=4)

        # 绘制x符号
        center_x = close_rect.x + close_rect.width // 2
        center_y = close_rect.y + close_rect.height // 2
        line_length = 6
        pygame.draw.line(surface, (255, 255, 255),
                         (center_x - line_length, center_y - line_length),
                         (center_x + line_length, center_y + line_length), 2)
        pygame.draw.line(surface, (255, 255, 255),
                         (center_x + line_length, center_y - line_length),
                         (center_x - line_length, center_y + line_length), 2)

        # 计算绘图区域
        plot_rect = pygame.Rect(
            rect.x + 10,
            rect.y + 40,
            rect.width - 20,
            rect.height - 60
        )

        # 绘制绘图区域背景
        pygame.draw.rect(surface, (30, 30, 40), plot_rect)
        pygame.draw.rect(surface, (80, 80, 100), plot_rect, 1)

        if len(self.full_curvature_data) > 1:
            # 找到最大最小曲率半径（排除NaN和无穷大）
            max_radius = 1.0
            min_radius = -1.0

            valid_radii = []
            for _, _, radius in self.full_curvature_data:
                # 检查是否为有效数字
                if not (math.isnan(radius) or math.isinf(radius)):
                    valid_radii.append(radius)

            if valid_radii:
                max_radius = max(valid_radii)
                min_radius = min(valid_radii)

            # 调整显示范围
            y_range = max(abs(max_radius), abs(min_radius)) * 1.2
            if y_range == 0:
                y_range = 1.0

            # 绘制坐标轴
            center_y_axis = plot_rect.y + plot_rect.height // 2

            # x轴（t轴）
            pygame.draw.line(surface, (150, 150, 150),
                             (plot_rect.x, center_y_axis),
                             (plot_rect.right, center_y_axis), 1)

            # y轴（曲率半径轴）
            pygame.draw.line(surface, (150, 150, 150),
                             (plot_rect.x, plot_rect.y),
                             (plot_rect.x, plot_rect.bottom), 1)

            # 绘制曲率半径曲线
            points = []
            for i, (t, _, radius) in enumerate(self.full_curvature_data):
                # 跳过NaN和无穷大的值
                if math.isnan(radius) or math.isinf(radius):
                    continue

                # 映射到绘图区域
                x = plot_rect.x + t * plot_rect.width

                # 防止除以0
                if y_range == 0:
                    y = center_y_axis
                else:
                    y_value = center_y_axis - (radius / y_range) * (plot_rect.height / 2)
                    # 再次检查y_value是否为NaN
                    if math.isnan(y_value):
                        continue
                    y = int(y_value)

                points.append((int(x), y))

            # 绘制曲线
            if len(points) > 1:
                # 使用渐变色绘制
                for i in range(len(points) - 1):
                    x1, y1 = points[i]
                    x2, y2 = points[i + 1]

                    # 根据曲率半径正负选择颜色
                    _, _, radius1 = self.full_curvature_data[i]
                    if radius1 > 0:
                        color = self.curvature_color_positive
                    else:
                        color = self.curvature_color_negative

                    pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)

            # 绘制当前t值位置
            if points:
                current_index = int(self.t_value * len(self.full_curvature_data))
                current_index = min(current_index, len(self.full_curvature_data) - 1)

                # 找到对应的有效点
                current_point = None
                for i in range(current_index, -1, -1):
                    if i < len(points):
                        current_point = points[i]
                        break

                if current_point:
                    # 绘制当前点
                    pygame.draw.circle(surface, (255, 255, 255), current_point, 4)

                    # 绘制垂直线
                    pygame.draw.line(surface, (255, 200, 100, 150),
                                     (current_point[0], plot_rect.y),
                                     (current_point[0], plot_rect.bottom), 1)

        # 显示当前曲率信息 - 使用中文字体
        if self.chinese_font:
            info_font = pygame.font.Font(self.chinese_font.path, 14) if hasattr(self.chinese_font,
                                                                                'path') else self.chinese_font
        else:
            info_font = pygame.font.Font(None, 14)

        # 曲率值
        curvature_text = f"曲率: {self.current_curvature:.6f}"
        curvature_surf = info_font.render(curvature_text, True, (255, 255, 255))
        surface.blit(curvature_surf, (rect.x + 10, rect.bottom - 55))

        # 曲率半径
        if math.isinf(self.current_curvature_radius):
            radius_text = f"曲率半径: ∞"
        elif math.isnan(self.current_curvature_radius):
            radius_text = f"曲率半径: N/A"
        elif abs(self.current_curvature_radius) > 1000:
            radius_text = f"曲率半径: ∞"
        else:
            radius_text = f"曲率半径: {self.current_curvature_radius:.2f}"
        radius_surf = info_font.render(radius_text, True, (255, 255, 255))
        surface.blit(radius_surf, (rect.x + 10, rect.bottom - 35))

        # t值
        t_text = f"t={self.t_value:.2f}"
        t_surf = info_font.render(t_text, True, (200, 200, 200))
        surface.blit(t_surf, (rect.x + 10, rect.bottom - 15))

    def toggle_curvature_circle(self):
        """切换曲率圆显示"""
        self.show_curvature_circle = not self.show_curvature_circle
        return self.show_curvature_circle

    def toggle_curvature_window(self):
        """切换曲率窗口显示"""
        self.show_curvature_window = not self.show_curvature_window
        return self.show_curvature_window