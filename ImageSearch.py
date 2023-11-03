import multiprocessing
import pyautogui
import platform
import os

import time


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

    @staticmethod
    def __listify_param(param: any, num: int) -> list[any]:
        # If param is of type list, and the count is less than num, the remaining elements are filled with param[0].
        result = []
        if type(param) != list:
            for i in range(num):
                result.append(param)
        else:
            if len(param) <= num:
                result = param
                for i in range(num - len(param)):
                    result.append(param[0])
        return result

    @staticmethod
    def __recombination_param(image_name_list: list[str],
                              click_status: bool or list[bool], click_button: str or list[str],
                              confidence: float or list[float] = 0.95) -> list[tuple]:
        click_status_list = ImageSearch.__listify_param(click_status, len(image_name_list))
        click_button_list = ImageSearch.__listify_param(click_button, len(image_name_list))
        confidence_list = ImageSearch.__listify_param(confidence, len(image_name_list))

        param_list = [()]
        for i in range(len(image_name_list)):
            param_list.append(
                (
                    image_name_list[i],
                    click_status_list[i],
                    click_button_list[i],
                    confidence_list[i]
                )
            )
        param_list.pop(0)
        return param_list

    def single_image_search(self, image_name: str or list[str],
                            click_status: bool, click_button: str, confidence: float) -> bool:
        self.detection_status = False
        image_path = self.recombination_path(image_name)
        self.pos = pyautogui.locateCenterOnScreen(image_path, confidence=confidence, grayscale=True)
        if self.pos is not None:
            self.detection_status = True
            if click_status:
                if click_button == 'left':
                    pyautogui.leftClick(self.pos)
                else:
                    pyautogui.rightClick(self.pos)
            return True
        return False

    @staticmethod
    def __print_image_status(image_name: str or list[str], is_print_result: bool,
                             detect_result: bool or list[bool] = None) -> None:
        os.system('cls')
        for i in range(len(image_name)):
            print(f'{image_name[i]} detecting...', end='')
            if is_print_result and detect_result is not None:
                if type(detect_result) is bool:
                    print(detect_result)
                else:
                    print(f'\t[{detect_result[i]}]')
            else:
                print()

        return

    def image_search(self, image_name: str or list[str],
                     loop_status: bool or list[bool] = False, click_status: bool or list[bool] = True,
                     click_button: str or list[str] = 'left',
                     confidence: float or list[float] = 0.95) -> bool or list[bool]:
        loop_count = 0
        if type(image_name) is list:
            param = ImageSearch.__recombination_param(image_name, click_status, click_button, confidence)
            loop_status_list = ImageSearch.__listify_param(loop_status, len(image_name))
            pool = multiprocessing.Pool()
            while True:
                # 한 턴 마다 cls를 하고 그 동안은 각 프로세스에서 stdout을 하면 어떨까? 해 볼만한 가치가 있을 것 같아.
                self.__print_image_status(image_name, False)
                result_list = pool.starmap(self.single_image_search, param)
                self.__print_image_status(image_name, True, result_list)

                # Remove lists that don't require repetitive work.
                temp_image_list = image_name
                if True in result_list or False in loop_status_list:
                    while True:
                        print(f'before entry: {param}')
                        time.sleep(5)
                        if len(temp_image_list) == 0:
                            break
                        for i in range(len(temp_image_list)):
                            if result_list[i] or not loop_status_list[i]:
                                temp_image_list.pop(i)
                                param.pop(i)
                                loop_status_list.pop(i)
                                break
                        print(f'after entry: {param}') # 지금 result_list는 팝이 되지 않아서 result_list 기준으로 계속 지워지고 반복되고 있음
                        # 개선이 필요함.
                        time.sleep(5)
                if len(temp_image_list) == 0:
                    break
            pool.close()
            pool.join()
        else:
            while True:
                print(f'{image_name} detecting...\t')
                if self.single_image_search(image_name, click_status, click_button, confidence):
                    print(f'successful [{loop_count}]')
                    return True
                print(f'failure [{loop_count}]')
                if not loop_status:
                    break
        return False
