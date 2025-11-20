import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests


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
    # 1. 执行 dump 命令并获取输出
    print("正在生成 UI 结构...", end="", flush=True)
    try:
        result = subprocess.run(
            ["hdc", "shell", "uitest", "dumpLayout"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout
        print(f"|ui dump done", end = "", flush=True)
        # print(f"设备返回: {output}", end = "", flush=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 执行 dumpLayout 命令失败: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("❌ 未找到 hdc 命令，请确保已安装并配置环境变量", file=sys.stderr)
        sys.exit(1)

    # 2. 使用正则从输出中提取文件路径
    match = re.search(r"saved to:(/data/local/tmp/.*\.json)", output)
    if not match:
        print("❌ 未能从输出中解析出文件路径。可能是 dump 失败了。", file=sys.stderr)
        sys.exit(1)

    remote_path = match.group(1).strip()
    # print(f"已定位文件路径: {remote_path}", file=sys.stderr)

    # 3. 拉取文件并保存为 layout.json
    local_path = Path("./layout.json")
    try:
        subprocess.run(
            ["hdc", "file", "recv", remote_path, str(local_path)],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ 拉取文件失败: {e}", file=sys.stderr)
        sys.exit(1)

    if not local_path.exists():
        print("❌ 拉取失败，文件未保存。", file=sys.stderr)
        sys.exit(1)

    print(f"|layout 文件已保存", flush=True, end="")

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
        print(f"文件未找到: {local_path}", file=sys.stderr)
    except json.JSONDecodeError:
        print(f"文件不是有效的JSON格式: {local_path}", file=sys.stderr)
    except Exception as e:
        print(f"读取文件时出错: {str(e)}", file=sys.stderr)
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
    main_child: list[dict] = data["children"]
    main_abality = get_abailty(main_child, "MainAbility")
    if main_abality is None:
        print("未找到 MainAbility")
        sys.exit(1)
    main_abality_child_1: dict = main_abality["children"][0]
    main_abality_child_2: dict = main_abality_child_1["children"][0]
    main_abality_child_3: dict = main_abality_child_2["children"][0]
    main_abality_child_4: dict = main_abality_child_3["children"][0]
    main_abality_child_5: dict = main_abality_child_4["children"][0]
    app_list_1: dict = main_abality_child_5["children"][1]
    new_app = ["新鲜应用", "新鲜游戏"]
    # print(
    #     f"MainAbility 子组件有: {main_abality_child_5['children'][0]['attributes']['text']}"
    # )
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

    # print(f"MainAbility 的子组件有: {app_list})
    # print(f"len childen: {len(app_list)}")

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
    print(f"|开始查询 {len(app_datas)} 个应用...", end="", flush=True)
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
                app_name = app_datas[idx]["name"]
                center_x, center_y = app_datas[idx]["center"]
                coords_str = app_datas[idx]["bounds"]
                coords = coords_str.replace("[", "").replace("]", ",").split(",")
                coords = [int(coord) for coord in coords if coord]
                x1, y1, x2, y2 = coords
                # print(f"app name: {app_name} - 坐标: ({x1}, {y1}) 到 ({x2}, {y2}), 中心点: ({center_x}, {center_y}) - 存在: {found}")
            except Exception as e:
                print(f"查询应用 {app_datas[idx]['name']} 时出错: {e}")
                app_datas[idx]["exists"] = None

    print(f"总共找到 {len(app_datas)} 个应用")
    return app_datas


def share_at(x: int, y: int) -> None:
    target_pos = f"{x} {y}"
    base_cmd = f"""hdc shell uinput -T -d {target_pos} -i 60 -u {target_pos} -i 900 -d 1150 200 -i 60 -u 1150 200 -i 600 -d 400 2200 -i 60 -u 400 2200 -i 900 -d 150 650 -i 60 -u 150 650 -i 400 -d 800 1700 -i 60 -u 800 1700 -i 300 -d 400 2800 -i 60 -u 400 2800 -i 300 -d 400 2800 -i 60 -u 400 2800"""
    wati_time = 3820 + 500  # ms
    subprocess.run(base_cmd, shell=True)
    # print(base_cmd)
    time.sleep(wati_time / 1000)


def 下滑_11() -> None:
    cmd = "hdc shell uinput -M -m 500 1000 -s 2355"
    subprocess.run(cmd, shell=True)
    time.sleep(1)


def share_app(app_datas: list[dict]) -> None:
    for app in app_datas:
        if not app["exists"]:
            x, y = app["center"]
            print(f"正在分享应用: {app['name']} at ({x}, {y})")
            share_at(x, y)
            time.sleep(0.5)
        # else:
        #     print(f"跳过已有的应用: {app['name']}")


if __name__ == "__main__":
    while True:
        data = get_layout()
        app_datas = analyze_data(data)
        share_app(app_datas)
        print("所有应用分享完成！")
        下滑_11()
