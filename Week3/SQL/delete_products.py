import os
from supabase import create_client, Client  # pip install supabase
from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
sb: Client = create_client(url, key)


def delete_product(product_id):
    resp = sb.table("products").delete().eq("product_id", product_id).execute()
    return resp.data


if __name__ == "__main__":
    pid = int(input("Enter product id to delete: ").strip())
    confirm = (
        input(f"Are you sure you want to delete product {pid}? (yes/no) ")
        .strip()
        .lower()
    )
    if confirm == "yes":
        deleted = delete_product(pid)
        if deleted:
            print("Deleted: ", deleted)
        else:
            print("No product deleted-- check pid")
    else:
        print("Delete cancelled")
