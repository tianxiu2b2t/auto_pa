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
    main_abality_child: list[dict] = main_abality['children']
    main_abality_child: dict = get_abailty(main_abality_child)
    main_abality_child: dict = get_abailty(main_abality_child['children'])
    main_abality_child: dict = get_abailty(main_abality_child['children'])
    main_abality_child: dict = get_abailty(main_abality_child['children'])
    main_abality_child: dict = get_abailty(main_abality_child['children'])
    app_list: dict = main_abality_child['children'][1]
    app_list: dict = app_list['children'][0]
    app_list: dict = app_list['children'][0]
    app_list: dict = app_list['children'][0]
    app_list: dict = app_list['children'][0]
    app_list: dict = app_list['children'][0]
    app_list: dict = app_list['children'][0]
    app_list: dict = app_list['children'][0]
    app_list: list[dict] = app_list['children']

    # print(f"MainAbility 的子组件有: {app_list}")
    print(f"len childen: {len(app_list)}")
    for app in app_list:
        sub1 = app['children'][0]
        sub2 = sub1['children'][0]
        sub3 = sub2['children'][0]
        sub4 = sub3['children'][0]
        # sub5 = sub4['children'][0]
        print(f"sub {sub4}\n sub len: {len(sub4['children'])}")
        # print(f"len: {len(app['children'])}, attributes: {app['attributes']}")
