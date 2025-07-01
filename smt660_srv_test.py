from InvenTreeManager import InvenTreeManager
from Settings import Settings

INVENTREE_API_URL = "http://parts.efps"  # Замени на свой URL
INVENTREE_API_USERNAME = "admin"  # Замени на свое имя пользователя
INVENTREE_API_PASSWORD = "EFPS1.parts"  # Замени на свой пароль


def main():
    try:
        sett = Settings()
        server = sett.load("server")

        itm = InvenTreeManager(
            url=server["url"],
            username=server["username"],
            password=server["password"],
        )
        itm.connect()
        print("Connect success")

    except Exception as e:
        error_message = f"Worker: Err: {e}"
        print(error_message)

        # self.progress_updated.emit(error_message)
        # self._is_running = False

    # finally:
    #     self.result_ready.emit(categories)
    #     self.finished.emit()  # Сигнал о завершении работы (успешно или с ошибкой)
    #     print("Worker: Done.")
    #     self._is_running = False


if __name__ == "__main__":
    main()
