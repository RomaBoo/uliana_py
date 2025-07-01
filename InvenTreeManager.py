# pip install inventree


import requests
from inventree.api import InvenTreeAPI
from inventree.company import Company
from inventree.part import Part, PartCategory
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

INVENTREE_API_URL = "http://inventree.efps"  # Замени на свой URL
INVENTREE_API_TOKEN = "token"  # Замени на свой токен
INVENTREE_API_USERNAME = "admin"  # Замени на свое имя пользователя
INVENTREE_API_PASSWORD = "1"  # Замени на свой пароль


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

    itm = InvenTreeManager(
        INVENTREE_API_URL,
        INVENTREE_API_USERNAME,
        INVENTREE_API_PASSWORD,
    )
    try:
        itm.connect()
    except Exception as e:
        print(f"Connect err InvenTree API: {e}")
        return


if __name__ == "__main__":
    main()
