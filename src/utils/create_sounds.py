import pygame
import numpy as np
import os


def create_sine_wave(frequency, duration, sample_rate=22050, volume=0.5):
    """创建正弦波"""
    samples = int(duration * sample_rate)
    t = np.arange(samples) / sample_rate
    wave = volume * np.sin(2 * np.pi * frequency * t)
    return (wave * 32767).astype(np.int16)


def save_sound(filename, wave_data, channels=2, sample_rate=22050):
    """保存音效为WAV文件"""
    stereo_data = np.column_stack([wave_data, wave_data])  # 转为立体声
    sound = pygame.sndarray.make_sound(stereo_data)
    pygame.mixer.init(sample_rate, -16, channels, 512)
    pygame.mixer.Sound.save(sound, filename)


def create_all_sounds():
    """创建所有音效文件"""
    # 确保sounds文件夹存在
    os.makedirs("sounds", exist_ok=True)

    # 创建点击音效
    click_wave = create_sine_wave(800, 0.05, volume=0.3)
    save_sound("sounds/click.wav", click_wave)

    # 创建添加控制点音效
    add_wave = create_sine_wave(600, 0.1, volume=0.4)
    save_sound("sounds/add_point.wav", add_wave)

    # 创建删除控制点音效
    delete_wave = create_sine_wave(400, 0.1, volume=0.4)
    save_sound("sounds/delete_point.wav", delete_wave)

    # 创建模式切换音效
    switch_wave = create_sine_wave(500, 0.15, volume=0.4)
    save_sound("sounds/mode_switch.wav", switch_wave)

    # 创建错误音效
    error_wave = create_sine_wave(300, 0.2, volume=0.5)
    save_sound("sounds/error.wav", error_wave)

    print("所有音效文件已创建完成！")


if __name__ == "__main__":
    pygame.init()
    create_all_sounds()