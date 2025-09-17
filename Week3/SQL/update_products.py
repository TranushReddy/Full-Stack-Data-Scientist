import os
from supabase import create_client, Client  # pip install supabase
from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
sb: Client = create_client(url, key)


def update_stock(sku, new_stock):
    resp = sb.table("products").update({"stock": new_stock}).eq("sku", sku).execute()
    return resp.data


if __name__ == "__main__":
    sku = input("Enter SKU to update: ").strip()
    new_stock = int(input("Enter new stock value: ").strip())
    updated = update_stock(sku, new_stock)
    print("Updated:", updated)
