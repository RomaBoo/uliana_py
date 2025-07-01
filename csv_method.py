import csv
import os

from PyQt5.QtWidgets import QMessageBox


class CsvLib:
    def __init__(self, parent=None):
        self.parent = parent  # например, ссылка на окно, чтобы показывать QMessageBox

    def del_lines(self, path):
        if not path or not os.path.exists(path):
            QMessageBox.warning(
                self.parent, "Ошибка", "Файл не существует или путь не указан."
            )
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Убираем первые 13 строк (оставляем с 13-й строки включительно — index 12)
            cleaned_lines = lines[12:]

            # Путь для сохранения нового файла
            output_path = os.path.splitext(path)[0] + "_processed.csv"

            with open(output_path, "w", encoding="utf-8") as f:
                f.writelines(cleaned_lines)

            QMessageBox.information(
                self.parent, "Файл обработан", f"Результат сохранён в:\n{output_path}"
            )
            return output_path  # если тебе нужно дальше использовать путь

        except Exception as e:
            QMessageBox.critical(
                self.parent, "Ошибка обработки", f"Произошла ошибка:\n{e}"
            )
