import json
import os
import re
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests


# 启用 Windows 终端 ANSI 转义序列支持
if sys.platform == "win32":
    os.system("")


class TUIDisplay:
    """TUI 显示类，用于动态更新输出"""

    def __init__(self):
        self.current_line = ""

    def clear_line(self):
        """清除当前行"""
        print("\r" + " " * 100 + "\r", end="", flush=True)

    def update(self, text: str):
        """更新当前行内容"""
        self.clear_line()
        print(text, end="", flush=True)
        self.current_line = text

    def finish(self, text: str = ""):
        """完成当前行，换行"""
        if text:
            self.clear_line()
            print(text, flush=True)
        else:
            print(flush=True)
        self.current_line = ""

    def print_status(self, round_num: int, stage: str, detail: str = ""):
        """打印实时状态"""
        status = f"🔄 第{round_num}轮 | {stage}"
        if detail:
            status += f" | {detail}"
        self.update(status)


tui = TUIDisplay()


# 统计信息全局变量
class Statistics:
    def __init__(self):
        self.start_time = datetime.now()
        self.total_rounds = 0
        self.total_apps_processed = 0
        self.total_apps_shared = 0
        self.exit_reason = "未知"

stats = Statistics()


def search(name: str) -> bool | None:
    target_url = f"http://shenjack.top:10003/api/v0/apps/list/1?sort=download_count&desc=true&page_size=1&search_key=name&search_value={name}&search_exact=true"
    response = requests.get(target_url)
    if response.status_code == 200:
        data = response.json()
        if not data["success"]:
            return False
        if "data" not in data:
            return False
        data = data["data"]
        if len(data["data"]) == 0:
            return False
        return True
    return None


