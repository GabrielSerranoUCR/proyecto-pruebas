"""Verificación del ambiente: versiones instaladas y conexión con Supabase."""

import pytest
import scipy
import sklearn

from proyecto_pruebas.logs_supabase import get_client


def main() -> None:
    """Imprime las versiones instaladas y verifica la conexión con Supabase."""
    print("SciPy:", scipy.__version__)
    print("Scikit-learn:", sklearn.__version__)
    print("Pytest:", pytest.__version__)
    supabase_connection()


def supabase_connection() -> None:
    """Comprueba la conexión con Supabase usando la tabla de prueba."""
    client = get_client()
    if client is None:
        print("Supabase no está configurado (SUPABASE_URL / SUPABASE_KEY).")
        return

    try:
        # Test the connection by fetching data from a test table
        response = client.table("users_test").select("*").execute()

        print("Successfully connected to Supabase!")
        print("Fetched rows:", response.data)

    except Exception as error:  # pylint: disable=broad-exception-caught
        print(f"An error occurred while connecting to Supabase: {error}")

if __name__ == "__main__":
    main()
