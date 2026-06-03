import sensor, image, time
from pyb import UART

def run(target_color="red"):
    # =============== 常量配置 ===============
    SPIN_SPEED = (988, 988)   # 原地旋转速度
    SIZE_THRESHOLD = 1156  # 面积阈值
    SAFE_BACK = (888,888) #距离安全区有些近，后退
    wrong_rec = (654, 654) #前进再转向
    # =============== 初始化串口 ===============
    uart = UART(3, 19200)

    # =============== 摄像头初始化 ===============
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA)    # 160x120
    sensor.skip_frames(10)
    sensor.set_auto_whitebal(False)
    sensor.set_auto_gain(False)
    sensor.set_auto_exposure(False, exposure_us=28000)  # 固定 28ms 曝光
    clock = time.clock()


    # 颜色阈值（可调）
    color_thresholds = {
    "red":   (23, 83, 22, 127, 21, 111),
    "blue":  (20, 85, 7, 127, -24, 127),
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
    frame_count = 0
    safe_back_buffer = []
    ball_color = []
    yes_value = 1
    no_value = 0
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
        if len(ball_color)>10:
            ball_color.pop(0)

        #找小球并靠近
        ball = find_nearest_ball(img)
        if ball:
            cx, cy, r = ball
            img.draw_circle(cx, cy, r, color=(255, 0, 0))
            img.draw_cross(cx, cy, color=(0, 255, 0))
            x_error = cx - img.width() / 2
            h_error = (2 * r) * (2 * r) - SIZE_THRESHOLD
            color = get_ball_color(img, ball)
            if color == target_color:
                ball_color.append(yes_value)
            else:
                ball_color.append(no_value)
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
                if 20 <= x_error <= 32 and h_error >= -650 and (x_error != 0 or h_error != 0):
                    if yes_value not in ball_color:
                        send_motor_command(*wrong_rec)
                        print(wrong_rec, "FPS:", round(frame_count / clock.avg(), 2))
                    else:
                        send_motor_command(x_error, h_error)
                        print(cx, cy, r, round(x_error, 2), round(h_error, 2),
                              "FPS001:", round(frame_count / clock.avg(), 2))
                        print("stop")
                        return "stop"  #停止，返回“stop”
                else:
                    send_motor_command(x_error, h_error)
                    print(cx, cy, r, round(x_error, 2), round(h_error, 2),
                          "FPS:", round(frame_count / clock.avg(), 2))
            frame_buffer.clear()
            frame_count = 0
