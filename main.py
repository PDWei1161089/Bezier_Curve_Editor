import pygame
import sys
import os
import json

# 导入算法模块
from src.algorithms.bezier_curve import BezierCurve
from src.algorithms.recursive_bezier import RecursiveBezier
from src.algorithms.vector_bezier import VectorBezier
from src.algorithms.dynamic_bezier import DynamicBezier
from src.algorithms.bernstein_window import BernsteinWindow

# 导入核心模块
from src.core.sound_manager import SoundManager
from src.core.config import ChineseText
from src.core.font_loader import FontLoader

# 导入工具模块
from src.utils.help_module import HelpModule
from src.utils.create_sounds import create_all_sounds

# 导入演示模块
from src.demo.demo_3d import Demo3D

# 添加src到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# ==================== 修复版资源路径处理 ====================
def get_resource_path(relative_path):
    """
    修复版资源路径获取函数
    返回资源的绝对路径，适用于打包和开发环境
    """
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境
        base_path = os.path.abspath(".")

    # 构建完整路径
    full_path = os.path.join(base_path, relative_path)

    # 标准化路径
    full_path = os.path.normpath(full_path)

    # 调试信息（打包时可以注释掉）
    # print(f"资源路径: {full_path}")
    # print(f"文件存在: {os.path.exists(full_path)}")

    return full_path


# ==================== 资源加载辅助函数 ====================
def load_image(filename):
    """加载图片文件 - 使用 get_resource_path"""
    # 构建图片路径
    image_path = get_resource_path(f"resources/icons/{filename}")

    print(f"加载图片: {image_path}")
    print(f"文件存在: {os.path.exists(image_path)}")

    if os.path.exists(image_path):
        try:
            return pygame.image.load(image_path)
        except pygame.error as e:
            print(f"加载图片失败: {e}")
            return None
    else:
        # 尝试旧路径（兼容性）
        old_path = get_resource_path(f"assets/icons/{filename}")
        if os.path.exists(old_path):
            try:
                return pygame.image.load(old_path)
            except pygame.error as e:
                print(f"加载旧路径图片失败: {e}")
        return None


def load_music_path(filename):
    """获取音乐文件路径 - 使用 get_resource_path"""
    music_path = get_resource_path(f"resources/sounds/{filename}")

    print(f"音乐文件路径: {music_path}")
    print(f"文件存在: {os.path.exists(music_path)}")

    if os.path.exists(music_path):
        return music_path
    else:
        # 尝试旧路径
        old_path = get_resource_path(f"sounds/{filename}")
        if os.path.exists(old_path):
            return old_path
        return None


def initialize_resources_debug():
    """初始化资源调试信息"""
    print("=" * 60)
    print("资源路径调试信息")
    print("=" * 60)

    # 使用 get_resource_path 测试各种资源
    test_paths = [
        ("图标目录", "resources/icons"),
        ("声音目录", "resources/sounds"),
        ("字体目录", "resources/fonts"),
        ("旧声音目录", "sounds"),
        ("旧图标目录", "assets/icons"),
    ]

    for name, relative_path in test_paths:
        full_path = get_resource_path(relative_path)
        exists = os.path.exists(full_path)
        status = "✅" if exists else "❌"
        print(f"{status} {name}: {full_path}")

        if exists:
            print(f"  目录内容:")
            try:
                for item in os.listdir(full_path):
                    item_path = os.path.join(full_path, item)
                    is_file = os.path.isfile(item_path)
                    print(f"    {'📄' if is_file else '📁'} {item}")
            except Exception as e:
                print(f"    读取失败: {e}")

    print("=" * 60)

class ModeButton:
    """模式切换按钮"""

    def __init__(self, x, y, width=120, height=40, text="", mode_id=""):
        """
        初始化模式按钮

        Args:
            x, y: 按钮位置
            width: 按钮宽度
            height: 按钮高度
            text: 按钮文本
            mode_id: 模式标识
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.mode_id = mode_id
        self.active = False
        self.hovered = False

        # 颜色
        self.active_color = (70, 130, 180)  # 激活状态
        self.inactive_color = (60, 60, 80)  # 非激活状态
        self.hover_color = (100, 160, 210)  # 悬停状态
        self.text_color = (255, 255, 255)
        self.border_color = (255, 255, 255)

    def draw(self, screen, font):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        # 确定颜色
        if self.active:
            bg_color = self.active_color
        elif self.hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.inactive_color

        # 绘制按钮背景
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=8)

        # 绘制文本
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

        return self.hovered

    def handle_click(self, pos):
        """处理点击"""
        return self.rect.collidepoint(pos)


class ControlButton:
    """控制按钮（用于递归模式）"""

    def __init__(self, x, y, width=120, height=25, text="", tooltip=""):
        """
        初始化控制按钮

        Args:
            x, y: 按钮位置
            width: 按钮宽度
            height: 按钮高度
            text: 按钮文本
            tooltip: 提示文本
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.tooltip = tooltip
        self.hovered = False
        self.clicked = False

        # 颜色
        self.normal_color = (80, 140, 190)
        self.hover_color = (110, 170, 220)
        self.text_color = (255, 255, 255)

    def draw(self, screen, font):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        # 确定颜色
        bg_color = self.hover_color if self.hovered else self.normal_color

        # 绘制按钮背景
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 1, border_radius=6)

        # 绘制文本
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

        # 绘制工具提示
        if self.hovered and self.tooltip:
            self.draw_tooltip(screen, font)

        return self.hovered

    def draw_tooltip(self, screen, font):
        """绘制工具提示"""
        tooltip_font = pygame.font.Font(None, 14)
        text_surf = tooltip_font.render(self.tooltip, True, (255, 255, 255))
        text_rect = text_surf.get_rect()

        # 工具提示位置（按钮下方）
        tooltip_rect = pygame.Rect(
            self.rect.centerx - text_rect.width // 2,
            self.rect.bottom + 5,
            text_rect.width + 10,
            18
        )

        # 绘制背景
        pygame.draw.rect(screen, (40, 40, 60), tooltip_rect, border_radius=4)
        pygame.draw.rect(screen, (100, 100, 120), tooltip_rect, 1, border_radius=4)

        # 绘制文字
        screen.blit(text_surf, (tooltip_rect.x + 5, tooltip_rect.y + 2))

    def handle_click(self, pos):
        """处理点击"""
        if self.rect.collidepoint(pos):
            self.clicked = True
            return True
        return False


