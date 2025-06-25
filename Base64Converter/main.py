from PyQt5.QtWidgets import QPlainTextEdit, QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, \
    QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QFontMetrics, QTextCursor, QIcon
import sys
import base64
from datetime import datetime
import time
import resources  # 导入编译后的资源模块


class SmartTextEdit(QPlainTextEdit):
    def __init__(self, parent=None, margin=20):
        super().__init__(parent)
        self.available_width = None
        self.margin = margin  # 边距，像素

        # 设置为等宽字体，更适合BASE64字符串
        font = self.font()
        font.setFamily("Courier New")
        font.setFixedPitch(True)
        self.setFont(font)

        # 监听窗口大小变化
        self.viewport().resizeEvent = self._on_viewport_resize

        # 禁用水平滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def _on_viewport_resize(self, event):
        # 当窗口大小变化时，可以选择重新计算行宽
        return super().viewport().resizeEvent(event)

    def insertFromMimeData(self, source):
        """重写插入方法，优化BASE64字符串的处理"""
        # 获取剪贴板文本
        text = source.text()


        print("insertFromMimeData 时间:")
        dt = datetime.fromtimestamp(time.time())
        print(dt)

        if text:
            # 获取当前文本域的可用宽度
            self.available_width = self.viewport().width() - self.margin

            '''
            # 应用智能换行
            wrapped_text = self.wrap_text(text, available_width)

            # 插入处理后的文本
            cursor = self.textCursor()
            cursor.insertText(wrapped_text)
            '''
            # 使用定时器异步处理文本，避免UI卡顿
            QTimer.singleShot(0, lambda: self._process_and_insert_text(text))
        else:
            # 如果不是文本，使用默认行为
            super().insertFromMimeData(source)

    def _process_and_insert_text(self, text):
        """异步处理文本并插入"""
        # 显示处理中的提示
        self.setPlainText("正在处理文本...")

        # 使用定时器将耗时操作拆分成小任务
        QTimer.singleShot(0, lambda: self._insert_wrapped_text(text))

    def _insert_wrapped_text(self, text):
        """执行文本换行处理并插入"""
        standard_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='

        char_width_dict = {}

        font_metrics = QFontMetrics(self.font())

        for c in standard_alphabet:
            char_width_dict[c] = font_metrics.width(c)


        print("_insert_wrapped_text 开始时间:")
        dt = datetime.fromtimestamp(time.time())
        print(dt)

        # 应用智能换行
        wrapped_text = ""

        lines = []
        current_line = []
        current_width = 0

        if text:
            for char in text:
                char_width = char_width_dict[char]
                if current_width + char_width <= self.available_width:
                    current_line.append(char)
                    current_width += char_width
                else:
                    lines.append(''.join(current_line))
                    current_line = [char]
                    current_width = char_width
            if current_line:
                lines.append(''.join(current_line))
            wrapped_text = '\n'.join(lines)

        # wrapped_text = self.wrap_text(text, available_width)
        print("while 循环结束时间:")
        dt = datetime.fromtimestamp(time.time())
        print(dt)

        # 恢复光标位置并插入处理后的文本
        cursor = self.textCursor()
        self.setPlainText(wrapped_text)
        print("setPlainText 结束时间:")
        dt = datetime.fromtimestamp(time.time())
        print(dt)
        cursor.setPosition(0)
        self.setTextCursor(cursor)


# 使用示例
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowIcon(QIcon(":/icon.ico"))  # 替换为你的 PNG 文件路径
    window.setWindowTitle("Base64字符串转文件工具")
    main_layout = QVBoxLayout(window)

    # 创建智能文本编辑器
    text_edit = SmartTextEdit(margin=20)
    text_edit.setPlaceholderText("请粘贴BASE64字符串...")
    text_edit.setLineWrapMode(QPlainTextEdit.NoWrap)  # 禁用默认换行

    # 添加文本编辑器到主布局
    main_layout.addWidget(text_edit)

    # 创建保存按钮并添加到布局
    save_button = QPushButton("存储为...")
    save_button.setMinimumWidth(200)  # 设置按钮最小宽度
    main_layout.addWidget(save_button, alignment=Qt.AlignCenter)


    def detect_file_type(data: bytes) -> str:
        """检测文件类型是PNG还是PDF"""
        # PNG文件的前8个字节是固定的
        PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
        # PDF文件以'%PDF-'开头
        PDF_SIGNATURE = b'%PDF-'

        if data.startswith(PNG_SIGNATURE):
            return 'PNG'
        elif data.startswith(PDF_SIGNATURE):
            return 'PDF'
        else:
            return '未知类型'

    def save_base64_file():
        """处理保存BASE64文件的逻辑"""
        # 获取BASE64文本
        base64_text = text_edit.toPlainText().strip()
        if not base64_text:
            QMessageBox.warning(window, "警告", "请先粘贴BASE64字符串!")
            return

        # 获取输出路径
        output_folder = ""

        # print("before replace \\n:")
        # print(base64_text)

        base64_text = base64_text.replace('\n', '')

        # print("after replace \\n:")
        # print(base64_text)

        output_path = None
        decoded_bytes = None
        try:
            # 解码BASE64数据
            # 字符串 → bytes
            encoded_bytes = base64_text.encode('ascii')
            # print("encoded_bytes:")
            # print(encoded_bytes)

            # bytes → bytes
            decoded_bytes = base64.b64decode(encoded_bytes)
            # print("decoded_bytes:")
            # print(decoded_bytes)

            file_type_str = detect_file_type(decoded_bytes)

            if file_type_str != 'PNG' and file_type_str != 'PDF':
                QMessageBox.critical(window, "错误", f"不是PNG 也不是 PDF")
                return

            if file_type_str == 'PNG':
                output_path, _ = QFileDialog.getSaveFileName(window, "保存 PNG 文件", "base64.png", "PNG Files (*.png)")

            elif file_type_str == 'PDF':
                output_path, _ = QFileDialog.getSaveFileName(window, "保存 PDF 文件", "base64.pdf", "PDF Files (*.pdf)")

            if not output_path:
                return  # 用户取消了保存

            print(file_type_str)
        except Exception as e:
            QMessageBox.critical(window, "错误", f"保存文件时出错:\n{str(e)}")

        try:
            # 解码BASE64数据
            # 保存到文件
            with open(output_path, 'wb') as f:
                f.write(decoded_bytes)

            QMessageBox.information(window, "成功", f"文件已成功保存到:\n{output_path}")
        except Exception as e:
            QMessageBox.critical(window, "错误", f"保存文件时出错:\n{str(e)}")


    # 连接按钮点击事件到处理函数
    save_button.clicked.connect(save_base64_file)

    window.setLayout(main_layout)
    window.setFixedSize(800, 600)
    window.show()

    sys.exit(app.exec_())