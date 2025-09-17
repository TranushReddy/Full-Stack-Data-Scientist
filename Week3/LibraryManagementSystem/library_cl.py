import os
from supabase import create_client, Client
from datetime import datetime

SUPABASE_URL = os.environ.get(
    "SUPABASE_URL", "https://konjgiwrilvsqghdvwlr.supabase.co"
)
SUPABASE_KEY = os.environ.get(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtvbmpnaXdyaWx2c3FnaGR2d2xyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwODE4MTUsImV4cCI6MjA3MzY1NzgxNX0.5zTui4ccgIqyu3uwmtDyw0R9FcK6KEQEvYEoDL5RIPA",
)


class Library:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.conn = self.supabase

    def add_member(self, name, email):
        try:
            self.supabase.table("members").insert(
                {"name": name, "email": email}
            ).execute()
            print(f"Member '{name}' registered successfully.")
        except Exception as e:
            print(f"Error adding member: {e}")

    def add_book(self, title, author, category, stock):
        try:
            self.supabase.table("books").insert(
                {"title": title, "author": author, "category": category, "stock": stock}
            ).execute()
            print(f"Book '{title}' by '{author}' added successfully.")
        except Exception as e:
            print(f"Error adding book: {e}")

    def list_all_books(self):
        try:
            response = self.supabase.table("books").select("*").execute()
            books = response.data
            if not books:
                print("No books found.")
                return

            print("\n--- All Books ---")
            for book in books:
                print(
                    f"ID: {book['book_id']}, Title: {book['title']}, Author: {book['author']}, Stock: {book['stock']}"
                )
        except Exception as e:
            print(f"Error listing books: {e}")

    def search_books(self, query, search_by="title"):
        try:
            if search_by == "title":
                response = (
                    self.supabase.table("books")
                    .select("*")
                    .filter("title", "ilike", f"%{query}%")
                    .execute()
                )
            elif search_by == "author":
                response = (
                    self.supabase.table("books")
                    .select("*")
                    .filter("author", "ilike", f"%{query}%")
                    .execute()
                )
            elif search_by == "category":
                response = (
                    self.supabase.table("books")
                    .select("*")
                    .filter("category", "ilike", f"%{query}%")
                    .execute()
                )
            else:
                print(
                    "Invalid search criteria. Please use 'title', 'author', or 'category'."
                )
                return

            books = response.data
            if not books:
                print(f"No books found matching '{query}'.")
                return

            print(f"\n--- Search Results for '{query}' ---")
            for book in books:
                print(
                    f"ID: {book['book_id']}, Title: {book['title']}, Author: {book['author']}, Stock: {book['stock']}"
                )
        except Exception as e:
            print(f"Error searching books: {e}")

    def show_member_details(self, member_id):
        try:
            member_res = (
                self.supabase.table("members")
                .select("*")
                .eq("member_id", member_id)
                .single()
                .execute()
            )
            member = member_res.data
            if not member:
                print(f"Member with ID {member_id} not found.")
                return

            borrowed_books_res = (
                self.supabase.table("borrow_records")
                .select("*, books(title, author)")
                .eq("member_id", member_id)
                .is_("return_date", None)
                .execute()
            )
            borrowed_books = borrowed_books_res.data

            print(
                f"\n--- Member Details for {member['name']} (ID: {member['member_id']}) ---"
            )
            print(f"Email: {member['email']}")
            print("Borrowed Books:")
            if not borrowed_books:
                print("   No books currently borrowed.")
            else:
                for record in borrowed_books:
                    book_info = record["books"]
                    print(
                        f"   - '{book_info['title']}' by '{book_info['author']}' (Borrowed on: {record['borrow_date'].split('T')[0]})"
                    )
        except Exception as e:
            print(f"Error fetching member details: {e}")

    def update_book_stock(self, book_id, new_stock):
        try:
            self.supabase.table("books").update({"stock": new_stock}).eq(
                "book_id", book_id
            ).execute()
            print(f"Book ID {book_id} stock updated to {new_stock}.")
        except Exception as e:
            print(f"Error updating book stock: {e}")

    def update_member_email(self, member_id, new_email):
        try:
            self.supabase.table("members").update({"email": new_email}).eq(
                "member_id", member_id
            ).execute()
            print(f"Member ID {member_id} email updated to {new_email}.")
        except Exception as e:
            print(f"Error updating member email: {e}")

    def delete_member(self, member_id):
        try:
            response = (
                self.supabase.table("borrow_records")
                .select("record_id")
                .eq("member_id", member_id)
                .is_("return_date", None)
                .execute()
            )
            if response.data:
                print("Error: Cannot delete member. They have unreturned books.")
                return

            self.supabase.table("members").delete().eq("member_id", member_id).execute()
            print(f"Member ID {member_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting member: {e}")

    def delete_book(self, book_id):
        try:
            response = (
                self.supabase.table("borrow_records")
                .select("record_id")
                .eq("book_id", book_id)
                .is_("return_date", None)
                .execute()
            )
            if response.data:
                print("Error: Cannot delete book. It is currently borrowed.")
                return

            self.supabase.table("books").delete().eq("book_id", book_id).execute()
            print(f"Book ID {book_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting book: {e}")

    def borrow_book(self, member_id, book_id):
        try:
            book_res = (
                self.supabase.table("books")
                .select("stock")
                .eq("book_id", book_id)
                .limit(1)
                .execute()
            )
            book = book_res.data
            if not book:
                print(f"Error: Book with ID {book_id} not found.")
                return

            book_stock = book[0]["stock"]
            if book_stock <= 0:
                print("Error: Book is not available.")
                return

            self.supabase.table("books").update({"stock": book_stock - 1}).eq(
                "book_id", book_id
            ).execute()

            self.supabase.table("borrow_records").insert(
                {
                    "member_id": member_id,
                    "book_id": book_id,
                    "borrow_date": datetime.now().isoformat(),
                }
            ).execute()

            print("Book borrowed successfully!")
        except Exception as e:
            print(f"Error borrowing book: {e}")

    def return_book(self, member_id, book_id):
        try:
            record_res = (
                self.supabase.table("borrow_records")
                .select("record_id")
                .eq("member_id", member_id)
                .eq("book_id", book_id)
                .is_("return_date", None)
                .limit(1)
                .execute()
            )
            record = record_res.data
            if not record:
                print("Error: No active borrow record found for this member and book.")
                return

            record_id = record[0]["record_id"]
            self.supabase.table("borrow_records").update(
                {"return_date": datetime.now().isoformat()}
            ).eq("record_id", record_id).execute()

            self.supabase.rpc("increment_book_stock", {"book_id": book_id}).execute()

            print("Book returned successfully!")
        except Exception as e:
            print(f"Error returning book: {e}")

    def get_most_borrowed_books(self, limit=5):
        try:
            response = self.supabase.rpc(
                "get_most_borrowed_books", {"p_limit": limit}
            ).execute()
            result = response.data
            print(f"\n--- Top {limit} Most Borrowed Books ---")
            if not result:
                print("No borrow history found.")
            else:
                for row in result:
                    print(
                        f"- '{row['title']}' by '{row['author']}' (Borrowed {row['borrow_count']} times)"
                    )
        except Exception as e:
            print(f"Error generating report: {e}")

    def get_overdue_books(self):
        try:
            response = self.supabase.rpc("get_overdue_books").execute()
            result = response.data
            print("\n--- Overdue Books (>14 days) ---")
            if not result:
                print("No overdue books found.")
            else:
                for row in result:
                    print(
                        f"- Member: {row['member_name']}, Book: '{row['book_title']}', Borrow Date: {row['borrow_date'].split('T')[0]}"
                    )
        except Exception as e:
            print(f"Error generating report: {e}")

    def count_borrowed_per_member(self):
        try:
            response = self.supabase.rpc("count_borrowed_per_member").execute()
            result = response.data
            print("\n--- Total Books Borrowed Per Member ---")
            if not result:
                print("No members found.")
            else:
                for row in result:
                    print(
                        f"- {row['member_name']}: {row['borrowed_count']} book(s) borrowed"
                    )
        except Exception as e:
            print(f"Error generating report: {e}")


