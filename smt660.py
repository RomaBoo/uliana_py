#pyuic5 UI.ui -o smt660_ui.py
import sys, os
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox
from smt660_ui import Ui_Dialog  # Импортируем UI класс из .ui-файла
from Settings import Settings


class MainDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.settings = Settings()
        self.file = self.settings.load("file")  #  1. Загружаем путь при запуске

        # Показываем путь в поле, если он есть
        if self.file:
            self.ui.filepath_line.setText(self.file)

        self.ui.searchfile_button.clicked.connect(self.choose_file) #когда кнопка ... нажата то -
        self.ui.ok_button.clicked.connect(self.confirm_path) #когда кнопка ок нажата то -

    def choose_file(self):
    # Проверка: был ли ранее сохранён путь и существует ли он на диске
        if self.file and os.path.exists(self.file):
            # Если файл существует — начнем с его папки
            start_path = os.path.dirname(self.file)
        else:
            # Иначе начнем с диска D (по умолчанию)
            start_path = "D:/"

        # Открываем диалог выбора файла, фильтруем только CSV-файлы
        file_path, _ = QFileDialog.getOpenFileName(
            self,                                 # Родительское окно
            "Выбери CSV файл",                    # Заголовок диалога
            start_path,                           # Папка, с которой начнём
            "CSV files (*.csv)"                   # Фильтр расширений
        )

        # Если пользователь действительно выбрал файл
        if file_path:
            # Сохраняем выбранный путь в переменную экземпляра
            self.file = file_path

            # Показываем путь в поле ввода
            self.ui.filepath_line.setText(file_path)

            # Сохраняем путь в settings.json, чтобы он запомнился на следующий раз
            self.settings.save("file", file_path)

            # Также можно сохранить последнюю открытую папку, если захочешь:
            self.settings.save("last_dir", os.path.dirname(file_path))


    def confirm_path(self):
        # 📥 3. Сохраняем и путь, введённый вручную
            path = self.ui.filepath_line.text().strip()
            if path and os.path.exists(path):
                self.file = path
                self.settings.save("file", path)

                # 📄 7. Удаляем первые 13 строк из CSV и сохраняем как .txt
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    # Убираем первые 13 строк
                    cleaned_lines = lines[12:]

                    # Создаём путь для .txt файла рядом с исходным
                    output_path = os.path.splitext(path)[0] + "_processed.csv"

                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.writelines(cleaned_lines)

                    QMessageBox.information(self, "Файл обработан", f"Результат сохранён в:\n{output_path}")
                    self.accept()

                except Exception as e:
                    QMessageBox.critical(self, "Ошибка обработки", f"Произошла ошибка:\n{e}")
            else:
                QMessageBox.warning(self, "Ошибка", "Файл не существует или путь не указан.")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainDialog()
    window.show()
    sys.exit(app.exec_())
