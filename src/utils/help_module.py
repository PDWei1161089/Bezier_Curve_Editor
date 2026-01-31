import pygame
from typing import List
# 导入配置
from src.core.config import ChineseText


class HelpModule:
    """操作说明模块 - 带翻页功能，支持中文"""

    def __init__(self, font, small_font, instructions_content=None):
        """
        初始化帮助模块

        Args:
            font: 主字体对象
            small_font: 小字体对象
            instructions_content: 中文说明内容
        """
        self.font = font
        self.small_font = small_font
        self.visible = False
        self.button_text = ChineseText.HELP_BUTTON

        # 使用传入的中文说明内容或默认英文内容
        if instructions_content:
            self.raw_instructions = instructions_content
        else:
            self.raw_instructions = ChineseText.HELP_CONTENT

        # 分页后的内容
        self.pages = []
        self.current_page = 0
        self.total_pages = 0

        # 分页设置
        self.lines_per_page = 12  # 每页显示的行数
        self.page_margin_bottom = 80  # 页面底部空白高度

        # 初始化分页
        self.paginate_content()

        # 按钮设置
        self.button_rect = None
        self.button_color = (70, 130, 180)  # 钢蓝色
        self.button_hover_color = (100, 160, 210)  # 浅钢蓝色
        self.button_text_color = (255, 255, 255)

        # 翻页按钮设置
        self.prev_button_rect = None
        self.next_button_rect = None
        self.page_button_color = (80, 140, 190)
        self.page_button_hover_color = (110, 170, 220)

    def paginate_content(self):
        """将内容分页"""
        self.pages.clear()
        current_page_lines = []
        current_line_count = 0

        for line in self.raw_instructions:
            if line == "":
                # 空行
                current_page_lines.append(line)
                current_line_count += 0.5  # 空行占半行
            else:
                current_page_lines.append(line)
                current_line_count += 1

            # 如果达到每页行数限制，开始新的一页
            if current_line_count >= self.lines_per_page:
                self.pages.append(current_page_lines.copy())
                current_page_lines.clear()
                current_line_count = 0

        # 添加最后一页
        if current_page_lines:
            self.pages.append(current_page_lines)

        self.total_pages = len(self.pages)

    def draw_button(self, screen, position=(270, 10), size=(120, 40)):
        """
        绘制帮助按钮

        Args:
            screen: pygame Surface对象
            position: 按钮位置 (x, y)
            size: 按钮大小 (width, height)
        """
        x, y = position
        width, height = size

        # 创建按钮矩形
        self.button_rect = pygame.Rect(x, y, width, height)

        # 检查鼠标是否悬停在按钮上
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.button_rect.collidepoint(mouse_pos)

        # 绘制按钮背景
        button_color = self.button_hover_color if is_hover else self.button_color
        pygame.draw.rect(screen, button_color, self.button_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.button_rect, 2, border_radius=8)

        # 绘制按钮文本
        text_surf = self.font.render(self.button_text, True, self.button_text_color)
        text_rect = text_surf.get_rect(center=self.button_rect.center)
        screen.blit(text_surf, text_rect)

        return is_hover

    def draw_page_buttons(self, screen, panel_x, panel_y, width, height):
        """绘制翻页按钮"""
        button_width = 100
        button_height = 40
        button_y = panel_y + height - 60  # 底部空白区域上方

        # 上一页按钮
        prev_button_x = panel_x + 50
        self.prev_button_rect = pygame.Rect(prev_button_x, button_y, button_width, button_height)

        mouse_pos = pygame.mouse.get_pos()
        prev_hover = self.prev_button_rect.collidepoint(mouse_pos)
        prev_color = self.page_button_hover_color if prev_hover else self.page_button_color

        pygame.draw.rect(screen, prev_color, self.prev_button_rect, border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), self.prev_button_rect, 2, border_radius=6)

        prev_text = self.small_font.render(ChineseText.PREV_PAGE, True, self.button_text_color)
        prev_text_rect = prev_text.get_rect(center=self.prev_button_rect.center)
        screen.blit(prev_text, prev_text_rect)

        # 下一页按钮
        next_button_x = panel_x + width - button_width - 50
        self.next_button_rect = pygame.Rect(next_button_x, button_y, button_width, button_height)

        next_hover = self.next_button_rect.collidepoint(mouse_pos)
        next_color = self.page_button_hover_color if next_hover else self.page_button_color

        pygame.draw.rect(screen, next_color, self.next_button_rect, border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), self.next_button_rect, 2, border_radius=6)

        next_text = self.small_font.render(ChineseText.NEXT_PAGE, True, self.button_text_color)
        next_text_rect = next_text.get_rect(center=self.next_button_rect.center)
        screen.blit(next_text, next_text_rect)

        # 页面指示器
        page_text = ChineseText.PAGE_TEXT.format(self.current_page + 1, self.total_pages)
        page_surf = self.small_font.render(page_text, True, (200, 200, 255))
        page_rect = page_surf.get_rect(center=(panel_x + width // 2, button_y + button_height // 2))
        screen.blit(page_surf, page_rect)

        return prev_hover, next_hover

    def handle_page_click(self, pos):
        """处理翻页按钮点击"""
        if self.prev_button_rect and self.prev_button_rect.collidepoint(pos):
            if self.current_page > 0:
                self.current_page -= 1
            return True
        elif self.next_button_rect and self.next_button_rect.collidepoint(pos):
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
            return True
        return False

    def draw_help_panel(self, screen, width=600, height=550):
        """
        绘制帮助面板

        Args:
            screen: pygame Surface对象
            width: 面板宽度
            height: 面板高度
        """
        if not self.visible or self.total_pages == 0:
            return

        # 计算面板位置（居中显示）
        panel_x = (screen.get_width() - width) // 2
        panel_y = (screen.get_height() - height) // 2

        # 创建半透明背景
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # 半透明黑色
        screen.blit(overlay, (0, 0))

        # 绘制面板背景
        panel_rect = pygame.Rect(panel_x, panel_y, width, height)
        pygame.draw.rect(screen, (40, 40, 60), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 150), panel_rect, 3, border_radius=10)

        # 绘制标题
        title = self.font.render(ChineseText.HELP_TITLE, True, (255, 255, 100))
        title_rect = title.get_rect(center=(panel_x + width // 2, panel_y + 30))
        screen.blit(title, title_rect)

        # 绘制当前页的内容
        if self.current_page < len(self.pages):
            current_page_content = self.pages[self.current_page]
            text_y = panel_y + 70

            for line in current_page_content:
                if line == "":
                    text_y += 15  # 空行间距
                    continue

                # 根据内容类型选择颜色和字体
                if line.startswith("操作说明:") or line.startswith("User Manual:"):
                    color = (255, 200, 100)
                    font_obj = self.font
                elif line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith(
                        "4.") or line.startswith("5.") or line.startswith("6."):
                    color = (100, 200, 255)
                    font_obj = self.small_font
                elif line.startswith("   •"):
                    color = (220, 220, 220)
                    font_obj = self.small_font
                else:
                    color = (200, 200, 200)
                    font_obj = self.small_font

                # 计算文本位置
                text_surf = font_obj.render(line, True, color)
                text_x = panel_x + 30
                screen.blit(text_surf, (text_x, text_y))
                text_y += 28 if font_obj == self.font else 24

        # 绘制翻页按钮
        prev_hover, next_hover = self.draw_page_buttons(screen, panel_x, panel_y, width, height)

        # 绘制关闭提示
        close_text = ChineseText.CLOSE_HELP
        close_surf = self.small_font.render(close_text, True, (200, 150, 150))
        close_rect = close_surf.get_rect(center=(panel_x + width // 2, panel_y + height - 25))
        screen.blit(close_surf, close_rect)

        # 绘制键盘快捷键提示
        if self.total_pages > 1:
            keys_text = ChineseText.PAGE_KEYS
            keys_surf = self.small_font.render(keys_text, True, (150, 200, 150))
            keys_rect = keys_surf.get_rect(center=(panel_x + width // 2, panel_y + height - 50))
            screen.blit(keys_surf, keys_rect)

    def toggle_visibility(self):
        """切换帮助面板的可见性"""
        self.visible = not self.visible
        if self.visible:
            self.current_page = 0  # 每次打开都从第一页开始

    def is_visible(self):
        """获取帮助面板的可见性"""
        return self.visible

    def handle_click(self, pos):
        """
        处理点击事件

        Args:
            pos: 点击位置 (x, y)

        Returns:
            bool: 如果点击了按钮返回True，否则返回False
        """
        if self.button_rect and self.button_rect.collidepoint(pos):
            self.toggle_visibility()
            return True
        elif self.visible:
            # 检查是否点击了翻页按钮
            if self.handle_page_click(pos):
                return True
            # 如果帮助面板可见，点击非按钮区域关闭
            panel_width = 600
            panel_height = 550
            panel_x = (pygame.display.get_surface().get_width() - panel_width) // 2
            panel_y = (pygame.display.get_surface().get_height() - panel_height) // 2

            # 检查点击是否在面板区域内
            if (panel_x <= pos[0] <= panel_x + panel_width and
                    panel_y <= pos[1] <= panel_y + panel_height):
                return True  # 点击在面板内，不关闭
            else:
                # 点击在面板外，关闭帮助
                self.visible = False
                return True
        return False

    def handle_keydown(self, key):
        """
        处理键盘事件
        """
        if not self.visible:
            return False

        handled = False

        if key == pygame.K_LEFT or key == pygame.K_UP:
            # 上一页
            if self.current_page > 0:
                self.current_page -= 1
                handled = True
        elif key == pygame.K_RIGHT or key == pygame.K_DOWN:
            # 下一页
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
                handled = True
        elif key == pygame.K_HOME:
            # 第一页
            self.current_page = 0
            handled = True
        elif key == pygame.K_END:
            # 最后一页
            self.current_page = self.total_pages - 1
            handled = True
        elif key == pygame.K_h or key == pygame.K_ESCAPE:
            # 关闭帮助
            self.visible = False
            handled = True

        if handled:
            print(f"帮助面板: 按键 {key} 已处理，当前页 {self.current_page + 1}/{self.total_pages}")

        return handled

    def update_instructions(self, current_mode, point_count):
        """
        更新操作说明中的实时信息

        Args:
            current_mode: 当前模式 ("添加" 或 "编辑")
            point_count: 控制点数量
        """
        # 如果需要，可以在这里更新操作说明的实时信息
        pass