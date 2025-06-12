class Games:
    publish_year = None
    name = None

    def __init__(self, publish_year, name):
        self.publish_year = publish_year
        self.name = name
        
    def get_info(self):
        print(f"Year: {self.publish_year} Name: {self.name}")