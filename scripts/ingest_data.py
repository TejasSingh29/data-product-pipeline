import os
import pandas as pd


def ingest_csv(filepath, delimiter=',', encoding='utf-8', dtype_dict=None):
    """
    Load a CSV file using explicit delimiter, encoding, and data types.

    Args:
        filepath: Path to CSV file.
        delimiter: Field separator. Default is comma (,).
        encoding: File encoding. Default is UTF-8.
        dtype_dict: Optional dictionary mapping column names to data types.

    Returns:
        Pandas DataFrame.
    """
    try:
        df = pd.read_csv(
            filepath,
            delimiter=delimiter,
            encoding=encoding,
            dtype=dtype_dict
        )

        print(f"✓ CSV loaded: {filepath}")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"  Columns: {list(df.columns)}")

        return df

    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        raise

    except UnicodeDecodeError:
        print(f"Encoding error: Could not decode with {encoding}")
        print("Try: latin-1, iso-8859-1, or cp1252")
        raise


def ingest_json(filepath, is_nested=False):
    """
    Load a JSON file and optionally flatten nested structures.

    Args:
        filepath: Path to JSON file.
        is_nested: If True, flatten nested JSON structures.

    Returns:
        Pandas DataFrame.
    """
    try:
        df = pd.read_json(filepath)

        if is_nested:
            df = pd.json_normalize(df.to_dict(orient='records'))
            print("✓ Nested JSON flattened to tabular format")

        print(f"✓ JSON loaded: {filepath}")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"  Columns: {list(df.columns)}")

        return df

    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        raise


def ingest_csv_with_fallback(
    filepath,
    delimiters=None,
    fallback_encodings=None
):
    """
    Load CSV using multiple delimiters and encoding fallbacks.

    Args:
        filepath: Path to CSV file.
        delimiters: List of delimiters to try.
        fallback_encodings: List of encodings to try.

    Returns:
        Pandas DataFrame.
    """

    if delimiters is None:
        delimiters = [',']

    if fallback_encodings is None:
        fallback_encodings = [
            'utf-8',
            'latin-1',
            'iso-8859-1',
            'cp1252'
        ]

    for delimiter in delimiters:
        for encoding in fallback_encodings:
            try:
                df = pd.read_csv(
                    filepath,
                    delimiter=delimiter,
                    encoding=encoding
                )

                print(
                    f"✓ Successfully loaded with "
                    f"delimiter='{delimiter}', encoding='{encoding}'"
                )

                return df

            except (
                UnicodeDecodeError,
                pd.errors.ParserError
            ):
                continue

    raise ValueError(
        f"Could not load {filepath} "
        f"with any encoding/delimiter combination"
    )


def document_ingestion(df, source_file):
    """
    Print a detailed ingestion report for audit purposes.
    """

    print(f"\n{'=' * 60}")
    print(f"INGESTION REPORT: {source_file}")
    print(f"{'=' * 60}")

    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn Names & Data Types:")
    print(df.dtypes)

    print("\nNull Values Per Column:")
    print(df.isnull().sum())

    print("\nFirst 3 Rows:")
    print(df.head(3).to_string(index=False))

    print(f"{'=' * 60}\n")

    return df


def ensure_directory(directory):
    """
    Create a directory if it does not already exist.
    """
    os.makedirs(directory, exist_ok=True)


if __name__ == "__main__":

    print("Starting multi-format ingestion...\n")

    # Make sure processed directory exists
    ensure_directory("data/processed")

    # ---------------------------------------------------------
    # TASK 1: Load CSV with explicit parameters
    # ---------------------------------------------------------

    csv_df = ingest_csv(
        "data/raw/customers.csv",
        delimiter=',',
        encoding='utf-8',
        dtype_dict={
            "customer_id": "int64",
            "name": "string",
            "email": "string",
            "signup_date": "string"
        }
    )

    document_ingestion(csv_df, "customers.csv")

    # ---------------------------------------------------------
    # TASK 2: Load JSON with nested structure handling
    # ---------------------------------------------------------

    json_df = ingest_json(
        "data/raw/transactions.json",
        is_nested=True
    )

    document_ingestion(json_df, "transactions.json")

    # ---------------------------------------------------------
    # TASK 3: Test encoding fallback
    # ---------------------------------------------------------

    print("Testing CSV encoding fallback...\n")

    fallback_df = ingest_csv_with_fallback(
        "data/raw/customers.csv",
        delimiters=[',', ';', '\t'],
        fallback_encodings=[
            'utf-8',
            'latin-1',
            'iso-8859-1',
            'cp1252'
        ]
    )

    print(
        f"Fallback test completed: "
        f"{fallback_df.shape[0]} rows × "
        f"{fallback_df.shape[1]} columns\n"
    )

    # ---------------------------------------------------------
    # TASK 5: Save processed data
    # ---------------------------------------------------------

    csv_df.to_csv(
        "data/processed/customers_ingested.csv",
        index=False
    )

    json_df.to_csv(
        "data/processed/transactions_ingested.csv",
        index=False
    )

    print("✓ All data ingested and saved to processed/")