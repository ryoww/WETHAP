import ssd1306


class DisplayManager:
    """ssd1306表示処理をまとめたクラス
    Args:
        i2c (I2C): I2Cオブジェクト
        margin (int, optional): 文字間のマージン量
        width (int, optional): ssd1306デバイスの横ピクセル数
        height (int, optional): ssd1306デバイスの縦ピクセル数
    """
    def __init__(self, i2c, margin=3, width=128, height=64):
        self.grid = 8
        self.width = width
        self.height = height
        self.margin = margin
        self.line_len = self.width // self.grid
        self.current = 0
        try:
            self.display = ssd1306.SSD1306_I2C(self.width, self.height, i2c)
        except:
            self.display = None
            print("ssd1306 not connect")
        else:
            print("ssd1306 connected")

    def clear(self):
        """無表示化"""
        if self.display:
            self.current = 0
            self.display.fill(0)
            self.display.show()
        return self

    def add_text(self, text, row=None, new=False):
        """表示行追加
        Args:
            text (str): 表示させるテキスト
            row (int, optional): 表示行を指定 未指定で次の行に追加
            new (bool, optional): Trueで新規 Falseで追加モード
        """
        if self.display:
            if new:
                self.display.fill(0)
                self.current = 0
            write = row if row else self.current
            self.display.text(text, (self.width - len(text) * self.grid) // 2, write * (self.grid + self.margin))
            self.current = write + 1
        return self

    def multi_text(self, *texts):
        """複数行を中央揃えで表示
        Args:
            (str): 表示するテキストを入力 複数入力可
        """
        if self.display:
            self.display.fill(0)
            if len(texts) % 2 == 0:
                self.current = (6 - len(texts)) // 2
                print(self.current)
                [self.add_text(text) for text in texts]
            else:
                char = self.grid + self.margin
                pos = ((self.height + char) - char * len(texts)) // 2
                [self.display.text(text, (self.width - len(text) * self.grid) // 2, pos + char * i) for i, text in enumerate(texts)]
            self.display.show()
            self.current = 0
        return self

    def split_text(self, text):
        """行の表示限界を超える長さの文字列を分割して表示
        Args:
            text (str like): 表示するテキストを入力
        """
        if self.display:
            text = str(text)
            self.multi_text(*[text[i : i + self.line_len] for i in range(0, len(text), self.line_len)])

    def line(self, row=None):
        """現在の表示行の下に線を追加
        Args:
            row (int, optional): 表示行を指定 未指定で次の行に追加
        """
        if self.display:
            write = row if row else self.current - 1
            self.display.hline(0, (write + 1) * (self.grid + self.margin // 2), self.width, 1)
        return self

    def show(self, new=True):
        """描画更新
        Args:
            new (bool, optional): Trueで描画後現在行を初期化 Falseで描画後現在行を初期化しない
        """
        if self.display:
            if new:
                self.current = 0
            self.display.show()
        return self
