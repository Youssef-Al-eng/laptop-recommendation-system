import json
from config import PRODUCTS_FILE


class DatasetLoader:

    def __init__(self):

        self.file_path = PRODUCTS_FILE

    def load_products(self):

        try:

            with open(self.file_path, "r", encoding="utf-8") as file:

                products = json.load(file)

            return products

        except FileNotFoundError:

            print("Products file not found")

            return []

        except json.JSONDecodeError:

            print("Error reading JSON file")

            return []

    def count_products(self):

        products = self.load_products()

        return len(products)

    def preview_products(self, n=5):

        products = self.load_products()

        return products[:n]
