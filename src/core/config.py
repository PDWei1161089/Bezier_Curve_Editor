# config.py - 存储所有中文文本

class ChineseText:
    """中文字符串配置"""

    # 窗口标题
    WINDOW_TITLE = "Bezier Curve Editor"

    # 模式按钮
    MODE_CREATE = "创建模式 (1)"
    MODE_RECURSIVE = "递归构造 (2)"
    MODE_VECTOR = "向量表示 (3)"
    MODE_DYNAMIC = "动力学分析 (4)"  # 新的模式按钮

    # 帮助按钮
    HELP_BUTTON = "使用说明 (H)"

    # 基本信息面板
    BASIC_INFO = "基本信息(I)"
    MODE_ADD = "当前模式: 添加"
    MODE_EDIT = "当前模式: 编辑"
    MODE_RECURSIVE_TEXT = "当前模式: 递归构造"
    CONTROL_POINTS = "控制点数量"
    SOUND_STATUS = "音效: {} | 音乐: {}"
    SOUND_ON = "开"
    SOUND_OFF = "关"

    # 音频控制
    AUDIO_CONTROLS = "音频控制 (A)"
    SOUND_LABEL = "音效:"
    MUSIC_LABEL = "音乐:"

    # 状态栏
    BEZIER_FORMULA = "贝塞尔曲线 (n={}) 使用Bernstein多项式"
    RECURSIVE_INFO = "递归层级: {}/{} 参数t: {:.2f}"
    MIN_POINTS = "添加至少2个控制点"
    # 更新快捷键提示
    SHORTCUTS = "1/2/3: 模式切换 | H: 帮助 | ESC: 退出"
    RECURSIVE_CONTROLS = "递归构造控制 (F3)"
    NEXT_STEP = "下一步(Space)"
    NEXT_STEP_TOOLTIP = "Space"
    PREV_STEP = "上一步(B)"
    PREV_STEP_TOOLTIP = "B"
    RESET = "重置(R)"
    RESET_TOOLTIP = "R"
    TOGGLE_CONSTRUCTION = "构造显示(C)"
    TOGGLE_CONSTRUCTION_TOOLTIP = "C"
    RATIO_SLIDER = "参数 t"

    # 向量控制文本
    VECTOR_CONTROLS = "向量表示控制(F4)"
    TOGGLE_VECTORS = "显示向量(V)"
    TOGGLE_CURVE = "显示曲线(C)"
    ADJUST_ORIGIN = "调整原点(P)"
    RESET_ORIGIN = "重置原点(R)"
    TOGGLE_VECTOR_MODE = "向量模式(F)"
    TOGGLE_VECTOR_MODE_TOOLTIP = "F"

    # Bernstein窗口控制
    BERNSTEIN_WINDOW = "基函数窗口(W)"
    SHOW_BERNSTEIN = "显示基函数窗口(D)"
    TOGGLE_BERNSTEIN_VIEW = "切换视图"

    # 缩放控制文本
    ZOOM_CONTROLS = "缩放控制"
    ZOOM_IN = "放大"
    ZOOM_OUT = "缩小"
    ZOOM_RESET = "重置缩放"
    ZOOM_IN_TOOLTIP = "+=键 或 鼠标滚轮上"
    ZOOM_OUT_TOOLTIP = "-=键 或 鼠标滚轮下"
    ZOOM_RESET_TOOLTIP = "0键"

    # 动力学模式文本
    MODE_DYNAMIC_TEXT = "当前模式: 动力学分析"
    DYNAMIC_CONTROLS = "动力学控制(F7)"

    # 导数向量文本
    VELOCITY_VECTOR = "速度向量"
    ACCELERATION_VECTOR = "加速度向量"
    JERK_VECTOR = "急动度向量"

    # 控制按钮
    TOGGLE_VELOCITY = "速度向量(V)"
    TOGGLE_ACCELERATION = "加速度向量(Z)"
    TOGGLE_JERK = "急动度向量(J)"

    # 状态信息
    VELOCITY_INFO = "速度: {:.1f} (长度)"
    ACCELERATION_INFO = "加速度: {:.1f} (长度)"
    JERK_INFO = "急动度: {:.1f} (长度)"

    # 帮助面板标题
    HELP_TITLE = "Bezier曲线编辑器 - 使用说明"
    CLOSE_HELP = "点击任意位置或按H键关闭"
    PAGE_KEYS = "使用 ← → 方向键或点击按钮翻页"
    PAGE_TEXT = "第 {} / {} 页"
    PREV_PAGE = "上一页"
    NEXT_PAGE = "下一页"

    # 面板控制文本
    TOGGLE_AUDIO_PANEL = "显示/隐藏音频面板"
    TOGGLE_RECURSIVE_PANEL = "显示/隐藏递归面板"
    TOGGLE_VECTOR_PANEL = "显示/隐藏向量面板"

    # 面板控制快捷键提示
    AUDIO_PANEL_HOTKEY = "F2"
    RECURSIVE_PANEL_HOTKEY = "F3"
    VECTOR_PANEL_HOTKEY = "F4"

    # 帮助内容 - 添加递归模式说明
    HELP_CONTENT = [
        "操作说明:",
        "",
        "重要提示: 请关闭中文输入法或开启英文模式，否则快捷键无法使用",
        "",
        "--- 通用快捷键 ---",
        "1键: 切换到创建模式",
        "2键: 切换到递归构造模式",
        "3键: 切换到向量表示模式",
        "4键: 切换到动力学分析模式",
        "I键: 显示/隐藏基本信息面板",
        "F1键: 快速打开帮助",
        "F2键: 显示/隐藏音频控制面板",
        "F3键: 显示/隐藏递归控制面板",
        "F4键: 显示/隐藏向量控制面板",
        "F5键: 重置所有面板位置",
        "F6键: 显示/隐藏基本信息面板",
        "F7键: 显示/隐藏动力学控制面板",
        "S键: 切换音效开关",
        "M键: 切换音乐开关",
        "H键: 显示/隐藏帮助",
        "ESC键: 退出程序（在调整原点模式下取消调整）",
        "+键 / -键: 放大/缩小视图",
        "0键: 重置缩放",
        "P键: 重置平移",
        "O键: 同时重置缩放和平移",
        "鼠标滚轮: 缩放视图",
        "鼠标中键: 快速重置视图（缩放+平移）",
        "左键拖拽空白处: 平移整个视图",
        "",
        "--- 创建模式 (按1键进入) ---",
        "左键点击空白处: 添加控制点",
        "右键点击控制点: 删除该控制点",
        "空格键: 切换添加/编辑模式",
        "C键: 清空所有控制点",
        "R键: 删除最后一个控制点",
        "编辑模式下左键拖动控制点: 移动控制点位置",
        "添加至少2个点后自动绘制贝塞尔曲线",
        "",
        "--- 递归构造模式 (按2键进入) ---",
        "需要先在创建模式中添加控制点",
        "空格键: 进行下一步递归构造",
        "B键: 返回上一步构造",
        "R键: 重置构造过程",
        "C键: 显示/隐藏构造过程",
        "拖动滑块调整参数t值",
        "曲线显示从t=0到当前t值的部分",
        "",
        "--- 向量表示模式 (按3键进入) ---",
        "需要先在创建模式中添加至少2个控制点",
        "V键: 显示/隐藏向量",
        "C键: 显示/隐藏曲线",
        "W键: 显示/隐藏Bernstein基函数窗口",
        "D键: 显示/隐藏Bernstein基函数数据面板",
        "F键: 切换向量模式（首尾连接/起点在原点）",
        "P键: 进入调整原点模式（点击空白处设置新原点）",
        "R键: 重置原点位置到控制点中心",
        "ESC键: 在调整原点模式下取消调整",
        "拖动滑块调整参数t值",
        "PageUp/左箭头键: Bernstein数据面板上一页",
        "PageDown/右箭头键: Bernstein数据面板下一页",
        "不同颜色的向量表示不同的Bernstein基函数",
        "Bernstein窗口显示基函数随t值的变化",
        "",
        "--- 动力学分析模式 (按4键进入) ---",
        "需要先在创建模式中添加控制点",
        "W键: 显示/隐藏向量轨迹窗口",
        "V键: 显示/隐藏速度向量（一阶导数）",
        "Z键: 显示/隐藏加速度向量（二阶导数）",
        "J键: 显示/隐藏急动度向量（三阶导数）",
        "C键: 清除向量历史数据",
        "X键: 显示/隐藏速度向量轨迹窗口",
        "D键: 显示/隐藏加速度向量轨迹窗口",
        "K键: 显示/隐藏急动度向量轨迹窗口",
        "N键: 显示/隐藏曲率圆",
        "L键: 显示/隐藏曲率半径变化窗口",
        "曲率圆半径为正时显示红色，为负时显示蓝色",
        "曲率圆显示当前t值对应的瞬时曲率圆",
        "拖动滑块调整参数t值",
        "需要2个控制点才能显示速度",
        "需要3个控制点才能显示加速度",
        "需要4个控制点才能显示急动度",
        "向量轨迹窗口显示完整导数向量曲线",
        "当前t值对应的点在向量轨迹上高亮显示",
        "",
        "--- 3D演示模式 (按5键进入) ---",
        "需要先在创建模式中添加至少2个控制点",
        "自动生成单调递增的Z分量（20%-80%范围）",
        "显示RGB立方体（255x255x255）",
        "W/X键: 上下旋转视角",
        "C/D键: 左右旋转视角",
        "Q/E键: 缩放视角",
        "R键: 重置视角到默认",
        "Z键: 重新生成Z分量（保持单调性）",
        "L键: 显示/隐藏立方体",
        "B键: 显示/隐藏坐标轴",
        "控制点和曲线颜色由其坐标决定（RGB值）",
        "立方体棱边按坐标位置渐变着色",
        "F9键: 显示/隐藏3D控制面板",
        "",
        "--- 面板控制 ---",
        "左键拖拽面板标题栏: 移动面板位置",
        "面板右上角的X按钮: 关闭面板",
        "A键: 显示/隐藏音频控制",
        "D键: 在向量模式下显示/隐藏数据面板",
        "",
        "--- 视图控制 ---",
        "鼠标滚轮: 缩放视图",
        "左键拖拽空白处: 平移视图",
        "中键点击: 快速重置视图",
        "+键: 放大视图",
        "-键: 缩小视图",
        "0键: 重置缩放",
        "P键: 重置平移",
        "",
        "--- 音频控制 ---",
        "S键: 切换音效开关",
        "M键: 切换音乐开关",
    ]