# pip install inventree


import requests
from inventree.api import InvenTreeAPI
from inventree.company import Company
from inventree.part import Part, PartCategory
from inventree.stock import StockItem, StockLocation
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

# INVENTREE_API_URL = "http://inventree.efps"  # Замени на свой URL
# INVENTREE_API_TOKEN = "token"  # Замени на свой токен
# INVENTREE_API_USERNAME = "admin"  # Замени на свое имя пользователя
# INVENTREE_API_PASSWORD = "1"  # Замени на свой пароль


class InvenTreeManager:
    progress_updated = pyqtSignal(str)  # Передаем строку сообщения
    value_updated = pyqtSignal(int)  # Передаем числовое значение для прогресс-бара
    finished = pyqtSignal()  # Сигнал о завершении работы
    result_ready = pyqtSignal(list)

    def __init__(self, url, username=None, password=None, token=None):
        self.url = url
        self.username = username
        self.password = password
        self.token = token
        self._is_running = False
        self.parts = None
        self.stock_items = None
        self.locations = None

    def connect(self):
        try:
            if self.token:
                self.api = InvenTreeAPI(self.url, token=self.token)
            else:
                self.api = InvenTreeAPI(
                    self.url, username=self.username, password=self.password
                )
            # print("Connect succes InvenTree API.")
            # return api
        except Exception as e:
            raise Exception(f"Connect failed: {e}")

    def get_parts(self, part_name):
        parts = Part.list(self.api, filters={"name": part_name})
        return parts

    def get_part_id_by_name(self, api, part_name):
        if not self.parts:
            self.parts = self.get_parts(part_name)

        for part in self.parts:
            name = part.name.lower()
            if name == part_name.lower():
                return part.pk
        return None

    def get_stock_locations_for_part_name(self, part_name):
        """
        Получает список уникальных StockLocation (имя и ID) для детали по ее имени.
        """
        api = self.api
        part_id = self.get_part_id_by_name(api, part_name)
        if not part_id:
            return []

        print(f"Поиск расположений для детали '{part_name}' (ID: {part_id})...")

        try:
            # Получаем все StockItem'ы, связанные с данной деталью
            if not self.stock_items:
                self.stock_items = StockItem.list(api, filters={"part": None})

            if not self.locations:
                self.locations = StockLocation.list(api, filters={"name": None})

            unique_locations = {}

            for item in self.stock_items:
                None
                part_id_loc = item._data.get("part")
                if part_id == part_id_loc:
                    location_id = item.pk

                    for location in self.locations:
                        # location_pk = location.pk
                        if location.pk == item._data.get("location"):
                            loc_type = location._data.get("location_type_detail")
                            if location_id not in unique_locations:
                                unique_locations = {
                                    "id": location_id,
                                    "name": location._data.get("name"),
                                    "path": location._data.get("pathstring"),
                                    "type": loc_type["name"],
                                    "feed": loc_type["description"],
                                }

            return unique_locations

        except Exception as e:
            print(
                f"Произошла ошибка при получении StockLocation для детали '{part_name}': {e}"
            )
            return []

    def get_smt600_locations_for_part_name(self, part_name, feeder_type):
        stock_location = self.get_stock_locations_for_part_name(part_name)
        if not stock_location:
            return None

        if stock_location["feed"] != "Feeder":
            return None

        if stock_location["type"] != feeder_type:
            return None

        fpth = stock_location["path"]
        if "SMT660/Feeder/FP_" in fpth:
            fpth = fpth.split("/")
            fplace = int(fpth[2].replace("FP_", ""))
            return fplace
        else:
            return None

    def get_cats(self):
        cat_path_list = PartCategory.list(self.api, filters={"parent": "null"})
        return cat_path_list

    def get_mpn_sku_id(self, row, part_idx):
        # pn = row[part_idx["pn"]["n"]]
        pn_id = row[part_idx["pn"]["n_id"]]
        sku_id = -1
        mpn_id = -1
        # print(f"pn: {pn}, pn_id: {pn_id}")
        if pn_id == "None":
            return mpn_id, sku_id

        mnf_id = row[part_idx["mnf"]["n_id"]]
        mpn = row[part_idx["mpn"]["n"]]
        sup_id = row[part_idx["sup"]["n_id"]]
        sku = row[part_idx["sku"]["n"]]
        try:
            part = Part(self.api, pn_id)
            manufacturer_parts = part.getManufacturerParts()
            supplier_parts = part.getSupplierParts()

            for mp in manufacturer_parts:
                if (
                    mp._data.get("manufacturer") == mnf_id
                    and mp._data.get("MPN") == mpn
                ):
                    mpn_id = int(mp._data.get("pk"))
                    break

            for sp in supplier_parts:
                # db_sup_id = sp._data.get("supplier")
                # db_sku = sp._data.get("SKU")
                if sp._data.get("supplier") == sup_id:
                    if sp._data.get("SKU") == sku:
                        sku_id = int(sp._data.get("pk"))
                        break

        except Exception as e:
            print(f"Err MPN/SKU: {e}")
        return mpn_id, sku_id

    def get_mnf(self):
        mnf_s = Company.list(self.api, filters={"is_manufacturer": True})
        return mnf_s

    def get_sup(self):
        suppliers = Company.list(self.api, filters={"is_supplier": True})
        return suppliers

    def get_category_tree(self, parent_id=None):
        categories = PartCategory.list(self.api, filters={"parent": parent_id})
        tree = []
        for category in categories:
            node = {
                "id": category.pk,
                "name": category.name,
                "path": category.pathstring,
            }
            tree.append(node)
        return tree


def main():
    None

    # itm = InvenTreeManager(
    #     INVENTREE_API_URL,
    #     INVENTREE_API_USERNAME,
    #     INVENTREE_API_PASSWORD,
    # )
    # try:
    #     itm.connect()
    # except Exception as e:
    #     print(f"Connect err InvenTree API: {e}")
    #     return


if __name__ == "__main__":
    main()
