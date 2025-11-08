def get_pos_coords(pos: int) -> tuple[int]:
    pass

def get_mouse_command(action_detail: dict[str, int]) -> str:
    action_map = {0: '4', 1: '8', 2: 'C'}
    button_map = {0: '0', 1: '1', 2: '2', 3: '5', 4: '6'}

    pos = action_detail["position"]
    coords = get_pos_coords(pos)

    action = action_map[action_detail["action"]]
    button = button_map[action_detail["button"]]

    command1 = f"ydotool mousemove --absolute {coords[0], coords[1]}"
    command2 = f"ydotool click {action}{button}"

    final_command = f"{command1} && {command2}"

    return final_command

def get_keys_command(action_detail: dict) -> str:
    delay = action_detail["delay"]
    codes = action_detail["codes"]

    key_list = []

    for code in codes:
        key_list.append(f"{code[0]}:{code[1]}")

    keys_str = " ".join(key_list)
    final_command = f"ydotool key -d {delay} {keys_str}"
    return final_command

def get_type_command(action_detail: dict):
    delay = action_detail["delay"]
    string = action_detail["string"]

    final_command = f"ydotool -d {delay} type \"{string}\""
    return final_command

def get_keyboard_command(action_detail: dict) -> str:
    using_code = action_detail["using_code"]

    if using_code:
        return get_keys_command(action_detail)
    else:
        return get_type_command(action_detail)

def get_action_command(action: tuple[int, dict]) -> str:
    action_code = action[0]
    action_detail = action[1]

    if action_code == 0:
        return get_mouse_command(action_detail)
    elif action_code == 1:
        return get_keyboard_command(action_detail)
    

if __name__ == "__main__":

    action = (
        1,
        {
            "using_code": False,
            "string": "hello world",
            "delay": 20
        }
    )
    
    print(get_action_command(action))