import pygame
import os
import sys
from typing import Dict


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
        # 开发环境 - 从声音文件位置计算项目根目录
        current_file = os.path.abspath(__file__)
        # 从 src/core 向上到项目根目录
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

    # 构建完整路径
    full_path = os.path.join(base_path, relative_path)

    # 标准化路径
    full_path = os.path.normpath(full_path)

    return full_path


class SoundManager:
    """音效管理器 - 支持MP3格式"""

    def __init__(self, sounds_folder="resources/sounds"):
        """
        初始化音效管理器

        Args:
            sounds_folder: 音效文件夹路径（相对于项目根目录）
        """
        # 使用 get_resource_path 获取正确的声音文件夹路径
        self.sounds_folder = get_resource_path(sounds_folder)

        # 调试信息
        print("=" * 40)
        print("初始化音效管理器")
        print("=" * 40)
        print(f"声音文件夹路径: {self.sounds_folder}")
        print(f"路径存在: {os.path.exists(self.sounds_folder)}")

        # 检查声音文件夹内容
        if os.path.exists(self.sounds_folder):
            print("声音文件夹内容:")
            for item in os.listdir(self.sounds_folder):
                item_path = os.path.join(self.sounds_folder, item)
                is_file = os.path.isfile(item_path)
                print(f"  {'📄' if is_file else '📁'} {item}")
        else:
            print(f"⚠ 警告: 声音文件夹不存在")
            print("尝试查找其他可能的位置...")

            # 尝试其他可能的路径
            possible_paths = [
                "resources/sounds",  # 新结构
                "sounds",  # 旧结构
                "../resources/sounds",  # 相对路径
                "../../resources/sounds",  # 更上级
            ]

            for path in possible_paths:
                test_path = get_resource_path(path)
                if os.path.exists(test_path):
                    print(f"✅ 在 '{path}' 找到声音文件夹")
                    self.sounds_folder = test_path
                    break

        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_playing = False
        self.sound_enabled = True
        self.music_enabled = True

        # 音量设置
        self.sound_volume = 0.7
        self.music_volume = 0.5

        # 初始化pygame mixer
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("✅ Pygame mixer 初始化成功")
        except pygame.error as e:
            print(f"❌ Pygame mixer 初始化失败: {e}")
            print("尝试使用默认参数初始化...")
            try:
                pygame.mixer.init()
                print("✅ 使用默认参数初始化成功")
            except pygame.error as e2:
                print(f"❌ 仍然失败: {e2}")
                print("音效功能将不可用")

        # 预定义的音效名称和对应的文件名
        self.sound_files = {
            'click': 'click.mp3',
            'add_point': 'add_point.mp3',
            'delete_point': 'delete_point.mp3',
            'mode_switch': 'mode_switch.mp3',
            'error': 'error.mp3'
        }

        # 加载所有音效
        self.load_sounds()

        print("=" * 40)

    def load_sounds(self):
        """加载所有MP3音效文件"""
        # 确保音效文件夹存在
        if not os.path.exists(self.sounds_folder):
            print(f"❌ 错误: 声音文件夹 '{self.sounds_folder}' 不存在!")
            print(f"请确保声音文件夹包含以下文件:")
            for sound_name, filename in self.sound_files.items():
                print(f"  - {filename} ({sound_name})")
            return

        # 检查并加载每个音效文件
        loaded_count = 0
        for sound_name, filename in self.sound_files.items():
            filepath = os.path.join(self.sounds_folder, filename)

            if not os.path.exists(filepath):
                print(f"⚠ 警告: 音效文件 '{filename}' 未找到!")
                print(f"  完整路径: {filepath}")
                continue

            try:
                # 加载MP3文件
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(self.sound_volume)
                self.sounds[sound_name] = sound
                print(f"✅ 加载音效: {filename}")
                loaded_count += 1
            except pygame.error as e:
                print(f"❌ 加载MP3文件 '{filename}' 失败: {e}")
                print("确保MP3文件有效且未损坏。")
                print(f"文件路径: {filepath}")
            except Exception as e:
                print(f"❌ 加载 '{filename}' 时出现意外错误: {e}")

        print(f"总计加载 {loaded_count}/{len(self.sound_files)} 个音效文件")

    def play_sound(self, sound_name: str) -> bool:
        """
        播放指定音效

        Args:
            sound_name: 音效名称 (click, add_point, delete_point, mode_switch, error)

        Returns:
            bool: 是否成功播放
        """
        if not self.sound_enabled:
            return False

        if sound_name not in self.sounds:
            print(f"音效 '{sound_name}' 未找到。可用音效: {list(self.sounds.keys())}")
            return False

        try:
            self.sounds[sound_name].play()
            return True
        except Exception as e:
            print(f"播放音效 '{sound_name}' 时出错: {e}")
            return False

    def play_background_music(self, music_file: str = "background.mp3") -> bool:
        """
        播放背景音乐

        Args:
            music_file: 音乐文件名

        Returns:
            bool: 是否成功播放
        """
        if not self.music_enabled:
            return False

        music_path = os.path.join(self.sounds_folder, music_file)

        if not os.path.exists(music_path):
            print(f"⚠ 背景音乐文件未找到: {music_path}")

            # 尝试其他常见格式
            alt_extensions = ['.mp3', '.ogg', '.wav', '.flac']
            for ext in alt_extensions:
                if music_file.endswith('.mp3'):
                    alt_filename = music_file.replace('.mp3', ext)
                else:
                    alt_filename = music_file.rsplit('.', 1)[0] + ext

                alt_path = os.path.join(self.sounds_folder, alt_filename)
                if os.path.exists(alt_path):
                    music_path = alt_path
                    print(f"✅ 找到替代格式: {alt_filename}")
                    break

        if not os.path.exists(music_path):
            print(f"❌ 背景音乐未找到: {music_path}")
            print(f"请添加背景音乐文件 (MP3, OGG, 或 WAV 格式) 到声音文件夹:")
            print(f"文件夹路径: {self.sounds_folder}")

            # 列出当前文件夹内容
            if os.path.exists(self.sounds_folder):
                print("当前文件夹内容:")
                for item in os.listdir(self.sounds_folder):
                    if item.lower().endswith(('.mp3', '.ogg', '.wav', '.flac')):
                        print(f"  📄 {item}")
            return False

        try:
            print(f"🎵 加载背景音乐: {os.path.basename(music_path)}")
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # -1表示循环播放
            self.music_playing = True
            print(f"✅ 正在播放背景音乐: {os.path.basename(music_path)}")
            return True
        except pygame.error as e:
            print(f"❌ 加载背景音乐失败: {e}")
            print(f"文件路径: {music_path}")
            print("可能原因: 文件格式不受支持或文件损坏")
            return False
        except Exception as e:
            print(f"❌ 播放背景音乐时出现意外错误: {e}")
            return False

    def stop_background_music(self):
        """停止背景音乐"""
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
            print("背景音乐已停止")

    def pause_background_music(self):
        """暂停背景音乐"""
        if self.music_playing:
            pygame.mixer.music.pause()
            print("背景音乐已暂停")

    def unpause_background_music(self):
        """恢复背景音乐"""
        if self.music_playing:
            pygame.mixer.music.unpause()
            print("背景音乐已恢复")

    def toggle_sound(self) -> bool:
        """
        切换音效开关

        Returns:
            bool: 切换后的音效状态
        """
        self.sound_enabled = not self.sound_enabled
        status = "开启" if self.sound_enabled else "关闭"
        print(f"音效 {status}")
        return self.sound_enabled

    def toggle_music(self) -> bool:
        """
        切换音乐开关

        Returns:
            bool: 切换后的音乐状态
        """
        self.music_enabled = not self.music_enabled

        if self.music_enabled:
            if not self.music_playing:
                self.play_background_music()
            else:
                self.unpause_background_music()
        else:
            self.pause_background_music()

        status = "开启" if self.music_enabled else "关闭"
        print(f"背景音乐 {status}")
        return self.music_enabled

    def set_sound_volume(self, volume: float):
        """
        设置音效音量

        Args:
            volume: 音量 (0.0 到 1.0)
        """
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound_name, sound in self.sounds.items():
            sound.set_volume(self.sound_volume)
        print(f"音效音量设置为 {self.sound_volume:.2f}")

    def set_music_volume(self, volume: float):
        """
        设置音乐音量

        Args:
            volume: 音量 (0.0 到 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        print(f"音乐音量设置为 {self.music_volume:.2f}")

    def get_volume_level(self) -> tuple:
        """
        获取当前音量级别

        Returns:
            tuple: (sound_volume, music_volume)
        """
        return self.sound_volume, self.music_volume

    def cleanup(self):
        """清理资源"""
        self.stop_background_music()
        pygame.mixer.quit()
        print("音效系统已清理")

    def get_loaded_sounds(self) -> list:
        """
        获取已加载的音效列表

        Returns:
            list: 已加载的音效名称列表
        """
        return list(self.sounds.keys())

    def get_status(self) -> dict:
        """
        获取音效管理器状态

        Returns:
            dict: 包含各种状态信息
        """
        return {
            'sound_enabled': self.sound_enabled,
            'music_enabled': self.music_enabled,
            'music_playing': self.music_playing,
            'sound_volume': self.sound_volume,
            'music_volume': self.music_volume,
            'loaded_sounds': self.get_loaded_sounds(),
            'sounds_folder': self.sounds_folder
        }


# 测试函数
def test_sound_manager():
    """测试音效管理器"""
    print("测试音效管理器...")

    # 初始化
    pygame.init()
    sound_manager = SoundManager()

    # 打印状态
    status = sound_manager.get_status()
    print("\n音效管理器状态:")
    for key, value in status.items():
        if key != 'sounds_folder':
            print(f"  {key}: {value}")

    # 测试播放音效
    print("\n测试音效播放:")
    for sound_name in ['click', 'add_point', 'delete_point']:
        if sound_name in sound_manager.sounds:
            print(f"  播放 {sound_name}...")
            sound_manager.play_sound(sound_name)
            pygame.time.wait(300)  # 等待300ms

    # 测试背景音乐
    print("\n测试背景音乐...")
    sound_manager.play_background_music()

    # 等待一段时间
    pygame.time.wait(3000)

    # 测试音量控制
    print("\n测试音量控制...")
    sound_manager.set_sound_volume(0.5)
    sound_manager.set_music_volume(0.3)

    # 清理
    sound_manager.cleanup()
    pygame.quit()

    print("\n测试完成!")


if __name__ == "__main__":
    test_sound_manager()