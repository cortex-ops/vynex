from typing import Tuple

class Parser():
    def __init__(self, img_shape: Tuple[int, ...], divisions: Tuple[int, int]):
        self.img_shape = img_shape
        self.divisions = divisions

    def get_cell_center_coords(self, pos: int) -> Tuple[int, int]:
        num_rows, num_cols = self.divisions
        
        cell_height = self.img_shape[0] // num_rows
        cell_width = self.img_shape[1] // num_cols
        
        index = pos - 1
        
        row = index // num_cols
        col = index % num_cols
        
        # 4. Calculate center of the cell
        x_center = (col * cell_width) + (cell_width // 2)
        y_center = (row * cell_height) + (cell_height // 2)
        
        return (x_center, y_center)

    def get_pos_coords(self, pos: int) -> Tuple[int, int]:    
        coords = self.get_cell_center_coords(pos)
        return coords

    def get_mouse_command(self, action_detail: dict[str, int]) -> str:
        action_map = {0: '4', 1: '8', 2: 'C'}
        button_map = {0: '0', 1: '1', 2: '2', 3: '5', 4: '6'}

        pos = action_detail["position"]
        x, y = self.get_pos_coords(pos)

        action = action_map[action_detail["action"]]
        button = button_map[action_detail["button"]]

        command1 = f"ydotool mousemove --absolute {x} {y}"
        command2 = f"ydotool click {action}{button}"

        final_command = f"{command1} && {command2}"

        return final_command

    def get_keys_command(self, action_detail: dict) -> str:
        delay = action_detail["delay"]
        codes = action_detail["codes"]

        key_list = []

        for code in codes:
            key_list.append(f"{code[0]}:{code[1]}")

        keys_str = " ".join(key_list)
        final_command = f"ydotool key -d {delay} {keys_str}"
        return final_command

    def get_type_command(self, action_detail: dict):
        delay = action_detail["delay"]
        string = action_detail["string"]

        final_command = f"ydotool type -d {delay} \"{string}\""
        return final_command

    def get_keyboard_command(self, action_detail: dict) -> str:
        using_code = action_detail["using_code"]

        if using_code:
            return self.get_keys_command(action_detail)
        else:
            return self.get_type_command(action_detail)

    def get_wait_command(self, action_detail: dict[str, int]) -> str:
        delay = action_detail["time"] / 1000

        final_command = f"sleep {delay}"
        return final_command
    
    def get_end_command(action_detail: dict[str, bool]) -> bool:
        to_stop = action_detail["stop"]
        return to_stop

    def get_action_command(self, action: tuple[int, dict]) -> str:
        action_code = action[0]
        action_detail = action[1]

        if action_code == 0:
            return self.get_mouse_command(action_detail)
        elif action_code == 1:
            return self.get_keyboard_command(action_detail)
        elif action_code == 2:
            return self.get_wait_command(action_detail)
        elif action_code == 3:
            return self.get_end_command(action_detail)
        

    def get_actions_command(self, actions: list[tuple[int, dict]]) -> Tuple[str, bool]:
        command_list = []

        for action in actions:
            command_list.append(self.get_action_command(action))

        end_command = command_list.pop()

        final_command = " && ".join(command_list)
        return final_command, end_command

    def parse_actions_string(self, action_string: str) -> Tuple[str, bool]:
        actions = eval(action_string)
        return self.get_actions_command(actions)

if __name__ == "__main__":

    parser = Parser((1080, 1920, 3))

    action = input("Enter action: ")
    
    print(parser.parse_actions_string(action))