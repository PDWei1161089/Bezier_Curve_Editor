import pygame
import math
from typing import List


class BernsteinWindow:
    """Bernstein基函数可视化窗口"""

    def __init__(self, width=450, height=300, font=None, small_font=None):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.surface.set_alpha(255)
        self.visible = False

        # 字体设置 - 使用传入的中文字体
        self.font = font if font else pygame.font.Font(None, 14)
        self.small_font = small_font if small_font else pygame.font.Font(None, 12)
        self.title_font = pygame.font.Font(None, 20)  # 标题字体稍大

        # 坐标轴设置
        self.margin_left = 60
        self.margin_right = 30
        self.margin_top = 30
        self.margin_bottom = 45

        # 绘图区域
        self.graph_width = width - self.margin_left - self.margin_right
        self.graph_height = height - self.margin_top - self.margin_bottom

        # 颜色定义
        self.bg_color = (40, 40, 60)
        self.axis_color = (180, 180, 200)
        self.grid_color = (80, 80, 100)
        self.text_color = (240, 240, 255)

        # Bernstein基函数颜色（与向量可视化一致）
        self.function_colors = [
            (255, 120, 120),  # 更亮的红色
            (120, 255, 120),  # 更亮的绿色
            (120, 120, 255),  # 更亮的蓝色
            (255, 255, 120),  # 更亮的黄色
            (255, 120, 255),  # 更亮的紫色
            (120, 255, 255)  # 更亮的青色
        ]

        # 当前状态
        self.n = 0  # 阶数
        self.t_value = 0.5
        self.bernstein_values = []
        self.show_all_functions = True

        # 新增：拖拽相关属性
        self.dragging = False  # 是否正在拖拽窗口
        self.drag_offset_x = 0  # 拖拽偏移量X
        self.drag_offset_y = 0  # 拖拽偏移量Y
        self.last_position = (0, 0)  # 上次位置
        self.drag_handle_height = 25  # 标题栏高度，用于拖拽
        self.title_bar_rect = None  # 标题栏矩形区域

        # 拖拽把手颜色
        self.title_bar_color = (60, 60, 80, 220)
        self.title_text_color = (255, 255, 100)
        self.drag_handle_color = (100, 150, 200)
        self.close_button_rect = None

        self.data_current_page = 0  # 数据面板当前页码
        self.data_per_page = 7  # 每页显示的函数数量
        self.data_total_pages = 1  # 总页数

    def set_n(self, n: int):
        """设置Bezier曲线的阶数（控制点数-1）"""
        self.n = n
        self.update_data_pages()  # 新增：更新分页信息

    def set_t(self, t: float):
        """设置参数t值"""
        self.t_value = max(0.0, min(1.0, t))
        self.calculate_bernstein_values()

    def calculate_bernstein_values(self):
        """计算所有基函数的值"""
        self.bernstein_values = []

        if self.n <= 0:
            return

        for i in range(self.n + 1):
            value = self.bernstein_polynomial(self.n, i, self.t_value)
            self.bernstein_values.append(value)

    def bernstein_polynomial(self, n: int, i: int, t: float) -> float:
        """计算Bernstein基函数值"""
        if n == 0:
            return 1.0 if i == 0 else 0.0

        # 使用math.comb计算组合数
        return math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

    def handle_event(self, event, window_position):
        """
        处理窗口事件（鼠标点击、移动等）

        Args:
            event: pygame事件
            window_position: 窗口当前位置 (x, y)

        Returns:
            tuple: (handled, new_position) 是否处理了事件，新的窗口位置
        """
        if not self.visible:
            return False, window_position

        new_position = window_position
        handled = False

        # 计算标题栏的绝对位置
        title_bar_absolute = pygame.Rect(
            window_position[0],
            window_position[1],
            self.width,
            self.drag_handle_height
        )

        # 计算关闭按钮的绝对位置
        close_btn_absolute = None
        if hasattr(self, 'close_button_rect') and self.close_button_rect:
            close_btn_absolute = pygame.Rect(
                window_position[0] + 10,
                window_position[1] + 5,
                15, 15
            )

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 检查是否点击了关闭按钮
            if close_btn_absolute and close_btn_absolute.collidepoint(event.pos):
                self.visible = False
                print("点击关闭按钮，隐藏Bernstein窗口")
                return True, window_position  # 返回 True 表示已处理

            # 检查是否点击了标题栏
            if title_bar_absolute.collidepoint(event.pos):
                self.dragging = True
                self.drag_offset_x = event.pos[0] - window_position[0]
                self.drag_offset_y = event.pos[1] - window_position[1]
                print(f"开始拖拽Bernstein窗口，偏移({self.drag_offset_x}, {self.drag_offset_y})")
                return True, window_position  # 返回 True 表示已处理

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                print(f"结束拖拽Bernstein窗口，最终位置{new_position}")
                return True, new_position  # 返回 True 表示已处理

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # 计算新位置
                new_x = event.pos[0] - self.drag_offset_x
                new_y = event.pos[1] - self.drag_offset_y

                # 限制窗口在屏幕内（可选）
                # 这里可以添加边界检查，例如：
                # new_x = max(0, min(new_x, screen_width - self.width))
                # new_y = max(0, min(new_y, screen_height - self.height))

                new_position = (new_x, new_y)
                return True, new_position  # 返回 True 表示已处理

        return False, window_position  # 返回 False 表示未处理

    def draw(self, screen, position=(0, 0)):
        """绘制Bernstein窗口"""
        if not self.visible:
            return

        # 保存当前位置
        self.last_position = position

        # 清空背景
        self.surface.fill(self.bg_color)

        # 绘制标题栏（新增）
        self.draw_title_bar()

        # 调整绘图区域的Y坐标（考虑标题栏高度）
        content_y_offset = self.drag_handle_height

        # 保存原始边距
        original_margin_top = self.margin_top

        # 临时调整上边距以考虑标题栏
        self.margin_top += content_y_offset

        # 重新计算绘图区域
        self.graph_height = self.height - self.margin_top - self.margin_bottom

        # 绘制网格和坐标轴
        self.draw_grid_and_axes()

        # 绘制Bernstein基函数
        if self.n > 0:
            if self.show_all_functions:
                self.draw_all_functions()
            else:
                self.draw_current_values()

            # 绘制当前t值标记线
            self.draw_t_marker()

            # 绘制图例
            # self.draw_legend()

        # 恢复原始边距
        self.margin_top = original_margin_top
        self.graph_height = self.height - self.margin_top - self.margin_bottom

        # 将窗口绘制到主屏幕
        screen.blit(self.surface, position)

        # 更新标题栏的绝对位置（用于点击检测）
        if self.title_bar_rect:
            self.title_bar_rect.x = position[0]
            self.title_bar_rect.y = position[1]

        # 更新关闭按钮的绝对位置
        if hasattr(self, 'close_button_rect') and self.close_button_rect:
            self.close_button_rect.x = position[0] + 10
            self.close_button_rect.y = position[1] + 5

    def draw_grid_and_axes(self):
        """绘制网格和坐标轴"""
        # 绘制外框
        pygame.draw.rect(self.surface, self.axis_color,
                         (self.margin_left - 1, self.margin_top - 1,
                          self.graph_width + 2, self.graph_height + 2), 2)

        # 绘制网格线（垂直）
        grid_steps = 6
        for i in range(grid_steps + 1):
            x = self.margin_left + i * (self.graph_width // grid_steps)
            pygame.draw.line(self.surface, self.grid_color,
                             (x, self.margin_top),
                             (x, self.margin_top + self.graph_height), 1)

            # 标签
            t_value = i / float(grid_steps)
            text = self.small_font.render(f"{t_value:.1f}", True, self.text_color)
            text_rect = text.get_rect(center=(x, self.margin_top + self.graph_height + 12))
            self.surface.blit(text, text_rect)

        # 绘制网格线（水平）
        for i in range(grid_steps + 1):
            y = self.margin_top + i * (self.graph_height // grid_steps)
            pygame.draw.line(self.surface, self.grid_color,
                             (self.margin_left, y),
                             (self.margin_left + self.graph_width, y), 1)

            # 标签 - 增加左边距，避免与坐标轴重合
            value = 1.0 - i / float(grid_steps)
            text = self.small_font.render(f"{value:.1f}", True, self.text_color)
            # 增加左边距，从-20改为-25
            text_rect = text.get_rect(center=(self.margin_left - 25, y))
            self.surface.blit(text, text_rect)

        # 坐标轴标签 - 调整位置
        t_label = self.font.render("参数 t", True, self.text_color)
        # 调整横轴标签位置，确保在窗口内
        t_label_x = self.margin_left + self.graph_width // 2 - t_label.get_width() // 2
        t_label_y = self.margin_top + self.graph_height + 25
        # 确保标签在窗口内
        if t_label_y + t_label.get_height() > self.height - 5:
            t_label_y = self.height - t_label.get_height() - 5
        self.surface.blit(t_label, (t_label_x, t_label_y))

        b_label = self.font.render("B(t)", True, self.text_color)
        # 调整纵轴标签位置，确保在窗口内
        b_label_x = 25  # 从20改为25，离坐标轴更远
        b_label_y = self.margin_top + self.graph_height // 2 - b_label.get_height() // 2
        self.surface.blit(b_label, (b_label_x, b_label_y))

    def draw_all_functions(self):
        """绘制所有Bernstein基函数"""
        if self.n <= 0:
            return

        # 绘制每个基函数
        for i in range(self.n + 1):
            color = self.function_colors[i % len(self.function_colors)]

            points = []
            for step in range(51):  # 减少点数到51个（原101）
                t = step / 50.0
                b_value = self.bernstein_polynomial(self.n, i, t)

                # 转换为屏幕坐标
                x = self.margin_left + t * self.graph_width
                y = self.margin_top + (1 - b_value) * self.graph_height

                points.append((x, y))

            # 绘制曲线
            if len(points) > 1:
                pygame.draw.lines(self.surface, color, False, points, 1)  # 线宽从2减少到1

                # 在当前t值处绘制点
                if self.bernstein_values and i < len(self.bernstein_values):
                    b_current = self.bernstein_values[i]
                    x_current = self.margin_left + self.t_value * self.graph_width
                    y_current = self.margin_top + (1 - b_current) * self.graph_height

                    pygame.draw.circle(self.surface, (255, 255, 255),
                                       (int(x_current), int(y_current)), 3)  # 点大小从5减少到3
                    pygame.draw.circle(self.surface, color,
                                       (int(x_current), int(y_current)), 3, 1)

    def draw_current_values(self):
        """绘制当前t值处的函数值（柱状图）"""
        if not self.bernstein_values:
            return

        bar_width = self.graph_width / (self.n + 1) / 2
        max_value = max(self.bernstein_values) if self.bernstein_values else 1.0

        for i, value in enumerate(self.bernstein_values):
            color = self.function_colors[i % len(self.function_colors)]

            # 计算柱状图位置
            x = self.margin_left + (i + 0.5) * (self.graph_width / (self.n + 1))
            bar_height = (value / max_value) * self.graph_height * 0.8
            y = self.margin_top + self.graph_height - bar_height

            # 绘制柱状图
            bar_rect = pygame.Rect(x - bar_width / 2, y, bar_width, bar_height)
            pygame.draw.rect(self.surface, color, bar_rect)
            pygame.draw.rect(self.surface, (255, 255, 255), bar_rect, 1)

            # 绘制数值标签（更小的字体）
            if value > 0.1:  # 只显示较大的值
                value_text = self.small_font.render(f"{value:.2f}", True, (255, 255, 255))  # 2位小数
                text_rect = value_text.get_rect(center=(x, y - 8))  # 调整位置
                self.surface.blit(value_text, text_rect)

            # 绘制索引标签
            index_text = self.small_font.render(f"B{i}", True, color)
            index_rect = index_text.get_rect(center=(x, self.margin_top + self.graph_height + 15))
            self.surface.blit(index_text, index_rect)

    def draw_t_marker(self):
        """绘制当前t值标记线"""
        x = self.margin_left + self.t_value * self.graph_width

        # 垂直标记线
        pygame.draw.line(self.surface, (255, 255, 0),
                         (x, self.margin_top),
                         (x, self.margin_top + self.graph_height), 2)

        # t值标签
        t_text = self.font.render(f"t = {self.t_value:.3f}", True, (255, 255, 0))
        text_rect = t_text.get_rect()
        text_rect.topleft = (x + 5, self.margin_top + 5)

        # 标签背景
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(self.surface, (40, 40, 60, 200), bg_rect, border_radius=3)
        pygame.draw.rect(self.surface, (100, 100, 120), bg_rect, 1, border_radius=3)

        self.surface.blit(t_text, text_rect)

    def draw_legend(self):
        """绘制图例"""
        if self.n <= 0:
            return

        # 图例位置（调整到更合适的位置）
        legend_x = self.margin_left + self.graph_width - 120  # 右对齐
        legend_y = self.margin_top

        # 检查图例是否超出窗口
        if legend_x < self.margin_left:
            legend_x = self.margin_left

        # 图例标题
        try:
            title_text = self.small_font.render("基函数:", True, self.text_color)
            self.surface.blit(title_text, (legend_x, legend_y))
        except:
            title_text = self.small_font.render("Basis:", True, self.text_color)
            self.surface.blit(title_text, (legend_x, legend_y))

        # 限制显示的基函数数量，防止超出窗口
        max_functions_to_show = min(self.n + 1, 5)  # 最多显示5个
        line_height = 18  # 减小行高

        # 每个基函数的图例项
        for i in range(max_functions_to_show):
            color_idx = i % len(self.function_colors)
            color = self.function_colors[color_idx]

            # 颜色方块
            y_pos = legend_y + 20 + i * line_height
            pygame.draw.rect(self.surface, color,
                             (legend_x, y_pos, 10, 10))  # 缩小方块
            pygame.draw.rect(self.surface, (255, 255, 255),
                             (legend_x, y_pos, 10, 10), 1)

            # 标签 - 显示具体数值
            if self.bernstein_values and i < len(self.bernstein_values):
                value = self.bernstein_values[i]
                if abs(value) < 0.0001:
                    value_str = "0"
                elif abs(value - 1.0) < 0.0001:
                    value_str = "1"
                else:
                    value_str = f"{value:.3f}"

                label = f"B{i} = {value_str}"
            else:
                label = f"B{i}"

            try:
                label_text = self.small_font.render(label, True, self.text_color)
                self.surface.blit(label_text, (legend_x + 15, y_pos - 2))
            except Exception as e:
                label = f"B{i}"
                label_text = self.small_font.render(label, True, self.text_color)
                self.surface.blit(label_text, (legend_x + 15, y_pos - 2))

    def draw_title(self):
        """绘制窗口标题"""
        if self.n > 0:
            title = f"Bernstein基函数 (n={self.n})"
        else:
            title = "Bernstein基函数可视化"

        # 方法1：使用传入的字体
        if self.font:
            try:
                # 使用小一点的标题
                title_text = self.small_font.render(title, True, (255, 255, 100))
            except:
                title_text = self.title_font.render(title, True, (255, 255, 100))
        else:
            title_text = self.title_font.render(title, True, (255, 255, 100))

        title_rect = title_text.get_rect(center=(self.width // 2, 15))  # 上移标题
        self.surface.blit(title_text, title_rect)

    def draw_title_bar(self):
        """绘制标题栏（用于拖拽）"""
        if not self.visible:
            return

        # 创建标题栏矩形
        self.title_bar_rect = pygame.Rect(0, 0, self.width, self.drag_handle_height)

        # 绘制标题栏背景（渐变效果）
        for i in range(self.drag_handle_height):
            # 计算渐变颜色
            ratio = i / self.drag_handle_height
            r = int(self.title_bar_color[0] * (1 - ratio) + 80 * ratio)
            g = int(self.title_bar_color[1] * (1 - ratio) + 100 * ratio)
            b = int(self.title_bar_color[2] * (1 - ratio) + 120 * ratio)

            pygame.draw.line(self.surface, (r, g, b),
                             (0, i), (self.width, i), 1)

        # 绘制标题栏边框
        pygame.draw.rect(self.surface, (100, 100, 150), self.title_bar_rect, 1)

        # 绘制标题文本
        if self.n > 0:
            title = f"Bernstein Basis Functions (n={self.n})"
        else:
            title = "Bernstein Basis Functions"

            # 尝试多种字体渲染方案
        title_surface = None
        shadow_surface = None

        # 方案1：使用传入的主字体（如果支持中文）
        if self.font:
            try:
                # 先测试字体是否能渲染中文
                test_surface = self.font.render("中", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    # 创建标题字体（主字体但调整大小）
                    title_font = pygame.font.Font(self.font.font_file if hasattr(self.font, 'font_file') else None, 18)
                    shadow_surface = title_font.render(title, True, (0, 0, 0, 150))
                    title_surface = title_font.render(title, True, self.title_text_color)
            except Exception as e:
                print(f"主字体渲染中文失败: {e}")
        # 方案2：使用小字体（如果支持中文）
        if title_surface is None and self.small_font:
            try:
                # 创建放大的小字体
                title_font = pygame.font.Font(
                    self.small_font.font_file if hasattr(self.small_font, 'font_file') else None,
                    18
                )
                shadow_surface = title_font.render(title, True, (0, 0, 0, 150))
                title_surface = title_font.render(title, True, self.title_text_color)
            except Exception as e:
                print(f"小字体渲染中文失败: {e}")

        # 绘制标题（带阴影效果）
        # 阴影
        shadow_text = self.title_font.render(title, True, (0, 0, 0, 150))
        shadow_rect = shadow_text.get_rect(center=(self.width // 2 + 1, self.drag_handle_height // 2 + 1))
        self.surface.blit(shadow_text, shadow_rect)

        # 前景
        title_text = self.title_font.render(title, True, self.title_text_color)
        title_rect = title_text.get_rect(center=(self.width // 2, self.drag_handle_height // 2))
        self.surface.blit(title_text, title_rect)

        # 在标题栏右侧绘制拖拽指示器
        self.draw_drag_indicator(self.width - 40, 8)

        # 在标题栏左侧绘制关闭按钮
        self.draw_close_button(10, 5)

    def draw_drag_indicator(self, x, y):
        """绘制拖拽指示器（四个点）"""
        dot_size = 3
        dot_spacing = 5

        positions = [
            (x, y),
            (x + dot_spacing, y),
            (x, y + dot_spacing),
            (x + dot_spacing, y + dot_spacing),
        ]

        for pos in positions:
            pygame.draw.circle(self.surface, (255, 255, 255), pos, dot_size)

    def draw_close_button(self, x, y):
        """绘制关闭按钮"""
        close_btn_size = 15
        close_btn_rect = pygame.Rect(x, y, close_btn_size, close_btn_size)

        # 绘制关闭按钮背景
        pygame.draw.rect(self.surface, (200, 80, 80), close_btn_rect, border_radius=3)
        pygame.draw.rect(self.surface, (255, 120, 120), close_btn_rect, 1, border_radius=3)

        # 绘制X符号
        center_x = close_btn_rect.x + close_btn_rect.width // 2
        center_y = close_btn_rect.y + close_btn_rect.height // 2
        line_length = 5

        # 绘制斜线
        pygame.draw.line(self.surface, (255, 255, 255),
                         (center_x - line_length, center_y - line_length),
                         (center_x + line_length, center_y + line_length), 2)
        pygame.draw.line(self.surface, (255, 255, 255),
                         (center_x + line_length, center_y - line_length),
                         (center_x - line_length, center_y + line_length), 2)

        self.close_button_rect = close_btn_rect

    def toggle_visibility(self):
        """切换窗口可见性"""
        self.visible = not self.visible

    def toggle_view_mode(self):
        """切换显示模式（曲线图/柱状图）"""
        self.show_all_functions = not self.show_all_functions

    def get_status(self):
        """获取窗口状态"""
        return {
            'visible': self.visible,
            'n': self.n,
            't_value': self.t_value,
            'show_all_functions': self.show_all_functions,
            'bernstein_values': self.bernstein_values.copy() if self.bernstein_values else []
        }

    def next_data_page(self):
        """数据面板下一页"""
        if self.data_current_page < self.data_total_pages - 1:
            self.data_current_page += 1
            return True
        return False

    def prev_data_page(self):
        """数据面板上一页"""
        if self.data_current_page > 0:
            self.data_current_page -= 1
            return True
        return False

    def update_data_pages(self):
        """更新数据面板分页信息"""
        if self.n <= 0:
            self.data_total_pages = 1
        else:
            self.data_total_pages = max(1, (self.n + 1 + self.data_per_page - 1) // self.data_per_page)
