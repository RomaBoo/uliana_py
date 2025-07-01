import csv
import os
import json
from PyQt5.QtWidgets import QMessageBox
from Settings import Settings


class CsvLib:
    def __init__(self, parent=None):
        self.parent = parent
        self.settings = Settings()

    def del_lines(self, path, lines_to_remove=12):
        if not path or not os.path.exists(path):
            QMessageBox.warning(self.parent, "Ошибка", "Файл не существует или путь не указан.")
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            cleaned_lines = lines[lines_to_remove:]
            output_path = os.path.splitext(path)[0] + "_processed.csv"

            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)

            QMessageBox.information(self.parent, "Файл обработан", f"Результат сохранён в:\n{output_path}")
            return output_path

        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка обработки", f"Произошла ошибка:\n{e}")

    def generate_footprint_json(self, path):
        if not path or not os.path.exists(path):
            QMessageBox.warning(self.parent, "Ошибка", "Файл не существует или путь не указан.")
            return

        try:
            columns = self.settings.load("coloumns")  # ["Footprint", "Rotation", "FeedT"]
            if not isinstance(columns, list) or len(columns) < 2:
                QMessageBox.warning(self.parent, "Ошибка", "Некорректные настройки колонок.")
                return

            key_column = columns[0]
            value_columns = columns[1:]
            result = {}

            with open(path, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                # 🔎 Проверка: все ли нужные колонки есть в CSV
                fieldnames = reader.fieldnames
                missing = [col for col in columns if col not in fieldnames]
                if missing:
                    QMessageBox.warning(
                        self.parent,
                        "Ошибка колонок",
                        f"Не найдены колонки в CSV: {', '.join(missing)}\n\n"
                        f"Доступные заголовки: {', '.join(fieldnames or [])}"
                    )
                    return

                for row in reader:
                    key = row[key_column].strip()

                    if key not in result:
                        entry = {}
                        for col in value_columns:
                            val = row.get(col, "").strip()
                            try:
                                val = float(val)
                            except ValueError:
                                pass
                            entry[col] = val

                        result[key] = entry

            project_dir = os.path.dirname(os.path.abspath(__file__))  # путь к текущему .py-файлу
            output_path = os.path.join(project_dir, "footprint.json")

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            QMessageBox.information(self.parent, "Готово", f"Файл footprint.json создан:\n{output_path}")
            return output_path

        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Произошла ошибка:\n{e}")
