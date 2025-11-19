import sys
import json

def get_layout_data() -> dict[str, str | list]:
    if len(sys.argv) < 2:
        print("请提供文件名作为参数")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"文件未找到: {filename}")
    except json.JSONDecodeError:
        print(f"文件不是有效的JSON格式: {filename}")
    except Exception as e:
        print(f"读取文件时出错: {str(e)}")
    sys.exit(1)


def get_abailty(data: list[dict], name: str | None = None) -> dict | None:
    if name is None:
        return data[0] if data else None
    for item in data:
        if item.get('attributes')['abilityName'] == name:
            return item
    return None


if __name__ == "__main__":
    data = get_layout_data()

    main_child: list[dict] = data['children']
    main_abality = get_abailty(main_child, 'MainAbility')
    if main_abality is None:
        print("未找到 MainAbility")
        sys.exit(1)
    main_abality_child_1: list[dict] = main_abality['children'][0]
    main_abality_child_2: dict = main_abality_child_1['children'][0]
    main_abality_child_3: dict = main_abality_child_2['children'][0]
    main_abality_child_4: dict = main_abality_child_3['children'][0]
    main_abality_child_5: dict = main_abality_child_4['children'][0]
    app_list_1: dict = main_abality_child_5['children'][1]
    app_list_2: dict = app_list_1['children'][0]
    app_list_3: dict = app_list_2['children'][0]
    app_list_4: dict = app_list_3['children'][0]
    app_list_5: dict = app_list_4['children'][0]
    app_list_6: dict = app_list_5['children'][0]
    app_list_7: dict = app_list_6['children'][0]
    app_list_8: dict = app_list_7['children'][0]
    app_list: list[dict] = app_list_8['children']

    # print(f"MainAbility 的子组件有: {app_list}")
    print(f"len childen: {len(app_list)}")
    for app in app_list:
        sub1 = app['children'][0]
        sub2 = sub1['children'][0]
        sub3 = sub2['children'][0]
        sub4 = sub3['children'][0]
        if len(sub4['children']) < 4:
            # 跳过不完整 app 框
            continue
        sub5 = sub4['children'][2]
        sub6 = sub5['children'][0]
        app_name = sub6['attributes']['originalText']
        app_box: str = sub6['attributes']['bounds']
        # 解析 bounds 字符串格式: [x1,y1][x2,y2]
        coords = app_box.replace('[', '').replace(']', ',').split(',')
        coords = [int(coord) for coord in coords if coord]
        if len(coords) == 4:
            x1, y1, x2, y2 = coords
            width = x2 - x1
            height = y2 - y1
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            print(f"app name: {app_name} - 坐标: ({x1}, {y1}) 到 ({x2}, {y2}), 尺寸: {width}x{height}, 中心点: ({center_x}, {center_y})")
        else:
            print(f"app name: {app_name} - 无效的坐标格式: {app_box}")
