import os
import scipy
import sklearn
import pytest
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

supabase_url: str = os.environ.get("SUPABASE_URL", "")
supabase_key: str = os.environ.get("SUPABASE_KEY", "")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")

client: Client = create_client(supabase_url, supabase_key)

def main() -> None:
    print("SciPy:", scipy.__version__)
    print("Scikit-learn:", sklearn.__version__)
    print("Pytest:", pytest.__version__)
    supabase_connection()

def supabase_connection() -> None:
    try:
        # Test the connection by fetching data from a test table
        response = client.table("users_test").select("*").execute()

        print("Successfully connected to Supabase!")
        print("Fetched rows:", response.data)

    except Exception as error:
        print(f"An error occurred while connecting to Supabase: {error}")

if __name__ == "__main__":
    main()
