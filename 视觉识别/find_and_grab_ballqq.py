import sensor, image, time
from pyb import UART

def run(target_color="red"):
    # =============== 常量配置 ===============
    SPIN_SPEED = (988, 988)   # 原地旋转速度
    SIZE_THRESHOLD = 1156  # 面积阈值
    SAFE_BACK = (888,888) #距离安全区有些近，后退
    # =============== 初始化串口 ===============
    uart = UART(3, 19200)

    # =============== 摄像头初始化 ===============
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA)    # 160x120
    sensor.skip_frames(10)
    sensor.set_auto_whitebal(False)
    sensor.set_auto_gain(False)
    sensor.set_auto_exposure(False, exposure_us=28000)  # 固定 30ms 曝光
    clock = time.clock()


    # 颜色阈值（可调）
    color_thresholds = {
        "red":   (35, 71, 48, 111, 39, 93),
        "blue":  (35, 71, 32, 127, 10, 121),
        "yellow":(30, 70, -10, 20, 40, 127),
        "black": (0, 40, -10, 10, -10, 10)
    }
    red_threshold    = (20, 55, 25, 80, 2, 77)
    blue_threshold   = (45, 65, -50, 30, -75, -15)
    purple_threshold = (25, 50, 10, 40, -80, -20)

    # =============== 工具函数 ===============
    def send_motor_command(left_speed, right_speed):
        cmd = "L:{};R:{}\r\n".format(int(left_speed), int(right_speed))
        uart.write(cmd)

    def find_nearest_ball(img):
        nearest_blob = None
        max_area = 0
        for c in img.find_circles(threshold=2800, x_margin=10, y_margin=10,
                                   r_margin=10, r_min=3, r_max=25, r_step=1):
            area_size = (2 * c.r()) * (2 * c.r())
            if area_size > max_area:
                max_area = area_size
                nearest_blob = (c.x(), c.y(), c.r())
        return nearest_blob

    def find_large_balls(img):
        balls = []
        for c in img.find_circles(threshold=2800, x_margin=10, y_margin=10,
                                   r_margin=10, r_min=8, r_max=25, r_step=1):
            balls.append((c.x(), c.y(), c.r()))
        return balls

    def get_ball_color(img, ball):
        cx, cy, r = ball
        roi_size = int(r * 1)
        roi = (max(cx - roi_size//2, 0), max(cy - roi_size//2, 0),
               roi_size, roi_size)
        stats = {}
        for name, th in color_thresholds.items():
            blobs = img.find_blobs([th], roi=roi, pixels_threshold=5, area_threshold=5)
            if blobs:
                stats[name] = blobs[0].pixels()
        if stats:
            return max(stats, key=stats.get)
        return None

    # =============== 主循环变量 ===============
    frame_buffer = []
    frame_buffer_2 = []
    frame_count = 0
    frame_count_2 = 0
    large_ball_detected_history = []
    safe_back_buffer = []
    # =============== 主循环 ===============
    while True:
        clock.tick()
        img = sensor.snapshot()
        # # 找紫色
        purple_blobs = img.find_blobs([purple_threshold], pixels_threshold=20, area_threshold=20,
                                       merge=True, margin=5)

        # 找红色安全区
        red_safe_blobs = img.find_blobs([red_threshold], pixels_threshold=20, area_threshold=20,
                                         merge=True, margin=20)

        # 找蓝色安全区
        blue_safe_blobs = img.find_blobs([blue_threshold], pixels_threshold=20, area_threshold=20,
                                           merge=True, margin=10)

        # 如果有紫色
        if purple_blobs:
            # 获取红色最大面积
            red_area = max((b.pixels() for b in red_safe_blobs), default=0)
            # 获取蓝色最大面积
            blue_area = max((b.pixels() for b in blue_safe_blobs), default=0)

            # 如果红色或蓝色的最大面积 > 2000
            if red_area > 2000 or blue_area > 2000:
                safe_back_buffer.append(SAFE_BACK)
                if len(safe_back_buffer) >= 8:
                    safe_spin_count = sum(1 for f in frame_buffer if f == SAFE_BACK)
                    if safe_spin_count >= 6:
                        send_motor_command(*SAFE_BACK)
                        safe_back_buffer.clear()
                continue

        # Step 1: 检测大球
        large_balls = find_large_balls(img)
        if large_balls:
            # 遍历每个大球画出来
            for b in large_balls:
                cx, cy, r = b
                img.draw_circle(cx, cy, r, color=(255, 0, 0))   # 画红色圆
                img.draw_cross(cx, cy, color=(0, 255, 0))       # 画绿色十字
        detected_big_ball = len(large_balls) > 0
        large_ball_detected_history.append(detected_big_ball)
        if len(large_ball_detected_history) > 6:
            large_ball_detected_history.pop(0)

        target_ball = None

        # 如果最近6帧有大球 → 按颜色优先级选择
        if any(large_ball_detected_history):
            color_priority = ["black", target_color]
            colored_balls = []
            for b in large_balls:
                color = get_ball_color(img, b)
                if color in color_priority:
                    colored_balls.append((b, color))

            if colored_balls:
                colored_balls.sort(
                    key=lambda x: (
                        color_priority.index(x[1]),
                        abs(x[0][0] - img.width() / 2)
                    )
                )
                target_ball, target_color_found = colored_balls[0]
            else:
                send_motor_command(*SPIN_SPEED)

        # Step 2: 控制大球
        if target_ball:
            cx, cy, r = target_ball
            img.draw_circle(cx, cy, r, color=(255, 255, 0))
            img.draw_cross(cx, cy, color=(255, 255, 0))
            x_error = cx - img.width() / 2
            h_error = (2 * r) * (2 * r) - SIZE_THRESHOLD
            frame_buffer_2.append((cx, cy, r, x_error, h_error))
            frame_count_2 += 1

            if len(frame_buffer_2) >= 8:
                frame_buffer_2.sort(key=lambda x: x[2])
                mid_index = len(frame_buffer_2) // 2
                result = frame_buffer_2[mid_index]
                cx, cy, r, x_error, h_error = result
                #输出转速
                send_motor_command(x_error, h_error)
                print(cx, cy, r, round(x_error, 2), round(h_error, 2),
                      "FPS001:", round(frame_count_2 / clock.avg(), 2))
                if 20 <= x_error <= 35 and h_error >= -650 and (x_error != 0 or h_error != 0):
                    print("stop")
                    return "stop"  #停止，返回“stop”
                frame_buffer_2.clear()
                frame_count_2 = 0
            continue

        # Step 3: 没有大球 → 按形状找最近球
        if not any(large_ball_detected_history) and len(large_ball_detected_history) == 6:
            ball = find_nearest_ball(img)
            if ball:
                cx, cy, r = ball
                img.draw_circle(cx, cy, r, color=(0, 0, 255))
                img.draw_cross(cx, cy, color=(0, 0, 255))
                x_error = cx - img.width() / 2
                h_error = (2 * r) * (2 * r) - SIZE_THRESHOLD
                frame_buffer.append((cx, cy, r, x_error, h_error))
            else:
                frame_buffer.append(SPIN_SPEED)

            frame_count += 1
            if len(frame_buffer) >= 10:
                spin_count = sum(1 for f in frame_buffer if f == SPIN_SPEED)
                if spin_count >= 9:
                    send_motor_command(*SPIN_SPEED)
                    print(SPIN_SPEED, "FPS:", round(frame_count / clock.avg(), 2))
                else:
                    valid_frames = [f for f in frame_buffer if f != SPIN_SPEED]
                    valid_frames.sort(key=lambda x: x[2])
                    mid_index = len(valid_frames) // 2
                    result = valid_frames[mid_index]
                    cx, cy, r, x_error, h_error = result
                    send_motor_command(x_error, h_error)
                    print(cx, cy, r, round(x_error, 2), round(h_error, 2),
                          "FPS:", round(frame_count / clock.avg(), 2))
                frame_buffer.clear()
                frame_count = 0
