import pygame
import os
import sys


class FontLoader:
    """字体加载器，专门处理中文字体显示"""

    @staticmethod
    def get_resource_path(relative_path):
        """获取资源绝对路径"""
        try:
            # PyInstaller 创建临时文件夹
            base_path = sys._MEIPASS
        except AttributeError:
            # 开发环境 - 从字体文件位置计算项目根目录
            current_file = os.path.abspath(__file__)
            # 从 src/core 向上到项目根目录
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

        full_path = os.path.join(base_path, relative_path)
        return os.path.normpath(full_path)

    @classmethod
    def load_chinese_fonts(cls):
        """
        加载中文字体，优先尝试中文系统字体

        Returns:
            tuple: (main_font, small_font, chinese_available)
        """
        chinese_available = False

        # 系统字体路径列表
        system_fonts = []

        # Windows中文系统字体路径
        if sys.platform.startswith('win'):
            system_fonts = [
                "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑粗体
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
                "C:/Windows/Fonts/simkai.ttf",  # 楷体
                "C:/Windows/Fonts/Deng.ttf",  # 等线
                "C:/Windows/Fonts/Dengb.ttf",  # 等线粗体
            ]
        # macOS中文系统字体
        elif sys.platform.startswith('darwin'):
            system_fonts = [
                "/System/Library/Fonts/PingFang.ttc",  # 苹方
                "/System/Library/Fonts/STHeiti Light.ttc",  # 华文黑体
                "/System/Library/Fonts/STHeiti Medium.ttc",
            ]
        # Linux中文字体
        else:
            system_fonts = [
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 文泉驿微米黑
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # 文泉驿正黑
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Noto字体
            ]

        # 项目资源字体路径（使用新的目录结构）
        project_fonts = [
            "resources/fonts/msyh.ttf",  # 微软雅黑
            "resources/fonts/simhei.ttf",  # 黑体
            "fonts/msyh.ttf",  # 兼容旧路径
            "fonts/simhei.ttf",  # 兼容旧路径
        ]

        # 转换项目字体为绝对路径
        project_fonts_full = [cls.get_resource_path(font) for font in project_fonts]

        # 合并所有字体路径
        all_fonts = project_fonts_full + system_fonts

        main_font = None
        small_font = None

        for font_path in all_fonts:
            if os.path.exists(font_path):
                try:
                    # 加载主字体
                    main_font = pygame.font.Font(font_path, 18)
                    # 加载小字体
                    small_font = pygame.font.Font(font_path, 14)

                    # 测试中文字符显示
                    test_text = "测试"
                    try:
                        main_font.render(test_text, True, (255, 255, 255))
                        chinese_available = True
                        print(f"✓ 成功加载中文字体: {os.path.basename(font_path)}")
                        return main_font, small_font, chinese_available
                    except:
                        print(f"字体文件存在但可能不支持中文: {font_path}")
                        continue

                except Exception as e:
                    print(f"加载字体失败 {font_path}: {e}")
                    continue

        # 如果找不到中文字体，使用系统英文字体
        print("⚠ 未找到中文字体，使用英文字体")
        try:
            main_font = pygame.font.SysFont("arial", 18)
            small_font = pygame.font.SysFont("arial", 14)
        except:
            main_font = pygame.font.Font(None, 18)
            small_font = pygame.font.Font(None, 14)

        return main_font, small_font, chinese_available