def get_layout() -> dict[str, str | list]:
    """
    执行 hdc shell uitest dumpLayout 命令，获取 UI 结构并保存到 layout.json
    """
    tui.update("📱 正在生成 UI 结构...")

    try:
        result = subprocess.run(
            ["hdc", "shell", "uitest", "dumpLayout"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout
    except subprocess.CalledProcessError as e:
        tui.finish(f"❌ 执行 dumpLayout 命令失败: {e}")
        sys.exit(1)
    except FileNotFoundError:
        tui.finish("❌ 未找到 hdc 命令，请确保已安装并配置环境变量")
        sys.exit(1)

    # 2. 使用正则从输出中提取文件路径
    match = re.search(r"saved to:(/data/local/tmp/.*\.json)", output)
    if not match:
        tui.finish("❌ 未能从输出中解析出文件路径。可能是 dump 失败了。")
        sys.exit(1)

    remote_path = match.group(1).strip()

    tui.update("📥 正在拉取 layout 文件...")

    # 3. 拉取文件并保存为 layout.json
    local_path = Path("./layout.json")
    try:
        subprocess.run(
            ["hdc", "file", "recv", remote_path, str(local_path)],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        tui.finish(f"❌ 拉取文件失败: {e}")
        sys.exit(1)

    if not local_path.exists():
        tui.finish("❌ 拉取失败，文件未保存。")
        sys.exit(1)

    # 4. (可选) 删除设备上的临时文件
    try:
        subprocess.run(
            ["hdc", "shell", "rm", remote_path], check=True, capture_output=True
        )
    except subprocess.CalledProcessError:
        pass  # 删除失败不影响主流程

    # 5. 读取并返回 JSON 数据
    try:
        data = json.loads(local_path.read_text(encoding="utf-8"))
        return data
    except FileNotFoundError:
        tui.finish(f"❌ 文件未找到: {local_path}")
    except json.JSONDecodeError:
        tui.finish(f"❌ 文件不是有效的JSON格式: {local_path}")
    except Exception as e:
        tui.finish(f"❌ 读取文件时出错: {str(e)}")
    sys.exit(1)


def get_layout_data() -> dict[str, str | list]:
    """
    兼容旧接口：支持从命令行参数读取文件，或直接调用 get_layout
    """
    if len(sys.argv) >= 2:
        # 从命令行参数读取文件
        file_path = Path(sys.argv[1])
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            return data
        except FileNotFoundError:
            print(f"文件未找到: {file_path}")
        except json.JSONDecodeError:
            print(f"文件不是有效的JSON格式: {file_path}")
        except Exception as e:
            print(f"读取文件时出错: {str(e)}")
        sys.exit(1)
    else:
        # 直接调用 get_layout 自动获取
        return get_layout()


def get_abailty(data: list[dict], name: str | None = None) -> dict | None:
    if name is None:
        return data[0] if data else None
    for item in data:
        if item.get("attributes")["abilityName"] == name:
            return item
    return None


def analyze_data(data) -> list[dict]:
    tui.update("🔍 正在解析应用列表...")

    main_child: list[dict] = data["children"]
    main_abality = get_abailty(main_child, "MainAbility")
    if main_abality is None:
        tui.finish("❌ 未找到 MainAbility")
        sys.exit(1)
    main_abality_child_1: dict = main_abality["children"][0]
    main_abality_child_2: dict = main_abality_child_1["children"][0]
    main_abality_child_3: dict = main_abality_child_2["children"][0]
    main_abality_child_4: dict = main_abality_child_3["children"][0]
    main_abality_child_5: dict = main_abality_child_4["children"][0]
    app_list_1: dict = main_abality_child_5["children"][1]
    new_app = ["新鲜应用", "新鲜游戏"]

    if main_abality_child_5["children"][0]["attributes"]["text"] in new_app:
        app_list_2: dict = app_list_1["children"][0]
        app_list_3: dict = app_list_2["children"][0]
        app_list_4: dict = app_list_3["children"][0]
        app_list_5: dict = app_list_4["children"][0]
        app_list_6: dict = app_list_5["children"][0]
        app_list_7: dict = app_list_6["children"][0]
        app_list_8: dict = app_list_7["children"][0]
        app_list: list[dict] = app_list_8["children"]
    else:
        app_list_2: dict = app_list_1["children"][0]
        app_list_3: dict = app_list_2["children"][0]
        app_list_4: dict = app_list_3["children"][0]
        app_list_5: dict = app_list_4["children"][0]
        app_list_6: dict = app_list_5["children"][0]
        app_list: list[dict] = app_list_6["children"]

    # 第一步：收集所有应用的基本信息
    app_datas: list[dict] = []
    for app in app_list:
        sub1 = app["children"][0]
        sub2 = sub1["children"][0]
        sub3 = sub2["children"][0]
        sub4 = sub3["children"][0]
        if len(sub4["children"]) < 4:
            # 跳过不完整 app 框
            continue
        sub5 = sub4["children"][2]
        sub6 = sub5["children"][0]
        app_name = sub6["attributes"]["text"]
        app_box: str = sub6["attributes"]["bounds"]
        # 解析 bounds 字符串格式: [x1,y1][x2,y2]
        coords = app_box.replace("[", "").replace("]", ",").split(",")
        coords = [int(coord) for coord in coords if coord]
        if len(coords) == 4:
            x1, y1, x2, y2 = coords
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            app_datas.append(
                {
                    "name": app_name,
                    "bounds": app_box,
                    "center": (center_x, center_y),
                    "exists": None,  # 稍后批量查询
                }
            )

    # 第二步：使用多线程批量查询应用是否存在
    total_apps = len(app_datas)
    tui.update(f"🔎 正在查询应用 (0/{total_apps})...")

    completed_count = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 提交所有查询任务
        future_to_index = {
            executor.submit(search, app_data["name"]): idx
            for idx, app_data in enumerate(app_datas)
        }

        # 收集查询结果
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                found = future.result()
                app_datas[idx]["exists"] = found
                completed_count += 1
                tui.update(f"🔎 正在查询应用 ({completed_count}/{total_apps})...")
            except Exception as e:
                tui.finish(f"⚠️  查询应用 {app_datas[idx]['name']} 时出错: {e}")
                app_datas[idx]["exists"] = None
                completed_count += 1

    new_apps_count = len([app for app in app_datas if not app['exists']])
    tui.update(f"✅ 找到 {total_apps} 个应用，其中 {new_apps_count} 个新应用")

    return app_datas


def share_at(x: int, y: int) -> None:
    target_pos = f"{x} {y}"
    base_cmd = f"""hdc shell uinput -T -d {target_pos} -i 60 -u {target_pos} -i 900 -d 1150 200 -i 60 -u 1150 200 -i 600 -d 400 2200 -i 60 -u 400 2200 -i 900 -d 150 650 -i 60 -u 150 650 -i 400 -d 800 1700 -i 60 -u 800 1700 -i 300 -d 400 2800 -i 60 -u 400 2800 -i 300 -d 400 2800 -i 60 -u 400 2800"""
    wati_time = 3820 + 500  # ms
    subprocess.run(base_cmd, shell=True, capture_output=True)
    time.sleep(wati_time / 1000)


def 下滑_11() -> None:
    tui.update("📜 正在下滑页面...")
    cmd = "hdc shell uinput -M -m 500 1000 -s 2355"
    subprocess.run(cmd, shell=True, capture_output=True)
    time.sleep(1)


def share_app(app_datas: list[dict]) -> None:
    new_apps = [app for app in app_datas if not app["exists"]]
    total_new = len(new_apps)

    if total_new == 0:
        return

    for idx, app in enumerate(new_apps, 1):
        x, y = app["center"]
        print(f"分享 {app['name']} 应用 ", end="", flush=True)
        share_at(x, y)
        time.sleep(0.5)


def play_beep(count: int = 3):
    """播放提示音"""
    for _ in range(count):
        print("\a", end="", flush=True)
        time.sleep(0.2)


def print_statistics():
    """打印统计信息"""
    end_time = datetime.now()
    duration = end_time - stats.start_time
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    tui.finish()  # 确保换行
    print("\n" + "="*60)
    print("📊 运行统计信息")
    print("="*60)
    print(f"🔄 总运行轮次: {stats.total_rounds}")
    print(f"📱 总处理应用数: {stats.total_apps_processed}")
    print(f"🆕 总分享新应用数: {stats.total_apps_shared}")
    print(f"⏱️  运行总时长: {int(hours)}小时 {int(minutes)}分钟 {int(seconds)}秒")
    print(f"🚪 退出原因: {stats.exit_reason}")
    print("="*60)


def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    stats.exit_reason = "用户按下 Ctrl+C 强制退出"
    print_statistics()
    play_beep()
    sys.exit(0)


if __name__ == "__main__":
    # 注册 Ctrl+C 信号处理器
    signal.signal(signal.SIGINT, signal_handler)

    print("🚀 程序启动...")
    print("💡 按 Ctrl+C 可随时退出并查看统计信息\n")

    previous_app_datas = None

    try:
        while True:
            stats.total_rounds += 1
            tui.update(f"🔄 第 {stats.total_rounds} 轮处理")

            data = get_layout()
            app_datas = analyze_data(data)

            # 更新统计信息
            stats.total_apps_processed += len(app_datas)
            new_apps_count = len([app for app in app_datas if not app['exists']])
            stats.total_apps_shared += new_apps_count

            # 检查是否与上次数据一致
            if previous_app_datas is not None:
                # 比较应用名称列表是否一致
                current_names = [app['name'] for app in app_datas]
                previous_names = [app['name'] for app in previous_app_datas]
                if current_names == previous_names:
                    tui.finish("ℹ️  检测到应用列表未变化，退出程序")
                    stats.exit_reason = "应用列表未变化，正常退出"
                    print_statistics()
                    play_beep()
                    break

            share_app(app_datas)
            下滑_11()
            tui.finish(f"✅ {stats.total_rounds}轮完成")

            # 保存当前数据用于下次比较
            previous_app_datas = app_datas
    except Exception as e:
        stats.exit_reason = f"程序异常退出: {str(e)}"
        print_statistics()
        play_beep()
        raise
