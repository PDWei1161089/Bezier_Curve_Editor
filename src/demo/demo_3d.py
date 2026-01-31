"""
demo_3d.py - 3D演示模式（动态外接立方体版本）
将2D Bezier曲线扩展到3D空间，用RGB立方体可视化
立方体大小自动适应控制点和曲线范围
优化版：Z轴作为向上轴，首尾固定为0和255
"""

import pygame
import math
import random
from typing import List, Tuple


class Demo3D:
    """3D演示模式 - Z轴作为向上轴"""

    def __init__(self):
        # 原始2D控制点
        self.control_points_2d = []
        # 3D控制点 (x, y, z) - 注意：这里z是向上轴
        self.control_points_3d = []
        # 3D曲线点
        self.curve_points_3d = []

        # 原始坐标范围（用于动态调整）
        self.original_x_range = (0, 0)
        self.original_y_range = (0, 0)
        self.original_z_range = (0, 0)

        # 动态立方体参数
        self.cube_size = 255  # RGB立方体最大尺寸
        self.visible_cube_size = 0  # 动态计算的可见立方体大小
        self.cube_vertices = []  # 立方体8个顶点
        self.cube_edges = []  # 立方体12条棱边

        # 缩放和平移参数（用于将点映射到立方体）
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale_z = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.offset_z = 0

        # 颜色映射缓存
        self.color_cache = {}

        # 视角参数 - 修改为更适合Z轴向上的视角
        self.view_angle_x = 45  # X轴旋转角度
        self.view_angle_y = -20  # Y轴旋转角度（负数让视角从上往下看）
        self.view_zoom = 1.2
        self.center_x, self.center_y = 600, 450

        # 预定义方向颜色 - 重新定义：X=红，Y=绿，Z=蓝（向上）
        self.axis_colors = {
            'X': (255, 0, 0),    # 红
            'Y': (0, 255, 0),    # 绿  
            'Z': (0, 0, 255),    # 蓝（向上）
            'origin': (255, 255, 255),
            'max_point': (255, 255, 255)
        }

        # 显示控制
        self.show_cube = True
        self.show_axes = True
        self.show_control_points = True
        self.show_curve = True
        self.show_coordinates = True

        # Z值生成选项（Z轴向上）
        self.z_generation_method = "smooth_random"  # 可选: "smooth_random", "sine_wave", "bezier", "parabolic"

    def calculate_bounding_box(self, points_3d):
        """计算3D点的包围盒"""
        if not points_3d:
            return (0, 0, 0), (0, 0, 0)

        # 初始化最小最大值
        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')

        for x, y, z in points_3d:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            min_z = min(min_z, z)  # z是向上轴
            max_x = max(max_x, x)
            max_y = max(max_y, y)
            max_z = max(max_z, z)

        # 确保有有效范围
        if min_x == max_x:
            max_x = min_x + 1
        if min_y == max_y:
            max_y = min_y + 1
        if min_z == max_z:
            max_z = min_z + 1

        return (min_x, min_y, min_z), (max_x, max_y, max_z)

    def normalize_and_scale_points(self, points_3d):
        """将3D点归一化并缩放到RGB立方体（0-255）"""
        if not points_3d:
            return []

        # 计算原始范围
        (min_x, min_y, min_z), (max_x, max_y, max_z) = self.calculate_bounding_box(points_3d)

        # 存储原始范围
        self.original_x_range = (min_x, max_x)
        self.original_y_range = (min_y, max_y)
        self.original_z_range = (min_z, max_z)

        # 计算范围大小
        range_x = max_x - min_x
        range_y = max_y - min_y
        range_z = max_z - min_z

        # 找到最大范围，用于统一缩放
        max_range = max(range_x, range_y, range_z)
        if max_range == 0:
            max_range = 1

        # 计算缩放因子（留10%边距）
        margin = 0.1  # 10%边距
        scale = self.cube_size * (1 - margin) / max_range

        # 计算偏移，使点居中
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        center_z = (min_z + max_z) / 2

        offset_x = self.cube_size / 2 - center_x * scale
        offset_y = self.cube_size / 2 - center_y * scale
        offset_z = self.cube_size / 2 - center_z * scale

        # 存储缩放和偏移参数
        self.scale_x = self.scale_y = self.scale_z = scale
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.offset_z = offset_z

        # 转换所有点
        scaled_points = []
        for x, y, z in points_3d:
            # 应用缩放和偏移
            scaled_x = x * scale + offset_x
            scaled_y = y * scale + offset_y
            scaled_z = z * scale + offset_z  # z是向上轴

            # 确保在0-255范围内
            scaled_x = max(0, min(255, scaled_x))
            scaled_y = max(0, min(255, scaled_y))
            scaled_z = max(0, min(255, scaled_z))

            scaled_points.append((scaled_x, scaled_y, scaled_z))

        # 计算可见立方体大小（基于缩放后的点）
        (scaled_min_x, scaled_min_y, scaled_min_z), (scaled_max_x, scaled_max_y, scaled_max_z) = \
            self.calculate_bounding_box(scaled_points)

        # 可见立方体大小是缩放后点的最大范围
        self.visible_cube_size = max(
            scaled_max_x - scaled_min_x,
            scaled_max_y - scaled_min_y,
            scaled_max_z - scaled_min_z
        )

        print(f"原始范围: X({min_x:.1f}-{max_x:.1f}), Y({min_y:.1f}-{max_y:.1f}), Z({min_z:.1f}-{max_z:.1f})")
        print(f"缩放因子: {scale:.3f}")
        print(f"偏移: ({offset_x:.1f}, {offset_y:.1f}, {offset_z:.1f})")
        print(f"可见立方体大小: {self.visible_cube_size:.1f}")

        return scaled_points

    def generate_initial_3d_points(self, points_2d):
        """从2D点生成初始3D点（Z轴作为向上轴，首尾固定为0和255）"""
        if len(points_2d) < 2:
            return []

        n = len(points_2d)
        z_values = []  # Z值列表（向上轴）
        
        # 确保第一个点Z=0（底部），最后一个点Z=255（顶部）
        z_values.append(0.0)  # 第一个点固定在底部
        
        if n == 2:
            # 只有两个点的情况
            z_values.append(255.0)  # 第二个点固定在顶部
        elif n == 3:
            # 三个点的情况：0, 中间随机, 255
            mid_z = random.uniform(50, 200)
            z_values.append(mid_z)
            z_values.append(255.0)
        else:
            # 四个点以上的情况
            # 根据选择的生成方法生成中间点的Z值（高度）
            if self.z_generation_method == "smooth_random":
                # 平滑随机分布
                for i in range(1, n-1):
                    # 使用归一化位置进行插值
                    t = i / (n - 1)
                    # 基础值在0-255之间线性插值（从底部到顶部）
                    base_z = 255 * t
                    # 添加随机扰动，但限制幅度
                    perturbation = random.uniform(-50, 50)
                    # 确保扰动不会使值超出范围
                    z = base_z + perturbation
                    z = max(0, min(255, z))
                    z_values.append(z)
                    
            elif self.z_generation_method == "sine_wave":
                # 正弦波分布 - 产生起伏效果
                for i in range(1, n-1):
                    t = i / (n - 1)
                    # 使用正弦函数生成起伏
                    wave = math.sin(2 * math.pi * t + random.uniform(0, 0.5))
                    # 振幅逐渐减小
                    amplitude = 80 * (1 - abs(t - 0.5))  # 中间振幅大，两端小
                    z = 127.5 + amplitude * wave  # 以127.5为中心
                    z = max(0, min(255, z))
                    z_values.append(z)
                    
            elif self.z_generation_method == "bezier":
                # 使用Bezier曲线生成Z值
                # 创建控制点：起点0，终点255，中间两个控制点随机
                cp1 = random.uniform(30, 100)
                cp2 = random.uniform(155, 225)
                
                for i in range(1, n-1):
                    t = i / (n - 1)
                    # 三次Bezier曲线
                    z = (1-t)**3 * 0 + 3*(1-t)**2*t * cp1 + 3*(1-t)*t**2 * cp2 + t**3 * 255
                    z = max(0, min(255, z))
                    z_values.append(z)
                    
            elif self.z_generation_method == "parabolic":
                # 抛物线分布 - 中间高，两边低
                for i in range(1, n-1):
                    t = i / (n - 1)
                    # 抛物线：在t=0.5处达到最大值
                    max_height = random.uniform(180, 255)
                    z = 4 * max_height * t * (1 - t)  # 标准抛物线
                    z = max(0, min(255, z))
                    z_values.append(z)
            
            else:  # 默认方法：平滑递增
                # 平滑递增分布
                for i in range(1, n-1):
                    t = i / (n - 1)
                    # 基础线性增长
                    base = 255 * t
                    # 添加一些随机性但保持趋势
                    if i == 1:
                        z = random.uniform(base * 0.3, base * 1.2)
                    else:
                        prev_z = z_values[-1]
                        # 确保大致递增但允许小幅波动
                        min_z = max(0, prev_z - 20)
                        max_z = min(255, prev_z + 40)
                        z = random.uniform(min_z, max_z)
                    
                    z = max(0, min(255, z))
                    z_values.append(z)
            
            # 添加最后一个点Z=255（顶部）
            z_values.append(255.0)

        # 验证Z值范围
        z_min = min(z_values)
        z_max = max(z_values)
        print(f"Z值范围（高度）: {z_min:.1f} - {z_max:.1f}")
        print(f"Z值生成方法: {self.z_generation_method}")
        print(f"底部点Z值: {z_values[0]}, 顶部点Z值: {z_values[-1]}")
        
        # 显示所有Z值
        for i, z in enumerate(z_values):
            print(f"  点{i}: 高度Z={z:.1f}")

        # 创建3D点：将2D点作为X,Y坐标，Z作为高度
        points_3d = []
        for i, (x, y) in enumerate(points_2d):
            # 注意：这里z_values[i]是高度（向上轴）
            points_3d.append((float(x), float(y), float(z_values[i])))

        return points_3d

    def set_control_points(self, points_2d: List[Tuple[int, int]]):
        """设置2D控制点并生成3D点"""
        self.control_points_2d = points_2d.copy()

        if not points_2d or len(points_2d) < 2:
            self.control_points_3d = []
            self.curve_points_3d = []
            return

        print("\n=== 生成3D控制点（Z轴向上）===")

        # 1. 生成初始3D点（Z作为高度）
        initial_3d_points = self.generate_initial_3d_points(points_2d)

        # 2. 将初始3D点缩放到RGB立方体
        self.control_points_3d = self.normalize_and_scale_points(initial_3d_points)

        # 3. 生成3D曲线
        self.generate_3d_curve()

        # 4. 生成RGB立方体（基于缩放后的点）
        self.generate_rgb_cube()

        # 5. 验证所有点在立方体内
        self.validate_points_in_cube()

    def bernstein_polynomial(self, n: int, i: int, t: float) -> float:
        """计算Bernstein基函数值"""
        if n == 0:
            return 1.0 if i == 0 else 0.0
        return math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

    def generate_3d_curve(self):
        """生成3D Bezier曲线"""
        self.curve_points_3d.clear()

        if len(self.control_points_3d) < 2:
            return

        n = len(self.control_points_3d) - 1
        steps = 100

        # 使用归一化前的原始3D点生成曲线
        initial_3d_points = self.generate_initial_3d_points(self.control_points_2d)

        # 生成原始曲线
        raw_curve_points = []
        for step in range(steps + 1):
            t = step / steps

            x, y, z = 0.0, 0.0, 0.0
            for i, (px, py, pz) in enumerate(initial_3d_points):
                b = self.bernstein_polynomial(n, i, t)
                x += px * b
                y += py * b
                z += pz * b  # z是高度

            raw_curve_points.append((x, y, z))

        # 将原始曲线点缩放到RGB立方体
        self.curve_points_3d = self.normalize_and_scale_points(raw_curve_points)

        print(f"生成曲线点: {len(self.curve_points_3d)} 个")
        
        # 验证曲线首尾点的Z值
        if self.curve_points_3d:
            first_z = self.curve_points_3d[0][2]
            last_z = self.curve_points_3d[-1][2]
            print(f"曲线底部Z值: {first_z:.1f}, 曲线顶部Z值: {last_z:.1f}")

    def generate_rgb_cube(self):
        """生成RGB立方体（基于实际点范围）"""
        # 使用完整的RGB立方体（0-255）
        full_size = 255

        # 8个顶点（完整RGB立方体）
        # 注意：这里Z轴是向上的（蓝色轴）
        self.cube_vertices = [
            (0, 0, 0),  # 0: 原点 (黑) - 底部
            (full_size, 0, 0),  # 1: 红 - 底部
            (0, full_size, 0),  # 2: 绿 - 底部
            (0, 0, full_size),  # 3: 蓝 - 顶部（Z轴向上）
            (full_size, full_size, 0),  # 4: 黄 - 底部
            (full_size, 0, full_size),  # 5: 品红 - 顶部
            (0, full_size, full_size),  # 6: 青色 - 顶部
            (full_size, full_size, full_size)  # 7: 白 - 顶部
        ]

        # 12条棱边
        self.cube_edges = [
            (0, 1, 'X'), (2, 4, 'X'), (3, 5, 'X'), (6, 7, 'X'),  # X轴边
            (0, 2, 'Y'), (1, 4, 'Y'), (3, 6, 'Y'), (5, 7, 'Y'),  # Y轴边
            (0, 3, 'Z'), (1, 5, 'Z'), (2, 6, 'Z'), (4, 7, 'Z')   # Z轴边（垂直）
        ]

    def get_color_for_point(self, point):
        """根据点的坐标获取RGB颜色"""
        if point in self.color_cache:
            return self.color_cache[point]

        x, y, z = point

        # 直接使用坐标作为RGB值（已确保在0-255范围内）
        r = int(max(0, min(255, x)))    # X -> 红色
        g = int(max(0, min(255, y)))    # Y -> 绿色
        b = int(max(0, min(255, z)))    # Z -> 蓝色（高度）

        color = (r, g, b)
        self.color_cache[point] = color
        return color

    def project_3d_to_2d(self, point_3d):
        """将3D点投影到2D屏幕（Z轴向上）"""
        x, y, z = point_3d  # z是向上轴

        # 向上偏移，减少底部留白
        y_offset = -80

        # 转换为相对于立方体中心的坐标
        cx, cy, cz = 127.5, 127.5, 127.5  # RGB立方体中心
        x_rel, y_rel, z_rel = x - cx, y - cy, z - cz

        # 转换为弧度
        angle_x = math.radians(self.view_angle_x)
        angle_y = math.radians(self.view_angle_y)

        # 绕X轴旋转（控制上下视角）
        # 先绕X轴旋转，让Z轴向上更明显
        y1 = y_rel * math.cos(angle_x) - z_rel * math.sin(angle_x)
        z1 = y_rel * math.sin(angle_x) + z_rel * math.cos(angle_x)

        # 绕Y轴旋转（控制左右视角）
        x1 = x_rel * math.cos(angle_y) + z1 * math.sin(angle_y)
        z2 = -x_rel * math.sin(angle_y) + z1 * math.cos(angle_y)

        # 透视效果（增强深度感）
        perspective = 0.85
        if perspective < 1.0:
            depth_factor = 1.0 - (z2 / (255 * 3))
            x1 *= depth_factor * perspective
            y1 *= depth_factor * perspective

        # 应用缩放并移动到屏幕中心
        screen_x = self.center_x + x1 * self.view_zoom
        screen_y = self.center_y - y1 * self.view_zoom + y_offset  # 减去y1因为屏幕y轴向下

        return (int(screen_x), int(screen_y))

    def validate_points_in_cube(self):
        """验证所有点都在RGB立方体（0-255）内"""
        print("\n=== 验证点是否在RGB立方体内（Z轴向上） ===")

        all_in_cube = True

        # 验证控制点
        for i, (x, y, z) in enumerate(self.control_points_3d):
            if x < 0 or x > 255 or y < 0 or y > 255 or z < 0 or z > 255:
                print(f"控制点 {i} 超出范围: ({x:.1f}, {y:.1f}, {z:.1f})")
                all_in_cube = False
            else:
                status = "✓"
                if i == 0 and abs(z) < 1:  # 第一个点应该接近0（底部）
                    status = "✓(底部)"
                elif i == len(self.control_points_3d) - 1 and abs(z - 255) < 1:  # 最后一个点应该接近255（顶部）
                    status = "✓(顶部)"
                print(f"控制点 {i}: X={x:.1f}, Y={y:.1f}, 高度Z={z:.1f} {status}")

        if all_in_cube:
            print("✓ 所有点都在RGB立方体（0-255）内")
        else:
            print("✗ 有些点超出立方体")

        return all_in_cube

    def draw_rgb_cube(self, surface):
        """绘制RGB立方体"""
        if not self.show_cube:
            return

        # 绘制立方体棱边
        for v1_idx, v2_idx, axis in self.cube_edges:
            v1 = self.cube_vertices[v1_idx]
            v2 = self.cube_vertices[v2_idx]

            color1 = self.get_color_for_point(v1)
            color2 = self.get_color_for_point(v2)

            screen_v1 = self.project_3d_to_2d(v1)
            screen_v2 = self.project_3d_to_2d(v2)

            self.draw_gradient_line(surface, screen_v1, screen_v2, color1, color2, 2)

        # 只显示原点和白色顶点
        important_vertices = [0, 7]
        for i in important_vertices:
            vertex = self.cube_vertices[i]
            screen_pos = self.project_3d_to_2d(vertex)
            color = self.get_color_for_point(vertex)

            pygame.draw.circle(surface, color, screen_pos, 8)
            pygame.draw.circle(surface, (255, 255, 255), screen_pos, 8, 2)

            if self.show_coordinates:
                font = pygame.font.Font(None, 14)
                if i == 0:
                    text = font.render("(0,0,0)", True, (255, 255, 255))
                    surface.blit(text, (screen_pos[0] + 10, screen_pos[1] - 10))
                elif i == 7:
                    text = font.render("(255,255,255)", True, (255, 255, 255))
                    surface.blit(text, (screen_pos[0] + 10, screen_pos[1] - 10))

    def draw_gradient_line(self, surface, start, end, color1, color2, width=2):
        """绘制渐变颜色的线段"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = max(1, math.sqrt(dx * dx + dy * dy))

        if length < 2:
            mid_color = (
                (color1[0] + color2[0]) // 2,
                (color1[1] + color2[1]) // 2,
                (color1[2] + color2[2]) // 2
            )
            pygame.draw.line(surface, mid_color, start, end, width)
            return

        steps = max(2, int(length / 3))

        for i in range(steps - 1):
            t1 = i / (steps - 1)
            t2 = (i + 1) / (steps - 1)

            x1 = start[0] + dx * t1
            y1 = start[1] + dy * t1
            x2 = start[0] + dx * t2
            y2 = start[1] + dy * t2

            r = int(color1[0] * (1 - t1) + color2[0] * t1)
            g = int(color1[1] * (1 - t1) + color2[1] * t1)
            b = int(color1[2] * (1 - t1) + color2[2] * t1)
            segment_color = (r, g, b)

            pygame.draw.line(surface, segment_color,
                           (int(x1), int(y1)), (int(x2), int(y2)), width)

    def draw_control_points(self, surface):
        """绘制3D控制点"""
        if not self.control_points_3d or not self.show_control_points:
            return

        # 绘制控制点连线
        if len(self.control_points_3d) > 1:
            for i in range(len(self.control_points_3d) - 1):
                p1 = self.control_points_3d[i]
                p2 = self.control_points_3d[i + 1]

                color1 = self.get_color_for_point(p1)
                color2 = self.get_color_for_point(p2)

                screen_p1 = self.project_3d_to_2d(p1)
                screen_p2 = self.project_3d_to_2d(p2)

                self.draw_gradient_line(surface, screen_p1, screen_p2, color1, color2, 3)

        # 绘制控制点
        for i, point in enumerate(self.control_points_3d):
            color = self.get_color_for_point(point)
            screen_pos = self.project_3d_to_2d(point)

            # 根据高度（Z值）调整点的大小
            z = point[2]
            size = 8 + int(z / 255 * 4)  # 高度越高，点越大
            
            pygame.draw.circle(surface, color, screen_pos, size)
            pygame.draw.circle(surface, (255, 255, 255), screen_pos, size, 2)

            font = pygame.font.Font(None, 16)
            point_text = font.render(str(i), True, (255, 255, 255))
            surface.blit(point_text, (screen_pos[0] + size + 2, screen_pos[1] - 10))

            if self.show_coordinates and i < 3:
                coord_font = pygame.font.Font(None, 12)
                coord_text = f"X={int(point[0])},Y={int(point[1])},Z={int(point[2])}"
                coord_surf = coord_font.render(coord_text, True, (200, 200, 200))

                text_rect = coord_surf.get_rect()
                bg_rect = pygame.Rect(
                    screen_pos[0] + 15, screen_pos[1] + 10,
                    text_rect.width + 6, text_rect.height + 4
                )
                pygame.draw.rect(surface, (40, 40, 60, 200), bg_rect, border_radius=3)
                pygame.draw.rect(surface, color, bg_rect, 1, border_radius=3)

                surface.blit(coord_surf, (screen_pos[0] + 18, screen_pos[1] + 12))

    def draw_curve(self, surface):
        """绘制3D曲线"""
        if len(self.curve_points_3d) < 2 or not self.show_curve:
            return

        points_2d = [self.project_3d_to_2d(p) for p in self.curve_points_3d]
        colors = [self.get_color_for_point(p) for p in self.curve_points_3d]

        for i in range(len(points_2d) - 1):
            start = points_2d[i]
            end = points_2d[i + 1]
            color1 = colors[i]
            color2 = colors[i + 1]

            self.draw_gradient_line(surface, start, end, color1, color2, 4)

        if points_2d:
            # 标记起点（底部）和终点（顶部）
            # 起点（底部，Z≈0）
            pygame.draw.circle(surface, (0, 255, 0), points_2d[0], 10)  # 绿色表示底部
            pygame.draw.circle(surface, (0, 0, 0), points_2d[0], 10, 2)
            
            # 终点（顶部，Z≈255）
            pygame.draw.circle(surface, (0, 0, 255), points_2d[-1], 10)  # 蓝色表示顶部
            pygame.draw.circle(surface, (255, 255, 255), points_2d[-1], 10, 2)
            
            # 添加文字标签
            font = pygame.font.Font(None, 14)
            start_text = font.render("", True, (0, 255, 0))
            end_text = font.render("", True, (0, 0, 255))
            surface.blit(start_text, (points_2d[0][0] + 12, points_2d[0][1] - 12))
            surface.blit(end_text, (points_2d[-1][0] + 12, points_2d[-1][1] - 12))

    def draw_coordinate_axes(self, surface):
        """绘制坐标轴（Z轴向上）"""
        if not self.show_axes:
            return

        font = pygame.font.Font(None, 18)

        # 坐标轴端点：X轴（红），Y轴（绿），Z轴（蓝，向上）
        axis_endpoints = [
            (255, 0, 0, "X", (255, 0, 0)),      # X轴 - 红色
            (0, 255, 0, "Y", (0, 255, 0)),      # Y轴 - 绿色
            (0, 0, 255, "Z", (0, 0, 255))       # Z轴 - 蓝色（向上）
        ]

        origin_2d = self.project_3d_to_2d((0, 0, 0))

        for x, y, z, label, color in axis_endpoints:
            end_2d = self.project_3d_to_2d((x, y, z))

            pygame.draw.line(surface, color, origin_2d, end_2d, 3)

            label_text = font.render(label, True, color)
            surface.blit(label_text, (end_2d[0] + 5, end_2d[1] - 10))

            self.draw_arrow(surface, origin_2d, end_2d, color)

        # 原点标记
        origin_text = font.render("O", True, (255, 255, 255))
        surface.blit(origin_text, (origin_2d[0] + 8, origin_2d[1] - 8))

    def draw_arrow(self, surface, start, end, color, arrow_size=12):
        """绘制箭头"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)

        if length < arrow_size * 1.5:
            pygame.draw.circle(surface, color, end, 5)
            return

        dx = dx / length
        dy = dy / length

        tip_x = end[0] - dx * arrow_size * 0.8
        tip_y = end[1] - dy * arrow_size * 0.8

        perp_x = -dy * arrow_size * 0.6
        perp_y = dx * arrow_size * 0.6

        points = [
            end,
            (int(tip_x + perp_x), int(tip_y + perp_y)),
            (int(tip_x - perp_x), int(tip_y - perp_y))
        ]

        pygame.draw.polygon(surface, color, points)

        pygame.draw.line(surface, color,
                       (int(tip_x), int(tip_y)),
                       (int(tip_x + dx * 5), int(tip_y + dy * 5)), 3)

    def draw_info_panel(self, surface, font):
        """绘制信息面板"""
        if not font:
            return

        info_lines = [
            f"控制点: {len(self.control_points_3d)}",
            f"视角: X={self.view_angle_x}°, Y={self.view_angle_y}°",
            f"缩放: {self.view_zoom:.1f}x",
            f"RGB立方体: 0-255",
            f"Z轴: 向上（高度）",
            f"Z生成: {self.z_generation_method}",
            f"底部Z=0, 顶部Z=255",
            "W/X:上下视角 C/D:左右视角",
            "Q/E:缩放 R:重置 Z:切换Z生成"
        ]

        panel_width = 220
        panel_height = len(info_lines) * 18 + 10
        panel_x = surface.get_width() - panel_width - 10
        panel_y = 80

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, (40, 40, 60, 180), panel_rect, border_radius=6)
        pygame.draw.rect(surface, (100, 100, 150), panel_rect, 1, border_radius=6)

        for i, line in enumerate(info_lines):
            color = (220, 220, 220) if i < 6 else (180, 200, 255)
            text_surf = font.render(line, True, color)
            surface.blit(text_surf, (panel_x + 10, panel_y + 5 + i * 18))

    def draw(self, surface, small_font=None):
        """绘制完整的3D场景"""
        if len(self.color_cache) > 1000:
            self.color_cache.clear()

        self.draw_rgb_cube(surface)
        self.draw_coordinate_axes(surface)
        self.draw_curve(surface)
        self.draw_control_points(surface)

        if small_font:
            self.draw_info_panel(surface, small_font)

    def rotate_view(self, delta_x=0, delta_y=0):
        """旋转视角"""
        self.view_angle_x = (self.view_angle_x + delta_x) % 360
        self.view_angle_y = (self.view_angle_y + delta_y) % 360

        if abs(delta_x) > 5 or abs(delta_y) > 5:
            self.color_cache.clear()

    def zoom_view(self, factor):
        """缩放视角"""
        old_zoom = self.view_zoom
        self.view_zoom *= factor
        self.view_zoom = max(0.5, min(3.0, self.view_zoom))

        if abs(self.view_zoom - old_zoom) > 0.2:
            self.color_cache.clear()

    def reset_view(self):
        """重置视角到默认位置"""
        self.view_angle_x = 45  # 默认X轴旋转角度
        self.view_angle_y = -20  # 默认Y轴旋转角度
        self.view_zoom = 1.2
        self.color_cache.clear()

    def toggle_visibility(self, element):
        """切换元素的显示/隐藏"""
        if element == 'cube':
            self.show_cube = not self.show_cube
        elif element == 'axes':
            self.show_axes = not self.show_axes
        elif element == 'control_points':
            self.show_control_points = not self.show_control_points
        elif element == 'curve':
            self.show_curve = not self.show_curve
        elif element == 'coordinates':
            self.show_coordinates = not self.show_coordinates

    def regenerate_z_values(self):
        """重新生成Z分量（循环使用不同的生成方法）"""
        if self.control_points_2d:
            print("重新生成Z分量（高度）...")
            
            # 循环切换Z值生成方法
            methods = ["smooth_random", "sine_wave", "bezier", "parabolic"]
            current_index = methods.index(self.z_generation_method) if self.z_generation_method in methods else 0
            next_index = (current_index + 1) % len(methods)
            self.z_generation_method = methods[next_index]
            
            print(f"切换Z值生成方法为: {self.z_generation_method}")
            self.set_control_points(self.control_points_2d)

    def get_status(self):
        """获取当前状态"""
        status = {
            'num_points': len(self.control_points_3d),
            'cube_size': 255,
            'coordinate_system': 'Z轴向上',
            'z_generation_method': self.z_generation_method,
            'view_angles': (self.view_angle_x, self.view_angle_y),
            'view_zoom': self.view_zoom,
            'show_cube': self.show_cube,
            'show_axes': self.show_axes,
            'show_control_points': self.show_control_points,
            'show_curve': self.show_curve,
            'show_coordinates': self.show_coordinates
        }
        
        if self.control_points_3d:
            status['bottom_z'] = self.control_points_3d[0][2]
            status['top_z'] = self.control_points_3d[-1][2]
            
        return status

    def print_debug_info(self):
        """打印调试信息"""
        print("\n=== 3D演示模式调试信息（Z轴向上）===")
        print(f"坐标系: Z轴向上（高度）")
        print(f"控制点数量: {len(self.control_points_3d)}")
        print(f"曲线点数: {len(self.curve_points_3d)}")
        print(f"Z值生成方法: {self.z_generation_method}")
        print(f"视角: X={self.view_angle_x}°, Y={self.view_angle_y}°, 缩放={self.view_zoom:.1f}x")
        
        if self.control_points_3d:
            print(f"底部点Z值: {self.control_points_3d[0][2]:.1f} (应为0)")
            print(f"顶部点Z值: {self.control_points_3d[-1][2]:.1f} (应为255)")
            
        print(f"屏幕中心: ({self.center_x}, {self.center_y})")
        print("=" * 30)