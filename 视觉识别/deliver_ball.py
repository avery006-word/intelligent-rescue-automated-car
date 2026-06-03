# deliver_ball.py
import sensor, image, time
#from pid import PID
from pyb import UART

# ---------------- 常量配置 ----------------
SPIN_SPEED = (988, 988)  # 原地旋转左右轮速度，可在这里调整
turned_around = (777, 777)   #原地旋转180°

def run(target_color="red"):
    # ---------------- 串口初始化 ----------------
    uart = UART(3, 19200)

    # ---------------- 摄像头初始化 ----------------
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QQVGA) #160x120，宽度*高度
    sensor.skip_frames(10)
    sensor.set_auto_gain(False)
    sensor.set_auto_whitebal(False)
    sensor.set_auto_exposure(False, exposure_us=28000)  # 固定 30ms 曝光
    clock = time.clock()

    # ---------------- 颜色阈值 ----------------
    red_threshold    = (20, 55, 25, 80, 2, 77)
    blue_threshold   = (45, 65, -50, 30, -75, -15)
    purple_threshold = (25, 50, 10, 40, -80, -20)

    #-------------------------串口通信-------------------
    def send_motor_command(left_speed, right_speed):
        cmd = "L:{};R:{}\r\n".format(int(left_speed), int(right_speed))
        uart.write(cmd)

    # ---------------- 主循环 ----------------
    # 用于多帧稳定判断
    frame_buffer = []
    frame_count = 0


    while True:
        clock.tick()
        img = sensor.snapshot()
        purple_blobs = img.find_blobs([purple_threshold], pixels_threshold=20, area_threshold=20,
                                       merge=True, margin=5)
        if not purple_blobs:
            frame_buffer.append(SPIN_SPEED)
        else:
            purple_blob = max(purple_blobs, key=lambda b: b.area())
            img.draw_rectangle(purple_blob[0:4], color=(255, 0, 255))
            img.draw_cross(purple_blob.cx(), purple_blob.cy(), color=(0, 255, 0))

            x, y, w, h = purple_blob.rect()
            red_blobs = img.find_blobs([red_threshold], pixels_threshold=20, area_threshold=20,
                                          merge=True, margin=20)
            blue_blobs = img.find_blobs([blue_threshold], pixels_threshold=20, area_threshold=20,
                                        merge=True, margin=10)
            if target_color == "red":
                safe_blobs = red_blobs
                other_blobs = blue_blobs
            else:
                safe_blobs = blue_blobs
                other_blobs = red_blobs
            if safe_blobs:
                safe_blob = max(safe_blobs, key=lambda b: b.area())
                img.draw_rectangle(safe_blob[0:4], color=(255, 255, 0))
                img.draw_cross(safe_blob.cx(), safe_blob.cy(), color=(255, 255, 0))
                x_error = purple_blob.cx() - img.width() / 2
                h_error = 0
                frame_buffer.append((x_error, h_error))
            elif other_blobs:
                frame_buffer.append(turned_around)
                other_blob = max(other_blobs, key=lambda b: b.area())
                img.draw_rectangle(other_blob[0:4], color=(0, 255, 255))
                img.draw_cross(other_blob.cx(), other_blob.cy(), color=(255, 255, 0))
            else:
                x_error = purple_blob.cx() - img.width() / 2
                h_error = 666
                frame_buffer.append((x_error, h_error))
        frame_count += 1

        if len(frame_buffer) >= 10:
            spin_count = sum(1 for f in frame_buffer if f == SPIN_SPEED)
            spin_count_2 = sum(1 for f in frame_buffer if f == turned_around)

            if spin_count >= 8:
                send_motor_command(*SPIN_SPEED)
                print(SPIN_SPEED, "FPS:", round(frame_count / clock.avg(), 2))
            elif spin_count_2 >=8:
                send_motor_command(*turned_around)
                print(turned_around, "FPS:", round(frame_count / clock.avg(), 2))
            else:
                valid_frames = [f for f in frame_buffer if f not in [SPIN_SPEED, turned_around]]
                valid_frames.sort(key=lambda x: x[0])
                mid_index = len(valid_frames) // 2
                result = valid_frames[mid_index]
                #send_motor_command(999,666)
                send_motor_command(*result)
                #print(*result)
                print(round(result[0], 2), round(result[1], 2),
                      "FPS:", round(frame_count / clock.avg(), 2))
                if 20 <= x_error <= 35 and h_error == 0:
                    return "stopstop"  # 新增：立即结束 run() 并返回 "stopstop"
                    print("stopstop")

            frame_buffer.clear()
            frame_count = 0
