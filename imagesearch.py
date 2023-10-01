import pyautogui
import platform
import os


class ImageSearch:
    def __init__(self, default_path: str = None):
        self.default_path = default_path
        self.pos = None
        self.detection_status = False
        self.os_type = None, self.determine_os()

    def get_pos(self):
        return self.pos

    def get_detection_status(self):
        return self.detection_status

    def determine_os(self) -> None:
        self.os_type = platform.system()
        return

    def recombination_path(self, image_name: str) -> str:
        if self.default_path is None:
            image_path = image_name
        else:
            image_path = os.path.join(self.default_path, image_name)
        return image_path

    def image_search(self, image_name: str, loop_status: bool = False, click_status: bool = True,
                     click_button: str = 'left', confidence: float = 0.95) -> bool:
        self.detection_status = False
        image_path = self.recombination_path(image_name)
        count = 0
        while True:
            print(f'{image_name} detecting...', end='')
            self.pos = pyautogui.locateCenterOnScreen(image_path, 0, confidence=confidence, grayscale=True)
            if self.pos is not None:
                print(f'successful [{count}]')
                self.detection_status = True
                if click_status:
                    if click_button == 'left':
                        pyautogui.leftClick(self.pos)
                    else:
                        pyautogui.rightClick(self.pos)
                return True
            else:
                count += 1
                print(f'failure [{count}]', end='')
                if not loop_status:
                    print()
                    break
                print('\r', end='')
        return False