def main():
    library = Library()

    while True:
        print("\n--- Library Management System ---")
        print("1. Register a new member")
        print("2. Add a new book")
        print("3. List all books")
        print("4. Search for books")
        print("5. Show member details and borrowed books")
        print("6. Update book stock")
        print("7. Update member email")
        print("8. Delete a member")
        print("9. Delete a book")
        print("10. Borrow a book")
        print("11. Return a book")
        print("12. Generate reports")
        print("13. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter member's name: ")
            email = input("Enter member's email: ")
            library.add_member(name, email)
        elif choice == "2":
            title = input("Enter book title: ")
            author = input("Enter author name: ")
            category = input("Enter category: ")
            try:
                stock = int(input("Enter initial stock: "))
                library.add_book(title, author, category, stock)
            except ValueError:
                print("Invalid stock value. Please enter a number.")
        elif choice == "3":
            library.list_all_books()
        elif choice == "4":
            query = input("Enter search query: ")
            search_by = input("Search by (title/author/category): ")
            library.search_books(query, search_by)
        elif choice == "5":
            try:
                member_id = int(input("Enter member ID: "))
                library.show_member_details(member_id)
            except ValueError:
                print("Invalid member ID. Please enter a number.")
        elif choice == "6":
            try:
                book_id = int(input("Enter book ID: "))
                new_stock = int(input("Enter new stock count: "))
                library.update_book_stock(book_id, new_stock)
            except ValueError:
                print("Invalid ID or stock value. Please enter a number.")
        elif choice == "7":
            try:
                member_id = int(input("Enter member ID: "))
                new_email = input("Enter new email: ")
                library.update_member_email(member_id, new_email)
            except ValueError:
                print("Invalid member ID. Please enter a number.")
        elif choice == "8":
            try:
                member_id = int(input("Enter member ID to delete: "))
                library.delete_member(member_id)
            except ValueError:
                print("Invalid member ID. Please enter a number.")
        elif choice == "9":
            try:
                book_id = int(input("Enter book ID to delete: "))
                library.delete_book(book_id)
            except ValueError:
                print("Invalid book ID. Please enter a number.")
        elif choice == "10":
            try:
                member_id = int(input("Enter member ID: "))
                book_id = int(input("Enter book ID to borrow: "))
                library.borrow_book(member_id, book_id)
            except ValueError:
                print("Invalid ID. Please enter a number.")
        elif choice == "11":
            try:
                member_id = int(input("Enter member ID: "))
                book_id = int(input("Enter book ID to return: "))
                library.return_book(member_id, book_id)
            except ValueError:
                print("Invalid ID. Please enter a number.")
        elif choice == "12":
            print("\n--- Reports Menu ---")
            print("a. Top 5 most borrowed books")
            print("b. Overdue books")
            print("c. Total books borrowed per member")
            report_choice = input("Enter report choice (a/b/c): ")
            if report_choice == "a":
                library.get_most_borrowed_books()
            elif report_choice == "b":
                library.get_overdue_books()
            elif report_choice == "c":
                library.count_borrowed_per_member()
            else:
                print("Invalid report choice.")
        elif choice == "13":
            print("Exiting. Goodbye")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
