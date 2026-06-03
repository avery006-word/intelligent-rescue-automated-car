# main.py
import deliver_ball
import grab_first_ball
import find_and_grab_ballqq

VALID_RESULTS = ["stop", "stopstop"]  # 合法返回值

def main():
    # 初始颜色给定
    # target_color = "blue"
    target_color = "red"
    flagg = "no"

    while True:
        try:
            # Step 1: 抓第一个球
            if flagg == "no":
                result = grab_first_ball.run(target_color=target_color)
                if result not in VALID_RESULTS:
                    continue  # 返回值异常，直接进入下一轮
                if result == "stop":
                    flagg = "yes"
                    # Step 2: 送球
                    result = deliver_ball.run(target_color=target_color)
                    if result not in VALID_RESULTS:
                        continue
                    if result == "stopstop":
                        continue
            else:
                result = find_and_grab_ballqq.run(target_color=target_color)
                if result not in VALID_RESULTS:
                    continue
                if result == "stop":
                    # Step 4: 再送球
                    result = deliver_ball.run(target_color=target_color)
                    if result not in VALID_RESULTS:
                        continue
                    if result == "stopstop":
                        print("stopstop")
                        continue  # 重新进入循环

        except Exception as e:
            print("发生错误，跳过当前循环：", e)
            continue  # 出错就直接进入下一轮循环

if __name__ == "__main__":
    main()
