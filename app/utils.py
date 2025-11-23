import platform
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm  # 폰트 매니저 추가
import os


class FontManager:
    @staticmethod
    def get_font_name():
        system_name = platform.system()
        if system_name == 'Windows':
            return 'Malgun Gothic'
        elif system_name == 'Darwin':
            return 'AppleGothic'
        else:
            if os.path.exists('/usr/share/fonts/truetype/nanum/NanumGothic.ttf'):
                return 'NanumGothic'
            return 'DejaVu Sans'

    @staticmethod
    def get_font_path():
        system_name = platform.system()
        if system_name == 'Windows':
            return 'c:/Windows/Fonts/malgun.ttf'
        elif system_name == 'Darwin':
            return '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
        else:
            return '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

    @staticmethod
    def set_pyplot_font():
        font_path = FontManager.get_font_path()
        if font_path and os.path.exists(font_path):
            fm.fontManager.addfont(font_path)
            font_name = fm.FontProperties(fname=font_path).get_name()
            plt.rc('font', family=font_name)
        else:
            font_name = FontManager.get_font_name()
            plt.rc('font', family=font_name)

        plt.rcParams['axes.unicode_minus'] = False
        return font_name
