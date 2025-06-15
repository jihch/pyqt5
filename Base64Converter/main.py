from PyQt5.QtWidgets import QPlainTextEdit, QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, \
    QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFontMetrics, QTextCursor, QIcon
import sys
import base64
import resources  # 导入编译后的资源模块


class SmartTextEdit(QPlainTextEdit):
    def __init__(self, parent=None, margin=20):
        super().__init__(parent)
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

        if text:
            # 获取当前文本域的可用宽度
            available_width = self.viewport().width() - self.margin

            # 应用智能换行
            wrapped_text = self.wrap_text(text, available_width)

            # 插入处理后的文本
            cursor = self.textCursor()
            cursor.insertText(wrapped_text)
        else:
            # 如果不是文本，使用默认行为
            super().insertFromMimeData(source)

    def wrap_text(self, text, width_pixels):
        """智能换行文本，基于像素宽度"""
        if not text:
            return ""

        # 获取字体指标，用于计算字符宽度
        font_metrics = QFontMetrics(self.font())

        # 按行处理
        lines = text.split('\n')
        wrapped_lines = []

        for line in lines:
            tmp = self.wrap_line(line, width_pixels, font_metrics)
            wrapped_lines.append(tmp)

        return '\n'.join(wrapped_lines)

    def wrap_line(self, line, width_pixels, font_metrics):
        """处理单行文本的换行，基于像素宽度"""
        if not line:
            return ""

        # 计算整行文本的宽度
        line_width = font_metrics.width(line)

        # 如果整行宽度小于可用宽度，直接返回
        if line_width <= width_pixels:
            return line

        wrapped_lines = []
        current_line = ""
        remaining_text = line

        while remaining_text:
            # 尝试添加一个字符，检查是否超过宽度
            if font_metrics.width(current_line + remaining_text[0]) <= width_pixels:
                current_line += remaining_text[0]
                remaining_text = remaining_text[1:]
            else:
                # 如果当前行不为空，添加到结果中
                if current_line:
                    wrapped_lines.append(current_line)
                    current_line = ""
                else:
                    # 如果当前行为空但字符宽度超过限制，强制添加一个字符
                    wrapped_lines.append(remaining_text[0])
                    remaining_text = remaining_text[1:]

        # 添加最后一行
        if current_line:
            wrapped_lines.append(current_line)

        return '\n'.join(wrapped_lines)


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
        global output_path
        base64_text = text_edit.toPlainText().strip()
        if not base64_text:
            QMessageBox.warning(window, "警告", "请先粘贴BASE64字符串!")
            return

        # 获取输出路径
        output_folder = ""

        try:
            # 解码BASE64数据
            decoded_data = base64.b64decode(base64_text)

            file_type_str = detect_file_type(decoded_data)

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
            decoded_data = base64.b64decode(base64_text)

            # 保存到文件
            with open(output_path, 'wb') as f:
                f.write(decoded_data)

            QMessageBox.information(window, "成功", f"文件已成功保存到:\n{output_path}")
        except Exception as e:
            QMessageBox.critical(window, "错误", f"保存文件时出错:\n{str(e)}")


    # 连接按钮点击事件到处理函数
    save_button.clicked.connect(save_base64_file)

    window.setLayout(main_layout)
    window.setFixedSize(800, 600)
    window.show()

    sys.exit(app.exec_())