import platform
import matplotlib.pyplot as plt


class FontManager:
    @staticmethod
    def get_font_name():
        system_name = platform.system()
        if system_name == 'Windows':
            return 'Malgun Gothic'
        elif system_name == 'Darwin':
            return 'AppleGothic'
        else:
            return 'NanumGothic'

    @staticmethod
    def get_font_path():
        system_name = platform.system()
        if system_name == 'Windows':
            return 'c:/Windows/Fonts/malgun.ttf'
        elif system_name == 'Darwin':
            return '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
        return None

    @staticmethod
    def set_pyplot_font():
        font_name = FontManager.get_font_name()
        plt.rc('font', family=font_name)
        plt.rcParams['axes.unicode_minus'] = False
