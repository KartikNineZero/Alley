import logging
from pykeepa import ProductFinder, AmazonRegion

class ProductData:
    def __init__(self, asin, region=AmazonRegion.US):
        self.asin = asin
        self.region = region
        self.finder = ProductFinder(asin, region)
        self.product_data = None

    def get_data(self):
        if not self.product_data:
            try:
                self.product_data = self.finder.load_data()
            except Exception as e:
                logging.error(f"Error loading product data: {str(e)}")
        return self.product_data

    def get_price(self):
        data = self.get_data()
        if data and 'Offers' in data and 'listings' in data['Offers']:
            price = data['Offers']['listings']['Price']
            return price
        else:
            logging.error("Error retrieving price data.")
            return None

    def get_rating(self):
        data = self.get_data()
        if data and 'Offers' in data and 'Offer' in data['Offers']:
            rating = data['Offers']['Offer']['CustomerRating']
            return rating
        else:
            logging.error("Error retrieving rating data.")
            return None

# Example usage
product = ProductData('B002KT3XQM')
print(product.get_price())
print(product.get_rating())
