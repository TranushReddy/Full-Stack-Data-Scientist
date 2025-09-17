import os
from supabase import create_client, Client  # pip install supabase
from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
sb: Client = create_client(url, key)


def get_all_products():
    resp = sb.table("products").select("*").execute()
    return resp.data


if __name__ == "__main__":

    products = get_all_products()
    print("All products:", products)
