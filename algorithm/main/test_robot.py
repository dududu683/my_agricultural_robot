
import time
from main import SmartAgriRobot


def main():
    # 创建机器人实例
    robot = SmartAgriRobot()

    try:
        # 启动机器人
        robot.start()

        # 等待系统初始化
        time.sleep(2)

        # 执行巡检任务
        print("\n=== 执行巡检任务 ===")
        robot.set_task("INSPECT")
        while robot.state != "IDLE":
            time.sleep(1)

        # 执行采摘任务
        print("\n=== 执行采摘任务 ===")
        # 假设检测到一个果实ID=2
        robot.set_task("HARVEST", target=2)
        while robot.state != "IDLE":
            time.sleep(1)

        # 返回充电
        print("\n=== 返回充电 ===")
        robot.set_task("RETURN")
        while robot.state != "IDLE":
            time.sleep(1)

        # 等待充电完成
        time.sleep(5)

    except KeyboardInterrupt:
        print("用户中断")
    finally:
        # 关闭机器人
        robot.shutdown()


if __name__ == "__main__":
    main()