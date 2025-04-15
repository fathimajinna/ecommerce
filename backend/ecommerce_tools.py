

def get_product_details(product_name: str):
    """
    Hypothetical function to fetch product details from an e-commerce platform.
    Replace this with actual API calls to your platform.
    """

    if product_name.lower() == "example product":
        return {
            "name": "Example Product",
            "description": "A fantastic example product with great features.",
            "price": "$29.99",
            "availability": "In Stock",
            "features": ["Feature 1", "Feature 2"],
        }
    elif product_name.lower() == "another item":
        return {
            "name": "Another Item",
            "description": "A different product with its own unique qualities.",
            "price": "$19.99",
            "availability": "Out of Stock",
        }
    else:
        return None