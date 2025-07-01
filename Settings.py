import os, json


class Settings:
    def __init__(self, path=None):
        if path is not None:
            self.path = path
        else:
            self.path = "settings.json"

        if not os.path.exists(self.path): 
            with open(self.path, 'w', encoding="utf-8") as file:
                json.dump({}, file, indent=4)

    def save(self, key, value): #Открыть, добавить, сохранить
        with open(self.path, 'r', encoding="utf-8") as file:
            data = json.load(file)

        data[key] = value

        with open(self.path, 'w', encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load(self, key): #Открыть, прочитать
        with open(self.path, 'r', encoding="utf-8") as file:
            data = json.load(file)
        
        return data.get(key)

if __name__ == "__main__":
    sett = Settings()

    url = input("Enter url")
    user = input("Enter user")
    password = input("Enter password")

    dicti = { "server":
            {
                        "url" : url,
                        "user": user,
                        "password": password
            }       
                }

    sett.save("server", dicti["server"])
    fname = "name"
    dict2 = {
        "file": {
            "name":fname,
            "path":"path"
        }
    }
    sett.save("file", dict2["file"])

    readd = sett.load("server")
    print(readd)

    readd = sett.load("file")
    print(readd)
    #создать словарь, и записать весь словать в json(server -> : url, user,password)

