import csv
import json
import os

from InvenTreeManager import InvenTreeManager
from PyQt5.QtWidgets import QMessageBox

from Settings import Settings


class CsvLib:
    def __init__(self, parent=None):
        self.parent = parent
        self.settings = Settings()

    def del_lines(self, path, lines_to_remove=12):
        if not path or not os.path.exists(path):
            QMessageBox.warning(
                self.parent, "Ошибка", "Файл не существует или путь не указан."
            )
            return

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            cleaned_lines = lines[lines_to_remove:]
            output_path = os.path.splitext(path)[0] + "_processed.csv"

            with open(output_path, "w", encoding="utf-8") as f:
                f.writelines(cleaned_lines)

            QMessageBox.information(
                self.parent, "Файл обработан", f"Результат сохранён в:\n{output_path}"
            )
            return output_path

        except Exception as e:
            QMessageBox.critical(
                 self.parent, "Ошибка обработки", f"Произошла ошибка:\n{e}"
            )

    def generate_footprint_json(self, path):
        if not path or not os.path.exists(path):
            QMessageBox.warning(
                self.parent, "Ошибка", "Файл не существует или путь не указан."
            )
            return

        try:
            columns = self.settings.load(
                "coloumns"
            )  # ["Footprint", "Rotation", "FeedT"]
            if not isinstance(columns, list) or len(columns) < 2:
                QMessageBox.warning(
                    self.parent, "Ошибка", "Некорректные настройки колонок."
                )
                return

            key_column = columns[0]
            value_columns = columns[1:]
            result = {}

            with open(path, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                # 🔎 Проверка: все ли нужные колонки есть в CSV
                fieldnames = reader.fieldnames
                missing = [col for col in columns if col not in fieldnames]
                if missing:
                    QMessageBox.warning(
                        self.parent,
                        "Ошибка колонок",
                        f"Не найдены колонки в CSV: {', '.join(missing)}\n\n"
                        f"Доступные заголовки: {', '.join(fieldnames or [])}",
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

            project_dir = os.path.dirname(
                os.path.abspath(__file__)
            )  # путь к текущему .py-файлу
            output_path = os.path.join(project_dir, "footprint.json")

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

            QMessageBox.information(
                self.parent, "Готово", f"Файл footprint.json создан:\n{output_path}"
            )
            return output_path

        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Произошла ошибка:\n{e}")

    def apply_footprint_rotation(self, path):
        if not path or not os.path.exists(path):
            QMessageBox.warning(self.parent, "Ошибка", "Файл не существует или путь не указан.")
            return

        try:
            # Загружаем footprint.json из папки проекта
            with open("footprint.json", 'r', encoding='utf-8') as f:
                footprint_data = json.load(f)

            updated_rows = []
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames

                for row in reader:
                    original_fp = row.get("Footprint", "").strip()
                    feedt = row.get("FeedT", "").strip()
                    rot_str = row.get("Rotation", "").replace(",", ".").strip()

                    try:
                        rotation_csv = float(rot_str)
                    except ValueError:
                        rotation_csv = 0.0

                    # 🧩 Сохраняем ключ для footprint.json — всегда оригинальный
                    fp_key = original_fp

                    # ✏️ Обновляем колонку Footprint в CSV, если FeedT == Tray
                    if feedt.lower() == "tray":
                        row["Footprint"] = f"{original_fp}_t"

                    # Получаем Rotation из footprint.json
                    rotation_json = 0.0
                    if fp_key in footprint_data:
                        try:
                            rotation_json = float(footprint_data[fp_key].get("Rotation", 0.0))
                        except (ValueError, TypeError):
                            rotation_json = 0.0

                    # Складываем Rotation
                    new_rotation = rotation_csv + rotation_json

                    # 🔁 Если Rotation >= 360 — отнимаем 360
                    if new_rotation >= 360:
                        new_rotation -= 360

                    # Обновляем Rotation в строке
                    row["Rotation"] = str(new_rotation)

                    updated_rows.append(row)

            # Перезаписываем CSV
            with open(path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_rows)

            QMessageBox.information(self.parent, "Готово", f"Rotation и Footprint обновлены в:\n{path}")

        except Exception as e:
            QMessageBox.critical(self.parent, "Ошибка", f"Произошла ошибка:\n{e}")
    

    def update_feedn_from_inventree(self, csv_path):
            if not os.path.exists(csv_path):
                print("Файл не найден.")
                return

            sett = Settings()
            server = sett.load("server")
            itm = InvenTreeManager(
                url=server["url"],
                username=server["username"],
                password=server["password"],
            )
            itm.connect()

            output_path = csv_path.replace(".csv", "_updated.csv")

            with open(csv_path, newline='', encoding='utf-8') as infile, \
                open(output_path, 'w', newline='', encoding='utf-8') as outfile:

                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                for row in reader:
                    part_number = row.get("PartNumber", "").strip()
                    feed_t = row.get("FeedT", "").strip()

                    if feed_t != "Tray":
                        new_feedn = itm.get_smt600_locations_for_part_name(part_number, feed_t)
                        if new_feedn:
                            row["FeedN"] = new_feedn

                    writer.writerow(row)

            print(f"Обновлённый файл сохранён как: {output_path}")
