# pyuic5 UI.ui -o smt660_ui.py
import os
import sys

from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox

from csv_method import CsvLib
from Settings import Settings
from smt660_ui import Ui_Dialog  # Импортируем UI класс из .ui-файла


class MainDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.init()

        self.csv_processor = CsvLib(parent=self)

        self.ui.searchfile_button.clicked.connect(
            self.choose_file
        )  # когда кнопка ... нажата то -
        self.ui.ok_button.clicked.connect(
            self.confirm_path
        )  # когда кнопка ок нажата то -

    def init(self):
        settings = Settings()
        file = settings.load("file")
        if file:
            self.ui.filepath_line.setText(file)
    def choose_file(self):
<<<<<<< .mine
        settings = Settings()
        file = settings.load("file")  #  1. Загружаем путь при запуске
    # Проверка: был ли ранее сохранён путь и существует ли он на диске
=======
        # Проверка: был ли ранее сохранён путь и существует ли он на диске


>>>>>>> .theirs
        if file and os.path.exists(file):
            # Если файл существует — начнем с его папки
            start_path = os.path.dirname(file)
        else:
            # Иначе начнем с диска D (по умолчанию)
            start_path = "D:/"

        # Открываем диалог выбора файла, фильтруем только CSV-файлы
        file_path, _ = QFileDialog.getOpenFileName(
            self,  # Родительское окно
            "Выбери CSV файл",  # Заголовок диалога
            start_path,  # Папка, с которой начнём
            "CSV files (*.csv)",  # Фильтр расширений
        )

        # Если пользователь действительно выбрал файл
        if file_path:
            # Сохраняем выбранный путь в переменную экземпляра
            file = file_path

            # Показываем путь в поле ввода
            self.ui.filepath_line.setText(file_path)

            # Сохраняем путь в settings.json, чтобы он запомнился на следующий раз
            settings.save("file", file_path)

            # Также можно сохранить последнюю открытую папку, если захочешь:
            settings.save("last_dir", os.path.dirname(file_path))

    def confirm_path(self):
        
        settings = Settings()
        path = self.ui.filepath_line.text().strip()
        if path and os.path.exists(path):
            self.file = path
            settings.save("file", path)

            output_path = self.csv_processor.del_lines(path)

            if output_path:
                # 2. Генерируем footprint.json из уже обработанного CSV
                self.csv_processor.generate_footprint_json(output_path)
                self.accept()
        else:
            QMessageBox.warning(
                self, "Ошибка", "Файл не существует или путь не указан."
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainDialog()
    window.show()
    sys.exit(app.exec_())
