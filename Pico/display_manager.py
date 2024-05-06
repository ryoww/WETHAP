from machine import I2C

try:
    import ssd1306
except ImportError:
    import package

    package.install_requirements()
    import ssd1306


class DisplayManager:
    """ssd1306表示処理をまとめたクラス
    Args:
        i2c (I2C): I2Cオブジェクト
        margin (int, optional): 文字間のマージン量
        width (int, optional): ssd1306デバイスの横ピクセル数
        height (int, optional): ssd1306デバイスの縦ピクセル数
    """

    def __init__(
        self, i2c: I2C, margin: int = 3, width: int = 128, height: int = 64
    ) -> None:
        self.grid: int = 8
        self.width: int = width
        self.height: int = height
        self.margin: int = margin
        self.line_len: int = self.width // self.grid
        self.current: int = 0
        try:
            self.display = ssd1306.SSD1306_I2C(self.width, self.height, i2c)
        except Exception:
            self.display = None
            print("ssd1306 not connect")
        else:
            print("ssd1306 connected")

    @property
    def status(self):
        return self.display is not None

    def clear(self):
        """無表示化"""
        if self.status:
            self.current = 0
            self.display.fill(0)
            self.display.show()
        return self

    def add_text(self, text: str, row: int = None, new: bool = False):
        """表示行追加
        Args:
            text (str): 表示させるテキスト
            row (int, optional): 表示行を指定 未指定で次の行に追加
            new (bool, optional): Trueで新規 Falseで追加モード
        """
        if self.status:
            if new:
                self.display.fill(0)
                self.current = 0
            write = row if row else self.current
            self.display.text(
                text,
                (self.width - len(text) * self.grid) // 2,
                write * (self.grid + self.margin),
            )
            self.current = write + 1
        return self

    def multi_text(self, *texts: list[str], lines: list[int] = []):
        """複数行を中央揃えで表示
        Args:
            (str): 表示するテキストを入力 複数入力可
        """
        if self.status:
            self.display.fill(0)
            if len(texts) % 2 == 0:
                self.current = (
                    (self.height + self.margin) // (self.grid + self.margin)
                    - len(texts)
                ) // 2
                if 0 in lines:
                    self.line()
                for i, text in enumerate(texts):
                    self.add_text(text)
                    if i + 1 in lines:
                        self.line()
            else:
                char = self.grid + self.margin
                pos = ((self.height + char) - char * len(texts)) // 2
                if 0 in lines:
                    self.display.hline(
                        0,
                        pos - self.margin + (self.margin // 2) - 1,
                        self.width,
                        1,
                    )
                for i, text in enumerate(texts):
                    self.display.text(
                        text, (self.width - len(text) * self.grid) // 2, pos + char * i
                    )
                    if i + 1 in lines:
                        self.display.hline(
                            0,
                            (pos + char * i) + self.grid + (self.margin // 2) - 1,
                            self.width,
                            1,
                        )
            self.display.show()
            self.current = 0
        return self

    def split_text(self, text: str):
        """行の表示限界を超える長さの文字列を分割して表示
        Args:
            text (str like): 表示するテキストを入力
        """
        if self.status:
            text = str(text)
            self.multi_text(
                *[
                    text[i : i + self.line_len]
                    for i in range(0, len(text), self.line_len)
                ]
            )
        return self

    def line(self, row: int = None):
        """現在の表示行の下に線を追加
        Args:
            row (int, optional): 表示行を指定 未指定で次の行に追加
        """
        if self.status:
            write = row if row else self.current - 1
            if write < 0:
                return self
            self.display.hline(
                0,
                (write + 1) * self.grid + write * self.margin + (self.margin // 2) - 1,
                self.width,
                1,
            )
        return self

    def show(self, new: bool = True):
        """描画更新
        Args:
            new (bool, optional): Trueで描画後現在行を初期化 Falseで描画後現在行を初期化しない
        """
        if self.status:
            if new:
                self.current = 0
            self.display.show()
        return self