class SoundButton:
    """音效控制按钮类"""

    def __init__(self, x, y, size=40, sound_manager=None, font=None):
        """
        初始化音效按钮

        Args:
            x, y: 按钮位置
            size: 按钮大小
            sound_manager: 音效管理器实例
            font: 字体对象（用于工具提示）
        """
        self.rect = pygame.Rect(x, y, size, size)
        self.sound_manager = sound_manager
        self.size = size
        self.tooltip_font = font  # 工具提示字体

        # 加载图标
        self.icons = self.load_icons()

        # 按钮状态
        self.hovered = False
        self.clicked = False

    def load_icons(self):
        """加载图标文件"""
        icons = {}

        # 图标文件映射 - 使用新的 resources/icons 目录
        icon_files = {
            'sound_on': "resources/icons/sound_on.png",
            'sound_off': "resources/icons/sound_off.png",
            'music_on': "resources/icons/music_on.png",
            'music_off': "resources/icons/music_off.png",
            'zoom_in': "resources/icons/zoom_in.png",
            'zoom_out': "resources/icons/zoom_out.png",
            'zoom_reset': "resources/icons/zoom_reset.png",
        }

        # 加载每个图标
        for icon_name, relative_path in icon_files.items():
            icon_path = get_resource_path(relative_path)

            if os.path.exists(icon_path):
                try:
                    icon = pygame.image.load(icon_path)
                    # 转换格式以确保透明度正确
                    icon = icon.convert_alpha()
                    # 缩放到指定大小
                    icons[icon_name] = pygame.transform.scale(
                        icon, (self.size, self.size)
                    )
                    print(f"✅ 加载图标成功: {icon_name} -> {icon_path}")
                except Exception as e:
                    print(f"❌ 加载图标失败 {icon_path}: {e}")
                    # 图标加载失败时，使用备用颜色块
                    icons[icon_name] = self.create_fallback_icon(icon_name)
            else:
                print(f"⚠ 图标文件不存在: {icon_path}")
                # 图标文件不存在时，使用备用颜色块
                icons[icon_name] = self.create_fallback_icon(icon_name)

        return icons

    def create_fallback_icon(self, icon_name):
        """创建备用图标（当图标文件无法加载时）"""
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        # 根据图标名称设置不同颜色
        if 'sound' in icon_name:
            if 'on' in icon_name:
                color = (100, 200, 100)  # 绿色
                text = "音效开"
            else:
                color = (200, 100, 100)  # 红色
                text = "音效关"
        else:  # music
            if 'on' in icon_name:
                color = (100, 150, 200)  # 蓝色
                text = "音乐开"
            else:
                color = (150, 150, 150)  # 灰色
                text = "音乐关"

        # 绘制圆形背景
        pygame.draw.circle(surface, color,
                           (self.size // 2, self.size // 2),
                           self.size // 2 - 2)

        # 绘制文字
        font = pygame.font.Font(None, 12)
        text_surf = font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.size // 2, self.size // 2))
        surface.blit(text_surf, text_rect)

        return surface

    def draw(self, screen):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        # 绘制按钮背景
        bg_color = (80, 80, 100) if self.hovered else (60, 60, 80)
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (120, 120, 140) if self.hovered else (100, 100, 120),
                         self.rect, 2, border_radius=8)

        # 绘制图标
        if self.sound_manager:
            sound_on = self.sound_manager.sound_enabled
            music_on = self.sound_manager.music_enabled
        else:
            sound_on = True
            music_on = True

        # 根据按钮类型绘制相应图标
        if hasattr(self, 'button_type'):
            if self.button_type == 'sound':
                icon = self.icons['sound_on' if sound_on else 'sound_off']
            else:  # music
                icon = self.icons['music_on' if music_on else 'music_off']
            screen.blit(icon, self.rect)
        else:
            # 默认绘制音效图标
            icon = self.icons['sound_on' if sound_on else 'sound_off']
            screen.blit(icon, self.rect)

        # 绘制提示文本（悬停时）
        if self.hovered and hasattr(self, 'tooltip') and self.tooltip_font:
            self.draw_tooltip(screen)

    def draw_tooltip(self, screen):
        """绘制工具提示"""
        if not self.tooltip_font:
            return

        text_surf = self.tooltip_font.render(self.tooltip, True, (255, 255, 255))
        text_rect = text_surf.get_rect()

        # 工具提示位置（按钮上方）
        tooltip_rect = pygame.Rect(
            self.rect.centerx - text_rect.width // 2,
            self.rect.top - 25,
            text_rect.width + 10,
            20
        )

        # 绘制背景
        pygame.draw.rect(screen, (40, 40, 60), tooltip_rect, border_radius=4)
        pygame.draw.rect(screen, (100, 100, 120), tooltip_rect, 1, border_radius=4)

        # 绘制文字
        screen.blit(text_surf, (tooltip_rect.x + 5, tooltip_rect.y + 2))

    def handle_click(self, pos):
        """
        处理点击事件

        Returns:
            bool: 如果点击了按钮返回True，否则返回False
        """
        if self.rect.collidepoint(pos):
            self.clicked = True
            if self.sound_manager:
                if self.button_type == 'sound':
                    self.sound_manager.toggle_sound()
                    self.sound_manager.play_sound('click')
                else:  # music
                    self.sound_manager.toggle_music()
                    self.sound_manager.play_sound('click')
            return True
        return False

    def update(self, sound_manager=None, font=None):
        """更新按钮状态"""
        if sound_manager:
            self.sound_manager = sound_manager
        if font:
            self.tooltip_font = font


class VolumeSlider:
    """音量滑块控件"""

    def __init__(self, x, y, width=100, height=10, initial_volume=0.7, sound_manager=None, label=""):
        """
        初始化音量滑块

        Args:
            x, y: 滑块位置
            width: 滑块宽度
            height: 滑块高度
            initial_volume: 初始音量
            sound_manager: 音效管理器
            label: 滑块标签文本
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.slider_width = 20
        self.volume = initial_volume
        self.sound_manager = sound_manager
        self.dragging = False
        self.label = label

    def draw(self, screen, font):
        """绘制滑块和标签"""
        if self.label and font:
            # 绘制标签 - 调整位置
            label_surf = font.render(self.label, True, (220, 220, 220))
            label_x = self.rect.x - label_surf.get_width() - 5  # 从-10改为-5，更紧凑
            label_y = self.rect.centery - label_surf.get_height() // 2
            screen.blit(label_surf, (label_x, label_y))

        # 绘制背景轨道
        pygame.draw.rect(screen, (80, 80, 100), self.rect, border_radius=5)
        pygame.draw.rect(screen, (120, 120, 140), self.rect, 1, border_radius=5)

        # 绘制填充部分
        fill_width = int(self.volume * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, (100, 180, 100), fill_rect, border_radius=5)

        # 绘制滑块手柄
        slider_x = self.rect.x + int(self.volume * self.rect.width) - self.slider_width // 2
        slider_rect = pygame.Rect(slider_x, self.rect.y - 5,
                                  self.slider_width, self.rect.height + 10)
        pygame.draw.rect(screen, (200, 200, 220), slider_rect, border_radius=6)
        pygame.draw.rect(screen, (150, 150, 170), slider_rect, 2, border_radius=6)

    def handle_event(self, event):
        """处理滑块事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_volume_from_mouse(event.pos[0])
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_volume_from_mouse(event.pos[0])
            return True

        return False

    def update_volume_from_mouse(self, mouse_x):
        """根据鼠标位置更新音量"""
        # 计算音量值
        relative_x = max(0, min(self.rect.width, mouse_x - self.rect.x))
        self.volume = relative_x / self.rect.width

        # 更新音效管理器
        if self.sound_manager:
            if hasattr(self, 'volume_type'):
                if self.volume_type == 'sound':
                    self.sound_manager.set_sound_volume(self.volume)
                else:  # music
                    self.sound_manager.set_music_volume(self.volume)


class DraggablePanel:
    """可拖拽面板基类"""

    def __init__(self, x, y, width, height, title="", show_title=True):
        """
        初始化可拖拽面板

        Args:
            x, y: 面板位置
            width, height: 面板尺寸
            title: 面板标题
            show_title: 是否显示标题栏
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.original_width = width
        self.original_height = height
        self.title = title
        self.show_title = show_title
        self.title_height = 25 if show_title else 0

        # 拖拽状态
        self.dragging = False
        self.drag_offset = (0, 0)
        self.drag_handle_height = self.title_height  # 拖拽区域高度

        # 拖拽把手（标题栏或右上角小把手）
        if self.show_title:
            self.drag_handle_rect = pygame.Rect(
                x, y, width, self.title_height
            )
        else:
            # 如果不显示标题，在右上角添加小拖拽把手
            self.drag_handle_rect = pygame.Rect(
                x + width - 25, y, 25, 25
            )

        # 关闭按钮（可选）
        self.close_button_rect = None
        self.show_close_button = False

        # 面板可见性
        self.visible = True

        # 颜色
        self.bg_color = (40, 40, 60, 200)
        self.border_color = (100, 100, 150)
        self.title_bg_color = (60, 60, 80, 220)
        self.title_text_color = (255, 255, 100)
        self.drag_handle_color = (100, 150, 200)

    # 在DraggablePanel类的handle_event方法中添加调试信息：
    def handle_event(self, event):
        """
        处理面板事件

        Returns:
            bool: 如果事件被处理返回True，否则返回False
        """
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            print(f"面板 '{self.title}' 鼠标点击检查:")
            print(f"  鼠标位置: {mouse_pos}")
            print(f"  拖拽区域: {self.drag_handle_rect}")
            print(f"  是否在区域内: {self.drag_handle_rect.collidepoint(mouse_pos)}")

            if self.drag_handle_rect.collidepoint(mouse_pos):
                self.dragging = True
                self.drag_offset = (mouse_pos[0] - self.rect.x,
                                    mouse_pos[1] - self.rect.y)
                print(f"开始拖拽面板: {self.title}")
                print(f"拖拽偏移: {self.drag_offset}")
                return True

            # 检查关闭按钮点击
            if self.show_close_button and self.close_button_rect:
                if self.close_button_rect.collidepoint(mouse_pos):
                    self.visible = False
                    return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                print(f"结束拖拽面板: {self.title}")
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # 计算新位置，确保面板在窗口内
            new_x = event.pos[0] - self.drag_offset[0]
            new_y = event.pos[1] - self.drag_offset[1]

            # 限制面板在窗口内
            new_x = max(0, min(new_x, pygame.display.get_surface().get_width() - self.rect.width))
            new_y = max(0, min(new_y, pygame.display.get_surface().get_height() - self.rect.height))

            self.rect.x = new_x
            self.rect.y = new_y
            self.update_handle_position()
            print(f"拖拽中面板: {self.title}, 新位置=({new_x}, {new_y})")
            return True

        return False

    def update_handle_position(self):
        """更新拖拽把手位置"""
        if self.show_title:
            self.drag_handle_rect.x = self.rect.x
            self.drag_handle_rect.y = self.rect.y
            self.drag_handle_rect.width = self.rect.width
            self.drag_handle_rect.height = self.title_height
        else:
            self.drag_handle_rect.x = self.rect.x + self.rect.width - 25
            self.drag_handle_rect.y = self.rect.y
            self.drag_handle_rect.width = 25
            self.drag_handle_rect.height = 25

        # 更新关闭按钮位置
        if self.show_close_button:
            self.close_button_rect = pygame.Rect(
                self.rect.x + self.rect.width - 25,
                self.rect.y + (self.title_height - 20) // 2 if self.show_title else self.rect.y,
                20, 20
            )

    def draw_drag_handle(self, surface, font=None):
        """绘制拖拽把手"""
        if not self.visible:
            return

        if self.show_title:
            # 绘制标题栏作为拖拽区域
            pygame.draw.rect(surface, self.title_bg_color, self.drag_handle_rect)
            pygame.draw.rect(surface, self.border_color, self.drag_handle_rect, 1)

            # 绘制标题文本
            if font and self.title:
                title_text = font.render(self.title, True, self.title_text_color)
                text_x = self.drag_handle_rect.x + 10
                text_y = self.drag_handle_rect.y + (self.title_height - title_text.get_height()) // 2
                surface.blit(title_text, (text_x, text_y))

            # 在标题栏右侧绘制拖拽图标
            self.draw_drag_indicator(surface,
                                     self.drag_handle_rect.x + self.drag_handle_rect.width - 40,
                                     self.drag_handle_rect.y + 5
                                     )
        else:
            # 绘制小拖拽把手
            pygame.draw.rect(surface, self.drag_handle_color, self.drag_handle_rect, border_radius=4)
            pygame.draw.rect(surface, (255, 255, 255), self.drag_handle_rect, 1, border_radius=4)
            self.draw_drag_indicator(surface,
                                     self.drag_handle_rect.x + 4,
                                     self.drag_handle_rect.y + 4
                                     )

    def draw_drag_indicator(self, surface, x, y):
        """绘制拖拽指示器（四个点）"""
        # 绘制四个小点，表示可拖拽
        dot_size = 3
        dot_spacing = 5

        positions = [
            (x, y),
            (x + dot_spacing, y),
            (x, y + dot_spacing),
            (x + dot_spacing, y + dot_spacing),
        ]

        for pos in positions:
            pygame.draw.circle(surface, (255, 255, 255), pos, dot_size)

    def draw_close_button(self, surface):
        """绘制关闭按钮"""
        if not self.visible or not self.show_close_button or not self.close_button_rect:
            return

        # 绘制关闭按钮背景
        pygame.draw.rect(surface, (200, 80, 80), self.close_button_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 120, 120), self.close_button_rect, 1, border_radius=4)

        # 绘制X符号
        center_x = self.close_button_rect.x + self.close_button_rect.width // 2
        center_y = self.close_button_rect.y + self.close_button_rect.height // 2

        # 绘制斜线
        line_length = 6
        pygame.draw.line(surface, (255, 255, 255),
                         (center_x - line_length, center_y - line_length),
                         (center_x + line_length, center_y + line_length), 2)
        pygame.draw.line(surface, (255, 255, 255),
                         (center_x + line_length, center_y - line_length),
                         (center_x - line_length, center_y + line_length), 2)

    def draw_background(self, surface):
        """绘制面板背景"""
        if not self.visible:
            return

        # 创建带透明度的表面
        panel_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        panel_surface.fill(self.bg_color)

        # 绘制边框
        pygame.draw.rect(panel_surface, self.border_color,
                         (0, 0, self.rect.width, self.rect.height), 2)

        # 绘制到主表面
        surface.blit(panel_surface, (self.rect.x, self.rect.y))

    def draw(self, surface, font=None):
        """绘制整个面板"""
        if not self.visible:
            return

        # 绘制背景
        self.draw_background(surface)

        # 绘制拖拽把手
        self.draw_drag_handle(surface, font)

        # 绘制关闭按钮
        if self.show_close_button:
            self.draw_close_button(surface)

    def set_position(self, x, y):
        """设置面板位置"""
        self.rect.x = x
        self.rect.y = y
        self.update_handle_position()

    def toggle_visibility(self):
        """切换面板可见性"""
        self.visible = not self.visible

    def enable_close_button(self, enabled=True):
        """启用或禁用关闭按钮"""
        self.show_close_button = enabled
        if enabled:
            self.update_handle_position()


class BezierApp:
    def __init__(self):
        pygame.init()

        # 显示资源调试信息
        initialize_resources_debug()

        # 窗口设置
        self.width, self.height = 1200, 800  # 进一步增加宽度
        self.screen = pygame.display.set_mode((self.width, self.height))

        # 设置中文窗口标题
        pygame.display.set_caption(ChineseText.WINDOW_TITLE)

        # ====== 新增：设置窗口图标 ======
        try:
            # 使用你的修复版资源路径函数
            icon_path = get_resource_path("assets/icon.ico")

            print(f"尝试加载图标: {icon_path}")
            print(f"图标文件存在: {os.path.exists(icon_path)}")

            if os.path.exists(icon_path):
                # 加载图标
                icon = pygame.image.load(icon_path)
                # 设置窗口图标
                pygame.display.set_icon(icon)
                print("✅ 窗口图标设置成功")
            else:
                print("⚠ 警告: 图标文件未找到，将使用默认图标")
                # 可以创建一个简单的图标作为备用
                # self.create_fallback_icon()

        except Exception as e:
            print(f"❌ 设置窗口图标失败: {e}")
        # ====== 图标设置结束 ======

        # 颜色定义
        self.BG_COLOR = (30, 30, 50)
        # self.BG_COLOR = (250, 250, 245)
        self.TEXT_COLOR = (220, 220, 220)
        self.INFO_BG = (40, 40, 60)

        # 初始化中文字体
        self.font = None
        self.small_font = None
        self.chinese_available = False
        self.init_chinese_fonts()  # 现在调用字体初始化

        # 创建Bezier曲线对象
        self.bezier_curve = BezierCurve()

        # 创建递归构造对象
        self.recursive_bezier = RecursiveBezier()

        # 创建向量表示对象
        self.vector_bezier = VectorBezier()

        # 创建动力学分析对象
        self.dynamic_bezier = DynamicBezier()

        # 创建3D演示对象
        self.demo_3d = Demo3D()
        self.demo_3d_initialized = False

        # 动力学模式是否初始化
        self.dynamic_initialized = False

        # 创建缩放管理器
        self.scale_manager = ScaleManager()

        # 缩放按钮状态
        self.show_zoom_controls = True

        # 向量模式是否初始化
        self.vector_initialized = False

        # 创建可拖拽面板
        self.audio_panel = DraggablePanel(
            x=10,
            y=self.height - 160 - 60,  # 音频面板位置
            width=200,
            height=160,
            title=ChineseText.AUDIO_CONTROLS,
            show_title=True
        )
        self.audio_panel.show_close_button = False  # 音频面板不需要关闭按钮

        self.recursive_panel = DraggablePanel(
            x=230,  # 递归面板位置
            y=self.height - 160 - 60,
            width=240,
            height=160,
            title=ChineseText.RECURSIVE_CONTROLS,
            show_title=True
        )
        self.recursive_panel.show_close_button = False

        self.vector_panel = DraggablePanel(
            x=500,  # 向量面板位置
            y=self.height - 280 - 60,  # 调整y位置
            width=300,
            height=320,  # 增加高度以容纳更多按钮
            title=ChineseText.VECTOR_CONTROLS,
            show_title=True
        )
        self.vector_panel.show_close_button = False

        # 动力学控制面板
        self.dynamic_panel = DraggablePanel(
            x=800,  # 动力学面板位置
            y=self.height - 280 - 60,
            width=300,
            height=280,
            title="动力学控制(F7)",
            show_title=True
        )
        self.dynamic_panel.show_close_button = False
        # 确保拖拽区域更新
        self.dynamic_panel.update_handle_position()

        # 在 Bernstein 窗口面板后面添加数据面板
        self.bernstein_data_panel = DraggablePanel(
            x=self.width - 470,  # 默认位置（和Bernstein窗口对齐）
            y=430,  # Bernstein窗口下方
            width=470,  # 宽度和Bernstein窗口一致
            height=320,  # 高度根据基函数数量动态调整
            title="Bernstein基函数数据",
            show_title=True
        )
        self.bernstein_data_panel.show_close_button = True
        self.bernstein_data_panel.visible = False  # 默认隐藏

        # 3D控制面板
        self.demo_3d_panel = DraggablePanel(
            x=950,  # 3D面板位置
            y=self.height - 180 - 60,
            width=220,
            height=180,
            title="3D演示控制(F9)",
            show_title=True
        )
        self.demo_3d_panel.show_close_button = False
        self.demo_3d_panel.visible = True  # 默认显示

        # 在创建其他面板之后，添加基本信息面板
        self.info_panel = DraggablePanel(
            x=self.width - 300,  # 默认位置（右上角）
            y=180,  # 与原来的 info_y 保持一致
            width=280,  # 与原来的 info_width 一致
            height=140,  # 与原来的 info_height 一致
            title=ChineseText.BASIC_INFO,
            show_title=True
        )
        self.info_panel.show_close_button = False  # 不需要关闭按钮
        self.info_panel.visible = True  # 默认可见

        # 初始化中文字体
        self.font = None
        self.small_font = None
        self.chinese_available = False
        self.init_chinese_fonts()

        # 创建Bernstein窗口
        self.bernstein_window = BernsteinWindow(450, 300, self.font, self.small_font)
        self.bernstein_window.visible = False
        self.bernstein_window_position = (self.width - 470, 100)  # 默认位置

        # 创建音效管理器 - 使用修复版路径函数
        self.sound_manager = SoundManager("sounds")
        self.sound_manager.play_background_music()

        # 创建模式切换按钮
        self.mode_buttons = [
            ModeButton(10, 10, 120, 40, ChineseText.MODE_CREATE, "create"),
            ModeButton(140, 10, 120, 40, ChineseText.MODE_RECURSIVE, "recursive"),
            ModeButton(270, 10, 120, 40, ChineseText.MODE_VECTOR, "vector"),  # 新增向量模式
            ModeButton(400, 10, 150, 40, ChineseText.MODE_DYNAMIC, "dynamic"),
            ModeButton(560, 10, 120, 40, "3D演示(5)", "3ddemo")
        ]

        self.current_mode = "create"  # 当前模式
        self.mode_buttons[0].active = True  # 默认选中创建模式

        # 创建音效控制按钮
        self.sound_button = SoundButton(self.width - 50, 10, size=40,
                                        sound_manager=self.sound_manager,
                                        font=self.small_font)
        self.sound_button.button_type = 'sound'
        self.sound_button.tooltip = "开关音效 (S)"

        self.music_button = SoundButton(self.width - 100, 10, size=40,
                                        sound_manager=self.sound_manager,
                                        font=self.small_font)
        self.music_button.button_type = 'music'
        self.music_button.tooltip = "开关音乐 (M)"

        # 控制面板显示状态
        self.show_audio_controls = True
        self.show_recursive_controls = True
        self.show_vector_controls = True

        # 创建音量滑块 - 放在左侧
        sound_vol, music_vol = self.sound_manager.get_volume_level()
        self.sound_slider = VolumeSlider(self.width - 150, 60, width=80,
                                         initial_volume=sound_vol,
                                         sound_manager=self.sound_manager,
                                         label=ChineseText.SOUND_LABEL)
        self.sound_slider.volume_type = 'sound'

        self.music_slider = VolumeSlider(self.width - 150, 90, width=80,
                                         initial_volume=music_vol,
                                         sound_manager=self.sound_manager,
                                         label=ChineseText.MUSIC_LABEL)
        self.music_slider.volume_type = 'music'

        # 递归模式控制按钮 - 放在左侧，分开布局
        self.recursive_buttons = [
            ControlButton(self.width - 350, 60, 95, 25,  # 宽度改为95
                          ChineseText.PREV_STEP, ChineseText.PREV_STEP_TOOLTIP),
            ControlButton(self.width - 350, 95, 95, 25,  # 宽度改为95
                          ChineseText.NEXT_STEP, ChineseText.NEXT_STEP_TOOLTIP),
            ControlButton(self.width - 350, 130, 95, 25,  # 宽度改为95
                          ChineseText.RESET, ChineseText.RESET_TOOLTIP),
            ControlButton(self.width - 350, 165, 95, 25,  # 宽度改为95
                          ChineseText.TOGGLE_CONSTRUCTION, ChineseText.TOGGLE_CONSTRUCTION_TOOLTIP)
        ]

        # 递归模式参数滑块 - 放在左侧
        self.ratio_slider = VolumeSlider(self.width - 350, 200, width=100,
                                         initial_volume=0.5,
                                         sound_manager=None,
                                         label="")

        # 动力学模式参数滑块
        self.dynamic_t_slider = VolumeSlider(self.width - 350, 200, width=100,
                                             initial_volume=0.5,
                                             sound_manager=None,
                                             label="")

        # 向量模式控制按钮 - 恢复关键功能
        self.vector_buttons = [
            ControlButton(self.width - 350, 60, 90, 25,
                          ChineseText.TOGGLE_VECTORS, "V"),
            ControlButton(self.width - 350, 95, 90, 25,
                          ChineseText.TOGGLE_CURVE, "C"),
            ControlButton(self.width - 350, 130, 90, 25,
                          ChineseText.ADJUST_ORIGIN, "O"),  # 恢复调整原点
            ControlButton(self.width - 350, 165, 90, 25,
                          ChineseText.RESET_ORIGIN, "R"),  # 恢复重置原点
            ControlButton(self.width - 350, 200, 90, 25,
                          ChineseText.TOGGLE_VECTOR_MODE, ChineseText.TOGGLE_VECTOR_MODE_TOOLTIP)
        ]
        print("向量按钮初始化:")
        for i, button in enumerate(self.vector_buttons):
            print(f"  按钮{i}: {button.text}")
        self.bernstein_data_button = ControlButton(self.width - 250, 70, 120, 25,
                                                   "基函数数据(D)", "D")

        # 3D控制按钮
        self.demo_3d_buttons = [
            ControlButton(0, 0, 0, 25, "重置视角(R)", "R"),
            ControlButton(0, 0, 0, 25, "重新生成Z(Z)", "Z"),
            ControlButton(0, 0, 0, 25, "显示/隐藏立方体(L)", "L"),
            ControlButton(0, 0, 0, 25, "显示/隐藏坐标轴(B)", "B")
        ]

        # 视角控制键说明
        self.view_controls_text = []

        # 添加缩放按钮
        self.zoom_in_button = ControlButton(self.width - 450, 10, 40, 25, "+", "放大")
        self.zoom_out_button = ControlButton(self.width - 500, 10, 40, 25, "-", "缩小")
        self.zoom_reset_button = ControlButton(self.width - 550, 10, 50, 25, "重置", "重置缩放")

        # Bernstein窗口控制按钮
        self.bernstein_button = ControlButton(self.width - 250, 40, 120, 25,
                                              ChineseText.BERNSTEIN_WINDOW, "W")

        # 向量模式参数滑块
        self.vector_t_slider = VolumeSlider(self.width - 350, 200, width=100,
                                            initial_volume=0.5,
                                            sound_manager=None,
                                            label="")

        self.vector_window_button = ControlButton(self.width - 250, 100, 120, 25,
                                                  "向量窗口(W)", "W")

        # 创建帮助模块
        self.help_module = HelpModule(self.font, self.small_font, ChineseText.HELP_CONTENT)

        # 状态
        self.running = True
        self.drawing_mode = True  # True: 添加模式, False: 编辑模式
        # self.show_info = True
        self.recursive_initialized = False
        self.vector_initialized = False
        self.adjusting_origin = False  # 新增：是否正在调整原点

        # 调整后的位置（更靠右侧）
        self.zoom_buttons = [
            ZoomButton(self.width - 250, 10, 40, "zoom_in.png",
                       ChineseText.ZOOM_IN_TOOLTIP, self.scale_manager),
            ZoomButton(self.width - 200, 10, 40, "zoom_out.png",
                       ChineseText.ZOOM_OUT_TOOLTIP, self.scale_manager),
            ZoomButton(self.width - 150, 10, 40, "zoom_reset.png",
                       ChineseText.ZOOM_RESET_TOOLTIP, self.scale_manager)
        ]

    def init_chinese_fonts(self):
        """初始化中文字体"""
        self.font, self.small_font, self.chinese_available = FontLoader.load_chinese_fonts()

        # 添加调试信息
        print("=" * 50)
        print("字体加载状态:")
        print(f"主字体类型: {type(self.font)}")
        print(f"小字体类型: {type(self.small_font)}")
        print(f"中文可用: {self.chinese_available}")

        # 测试字体渲染
        if self.font:
            try:
                test_text = "中文测试"
                test_surface = self.font.render(test_text, True, (255, 255, 255))
                print(f"✓ 主字体渲染测试: '{test_text}' 成功")
            except Exception as e:
                print(f"✗ 主字体渲染失败: {e}")

        print("=" * 50)

        if self.chinese_available:
            print("✓ 中文显示已启用")
        else:
            print("⚠ 中文显示不可用，将显示英文文本")

    def switch_mode(self, new_mode):
        """切换模式"""
        if new_mode == self.current_mode:
            return

        self.current_mode = new_mode

        # 更新按钮激活状态
        for button in self.mode_buttons:
            button.active = (button.mode_id == new_mode)

        # 播放音效
        self.sound_manager.play_sound('mode_switch')

        # 如果切换到递归模式，初始化递归构造
        if new_mode == "recursive":
            if len(self.bezier_curve.control_points) >= 2:
                self.recursive_bezier.set_control_points(self.bezier_curve.control_points)
                self.recursive_initialized = True
                print("✓ 切换到递归构造模式")
                print(f"控制点数量: {len(self.bezier_curve.control_points)}")
                print(f"初始递归层级: 0/{len(self.bezier_curve.control_points) - 1}")

                # 显示初始状态
                status = self.recursive_bezier.get_status()
                print(f"状态: 已完成={status['completed']}, 显示构造={status['show_construction']}")
            else:
                print("✗ 需要至少2个控制点才能使用递归构造模式")
                # 如果没有足够点，切回创建模式
                self.switch_mode("create")

        # 新增：如果切换到向量模式
        elif new_mode == "vector":
            if len(self.bezier_curve.control_points) >= 2:
                self.vector_bezier.set_control_points(self.bezier_curve.control_points)
                self.vector_initialized = True
                print("✓ 切换到向量表示模式")
                print(f"控制点数量: {len(self.bezier_curve.control_points)}")
                print(f"当前向量模式: {self.vector_bezier.get_vector_mode_text()}")

                # 更新Bernstein窗口
                self.bernstein_window.set_n(len(self.bezier_curve.control_points) - 1)
                self.bernstein_window.set_t(0.5)
            else:
                print("✗ 需要至少2个控制点才能使用向量表示模式")
                self.switch_mode("create")

        # 新增：如果切换到动力学模式
        elif new_mode == "dynamic":
            if len(self.bezier_curve.control_points) >= 2:
                self.dynamic_bezier.set_control_points(self.bezier_curve.control_points)
                self.dynamic_initialized = True

                # 设置滑块初始值为动力学模式的当前t值
                self.dynamic_t_slider.volume = self.dynamic_bezier.t_value

                print("✓ 切换到动力学分析模式")
                print(f"控制点数量: {len(self.bezier_curve.control_points)}")
            else:
                print("✗ 需要至少2个控制点才能使用动力学分析模式")
                self.switch_mode("create")


        elif new_mode == "3ddemo":

            if len(self.bezier_curve.control_points) >= 2:

                # 首先将2D点限制在0-255范围内

                limited_points = []

                for x, y in self.bezier_curve.control_points:
                    # 限制在0-255范围内（RGB立方体的范围）

                    limited_x = max(0, min(x, 255))

                    limited_y = max(0, min(y, 255))

                    limited_points.append((limited_x, limited_y))

                self.demo_3d.set_control_points(limited_points)

                self.demo_3d_initialized = True

                print("✓ 切换到3D演示模式")

                print(f"控制点数量: {len(limited_points)}")

                self.demo_3d.print_debug_info()

            else:

                print("✗ 需要至少2个控制点才能使用3D演示模式")

                self.switch_mode("create")

        else:
            self.recursive_initialized = False
            self.vector_initialized = False
            print("切换到创建模式")

    def draw_info_panel(self):
        """绘制基本信息面板（现在可拖拽）"""
        if not self.info_panel.visible:  # 使用面板的可见性
            return

        # 使用面板的位置和尺寸
        info_x = self.info_panel.rect.x
        info_y = self.info_panel.rect.y
        info_width = self.info_panel.rect.width
        info_height = self.info_panel.rect.height

        # 先绘制面板背景（由DraggablePanel处理）
        self.info_panel.draw(self.screen, self.small_font)

        # 计算内容区域（考虑标题栏高度）
        content_x = info_x + 10
        content_y = info_y + self.info_panel.title_height + 10
        content_width = info_width - 20

        # 当前模式
        if self.current_mode == "create":
            mode_text = ChineseText.MODE_ADD if self.drawing_mode else ChineseText.MODE_EDIT
            mode_color = (100, 255, 100) if self.drawing_mode else (255, 100, 100)
        elif self.current_mode == "recursive":
            mode_text = ChineseText.MODE_RECURSIVE_TEXT
            mode_color = (180, 255, 180)
        elif self.current_mode == "vector":
            mode_text = "向量表示模式"
            mode_color = (180, 180, 255)  # 蓝色调
        elif self.current_mode == "dynamic":  # 新增动力学模式
            mode_text = "动力学模式"
            mode_color = (255, 180, 180)  # 红色调
        else:
            mode_text = "未知模式"
            mode_color = (200, 200, 200)

        mode_surf = self.small_font.render(mode_text, True, mode_color)
        self.screen.blit(mode_surf, (content_x, content_y))

        # 控制点数量
        points_y = content_y + 25
        points_text = f"{ChineseText.CONTROL_POINTS}: {self.bezier_curve.get_control_points_count()}"
        points_surf = self.small_font.render(points_text, True, self.TEXT_COLOR)
        self.screen.blit(points_surf, (content_x, points_y))

        # 模式特定信息
        info_y_offset = 25

        # 递归模式信息
        if self.current_mode == "recursive" and self.recursive_initialized:
            mode_info_y = points_y + info_y_offset
            status = self.recursive_bezier.get_status()
            mode_info_text = ChineseText.RECURSIVE_INFO.format(
                status['current_level'],
                len(self.bezier_curve.control_points) - 1,
                status['ratio']
            )
            mode_info_surf = self.small_font.render(mode_info_text, True, (180, 255, 180))
            self.screen.blit(mode_info_surf, (content_x, mode_info_y))
            info_y_offset += 25  # 增加偏移量

        # 向量模式信息
        elif self.current_mode == "vector" and self.vector_initialized:
            mode_info_y = points_y + info_y_offset

            # 获取向量模式状态
            if hasattr(self.vector_bezier, 'get_status'):
                status = self.vector_bezier.get_status()
                vector_info_text = f"参数t: {status['t_value']:.2f}"
            else:
                # 如果没有get_status方法，直接使用当前值
                vector_info_text = f"参数t: {self.vector_t_slider.volume:.2f}"

            # 添加向量模式信息
            vector_mode_text = self.vector_bezier.get_vector_mode_text() if hasattr(self.vector_bezier,
                                                                                    'get_vector_mode_text') else "未知"
            vector_info_text = f"t={self.vector_t_slider.volume:.2f} | {vector_mode_text}"

            mode_info_surf = self.small_font.render(vector_info_text, True, (180, 180, 255))
            self.screen.blit(mode_info_surf, (content_x, mode_info_y))
            info_y_offset += 25

        # 动力学模式信息（简化，只显示参数t）
        elif self.current_mode == "dynamic" and self.dynamic_initialized:
            mode_info_y = points_y + info_y_offset

            # 获取动力学状态
            status = self.dynamic_bezier.get_status()

            # 只显示当前t值
            dynamic_info_text = f"参数 t = {status['t_value']:.2f}"
            mode_info_surf = self.small_font.render(dynamic_info_text, True, (180, 255, 255))
            self.screen.blit(mode_info_surf, (content_x, mode_info_y))
            info_y_offset += 25

        # 音量信息
        sound_y = points_y + info_y_offset
        sound_on = ChineseText.SOUND_ON if self.sound_manager.sound_enabled else ChineseText.SOUND_OFF
        music_on = ChineseText.SOUND_ON if self.sound_manager.music_enabled else ChineseText.SOUND_OFF
        sound_text = ChineseText.SOUND_STATUS.format(sound_on, music_on)
        sound_surf = self.small_font.render(sound_text, True, (180, 180, 255))
        self.screen.blit(sound_surf, (content_x, sound_y))

    def draw_audio_controls(self):
        """绘制音效控制区域"""
        if not self.show_audio_controls or not self.audio_panel.visible:
            return

        # 使用可拖拽面板的位置和尺寸
        control_x = self.audio_panel.rect.x
        control_y = self.audio_panel.rect.y

        # 绘制面板
        self.audio_panel.draw(self.screen, self.small_font)

        # 标题栏高度
        title_height = 25

        # 设置滑块位置
        self.sound_slider.rect.x = control_x + 70
        self.sound_slider.rect.y = control_y + title_height + 20
        self.sound_slider.rect.width = 80

        self.music_slider.rect.x = control_x + 70
        self.music_slider.rect.y = control_y + title_height + 55
        self.music_slider.rect.width = 80

        # 绘制滑块（VolumeSlider会自己绘制标签）
        self.sound_slider.draw(self.screen, self.small_font)
        self.music_slider.draw(self.screen, self.small_font)

        # 注意：这里移除了手动绘制的标签
        # 因为VolumeSlider的draw方法已经绘制了标签

    def draw_recursive_controls(self):
        """绘制递归模式控制区域"""
        if not self.show_recursive_controls or self.current_mode != "recursive" or not self.recursive_initialized:
            return
        if not self.recursive_panel.visible:
            return

        # 使用可拖拽面板的位置和尺寸
        control_x = self.recursive_panel.rect.x
        control_y = self.recursive_panel.rect.y
        control_width = self.recursive_panel.rect.width
        control_height = self.recursive_panel.rect.height

        # 绘制面板（包括背景、标题栏和拖拽把手）
        self.recursive_panel.draw(self.screen, self.small_font)

        # 标题栏高度
        title_height = 25

        # 调整按钮位置（相对于面板）
        button_start_x = control_x + 20
        button_start_y = control_y + title_height + 20  # 标题栏下方20像素

        # 按钮尺寸
        btn_width = 95
        btn_height = 25
        btn_spacing_x = 10
        btn_spacing_y = 15

        # 第一行：上一步和下一步按钮
        self.recursive_buttons[0].rect.x = button_start_x
        self.recursive_buttons[0].rect.y = button_start_y
        self.recursive_buttons[0].rect.width = btn_width

        self.recursive_buttons[1].rect.x = button_start_x + btn_width + btn_spacing_x
        self.recursive_buttons[1].rect.y = button_start_y
        self.recursive_buttons[1].rect.width = btn_width

        # 第二行：重置和切换构造显示按钮
        self.recursive_buttons[2].rect.x = button_start_x
        self.recursive_buttons[2].rect.y = button_start_y + btn_height + btn_spacing_y
        self.recursive_buttons[2].rect.width = btn_width

        self.recursive_buttons[3].rect.x = button_start_x + btn_width + btn_spacing_x
        self.recursive_buttons[3].rect.y = button_start_y + btn_height + btn_spacing_y
        self.recursive_buttons[3].rect.width = btn_width

        # # 调整滑块位置
        # self.ratio_slider.rect.x = button_start_x
        # self.ratio_slider.rect.y = button_start_y + 2 * (btn_height + btn_spacing_y) + 10
        # self.ratio_slider.rect.width = control_width - 80  # 填满面板宽度减去边距

        # 调整滑块位置和大小
        slider_y = button_start_y + 2 * (btn_height + btn_spacing_y) + 10

        # 先绘制标签，计算标签宽度
        if self.small_font:
            slider_label = self.small_font.render("参数 t:", True, (220, 220, 220))
            label_width = slider_label.get_width() + 10  # 标签宽度+间距
            label_x = button_start_x + 5  # 面板内部
            label_y = slider_y + (self.ratio_slider.rect.height // 2) - 8

            # 设置滑块位置和大小
            self.ratio_slider.rect.x = button_start_x + label_width  # 从标签右边开始
            self.ratio_slider.rect.y = slider_y
            self.ratio_slider.rect.width = control_width - label_width - 40  # 减去标签宽度和右边距

            # 绘制滑块标签
            self.screen.blit(slider_label, (label_x, label_y))
        else:
            # 如果没有字体，滑块占满宽度
            self.ratio_slider.rect.x = button_start_x
            self.ratio_slider.rect.y = slider_y
            self.ratio_slider.rect.width = control_width - 40

        # 绘制控制按钮
        for button in self.recursive_buttons:
            button.draw(self.screen, self.small_font)

        # 绘制参数滑块
        self.ratio_slider.draw(self.screen, self.small_font)

    def draw_vector_controls(self):
        """绘制向量模式控制区域（完整版）"""
        if not self.show_vector_controls or self.current_mode != "vector" or not self.vector_initialized:
            return
        if not self.vector_panel.visible:
            return

        # 使用可拖拽面板的位置和尺寸
        control_x = self.vector_panel.rect.x
        control_y = self.vector_panel.rect.y
        control_width = self.vector_panel.rect.width
        control_height = self.vector_panel.rect.height

        # 绘制面板
        self.vector_panel.draw(self.screen, self.small_font)

        # 标题栏高度
        title_height = 25

        # 按钮布局
        button_start_x = control_x + 20
        button_start_y = control_y + title_height + 15

        # 垂直间距
        vertical_spacing = 32  # 稍微紧凑一点

        # 绘制所有向量按钮
        for i, button in enumerate(self.vector_buttons):
            button.rect.x = button_start_x
            button.rect.y = button_start_y + i * vertical_spacing
            button.rect.width = control_width - 40

        # Bernstein窗口按钮
        bernstein_y = button_start_y + len(self.vector_buttons) * vertical_spacing + 5
        self.bernstein_button.rect.x = button_start_x
        self.bernstein_button.rect.y = bernstein_y
        self.bernstein_button.rect.width = control_width - 40

        # Bernstein数据按钮
        self.bernstein_data_button.rect.x = button_start_x
        self.bernstein_data_button.rect.y = bernstein_y + vertical_spacing
        self.bernstein_data_button.rect.width = control_width - 40

        # 参数t滑块
        slider_y = bernstein_y + vertical_spacing * 2 + 5

        # 绘制滑块标签
        if self.small_font:
            slider_label = self.small_font.render("参数 t:", True, (220, 220, 220))
            label_width = slider_label.get_width() + 10
            label_x = button_start_x + 5
            label_y = slider_y + (self.vector_t_slider.rect.height // 2) - 8

            # 设置滑块位置和大小
            self.vector_t_slider.rect.x = button_start_x + label_width
            self.vector_t_slider.rect.y = slider_y
            self.vector_t_slider.rect.width = control_width - label_width - 40

            # 绘制滑块标签
            self.screen.blit(slider_label, (label_x, label_y))
        else:
            self.vector_t_slider.rect.x = button_start_x
            self.vector_t_slider.rect.y = slider_y
            self.vector_t_slider.rect.width = control_width - 40

        # 绘制所有按钮
        for button in self.vector_buttons:
            button.draw(self.screen, self.small_font)

        self.bernstein_button.draw(self.screen, self.small_font)
        self.bernstein_data_button.draw(self.screen, self.small_font)
        self.vector_t_slider.draw(self.screen, self.small_font)

    def draw_zoom_controls(self):
        """绘制缩放控制按钮（不包含缩放状态信息）"""
        if not self.show_zoom_controls:
            return

        # 只绘制缩放按钮，状态信息已移到状态栏
        for button in self.zoom_buttons:
            button.draw(self.screen, self.small_font)

    def draw_dynamic_controls(self):
        """绘制动力学控制区域"""
        if self.current_mode != "dynamic" or not self.dynamic_initialized:
            return
        if not self.dynamic_panel.visible:
            return

        # 使用可拖拽面板的位置和尺寸
        control_x = self.dynamic_panel.rect.x
        control_y = self.dynamic_panel.rect.y
        control_width = self.dynamic_panel.rect.width
        control_height = self.dynamic_panel.rect.height

        # 绘制面板（包括背景、标题栏和拖拽把手）
        self.dynamic_panel.draw(self.screen, self.small_font)

        # 标题栏高度
        title_height = 25

        # 按钮布局
        button_start_x = control_x + 20
        button_start_y = control_y + title_height + 20

        # 按钮尺寸和间距
        btn_width = control_width - 40
        btn_height = 25
        btn_spacing = 8

        # 创建动力学控制按钮（如果不存在）- 只保留基本控制+窗口开关
        if not hasattr(self, 'dynamic_buttons'):
            self.dynamic_buttons = [
                ControlButton(0, 0, btn_width, btn_height,
                              "速度向量(V)", "V"),
                ControlButton(0, 0, btn_width, btn_height,
                              "加速度向量(Z)", "Z"),
                ControlButton(0, 0, btn_width, btn_height,
                              "急动度向量(J)", "J"),
                ControlButton(0, 0, btn_width, btn_height,
                              "曲率圆(N)", "N"),  # 新增曲率圆按钮
                ControlButton(0, 0, btn_width, btn_height,
                              "窗口开关(W)", "W")  # 新增窗口开关按钮
            ]

        # 更新按钮位置
        current_y = button_start_y

        # 更新动力学控制按钮位置
        for i, button in enumerate(self.dynamic_buttons):
            button.rect.x = button_start_x
            button.rect.y = current_y
            button.rect.width = btn_width
            current_y += btn_height + btn_spacing

        current_y += 10  # 额外的间距用于滑块

        # 绘制按钮
        for button in self.dynamic_buttons:
            button.draw(self.screen, self.small_font)

        # 添加t值滑块（在按钮下方）
        slider_y = current_y

        # 绘制滑块标签
        if self.small_font:
            slider_label = self.small_font.render("参数 t:", True, (220, 220, 220))
            label_width = slider_label.get_width() + 10
            label_x = button_start_x + 5
            label_y = slider_y + (self.dynamic_t_slider.rect.height // 2) - 8

            # 设置滑块位置和大小
            self.dynamic_t_slider.rect.x = button_start_x + label_width
            self.dynamic_t_slider.rect.y = slider_y
            self.dynamic_t_slider.rect.width = control_width - label_width - 40

            # 绘制滑块标签
            self.screen.blit(slider_label, (label_x, label_y))
        else:
            self.dynamic_t_slider.rect.x = button_start_x
            self.dynamic_t_slider.rect.y = slider_y
            self.dynamic_t_slider.rect.width = control_width - 40

        # 绘制滑块
        self.dynamic_t_slider.draw(self.screen, self.small_font)

    def handle_dynamic_button_clicks(self, pos):
        """处理动力学面板按钮点击"""
        if not hasattr(self, 'dynamic_buttons'):
            return False

        # 检查动力学控制按钮点击
        for i, button in enumerate(self.dynamic_buttons):
            if button.handle_click(pos):
                if i == 0:  # 速度向量
                    self.dynamic_bezier.toggle_velocity()
                    self.sound_manager.play_sound('click')
                    print(f"速度向量显示: {'开启' if self.dynamic_bezier.show_velocity else '关闭'}")
                elif i == 1:  # 加速度向量
                    self.dynamic_bezier.toggle_acceleration()
                    self.sound_manager.play_sound('click')
                    print(f"加速度向量显示: {'开启' if self.dynamic_bezier.show_acceleration else '关闭'}")
                elif i == 2:  # 急动度向量
                    self.dynamic_bezier.toggle_jerk()
                    self.sound_manager.play_sound('click')
                    print(f"急动度向量显示: {'开启' if self.dynamic_bezier.show_jerk else '关闭'}")
                return True

        # 检查向量窗口按钮点击
        if hasattr(self, 'vector_window_button') and self.vector_window_button.handle_click(pos):
            self.dynamic_bezier.toggle_vector_windows()
            self.sound_manager.play_sound('click')
            print(f"向量轨迹窗口: {'显示' if self.dynamic_bezier.show_vector_windows else '隐藏'}")
            return True

        return False

    def reset_panel_positions(self):
        """重置所有面板到默认位置"""
        # 音频面板默认位置（左下角）
        self.audio_panel.set_position(10, self.height - 160 - 60)

        # 递归面板默认位置（中间偏下）
        self.recursive_panel.set_position(230, self.height - 240 - 60)

        # 向量面板默认位置（右下角）
        self.vector_panel.set_position(500, self.height - 280 - 60)

        # 动力学面板默认位置（最右侧）
        self.dynamic_panel.set_position(800, self.height - 280 - 60)

        # Bernstein窗口默认位置（右上角）
        self.bernstein_window_position = (self.width - 470, 100)

        # 基本信息面板默认位置（右上角，基本信息区域）
        self.info_panel.set_position(self.width - 300, 250)

        # ====== 新增：3D演示面板默认位置 ======
        self.demo_3d_panel.set_position(950, self.height - 180 - 60)

        self.sound_manager.play_sound('click')
        print("所有面板位置已重置到默认位置")

    def draw_status_bar(self):
        """绘制底部状态栏（包含缩放状态）"""
        status_height = 35  # 稍微增加一点高度
        status_y = self.height - status_height

        # 背景
        pygame.draw.rect(self.screen, (45, 45, 65), (0, status_y, self.width, status_height))
        pygame.draw.line(self.screen, (70, 70, 90), (0, status_y), (self.width, status_y), 1)

        # 状态栏分为四部分
        part_width = self.width // 4

        # 第一部分：模式状态
        mode_text = self.get_mode_status_text()
        mode_surf = self.small_font.render(mode_text, True, (220, 240, 255))
        mode_x = 15
        mode_y = status_y + (status_height - mode_surf.get_height()) // 2
        self.screen.blit(mode_surf, (mode_x, mode_y))

        # 第二部分：控制点信息
        points_text = f"控制点: {self.bezier_curve.get_control_points_count()}"
        points_surf = self.small_font.render(points_text, True, (180, 220, 180))
        points_x = part_width + 15
        points_y = status_y + (status_height - points_surf.get_height()) // 2
        self.screen.blit(points_surf, (points_x, points_y))

        # 第三部分：缩放和平移状态
        scale = self.scale_manager.get_scale()
        dx, dy = self.scale_manager.translation
        # 构建状态文本
        if abs(scale - 1.0) < 0.01 and dx == 0 and dy == 0:
            status_text = "视图: 正常"
            status_color = (200, 200, 200)
        else:
            status_parts = []
            if abs(scale - 1.0) >= 0.01:
                if scale > 1.0:
                    status_parts.append(f"放大{scale:.1f}x")
                else:
                    status_parts.append(f"缩小{scale:.1f}x")
            if dx != 0 or dy != 0:
                # 简化显示，只显示有显著偏移的情况
                if abs(dx) > 10 or abs(dy) > 10:
                    status_parts.append(f"平移({dx:+d},{dy:+d})")
            status_text = f"视图: {' '.join(status_parts)}"
            # 根据状态选择颜色
            if scale > 1.0:
                status_color = (100, 255, 100)  # 放大为绿色
            elif scale < 1.0:
                status_color = (255, 150, 100)  # 缩小为橙色
            else:
                status_color = (200, 200, 255)  # 只有平移为蓝色

        scale_surf = self.small_font.render(status_text, True, status_color)
        scale_x = part_width * 2 + 15
        scale_y = status_y + (status_height - scale_surf.get_height()) // 2
        self.screen.blit(scale_surf, (scale_x, scale_y))

        # 第四部分：快捷键提示
        shortcut_text = "H:帮助 ESC:退出"
        shortcut_surf = self.small_font.render(shortcut_text, True, (200, 200, 255))
        shortcut_x = self.width - shortcut_surf.get_width() - 15
        shortcut_y = status_y + (status_height - shortcut_surf.get_height()) // 2
        self.screen.blit(shortcut_surf, (shortcut_x, shortcut_y))

    # 添加辅助方法
    def get_mode_status_text(self):
        """获取模式状态文本（简化版，详细状态在状态栏显示）"""
        if self.current_mode == "create":
            mode_detail = "添加" if self.drawing_mode else "编辑"
            return f"创建模式 [{mode_detail}]"
        elif self.current_mode == "recursive":
            return "递归构造模式"
        elif self.current_mode == "vector":
            return "向量表示模式"
        elif self.current_mode == "dynamic":  # 新增
            return "动力学模式"
        return ""

    def get_center_hint_text(self):
        """获取中间提示文本（用于状态栏）"""
        if self.current_mode == "create":
            if self.drawing_mode:
                return "左键:添加点 右键:删除点 空格:切换模式"
            else:
                return "左键拖动控制点或空白处平移"
        elif self.current_mode == "recursive":
            return "左键拖动:平移视图 空格:下一步 B:上一步"
        elif self.current_mode == "vector":
            return "左键拖动:平移视图 F:切换向量模式"
        return "左键拖动:平移视图 H:查看帮助"

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # ====== 第一步：处理Bernstein窗口事件 ======
            if self.bernstein_window.visible:
                handled, new_pos = self.bernstein_window.handle_event(event, self.bernstein_window_position)
                if handled:
                    self.bernstein_window_position = new_pos
                    # 如果窗口被关闭，更新状态
                    if not self.bernstein_window.visible:
                        print("Bernstein窗口已关闭")
                    continue  # 跳过其他事件处理

            # ====== 第二步：处理其他面板事件 ======
            panel_handled = False

            # 基本信息面板事件
            if self.info_panel.visible:
                if self.info_panel.handle_event(event):
                    panel_handled = True

            # 音频面板事件
            if self.show_audio_controls and self.audio_panel.visible:
                if self.audio_panel.handle_event(event):
                    panel_handled = True

            # 递归面板事件
            if (self.show_recursive_controls and self.current_mode == "recursive"
                    and self.recursive_initialized and self.recursive_panel.visible):
                if self.recursive_panel.handle_event(event):
                    panel_handled = True

            # 向量面板事件
            if (self.show_vector_controls and self.current_mode == "vector"
                    and self.vector_initialized and self.vector_panel.visible):
                if self.vector_panel.handle_event(event):
                    panel_handled = True

            # Bernstein数据面板
            if self.bernstein_data_panel.visible:
                if self.bernstein_data_panel.handle_event(event):
                    panel_handled = True

            if (self.current_mode == "dynamic" and self.dynamic_initialized
                    and self.dynamic_panel.visible):
                if self.dynamic_panel.handle_event(event):
                    panel_handled = True
                    print(f"动力学面板处理了事件: {event.type}")  # 调试信息

            if (self.current_mode == "3ddemo" and self.demo_3d_initialized
                    and self.demo_3d_panel.visible):
                print(f"检查3D面板拖拽: panel_visible={self.demo_3d_panel.visible}, rect={self.demo_3d_panel.rect}")
                if self.demo_3d_panel.handle_event(event):
                    panel_handled = True
                    print(f"3D演示面板处理了事件: {event.type}")

            # 如果面板处理了事件，跳过其他处理
            if panel_handled:
                continue

            # 鼠标滚轮缩放
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # 滚轮向上，放大
                    if self.scale_manager.zoom_in():
                        self.sound_manager.play_sound('click')
                        print(f"放大: 缩放比例={self.scale_manager.get_scale():.1f}")
                elif event.y < 0:  # 滚轮向下，缩小
                    if self.scale_manager.zoom_out():
                        self.sound_manager.play_sound('click')
                        print(f"缩小: 缩放比例={self.scale_manager.get_scale():.1f}")

            # 处理音量滑块事件
            if self.show_audio_controls and self.sound_slider.handle_event(event):
                continue
            if self.show_audio_controls and self.music_slider.handle_event(event):
                continue

            # 处理参数滑块事件（递归模式）
            if (self.show_recursive_controls and self.current_mode == "recursive"
                    and self.recursive_initialized):
                if self.ratio_slider.handle_event(event):
                    new_ratio = self.ratio_slider.volume
                    self.recursive_bezier.set_ratio(new_ratio)
                    print(f"参数t调整为: {new_ratio:.2f}")
                    continue

            # 处理向量参数滑块事件
            if (self.show_vector_controls and self.current_mode == "vector"
                    and self.vector_initialized):
                if self.vector_t_slider.handle_event(event):
                    new_t = self.vector_t_slider.volume
                    self.vector_bezier.set_t(new_t)
                    self.bernstein_window.set_t(new_t)
                    print(f"参数t调整为: {new_t:.2f}")
                    continue

            if (self.current_mode == "dynamic" and self.dynamic_initialized):
                if self.dynamic_t_slider.handle_event(event):
                    new_t = self.dynamic_t_slider.volume
                    self.dynamic_bezier.set_t(new_t)
                    print(f"参数t调整为: {new_t:.2f}")
                    continue

            if event.type == pygame.KEYDOWN:
                # 首先检查帮助面板是否可见
                if self.help_module.is_visible():
                    # 帮助面板有最高优先级
                    if self.help_module.handle_keydown(event.key):
                        continue

                # ESC键处理
                if event.key == pygame.K_ESCAPE and self.adjusting_origin:
                    # 如果在调整原点模式，按ESC取消
                    self.adjusting_origin = False
                    self.sound_manager.play_sound('click')
                    print("调整原点模式已取消")
                    continue  # 阻止ESC键退出程序
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

                # 模式切换键
                elif event.key == pygame.K_1:
                    # 切换到创建模式
                    self.switch_mode("create")
                elif event.key == pygame.K_2:
                    # 切换到递归模式
                    self.switch_mode("recursive")
                elif event.key == pygame.K_3:  # 3键：向量模式
                    self.switch_mode("vector")
                elif event.key == pygame.K_4:  # 4键: 动力学模式
                    self.switch_mode("dynamic")
                elif event.key == pygame.K_5:  # 5键：3D演示模式
                    self.switch_mode("3ddemo")

                # ====== 动力学模式的按键处理（优先级最高） ======
                elif self.current_mode == "dynamic" and self.dynamic_initialized:
                    if event.key == pygame.K_w:  # W键：切换向量窗口
                        self.dynamic_bezier.toggle_vector_windows()
                        self.sound_manager.play_sound('click')
                        print(f"向量轨迹窗口: {'显示' if self.dynamic_bezier.show_vector_windows else '隐藏'}")
                    elif event.key == pygame.K_v:  # V键：切换速度向量
                        self.dynamic_bezier.toggle_velocity()
                        self.sound_manager.play_sound('click')
                        print(f"速度向量显示: {'开启' if self.dynamic_bezier.show_velocity else '关闭'}")
                    elif event.key == pygame.K_z:  # A键：切换加速度向量
                        self.dynamic_bezier.toggle_acceleration()
                        self.sound_manager.play_sound('click')
                        print(f"加速度向量显示: {'开启' if self.dynamic_bezier.show_acceleration else '关闭'}")
                    elif event.key == pygame.K_j:  # J键：切换急动度向量
                        self.dynamic_bezier.toggle_jerk()
                        self.sound_manager.play_sound('click')
                        print(f"急动度向量显示: {'开启' if self.dynamic_bezier.show_jerk else '关闭'}")
                    elif event.key == pygame.K_c:  # C键：清除向量历史
                        self.dynamic_bezier.clear_vector_history()
                        self.sound_manager.play_sound('click')
                        print("向量历史已清除")
                    elif event.key == pygame.K_x:  # S键：切换速度向量窗口
                        self.dynamic_bezier.toggle_velocity_window()
                        self.sound_manager.play_sound('click')
                        print(f"速度向量窗口: {'显示' if self.dynamic_bezier.show_velocity_window else '隐藏'}")
                    elif event.key == pygame.K_d:  # D键：切换加速度向量窗口
                        self.dynamic_bezier.toggle_acceleration_window()
                        self.sound_manager.play_sound('click')
                        print(f"加速度向量窗口: {'显示' if self.dynamic_bezier.show_acceleration_window else '隐藏'}")
                    elif event.key == pygame.K_k:  # K键：切换急动度向量窗口
                        self.dynamic_bezier.toggle_jerk_window()
                        self.sound_manager.play_sound('click')
                        print(f"急动度向量窗口: {'显示' if self.dynamic_bezier.show_jerk_window else '隐藏'}")
                    elif event.key == pygame.K_n:  # N键：切换曲率圆显示
                        self.dynamic_bezier.toggle_curvature_circle()
                        self.sound_manager.play_sound('click')
                        print(f"曲率圆显示: {'开启' if self.dynamic_bezier.show_curvature_circle else '关闭'}")
                    elif event.key == pygame.K_l:  # L键：切换曲率窗口
                        self.dynamic_bezier.toggle_curvature_window()
                        self.sound_manager.play_sound('click')
                        print(f"曲率窗口: {'显示' if self.dynamic_bezier.show_curvature_window else '隐藏'}")
                    else:
                        # 如果不是动力学模式的特定按键，继续检查其他模式
                        pass

                # ====== 3D演示模式的按键处理 ======
                elif self.current_mode == "3ddemo" and self.demo_3d_initialized:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_w:  # W: 上旋转
                            self.demo_3d.rotate_view(delta_x=5)
                            self.sound_manager.play_sound('click')
                        elif event.key == pygame.K_x:  # X: 下旋转
                            self.demo_3d.rotate_view(delta_x=-5)
                            self.sound_manager.play_sound('click')
                        elif event.key == pygame.K_c:  # C: 左旋转
                            self.demo_3d.rotate_view(delta_y=5)
                            self.sound_manager.play_sound('click')
                        elif event.key == pygame.K_d:  # D: 右旋转
                            self.demo_3d.rotate_view(delta_y=-5)
                            self.sound_manager.play_sound('click')
                        elif event.key == pygame.K_q:  # Q: 缩小
                            self.demo_3d.zoom_view(0.9)
                            self.sound_manager.play_sound('click')
                        elif event.key == pygame.K_e:  # E: 放大
                            self.demo_3d.zoom_view(1.1)
                            self.sound_manager.play_sound('click')
                        elif event.key == pygame.K_r:  # R: 重置视角
                            self.demo_3d.reset_view()
                            self.sound_manager.play_sound('click')
                        elif event.key == pygame.K_z:  # Z: 重新生成Z值
                            self.demo_3d.regenerate_z_values()
                            self.sound_manager.play_sound('click')
                            print("重新生成3D控制点")
                        elif event.key == pygame.K_l:  # L: 切换立方体显示
                            self.demo_3d.toggle_visibility('cube')
                            self.sound_manager.play_sound('click')
                            status = self.demo_3d.get_status()
                            print(f"立方体显示: {'开启' if status['show_cube'] else '关闭'}")
                        elif event.key == pygame.K_b:  # B: 切换坐标轴显示
                            self.demo_3d.toggle_visibility('axes')
                            self.sound_manager.play_sound('click')
                            status = self.demo_3d.get_status()
                            print(f"坐标轴显示: {'开启' if status['show_axes'] else '关闭'}")
                        elif event.key == pygame.K_F9:  # F9: 切换3D控制面板
                            # 检查是否在3D演示模式下
                            if self.current_mode == "3ddemo":
                                self.demo_3d_panel.toggle_visibility()
                                self.sound_manager.play_sound('click')
                                print(f"3D控制面板: {'显示' if self.demo_3d_panel.visible else '隐藏'}")
                                print(f"面板位置: {self.demo_3d_panel.rect}")
                                print(f"拖拽区域: {self.demo_3d_panel.drag_handle_rect}")
                            else:
                                print("F8键仅在3D演示模式下有效")

                # ====== 向量模式的按键处理 ======
                elif self.current_mode == "vector" and self.vector_initialized:
                    if event.key == pygame.K_w:  # W键：切换Bernstein窗口
                        self.bernstein_window.toggle_visibility()
                        # 如果显示窗口，重置到默认位置
                        if self.bernstein_window.visible:
                            self.bernstein_window_position = (self.width - 470, 100)
                        self.sound_manager.play_sound('click')
                        print(f"Bernstein窗口: {'显示' if self.bernstein_window.visible else '隐藏'}")
                    elif event.key == pygame.K_v:  # V键：切换向量显示
                        self.vector_bezier.show_vectors = not self.vector_bezier.show_vectors
                        self.sound_manager.play_sound('click')
                        print(f"向量显示: {'开启' if self.vector_bezier.show_vectors else '关闭'}")
                    elif event.key == pygame.K_c:  # C键：切换曲线显示
                        self.vector_bezier.show_curve = not self.vector_bezier.show_curve
                        self.sound_manager.play_sound('click')
                        print(f"曲线显示: {'开启' if self.vector_bezier.show_curve else '关闭'}")
                    elif event.key == pygame.K_f:  # F键：切换向量模式
                        mode = self.vector_bezier.toggle_vector_mode()
                        self.sound_manager.play_sound('mode_switch')
                        print(f"向量模式切换为: {self.vector_bezier.get_vector_mode_text()}")
                    elif event.key == pygame.K_p:  # O键：调整原点位置
                        self.adjusting_origin = True
                        self.sound_manager.play_sound('click')
                        print("调整原点模式已激活，点击空白处设置新原点")
                    elif event.key == pygame.K_r:  # R键：重置原点位置
                        self.vector_bezier.calculate_origin()
                        self.vector_bezier.calculate_control_vectors()
                        self.vector_bezier.update_vectors(self.vector_t_slider.volume)
                        self.sound_manager.play_sound('delete_point')
                        print("原点已重置到控制点中心")
                    elif event.key == pygame.K_d:  # D键：切换Bernstein数据面板
                        self.bernstein_data_panel.toggle_visibility()
                        self.sound_manager.play_sound('click')
                        print(f"基函数数据面板: {'显示' if self.bernstein_data_panel.visible else '隐藏'}")
                    else:
                        # 如果不是向量模式的特定按键，继续检查通用按键
                        pass

                # ====== 递归模式的按键处理 ======
                elif self.current_mode == "recursive" and self.recursive_initialized:
                    if event.key == pygame.K_SPACE:
                        # 递归模式：下一步构造
                        if not self.recursive_bezier.completed:
                            if self.recursive_bezier.next_step():
                                self.sound_manager.play_sound('add_point')
                                status = self.recursive_bezier.get_status()
                                print(
                                    f"递归构造: 第{status['current_level']}/{status['total_levels']}层，剩余{status['remaining_steps']}步")
                                # 打印当前递归点信息
                                print(f"递归点总数: {status['recursive_points_count']}")
                            else:
                                print("递归构造已完成")
                        else:
                            print("递归构造已完成，无法继续")
                    elif event.key == pygame.K_c:
                        # 递归模式：切换构造显示
                        self.recursive_bezier.toggle_construction()
                        status = self.recursive_bezier.get_status()
                        self.sound_manager.play_sound('click')
                        print(f"构造过程显示: {'开启' if status['show_construction'] else '关闭'}")
                    elif event.key == pygame.K_b:  # B键：上一步
                        if self.recursive_bezier.prev_step():
                            self.sound_manager.play_sound('delete_point')
                            status = self.recursive_bezier.get_status()
                            print(f"返回上一步: 当前层级={status['current_level']}/{status['total_levels']}")
                    elif event.key == pygame.K_r:
                        # 递归模式：重置构造
                        self.recursive_bezier.reset()
                        self.sound_manager.play_sound('delete_point')
                        print("重置递归构造")
                    else:
                        # 如果不是递归模式的特定按键，继续检查通用按键
                        pass

                # ====== 创建模式的按键处理 ======
                elif self.current_mode == "create":
                    if event.key == pygame.K_SPACE:
                        self.sound_manager.play_sound('click')
                        # 创建模式：切换添加/编辑模式
                        self.drawing_mode = not self.drawing_mode
                        print(f"模式切换: {'添加' if self.drawing_mode else '编辑'}")
                    elif event.key == pygame.K_c:
                        # 创建模式：清空所有点
                        self.bezier_curve.clear_control_points()
                        self.sound_manager.play_sound('delete_point')
                        print("清空所有控制点")
                    elif event.key == pygame.K_r:
                        # 创建模式：删除最后一个点
                        if self.bezier_curve.get_control_points_count() > 0:
                            self.bezier_curve.remove_last_control_point()
                            self.sound_manager.play_sound('delete_point')
                            print("删除最后一个控制点")
                    else:
                        # 如果不是创建模式的特定按键，继续检查通用按键
                        pass

                # ====== 通用按键处理（所有模式都适用） ======
                if event.key == pygame.K_i:
                    # 显示/隐藏基本信息面板
                    self.info_panel.toggle_visibility()
                    self.sound_manager.play_sound('click')
                    print(f"基本信息面板: {'显示' if self.info_panel.visible else '隐藏'}")
                elif event.key == pygame.K_F1:
                    # F1键快速打开帮助
                    self.help_module.visible = True
                    self.sound_manager.play_sound('click')
                elif event.key == pygame.K_F2:  # F2: 切换音频面板
                    self.audio_panel.toggle_visibility()
                    self.sound_manager.play_sound('click')
                    print(f"音频面板: {'显示' if self.audio_panel.visible else '隐藏'}")
                elif event.key == pygame.K_F3:  # F3: 切换递归面板
                    self.recursive_panel.toggle_visibility()
                    self.sound_manager.play_sound('click')
                    print(f"递归面板: {'显示' if self.recursive_panel.visible else '隐藏'}")
                elif event.key == pygame.K_F4:  # F4: 切换向量面板
                    self.vector_panel.toggle_visibility()
                    self.sound_manager.play_sound('click')
                    print(f"向量面板: {'显示' if self.vector_panel.visible else '隐藏'}")
                elif event.key == pygame.K_F5:  # F5: 重置所有面板位置
                    self.reset_panel_positions()
                elif event.key == pygame.K_F6:  # F6键：切换基本信息面板
                    self.info_panel.toggle_visibility()
                    self.sound_manager.play_sound('click')
                    print(f"基本信息面板: {'显示' if self.info_panel.visible else '隐藏'}")
                elif event.key == pygame.K_F7:  # F7: 切换动力学面板
                    self.dynamic_panel.toggle_visibility()
                    self.sound_manager.play_sound('click')
                    print(f"动力学面板: {'显示' if self.dynamic_panel.visible else '隐藏'}")
                    print(f"面板位置: {self.dynamic_panel.rect}")
                    print(f"拖拽区域: {self.dynamic_panel.drag_handle_rect}")
                elif event.key == pygame.K_F8:  # F8: 切换3D控制面板
                    self.demo_3d_panel.toggle_visibility()
                    self.sound_manager.play_sound('click')
                    print(f"3D控制面板: {'显示' if self.demo_3d_panel.visible else '隐藏'}")
                    print(f"面板位置: {self.demo_3d_panel.rect}")
                    print(f"拖拽区域: {self.demo_3d_panel.drag_handle_rect}")
                elif event.key == pygame.K_h:
                    # 显示/隐藏帮助
                    self.help_module.toggle_visibility()
                    self.sound_manager.play_sound('click')
                elif event.key == pygame.K_s:
                    # 切换音效
                    self.sound_manager.toggle_sound()
                    self.sound_manager.play_sound('click')
                elif event.key == pygame.K_m:
                    # 切换音乐
                    self.sound_manager.toggle_music()
                    self.sound_manager.play_sound('click')
                elif event.key == pygame.K_p:  # P键：重置平移
                    if self.scale_manager.translation != (0, 0):
                        self.scale_manager.translation = (0, 0)
                        self.sound_manager.play_sound('click')
                        print("平移已重置")
                elif event.key == pygame.K_o:  # H键：同时重置缩放和平移
                    if self.scale_manager.is_zoomed_or_panned():
                        self.scale_manager.reset()
                        self.sound_manager.play_sound('click')
                        print("视图已完全重置")
                elif event.key == pygame.K_a:  # 新增：音频控制开关
                    self.show_audio_controls = not self.show_audio_controls
                    self.sound_manager.play_sound('click')
                    print(f"音频控制: {'显示' if self.show_audio_controls else '隐藏'}")
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:  # +=键放大
                    if self.scale_manager.zoom_in():
                        self.sound_manager.play_sound('click')
                        print(f"放大: 缩放比例={self.scale_manager.get_scale():.1f}")
                elif event.key == pygame.K_MINUS:  # -=键缩小
                    if self.scale_manager.zoom_out():
                        self.sound_manager.play_sound('click')
                        print(f"缩小: 缩放比例={self.scale_manager.get_scale():.1f}")
                elif event.key == pygame.K_0:  # 0键重置缩放
                    if self.scale_manager.reset():
                        self.sound_manager.play_sound('click')
                        print(f"重置缩放: 缩放比例={self.scale_manager.get_scale():.1f}")
                elif event.key == pygame.K_PAGEDOWN or event.key == pygame.K_RIGHT:
                    # 处理 Bernstein 数据面板的下一页
                    if self.bernstein_data_panel.visible and self.current_mode == "vector":
                        if self.bernstein_window.next_data_page():
                            self.sound_manager.play_sound('click')
                            print(
                                f"数据面板: 下一页 {self.bernstein_window.data_current_page + 1}/{self.bernstein_window.data_total_pages}")
                        else:
                            print(f"数据面板: 已在最后一页")
                        continue
                elif event.key == pygame.K_PAGEUP or event.key == pygame.K_LEFT:
                    # 处理 Bernstein 数据面板的上一页
                    if self.bernstein_data_panel.visible and self.current_mode == "vector":
                        if self.bernstein_window.prev_data_page():
                            self.sound_manager.play_sound('click')
                            print(
                                f"数据面板: 上一页 {self.bernstein_window.data_current_page + 1}/{self.bernstein_window.data_total_pages}")
                        else:
                            print(f"数据面板: 已在第一页")
                        continue
                else:
                    # 将按键传递给帮助模块处理（用于翻页）
                    if self.help_module.handle_keydown(event.key):
                        continue

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # ====== 第一步：检查所有功能按钮（优先级最高） ======
                # 1. 缩放按钮
                for i, button in enumerate(self.zoom_buttons):
                    if button.handle_click(pos):
                        if button.icon_name and "zoom_in" in button.icon_name:
                            if self.scale_manager.zoom_in():
                                self.sound_manager.play_sound('click')
                                print(f"放大: 缩放比例={self.scale_manager.get_scale():.1f}")
                        elif button.icon_name and "zoom_out" in button.icon_name:
                            if self.scale_manager.zoom_out():
                                self.sound_manager.play_sound('click')
                                print(f"缩小: 缩放比例={self.scale_manager.get_scale():.1f}")
                        elif button.icon_name and "zoom_reset" in button.icon_name:
                            if self.scale_manager.reset():
                                self.sound_manager.play_sound('click')
                                print(f"重置缩放: 缩放比例={self.scale_manager.get_scale():.1f}")
                        return True

                # 2. 模式按钮
                for button in self.mode_buttons:
                    if button.handle_click(pos):
                        self.switch_mode(button.mode_id)
                        return True

                # 3. 帮助按钮
                if self.help_module.handle_click(pos):
                    self.sound_manager.play_sound('click')
                    return True

                # 4. 音效按钮
                if self.sound_button.handle_click(pos) or self.music_button.handle_click(pos):
                    return True

                # ====== 第二步：检查Bernstein数据面板的分页按钮 ======
                if (self.bernstein_data_panel.visible and self.current_mode == "vector" and
                        hasattr(self, 'data_prev_btn_rect') and hasattr(self, 'data_next_btn_rect')):

                    if self.data_prev_btn_rect.collidepoint(pos):
                        if self.bernstein_window.prev_data_page():
                            self.sound_manager.play_sound('click')
                            print(
                                f"数据面板: 上一页 {self.bernstein_window.data_current_page + 1}/{self.bernstein_window.data_total_pages}")
                        return True

                    if self.data_next_btn_rect.collidepoint(pos):
                        if self.bernstein_window.next_data_page():
                            self.sound_manager.play_sound('click')
                            print(
                                f"数据面板: 下一页 {self.bernstein_window.data_current_page + 1}/{self.bernstein_window.data_total_pages}")
                        return True

                # ====== 第三步：检查各个面板内的功能按钮 ======
                # 1. 递归控制面板按钮
                if (self.show_recursive_controls and self.current_mode == "recursive"
                        and self.recursive_initialized and self.recursive_panel.visible):
                    for i, button in enumerate(self.recursive_buttons):
                        if button.handle_click(pos):
                            button_handled = True
                            # 根据按钮索引执行相应操作
                            if i == 0:  # 上一步
                                if self.recursive_bezier.prev_step():
                                    self.sound_manager.play_sound('delete_point')
                                    status = self.recursive_bezier.get_status()
                                    print(f"返回上一步: 当前层级={status['current_level']}/{status['total_levels']}")
                            elif i == 1:  # 下一步
                                if not self.recursive_bezier.completed:
                                    if self.recursive_bezier.next_step():
                                        self.sound_manager.play_sound('add_point')
                                        status = self.recursive_bezier.get_status()
                                        print(
                                            f"递归构造: 第{status['current_level']}/{status['total_levels']}层，剩余{status['remaining_steps']}步")
                                else:
                                    print("递归构造已完成，无法继续")
                            elif i == 2:  # 重置
                                self.recursive_bezier.reset()
                                self.sound_manager.play_sound('delete_point')
                                print("重置递归构造")
                            elif i == 3:  # 切换构造显示
                                self.recursive_bezier.toggle_construction()
                                status = self.recursive_bezier.get_status()
                                self.sound_manager.play_sound('click')
                                print(f"构造过程显示: {'开启' if status['show_construction'] else '关闭'}")
                            return True

                # 2. 向量控制面板按钮
                if (self.show_vector_controls and self.current_mode == "vector"
                        and self.vector_initialized and self.vector_panel.visible):

                    # Bernstein窗口按钮
                    if self.bernstein_button.handle_click(pos):
                        self.bernstein_window.toggle_visibility()
                        if self.bernstein_window.visible:
                            self.bernstein_window_position = (self.width - 470, 100)
                        self.sound_manager.play_sound('click')
                        print(f"Bernstein窗口: {'显示' if self.bernstein_window.visible else '隐藏'}")
                        return True

                    # Bernstein数据面板开关按钮
                    if self.bernstein_data_button.handle_click(pos):
                        if self.current_mode == "vector" and self.vector_initialized:
                            self.bernstein_data_panel.toggle_visibility()
                            self.sound_manager.play_sound('click')
                            print(f"基函数数据面板: {'显示' if self.bernstein_data_panel.visible else '隐藏'}")
                        return True

                    # 向量控制按钮
                    for i, button in enumerate(self.vector_buttons):
                        if button.handle_click(pos):
                            if i == 0:  # 显示/隐藏向量
                                self.vector_bezier.show_vectors = not self.vector_bezier.show_vectors
                                self.sound_manager.play_sound('click')
                                print(f"向量显示: {'开启' if self.vector_bezier.show_vectors else '关闭'}")
                            elif i == 1:  # 显示/隐藏曲线
                                self.vector_bezier.show_curve = not self.vector_bezier.show_curve
                                self.sound_manager.play_sound('click')
                                print(f"曲线显示: {'开启' if self.vector_bezier.show_curve else '关闭'}")
                            elif i == 2:  # 调整原点
                                self.adjusting_origin = True
                                self.sound_manager.play_sound('click')
                                print("调整原点模式已激活，点击空白处设置新原点")
                            elif i == 3:  # 重置原点
                                self.vector_bezier.calculate_origin()
                                self.vector_bezier.calculate_control_vectors()
                                self.vector_bezier.update_vectors(self.vector_t_slider.volume)
                                self.sound_manager.play_sound('delete_point')
                                print("原点已重置到控制点中心")
                            elif i == 4:  # 切换向量模式
                                mode = self.vector_bezier.toggle_vector_mode()
                                self.sound_manager.play_sound('mode_switch')
                                print(f"向量模式切换为: {self.vector_bezier.get_vector_mode_text()}")
                            return True

                # 3. 动力学控制面板按钮
                if (self.current_mode == "dynamic" and self.dynamic_initialized
                        and self.dynamic_panel.visible and hasattr(self, 'dynamic_buttons')):

                    # 在鼠标点击事件处理的地方
                    for i, button in enumerate(self.dynamic_buttons):
                        if button.handle_click(pos):
                            if i == 0:  # 速度向量
                                self.dynamic_bezier.toggle_velocity()
                                self.sound_manager.play_sound('click')
                                print(f"速度向量显示: {'开启' if self.dynamic_bezier.show_velocity else '关闭'}")
                            elif i == 1:  # 加速度向量
                                self.dynamic_bezier.toggle_acceleration()
                                self.sound_manager.play_sound('click')
                                print(f"加速度向量显示: {'开启' if self.dynamic_bezier.show_acceleration else '关闭'}")
                            elif i == 2:  # 急动度向量
                                self.dynamic_bezier.toggle_jerk()
                                self.sound_manager.play_sound('click')
                                print(f"急动度向量显示: {'开启' if self.dynamic_bezier.show_jerk else '关闭'}")
                            elif i == 3:  # 曲率圆
                                self.dynamic_bezier.toggle_curvature_circle()
                                self.sound_manager.play_sound('click')
                                print(f"曲率圆显示: {'开启' if self.dynamic_bezier.show_curvature_circle else '关闭'}")
                            elif i == 4:  # 窗口开关
                                self.dynamic_bezier.toggle_vector_windows()
                                self.sound_manager.play_sound('click')
                                print(f"向量轨迹窗口: {'显示' if self.dynamic_bezier.show_vector_windows else '隐藏'}")
                            return True

                # 4. 3D演示控制面板按钮
                if (self.current_mode == "3ddemo" and self.demo_3d_initialized
                        and self.demo_3d_panel.visible and hasattr(self, 'demo_3d_buttons')):

                    for i, button in enumerate(self.demo_3d_buttons):
                        if button.handle_click(pos):
                            if i == 0:  # 重置视角
                                self.demo_3d.reset_view()
                                self.sound_manager.play_sound('click')
                                print("视角已重置")
                            elif i == 1:  # 重新生成Z值
                                self.demo_3d.regenerate_z_values()
                                self.sound_manager.play_sound('click')
                                print("重新生成Z分量")
                            elif i == 2:  # 切换立方体显示
                                self.demo_3d.toggle_visibility('cube')
                                self.sound_manager.play_sound('click')
                                status = self.demo_3d.get_status()
                                print(f"立方体显示: {'开启' if status['show_cube'] else '关闭'}")
                            elif i == 3:  # 切换坐标轴显示
                                self.demo_3d.toggle_visibility('axes')
                                self.sound_manager.play_sound('click')
                                status = self.demo_3d.get_status()
                                print(f"坐标轴显示: {'开启' if status['show_axes'] else '关闭'}")
                            return True

                # ====== 第四步：检查是否在调整原点模式 ======
                if self.adjusting_origin:
                    if self.current_mode == "vector" and self.vector_initialized:
                        world_pos = self.scale_manager.inverse_scale_point(pos)
                        self.vector_bezier.origin_point = world_pos
                        self.vector_bezier.calculate_control_vectors()
                        self.vector_bezier.update_vectors(self.vector_t_slider.volume)
                        self.adjusting_origin = False
                        self.sound_manager.play_sound('add_point')
                        print(f"原点已调整到: ({world_pos[0]:.1f}, {world_pos[1]:.1f})")
                    return True

                # ====== 第五步：检查面板拖拽事件（在按钮之后） ======
                # 按顺序让各个面板检查是否点击了拖拽区域
                panel_handled = False

                # 基本信息面板
                if self.info_panel.visible and self.info_panel.handle_event(event):
                    panel_handled = True

                # 音频面板
                if not panel_handled and self.show_audio_controls and self.audio_panel.visible and self.audio_panel.handle_event(
                        event):
                    panel_handled = True

                # 递归面板
                if not panel_handled and (self.show_recursive_controls and self.current_mode == "recursive"
                                          and self.recursive_initialized and self.recursive_panel.visible and self.recursive_panel.handle_event(
                            event)):
                    panel_handled = True

                # 向量面板
                if not panel_handled and (self.show_vector_controls and self.current_mode == "vector"
                                          and self.vector_initialized and self.vector_panel.visible and self.vector_panel.handle_event(
                            event)):
                    panel_handled = True

                # 动力学面板事件
                if not panel_handled and (self.current_mode == "dynamic" and self.dynamic_initialized
                                          and self.dynamic_panel.visible):
                    print(
                        f"检查动力学面板拖拽: panel_visible={self.dynamic_panel.visible}, rect={self.dynamic_panel.rect}")
                    if self.dynamic_panel.handle_event(event):
                        print("动力学面板处理了事件")
                        panel_handled = True

                # 检查3D演示面板
                if not panel_handled and (self.current_mode == "3ddemo" and self.demo_3d_initialized
                                          and self.demo_3d_panel.visible and self.demo_3d_panel.handle_event(event)):
                    panel_handled = True
                    print("3D演示面板处理了拖拽事件")

                # Bernstein数据面板（最后检查，因为它的分页按钮已经处理过了）
                if not panel_handled and self.bernstein_data_panel.visible and self.bernstein_data_panel.handle_event(
                        event):
                    panel_handled = True

                if panel_handled:
                    print(f"面板处理了拖拽事件")
                    return True

                # ====== 第六步：检查是否点击在面板非功能区域 ======
                if self.is_cursor_over_panel(pos):
                    print(f"点击在面板非功能区域，不触发平移")
                    return True

                # ====== 第七步：处理平移等底层操作 ======
                if event.button == 1:  # 左键
                    if self.current_mode == "create":
                        if self.drawing_mode:
                            # 添加模式：添加控制点
                            world_pos = self.scale_manager.inverse_scale_point(pos)
                            self.bezier_curve.add_control_point(world_pos)
                            self.sound_manager.play_sound('add_point')
                            print(f"添加控制点: ({world_pos[0]}, {world_pos[1]})")
                        else:
                            # 编辑模式
                            world_pos = self.scale_manager.inverse_scale_point(pos)
                            if self.bezier_curve.check_point_selection(world_pos):
                                # 点击到控制点
                                self.bezier_curve.dragging = True
                                self.sound_manager.play_sound('click')
                                print(f"选择控制点: ({world_pos[0]}, {world_pos[1]})")
                            else:
                                # 开始平移
                                self.scale_manager.start_pan(pos)
                                print(f"开始平移: 起点({pos[0]}, {pos[1]})")
                    else:
                        # 递归模式和向量模式：开始平移
                        self.scale_manager.start_pan(pos)
                        print(f"开始平移: 起点({pos[0]}, {pos[1]}) 模式={self.current_mode}")

                elif event.button == 3 and self.current_mode == "create":  # 右键删除
                    world_pos = self.scale_manager.inverse_scale_point(pos)
                    if self.bezier_curve.check_point_selection(world_pos):
                        if 0 <= self.bezier_curve.selected_point < len(self.bezier_curve.control_points):
                            del self.bezier_curve.control_points[self.bezier_curve.selected_point]
                            self.bezier_curve.selected_point = -1
                            self.bezier_curve.update_curve()
                            self.sound_manager.play_sound('delete_point')
                            print("删除控制点")

                elif event.button == 2:  # 中键重置
                    if self.scale_manager.reset():
                        self.sound_manager.play_sound('click')
                        print(f"重置视图: 缩放={self.scale_manager.get_scale():.1f}, 平移已重置")
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 左键松开
                    # 创建模式下的控制点拖拽结束
                    if self.current_mode == "create":
                        self.bezier_curve.dragging = False
                    # 结束平移（所有模式通用）
                    if self.scale_manager.is_panning:
                        self.scale_manager.end_pan()
                        print(
                            f"结束平移: 最终偏移({self.scale_manager.translation[0]}, {self.scale_manager.translation[1]}) 模式={self.current_mode}")
            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()

                cursor_on_bernstein_data_panel = (self.bernstein_data_panel.visible and
                                                  self.bernstein_data_panel.rect.collidepoint(pos))

                # 如果正在平移且光标移到了 Bernstein 数据面板上，停止平移
                if self.scale_manager.is_panning and cursor_on_bernstein_data_panel:
                    self.scale_manager.end_pan()
                    print(f"光标移动到 Bernstein 数据面板上，停止平移")

                # 首先检查光标是否在面板上
                cursor_over_panel = self.is_cursor_over_panel(event.pos)

                # 检查是否正在进行平移
                if self.scale_manager.is_panning:
                    # 如果正在平移且光标移到了面板上，停止平移
                    if cursor_over_panel:
                        self.scale_manager.end_pan()
                        print(f"光标移动到面板上，停止平移")
                    else:
                        # 更新平移
                        self.scale_manager.update_pan(event.pos)
                        print(
                            f"平移中: 偏移({self.scale_manager.translation[0]}, {self.scale_manager.translation[1]}) 模式={self.current_mode}")

                # 创建模式下的控制点拖拽（特殊处理）
                elif self.current_mode == "create" and self.bezier_curve.dragging:
                    # 拖动控制点
                    world_pos = self.scale_manager.inverse_scale_point(event.pos)
                    self.bezier_curve.move_selected_point(world_pos)

    def run(self):
        """运行主循环"""
        clock = pygame.time.Clock()

        while self.running:
            self.handle_events()

            # 清屏
            self.screen.fill(self.BG_COLOR)

            # 绘制网格背景
            self.draw_grid()

            # 根据模式绘制内容
            if self.current_mode == "create":
                # 绘制Bezier曲线
                self.bezier_curve.draw(self.screen, self.scale_manager)
            elif self.current_mode == "recursive" and self.recursive_initialized:
                # 绘制递归构造过程
                self.recursive_bezier.draw(self.screen, self.scale_manager)

                # 绘制部分曲线 - 增加线宽
                partial_curve = self.recursive_bezier.get_partial_curve(self.ratio_slider.volume)
                if len(partial_curve) > 1:
                    # 关键修复：对部分曲线应用缩放
                    scaled_curve = self.scale_manager.apply_scale_to_points(partial_curve)
                    pygame.draw.lines(self.screen, (0, 255, 0), False, scaled_curve, 4)

                    # 在曲线终点添加标记
                    if scaled_curve:
                        scaled_end_point = scaled_curve[-1]
                        pygame.draw.circle(self.screen, (255, 255, 0), scaled_end_point, 6)
                        pygame.draw.circle(self.screen, (255, 0, 0), scaled_end_point, 6, 2)
            elif self.current_mode == "vector" and self.vector_initialized:  # 新增向量模式
                # 绘制向量表示
                self.vector_bezier.draw(self.screen, self.scale_manager)

                # 绘制Bernstein窗口（如果可见）
                if self.bernstein_window.visible:
                    self.bernstein_window.draw(self.screen, self.bernstein_window_position)
            elif self.current_mode == "dynamic" and self.dynamic_initialized:  # 动力学模式
                self.dynamic_bezier.draw(self.screen, self.scale_manager, self.small_font)
            elif self.current_mode == "3ddemo" and self.demo_3d_initialized:
                # 绘制3D演示场景
                self.demo_3d.draw(self.screen, self.small_font)
            # 绘制Bernstein数据面板（在Bernstein窗口之后）
            if hasattr(self, 'bernstein_data_panel') and self.bernstein_data_panel.visible:
                self.draw_bernstein_data_panel()  # 这里改为调用完整版方法

            if self.adjusting_origin and self.current_mode == "vector":
                # 绘制提示文字 - 使用 small_font（UI字体）
                if self.small_font:
                    # 直接使用，无需try-catch
                    hint_text = self.small_font.render("调整原点模式：点击空白处设置新原点 (ESC取消)", True,
                                                       (255, 255, 100))
                else:
                    # 备用英文
                    hint_font = pygame.font.Font(None, 20)
                    hint_text = hint_font.render("Adjust Origin: Click to set new origin (ESC cancel)", True,
                                                 (255, 255, 100))
                hint_rect = hint_text.get_rect(center=(self.width // 2, 65))

                # 绘制背景
                bg_rect = hint_rect.inflate(20, 10)
                pygame.draw.rect(self.screen, (40, 40, 60, 200), bg_rect, border_radius=8)
                pygame.draw.rect(self.screen, (100, 100, 150), bg_rect, 2, border_radius=8)

                self.screen.blit(hint_text, hint_rect)

            # 绘制缩放控制
            self.draw_zoom_controls()

            # 绘制音效控制按钮（始终显示）
            self.sound_button.draw(self.screen)
            self.music_button.draw(self.screen)

            # 绘制模式切换按钮
            for button in self.mode_buttons:
                button.draw(self.screen, self.font)

            # 绘制帮助按钮（使用中文文本）
            self.help_module.button_text = ChineseText.HELP_BUTTON
            self.help_module.draw_button(self.screen, position=(690, 10))

            # 绘制控制面板
            self.draw_audio_controls()
            self.draw_recursive_controls()
            self.draw_vector_controls()
            self.draw_dynamic_controls()

            # 绘制3D控制面板
            if self.current_mode == "3ddemo":
                self.draw_demo_3d_controls()

            # 绘制缩放控制（如果有）
            if hasattr(self, 'draw_zoom_controls'):
                self.draw_zoom_controls()

            # 绘制基本信息面板
            self.draw_info_panel()

            # 绘制状态栏
            self.draw_status_bar()

            # 绘制帮助面板（如果可见）
            self.help_module.draw_help_panel(self.screen)
            # 绘制鼠标位置
            self.draw_mouse_position()

            pygame.display.flip()
            clock.tick(60)

        # 清理资源
        self.sound_manager.cleanup()
        pygame.quit()
        sys.exit()

    def draw_grid(self):
        """绘制网格（支持缩放和平移）"""
        scale = self.scale_manager.get_scale()
        dx, dy = self.scale_manager.translation

        if scale != 1.0 or dx != 0 or dy != 0:
            # 缩放和平移后的网格
            base_size = 50
            scaled_size = max(10, int(base_size * scale))  # 最小10像素

            # 考虑平移偏移
            offset_x = dx % scaled_size
            offset_y = dy % scaled_size

            # 垂直线
            for x in range(int(-offset_x), self.width + scaled_size, scaled_size):
                if 0 <= x <= self.width:
                    pygame.draw.line(self.screen, (60, 60, 80, 150),
                                     (x, 0), (x, self.height), 1)

            # 水平线
            for y in range(int(-offset_y), self.height + scaled_size, scaled_size):
                if 0 <= y <= self.height:
                    pygame.draw.line(self.screen, (60, 60, 80, 150),
                                     (0, y), (self.width, y), 1)
        else:
            # 原始网格
            grid_size = 50
            for x in range(0, self.width, grid_size):
                pygame.draw.line(self.screen, (60, 60, 80), (x, 0), (x, self.height), 1)
            for y in range(0, self.height, grid_size):
                pygame.draw.line(self.screen, (60, 60, 80), (0, y), (self.width, y), 1)

    def draw_mouse_position(self):
        """绘制鼠标位置和当前操作状态"""
        if self.help_module.is_visible():
            return

        pos = pygame.mouse.get_pos()
        world_pos = self.scale_manager.inverse_scale_point(pos)

        text = f"({world_pos[0]},{world_pos[1]})"

        # 添加Bernstein窗口拖拽状态
        if self.bernstein_window.visible:
            # 检查鼠标是否在标题栏上
            title_bar_rect = pygame.Rect(
                self.bernstein_window_position[0],
                self.bernstein_window_position[1],
                self.bernstein_window.width,
                25  # 标题栏高度
            )

            if title_bar_rect.collidepoint(pos):
                if self.bernstein_window.dragging:
                    text += " [拖拽Bernstein窗口中]"
                else:
                    text += " [可拖拽Bernstein窗口]"

        # 添加其他操作状态提示
        if self.scale_manager.is_panning:
            text += " [平移视图中]"
        elif self.current_mode == "create" and not self.drawing_mode and self.bezier_curve.dragging:
            text += " [拖拽控制点中]"

        rendered = self.small_font.render(text, True, (200, 200, 255))

        # 确保提示框不会超出屏幕
        text_width = rendered.get_width()
        text_x = pos[0] + 15
        if text_x + text_width > self.width:
            text_x = pos[0] - text_width - 15

        self.screen.blit(rendered, (text_x, pos[1] - 15))

    def calculate_panel_positions(self):
        """计算所有面板的位置，避免重叠"""
        panels = []

        # 音频控制面板
        if self.show_audio_controls:
            panels.append({
                'width': 200,
                'height': 160,
                'preferred_x': 10
            })

        # 递归控制面板
        if self.show_recursive_controls and self.current_mode == "recursive" and self.recursive_initialized:
            panels.append({
                'width': 240,
                'height': 240,
                'preferred_x': 230
            })

        # 向量控制面板
        if self.show_vector_controls and self.current_mode == "vector" and self.vector_initialized:
            panels.append({
                'width': 280,
                'height': 280,
                'preferred_x': 490
            })

        # 动力学控制面板（新增）
        if self.current_mode == "dynamic" and self.dynamic_initialized:
            panels.append({
                'width': 300,
                'height': 280,
                'preferred_x': 800
            })

        # 简单布局：从左到右排列，留出10像素间距
        current_x = 10
        for i, panel in enumerate(panels):
            panel['x'] = current_x
            panel['y'] = self.height - panel['height'] - 60
            current_x += panel['width'] + 10

        return panels

    def is_cursor_over_panel(self, pos):
        """
        检测光标是否在任何面板或UI元素上

        Args:
            pos: 光标位置 (x, y)

        Returns:
            bool: 如果光标在面板或UI元素上返回True，否则返回False
        """
        # 检查顶部UI元素区域
        if self.is_cursor_over_top_ui(pos):
            return True

        # 检查所有拖拽面板
        if self.is_cursor_over_draggable_panels(pos):
            return True

        # 检查Bernstein窗口
        if self.is_cursor_over_bernstein_window(pos):
            return True

        return False

    def is_cursor_over_top_ui(self, pos):
        """检测光标是否在顶部UI元素上"""
        # 检查缩放按钮
        for button in self.zoom_buttons:
            if button.rect.collidepoint(pos):
                return True

        # 检查音效按钮
        if self.music_button.rect.collidepoint(pos):
            return True
        if self.sound_button.rect.collidepoint(pos):
            return True

        # 检查模式切换按钮
        for button in self.mode_buttons:
            if button.rect.collidepoint(pos):
                return True

        # 检查帮助按钮
        if hasattr(self.help_module, 'button_rect') and self.help_module.button_rect:
            if self.help_module.button_rect.collidepoint(pos):
                return True

        return False

    def is_cursor_over_draggable_panels(self, pos):
        """检测光标是否在可拖拽面板上"""
        # 检查基本信息面板
        if self.info_panel.visible and self.info_panel.rect.collidepoint(pos):
            return True

        # 检查音频面板
        if (self.show_audio_controls and self.audio_panel.visible and
                self.audio_panel.rect.collidepoint(pos)):
            return True

        # 检查递归面板
        if (self.show_recursive_controls and self.current_mode == "recursive" and
                self.recursive_initialized and self.recursive_panel.visible and
                self.recursive_panel.rect.collidepoint(pos)):
            return True

        # 检查向量面板
        if (self.show_vector_controls and self.current_mode == "vector" and
                self.vector_initialized and self.vector_panel.visible and
                self.vector_panel.rect.collidepoint(pos)):
            return True

        # 检查动力学面板
        if (self.current_mode == "dynamic" and self.dynamic_initialized and
                self.dynamic_panel.visible and self.dynamic_panel.rect.collidepoint(pos)):
            return True

        # ====== 新增：检查3D演示面板 ======
        if (self.current_mode == "3ddemo" and self.demo_3d_initialized and
                self.demo_3d_panel.visible and self.demo_3d_panel.rect.collidepoint(pos)):
            return True

        return False

    def is_cursor_over_bernstein_window(self, pos):
        """检测光标是否在Bernstein窗口上"""
        if not self.bernstein_window.visible:
            return False

        # 检查整个Bernstein窗口区域
        bernstein_rect = pygame.Rect(
            self.bernstein_window_position[0],
            self.bernstein_window_position[1],
            self.bernstein_window.width,
            self.bernstein_window.height
        )

        return bernstein_rect.collidepoint(pos)

    def is_cursor_over_bernstein_data_panel(self, pos):
        """检测光标是否在 Bernstein 数据面板上"""
        if not self.bernstein_data_panel.visible:
            return False

        # 检查整个 Bernstein 数据面板区域
        return self.bernstein_data_panel.rect.collidepoint(pos)

    def draw_bernstein_data_panel(self):
        """绘制Bernstein基函数数据面板 - 简化固定高度版"""
        if not self.bernstein_data_panel.visible or self.current_mode != "vector":
            return

        # 获取Bernstein窗口的数据
        if not self.bernstein_window.visible or not hasattr(self.bernstein_window, 'bernstein_values'):
            # 如果没有数据，显示提示
            self.bernstein_data_panel.draw(self.screen, self.small_font)
            content_x = self.bernstein_data_panel.rect.x + 10
            content_y = self.bernstein_data_panel.rect.y + self.bernstein_data_panel.title_height + 10
            hint_text = "请先打开Bernstein窗口查看基函数"
            hint_surf = self.small_font.render(hint_text, True, (200, 200, 200))
            self.screen.blit(hint_surf, (content_x, content_y))
            return

        # 绘制面板（固定高度320）
        self.bernstein_data_panel.draw(self.screen, self.small_font)

        # 固定布局位置（基于320像素高度）
        panel_x = self.bernstein_data_panel.rect.x
        panel_y = self.bernstein_data_panel.rect.y
        panel_width = self.bernstein_data_panel.rect.width
        title_height = self.bernstein_data_panel.title_height

        content_x = panel_x + 10
        content_y = panel_y + title_height + 10
        content_width = panel_width - 20

        # ====== 固定位置定义（320像素高度下的布局）======
        t_y = content_y  # y=45 (标题栏25+边距10+10)
        header_y = t_y + 25  # y=70
        data_start_y = header_y + 20  # y=90
        page_control_y = data_start_y + 175  # y=265 (7行*25=175)
        total_y = page_control_y + 30  # y=295
        instruction_y = total_y + 20  # y=315
        # ====== 固定位置结束 ======

        # 获取Bernstein数据
        n = self.bernstein_window.n
        bernstein_values = self.bernstein_window.bernstein_values
        function_colors = self.bernstein_window.function_colors
        t_value = self.bernstein_window.t_value
        current_page = self.bernstein_window.data_current_page
        total_pages = self.bernstein_window.data_total_pages

        if n <= 0 or not bernstein_values:
            no_data_text = "没有可用的基函数数据"
            no_data_surf = self.small_font.render(no_data_text, True, (200, 200, 200))
            self.screen.blit(no_data_surf, (content_x, t_y))
            return

        # 每页固定显示7行
        per_page = 7
        row_height = 25

        # 更新分页设置
        if hasattr(self.bernstein_window, 'data_per_page'):
            self.bernstein_window.data_per_page = per_page
            self.bernstein_window.update_data_pages()

        # 计算当前页显示的数据范围
        start_index = current_page * per_page
        end_index = min(start_index + per_page, n + 1)

        # ====== 开始绘制 ======
        # 1. 绘制当前t值
        t_text = f"当前 t = {t_value:.3f}  阶数 n = {n}"
        t_surf = self.small_font.render(t_text, True, (255, 255, 100))
        self.screen.blit(t_surf, (content_x, t_y))

        # 最终列宽设置
        col1_width = 60  # 序号列
        col2_width = 60  # 颜色列
        col3_width = 70  # B(t)值
        col4_width = 150  # 贡献度（矩形条120 + 文本30）
        col_spacing = 8  # 列间距

        current_x = content_x
        index_title = self.small_font.render("序号", True, (255, 200, 100))
        self.screen.blit(index_title, (current_x, header_y))
        current_x += col1_width + col_spacing

        color_title = self.small_font.render("颜色", True, (255, 200, 100))
        self.screen.blit(color_title, (current_x, header_y))
        current_x += col2_width + col_spacing

        value_title = self.small_font.render("B(t)值", True, (255, 200, 100))
        self.screen.blit(value_title, (current_x, header_y))
        current_x += col3_width + col_spacing

        contrib_title = self.small_font.render("贡献度", True, (255, 200, 100))
        self.screen.blit(contrib_title, (current_x, header_y))

        # 3. 绘制分隔线
        line_y = header_y + 20
        pygame.draw.line(self.screen, (100, 100, 150),
                         (content_x, line_y),
                         (content_x + content_width, line_y), 1)

        # 绘制当前页的基函数数据（最多7个）
        for i in range(start_index, end_index):
            row_index = i - start_index
            row_y = line_y + 5 + row_index * row_height

            # 重置当前x位置
            current_x = content_x

            # 1. 序号
            func_name = f"B{i}"
            func_text = self.small_font.render(func_name, True, (220, 220, 220))
            self.screen.blit(func_text, (current_x, row_y))
            current_x += col1_width + col_spacing

            # 2. 颜色方块
            color_idx = i % len(function_colors)
            color = function_colors[color_idx]
            color_rect = pygame.Rect(current_x, row_y, 12, 12)  # 更小的方块
            pygame.draw.rect(self.screen, color, color_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), color_rect, 1)
            current_x += col2_width + col_spacing

            # 3. B(t)值
            if i < len(bernstein_values):
                b_value = bernstein_values[i]
                if abs(b_value) < 0.0001:
                    value_str = "0.000"
                elif abs(b_value - 1.0) < 0.0001:
                    value_str = "1.000"
                else:
                    value_str = f"{b_value:.3f}"
            else:
                value_str = "0.000"

            value_text = self.small_font.render(value_str, True, (180, 255, 180))
            self.screen.blit(value_text, (current_x, row_y))
            current_x += col3_width + col_spacing

            # 4. 贡献度可视化 - 紧凑版
            if i < len(bernstein_values):
                contribution = bernstein_values[i] * 100

                # 获取基函数颜色
                color_idx = i % len(function_colors)
                function_color = function_colors[color_idx]

                # 矩形条
                bar_x = current_x
                bar_y = row_y + 3
                bar_width = 120  # 适当宽度
                bar_height = 12  # 稍小高度

                # 背景
                bar_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
                pygame.draw.rect(self.screen, (50, 50, 70), bar_bg_rect, border_radius=2)
                pygame.draw.rect(self.screen, (80, 80, 100), bar_bg_rect, 1, border_radius=2)

                # 填充
                fill_width = int((contribution / 100.0) * bar_width)
                if fill_width > 0:
                    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
                    pygame.draw.rect(self.screen, function_color, fill_rect, border_radius=2)
                    pygame.draw.rect(self.screen, (255, 255, 255), fill_rect, 1, border_radius=2)

                # 百分比文本（紧挨着矩形条）
                if contribution < 0.01:
                    contrib_str = "0%"
                elif contribution < 1:
                    contrib_str = f"{contribution:.1f}%"
                else:
                    contrib_str = f"{contribution:.0f}%"

                text_x = bar_x + bar_width + 3  # 更小的间距
                text_y = row_y

                # 文本颜色根据基函数颜色调整亮度
                text_color = (
                    min(255, function_color[0] + 100),
                    min(255, function_color[1] + 100),
                    min(255, function_color[2] + 100)
                )

                contrib_text = self.small_font.render(contrib_str, True, text_color)
                self.screen.blit(contrib_text, (text_x, text_y))

                current_x += col4_width + col_spacing

        # 5. 绘制分页控制（在固定位置 page_control_y）
        page_y = page_control_y

        # 上一页按钮
        prev_btn_rect = pygame.Rect(content_x, page_y, 60, 25)
        prev_hover = prev_btn_rect.collidepoint(pygame.mouse.get_pos())
        prev_color = (100, 150, 200) if prev_hover else (80, 130, 180)

        pygame.draw.rect(self.screen, prev_color, prev_btn_rect, border_radius=4)
        pygame.draw.rect(self.screen, (255, 255, 255), prev_btn_rect, 1, border_radius=4)

        prev_text = self.small_font.render("上一页", True, (255, 255, 255))
        prev_text_rect = prev_text.get_rect(center=prev_btn_rect.center)
        self.screen.blit(prev_text, prev_text_rect)

        # 页面指示
        page_info = f"第 {current_page + 1} / {total_pages} 页"
        page_surf = self.small_font.render(page_info, True, (200, 200, 255))
        page_rect = page_surf.get_rect(center=(content_x + content_width // 2, page_y + 12))
        self.screen.blit(page_surf, page_rect)

        # 下一页按钮
        next_btn_rect = pygame.Rect(content_x + content_width - 60, page_y, 60, 25)
        next_hover = next_btn_rect.collidepoint(pygame.mouse.get_pos())
        next_color = (100, 150, 200) if next_hover else (80, 130, 180)

        pygame.draw.rect(self.screen, next_color, next_btn_rect, border_radius=4)
        pygame.draw.rect(self.screen, (255, 255, 255), next_btn_rect, 1, border_radius=4)

        next_text = self.small_font.render("下一页", True, (255, 255, 255))
        next_text_rect = next_text.get_rect(center=next_btn_rect.center)
        self.screen.blit(next_text, next_text_rect)

        # 保存按钮矩形用于点击检测
        self.data_prev_btn_rect = prev_btn_rect
        self.data_next_btn_rect = next_btn_rect

        # 6. 绘制总计行（在固定位置 total_y）
        total_y_pos = total_y

        # 计算当前显示页面的小计
        page_sum = 0.0
        for i in range(start_index, end_index):
            if i < len(bernstein_values):
                page_sum += bernstein_values[i]

        total_sum = sum(bernstein_values) if bernstein_values else 0.0
        total_text = f"小计: {page_sum:.3f} | 总计: {total_sum:.3f} (理论值: 1.000)"

        # 根据与1.0的接近程度选择颜色
        if abs(total_sum - 1.0) < 0.001:
            total_color = (100, 255, 100)  # 绿色
        elif abs(total_sum - 1.0) < 0.01:
            total_color = (255, 255, 100)  # 黄色
        else:
            total_color = (255, 150, 100)  # 橙色

        total_surf = self.small_font.render(total_text, True, total_color)
        self.screen.blit(total_surf, (content_x, total_y_pos))

        # 7. 绘制翻页说明（在固定位置 instruction_y）
        instruction_y_pos = instruction_y

        # 简单的判断：如果 small_font 能渲染中文就显示中文，否则显示英文
        if self.small_font:
            # 先尝试中文
            instruction_text = "点击按钮翻页 | 键盘: ← → 翻页"
            instruction_surf = self.small_font.render(instruction_text, True, (180, 180, 220))

            # 如果渲染结果有效（非空）就使用
            if instruction_surf.get_width() > 50:  # 中文文本应该有一定宽度
                instruction_rect = instruction_surf.get_rect(center=(content_x + content_width // 2, instruction_y_pos))
                self.screen.blit(instruction_surf, instruction_rect)
            else:
                # 中文渲染失败，使用英文
                instruction_text = "Click buttons or use ← → keys"
                instruction_surf = self.small_font.render(instruction_text, True, (180, 180, 220))
                instruction_rect = instruction_surf.get_rect(center=(content_x + content_width // 2, instruction_y_pos))
                self.screen.blit(instruction_surf, instruction_rect)

    def check_panel_events(self, event):
        """检查各个面板是否处理了事件"""
        panel_handled = False

        # 基本信息面板
        if self.info_panel.visible:
            if self.info_panel.handle_event(event):
                panel_handled = True

        # 音频面板
        if self.show_audio_controls and self.audio_panel.visible:
            if self.audio_panel.handle_event(event):
                panel_handled = True

        # 递归面板
        if (self.show_recursive_controls and self.current_mode == "recursive"
                and self.recursive_initialized and self.recursive_panel.visible):
            if self.recursive_panel.handle_event(event):
                panel_handled = True

        # 向量面板
        if (self.show_vector_controls and self.current_mode == "vector"
                and self.vector_initialized and self.vector_panel.visible):
            if self.vector_panel.handle_event(event):
                panel_handled = True

        # 动力学面板
        if (self.current_mode == "dynamic" and self.dynamic_initialized
                and self.dynamic_panel.visible):
            if self.dynamic_panel.handle_event(event):
                panel_handled = True

        # Bernstein数据面板
        if self.bernstein_data_panel.visible:
            if self.bernstein_data_panel.handle_event(event):
                panel_handled = True

        # ====== 新增：3D演示面板 ======
        if (self.current_mode == "3ddemo" and self.demo_3d_initialized
                and self.demo_3d_panel.visible):
            if self.demo_3d_panel.handle_event(event):
                panel_handled = True

        return panel_handled

    def draw_demo_3d_controls(self):
        """绘制3D演示控制面板"""
        if self.current_mode != "3ddemo" or not self.demo_3d_initialized:
            return
        if not self.demo_3d_panel.visible:
            return

        # 首先绘制面板背景和标题栏
        self.demo_3d_panel.draw(self.screen, self.small_font)

        # 按钮布局
        panel_x = self.demo_3d_panel.rect.x
        panel_y = self.demo_3d_panel.rect.y
        panel_width = self.demo_3d_panel.rect.width
        title_height = 25

        button_start_x = panel_x + 20
        button_start_y = panel_y + title_height + 15
        button_width = panel_width - 40
        button_height = 22  # 稍微矮一点
        button_spacing = 6  # 间距小一点

        # 更新按钮位置
        for i, button in enumerate(self.demo_3d_buttons):
            button.rect.x = button_start_x
            button.rect.y = button_start_y + i * (button_height + button_spacing)
            button.rect.width = button_width
            button.rect.height = button_height
            button.draw(self.screen, self.small_font)

        # 绘制视角控制说明
        controls_y = button_start_y + len(self.demo_3d_buttons) * (button_height + button_spacing) + 5

        if self.small_font:
            for i, text in enumerate(self.view_controls_text):
                text_surf = self.small_font.render(text, True, (180, 180, 220))
                self.screen.blit(text_surf, (button_start_x, controls_y + i * 18))


class ScaleManager:
    """全局缩放和平移管理器"""

    def __init__(self):
        self.scale = 1.0
        self.min_scale = 0.3
        self.max_scale = 3.0
        self.scale_step = 0.1
        self.scale_center = (600, 400)  # 默认缩放中心（屏幕中心）

        # 新增：平移相关属性
        self.translation = (0, 0)  # 平移偏移量 (dx, dy)
        self.is_panning = False  # 是否正在平移
        self.pan_start_pos = (0, 0)  # 平移开始位置
        self.pan_start_offset = (0, 0)  # 平移开始的偏移量

    def zoom_in(self):
        """放大"""
        new_scale = self.scale + self.scale_step
        if new_scale <= self.max_scale:
            self.scale = new_scale
            return True
        return False

    def zoom_out(self):
        """缩小"""
        new_scale = self.scale - self.scale_step
        if new_scale >= self.min_scale:
            self.scale = new_scale
            return True
        return False

    def reset(self):
        """重置缩放和平移"""
        self.scale = 1.0
        self.translation = (0, 0)
        return True

    def get_scale(self):
        """获取当前缩放比例"""
        return self.scale

    def set_scale_center(self, center):
        """设置缩放中心点"""
        self.scale_center = center

    def start_pan(self, start_pos):
        """开始平移"""
        self.is_panning = True
        self.pan_start_pos = start_pos
        self.pan_start_offset = self.translation

    def update_pan(self, current_pos):
        """更新平移"""
        if not self.is_panning:
            return

        dx = current_pos[0] - self.pan_start_pos[0]
        dy = current_pos[1] - self.pan_start_pos[1]

        self.translation = (
            self.pan_start_offset[0] + dx,
            self.pan_start_offset[1] + dy
        )

    def end_pan(self):
        """结束平移"""
        self.is_panning = False

    def apply_scale_and_translation_to_point(self, point):
        """将缩放和平移应用到点（世界坐标 -> 屏幕坐标）"""
        if self.scale == 1.0 and self.translation == (0, 0):
            return point

        x, y = point
        center_x, center_y = self.scale_center
        dx, dy = self.translation

        # 1. 相对于缩放中心进行缩放
        scaled_x = center_x + (x - center_x) * self.scale
        scaled_y = center_y + (y - center_y) * self.scale

        # 2. 应用平移
        translated_x = scaled_x + dx
        translated_y = scaled_y + dy

        return (int(translated_x), int(translated_y))

    def apply_scale_to_point(self, point):
        """向后兼容的方法（只应用缩放）"""
        return self.apply_scale_and_translation_to_point(point)

    def apply_scale_to_points(self, points):
        """将缩放和平移应用到点列表"""
        if (self.scale == 1.0 and self.translation == (0, 0)) or not points:
            return points

        scaled_points = []
        for point in points:
            scaled_points.append(self.apply_scale_and_translation_to_point(point))

        return scaled_points

    def inverse_scale_point(self, point):
        """将屏幕坐标反向转换回世界坐标（考虑缩放和平移）"""
        if self.scale == 1.0 and self.translation == (0, 0):
            return point

        x, y = point
        center_x, center_y = self.scale_center
        dx, dy = self.translation

        # 1. 反向平移
        untranslated_x = x - dx
        untranslated_y = y - dy

        # 2. 反向缩放
        original_x = center_x + (untranslated_x - center_x) / self.scale
        original_y = center_y + (untranslated_y - center_y) / self.scale

        return (int(original_x), int(original_y))

    def get_translation_status(self):
        """获取平移状态"""
        dx, dy = self.translation
        return f"平移: ({dx}, {dy})"

    def is_zoomed_or_panned(self):
        """检查是否有缩放或平移"""
        return self.scale != 1.0 or self.translation != (0, 0)


class ZoomButton:
    """缩放按钮类，使用图标"""

    def __init__(self, x, y, size=40, icon_name="", tooltip="", scale_manager=None):
        """
        初始化缩放按钮

        Args:
            x, y: 按钮位置
            size: 按钮大小
            icon_name: 图标名称
            tooltip: 提示文本
            scale_manager: 缩放管理器
        """
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.icon_name = icon_name
        self.tooltip = tooltip
        self.scale_manager = scale_manager
        self.hovered = False
        self.clicked = False

        # 加载图标
        self.icon = self.load_icon(icon_name)

        # 颜色
        self.normal_color = (80, 140, 190)
        self.hover_color = (110, 170, 220)
        self.disabled_color = (100, 100, 120)

    def load_icon(self, icon_name):
        """加载图标文件 - 使用新的resources目录结构"""
        if not icon_name:
            return None

        # 优先使用新的 resources/icons 目录
        icon_paths = [
            get_resource_path(os.path.join("resources", "icons", icon_name)),
            get_resource_path(os.path.join("assets", "icons", icon_name)),  # 兼容旧路径
        ]

        icon_path = None
        for path in icon_paths:
            if os.path.exists(path):
                icon_path = path
                break

        print(f"尝试加载缩放图标: {icon_path or '未找到'}")

        if icon_path and os.path.exists(icon_path):
            try:
                icon = pygame.image.load(icon_path)
                # 转换格式以确保透明度正确
                icon = icon.convert_alpha()
                # 缩放到指定大小
                scaled_icon = pygame.transform.scale(
                    icon, (self.size - 10, self.size - 10)  # 图标比按钮小一些
                )
                print(f"✅ 加载缩放图标成功: {icon_name}")
                return scaled_icon
            except Exception as e:
                print(f"❌ 加载缩放图标失败 {icon_path}: {e}")
                # 列出可能的图标文件帮助调试
                self._debug_icon_files()
                return self.create_fallback_icon()
        else:
            print(f"⚠ 缩放图标文件不存在")
            # 列出可用的图标文件
            self._debug_icon_files()
            return self.create_fallback_icon()

    def _debug_icon_files(self):
        """调试信息：列出可用的图标文件"""
        print("🔍 搜索可用的图标文件...")

        # 检查新的 resources/icons 目录
        resources_icons_path = get_resource_path(os.path.join("resources", "icons"))
        if os.path.exists(resources_icons_path):
            print(f"📁 resources/icons 目录内容:")
            try:
                for item in os.listdir(resources_icons_path):
                    if item.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        item_path = os.path.join(resources_icons_path, item)
                        is_file = os.path.isfile(item_path)
                        print(f"    📄 {item}")
            except Exception as e:
                print(f"    读取失败: {e}")
        else:
            print(f"📁 resources/icons 目录不存在: {resources_icons_path}")

        # 检查旧的 assets/icons 目录
        assets_icons_path = get_resource_path(os.path.join("assets", "icons"))
        if os.path.exists(assets_icons_path):
            print(f"📁 assets/icons 目录内容:")
            try:
                for item in os.listdir(assets_icons_path):
                    if item.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        item_path = os.path.join(assets_icons_path, item)
                        is_file = os.path.isfile(item_path)
                        print(f"    📄 {item}")
            except Exception as e:
                print(f"    读取失败: {e}")
        else:
            print(f"📁 assets/icons 目录不存在: {assets_icons_path}")

    def create_fallback_icon(self, color=None):
        """创建备用图标（当真实图标加载失败时使用）"""
        if color is None:
            # 根据图标名称选择颜色
            color_map = {
                'zoom_in': (0, 100, 0),  # 深绿色
                'zoom_out': (100, 0, 0),  # 深红色
                'zoom_reset': (0, 0, 100),  # 深蓝色
                'sound_on': (0, 100, 100),  # 青色
                'sound_off': (50, 50, 50),  # 灰色
                'music_on': (100, 0, 100),  # 紫色
                'music_off': (70, 70, 70),  # 深灰色
            }
            color = color_map.get(self.icon_name, (128, 128, 128))  # 默认灰色

        # 创建纯色图标
        size = self.size - 10
        icon = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(icon, color + (200,), (0, 0, size, size), border_radius=5)

        # 添加简单图标符号
        icon_center = size // 2

        # 根据图标名称绘制不同符号
        if self.icon_name == 'zoom_in':
            # 绘制加号
            pygame.draw.rect(icon, (255, 255, 255),
                             (icon_center - 8, icon_center - 2, 16, 4))
            pygame.draw.rect(icon, (255, 255, 255),
                             (icon_center - 2, icon_center - 8, 4, 16))
        elif self.icon_name == 'zoom_out':
            # 绘制减号
            pygame.draw.rect(icon, (255, 255, 255),
                             (icon_center - 8, icon_center - 2, 16, 4))
        elif self.icon_name == 'zoom_reset':
            # 绘制循环箭头
            pygame.draw.arc(icon, (255, 255, 255),
                            (icon_center - 7, icon_center - 7, 14, 14),
                            0, 3.14, 2)
        elif 'sound' in self.icon_name:
            # 绘制音量图标
            pygame.draw.polygon(icon, (255, 255, 255), [
                (icon_center - 5, icon_center + 5),
                (icon_center - 5, icon_center - 5),
                (icon_center, icon_center - 5),
                (icon_center + 5, icon_center),
                (icon_center, icon_center + 5)
            ])
            if 'off' in self.icon_name:
                # 绘制禁止线
                pygame.draw.line(icon, (255, 0, 0),
                                 (icon_center - 7, icon_center - 7),
                                 (icon_center + 7, icon_center + 7), 2)

        print(f"📝 使用备用图标: {self.icon_name}")
        return icon

    def create_fallback_icon(self):
        """创建备用图标（当图标文件无法加载时）"""
        surface = pygame.Surface((self.size - 10, self.size - 10), pygame.SRCALPHA)

        # 根据图标名称创建不同的备用图标
        if "zoom_in" in self.icon_name:
            # 放大图标：加号
            color = (100, 200, 100)
            # 绘制加号
            center = (self.size - 10) // 2
            pygame.draw.line(surface, (255, 255, 255),
                             (center, 5), (center, (self.size - 10) - 5), 3)
            pygame.draw.line(surface, (255, 255, 255),
                             (5, center), ((self.size - 10) - 5, center), 3)
        elif "zoom_out" in self.icon_name:
            # 缩小图标：减号
            color = (200, 100, 100)
            center = (self.size - 10) // 2
            pygame.draw.line(surface, (255, 255, 255),
                             (5, center), ((self.size - 10) - 5, center), 3)
        elif "reset" in self.icon_name or "zoom_reset" in self.icon_name:
            # 重置图标：圆形箭头
            color = (150, 150, 200)
            # 绘制圆形
            center = (self.size - 10) // 2
            radius = (self.size - 10) // 2 - 3
            pygame.draw.circle(surface, (255, 255, 255), (center, center), radius, 2)
            # 绘制箭头
            pygame.draw.line(surface, (255, 255, 255),
                             (center + radius - 5, center - 5),
                             (center + radius, center), 2)
            pygame.draw.line(surface, (255, 255, 255),
                             (center + radius - 5, center + 5),
                             (center + radius, center), 2)
        else:
            # 默认图标
            color = (150, 150, 150)

        # 绘制背景
        pygame.draw.rect(surface, color, (0, 0, self.size - 10, self.size - 10), border_radius=5)
        pygame.draw.rect(surface, (255, 255, 255), (0, 0, self.size - 10, self.size - 10), 2, border_radius=5)

        return surface

    def draw(self, screen, font=None):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        # 检查是否可用
        enabled = self.is_enabled()

        # 确定颜色
        if not enabled:
            bg_color = self.disabled_color
        elif self.hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.normal_color

        # 绘制按钮背景
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        border_color = (180, 180, 180) if not enabled else (255, 255, 255)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)

        # 图标半透明效果（如果禁用）
        if self.icon:
            icon_x = self.rect.x + (self.rect.width - self.icon.get_width()) // 2
            icon_y = self.rect.y + (self.rect.height - self.icon.get_height()) // 2

            if not enabled:
                # 创建半透明版本
                transparent_icon = self.icon.copy()
                transparent_icon.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
                screen.blit(transparent_icon, (icon_x, icon_y))
            else:
                screen.blit(self.icon, (icon_x, icon_y))

        # 只绘制可用按钮的工具提示
        if enabled and self.hovered and self.tooltip and font:
            self.draw_tooltip(screen, font)

        return self.hovered and enabled

    def draw_tooltip(self, screen, font):
        """绘制工具提示"""
        text_surf = font.render(self.tooltip, True, (255, 255, 255))
        text_rect = text_surf.get_rect()

        # 工具提示位置（按钮下方）
        tooltip_rect = pygame.Rect(
            self.rect.centerx - text_rect.width // 2,
            self.rect.bottom + 5,
            text_rect.width + 10,
            20
        )

        # 绘制背景
        pygame.draw.rect(screen, (40, 40, 60), tooltip_rect, border_radius=4)
        pygame.draw.rect(screen, (100, 100, 120), tooltip_rect, 1, border_radius=4)

        # 绘制文字
        screen.blit(text_surf, (tooltip_rect.x + 5, tooltip_rect.y + 2))

    def handle_click(self, pos):
        """处理点击"""
        if self.rect.collidepoint(pos):
            self.clicked = True
            return True
        return False

    def update_scale_manager(self, scale_manager):
        """更新缩放管理器引用"""
        self.scale_manager = scale_manager

    def is_enabled(self):
        """检查按钮是否可用"""
        if not self.scale_manager:
            return True

        if "zoom_in" in self.icon_name:
            return self.scale_manager.get_scale() < self.scale_manager.max_scale
        elif "zoom_out" in self.icon_name:
            return self.scale_manager.get_scale() > self.scale_manager.min_scale

        return True  # 重置按钮始终可用


if __name__ == "__main__":
    app = BezierApp()
    app.run()
