from pathlib import Path
import zipfile
import pandas as pd
import duckdb
from src.retail.config import RETAIL_RAW, TRANSACTIONS_PARQUET

EXPECTED = {'InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country'}

def extract_xlsx(zip_path=RETAIL_RAW):
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if n.lower().endswith(('.xlsx','.xls'))]
        if not names:
            raise ValueError('UCI archive contains no Excel file')
        target = Path('data/raw') / Path(names[0]).name
        target.parent.mkdir(parents=True, exist_ok=True)
        with z.open(names[0]) as src, target.open('wb') as dst:
            dst.write(src.read())
    return target

def convert_to_parquet(xlsx_path: Path, out=TRANSACTIONS_PARQUET):
    # pandas/openpyxl is intentionally used only once; subsequent processing is DuckDB/Parquet.
    sheets = pd.ExcelFile(xlsx_path).sheet_names
    frames = []
    for sheet in sheets:
        frame = pd.read_excel(xlsx_path, sheet_name=sheet, engine='openpyxl')
        if set(frame.columns) != EXPECTED:
            raise ValueError(f'Unexpected schema in {sheet}: {list(frame.columns)}')
        frames.append(frame)
    df = pd.concat(frames, ignore_index=True)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
    df['CustomerID'] = pd.to_numeric(df['CustomerID'], errors='coerce').astype('Int64')
    df['line_revenue'] = df['Quantity'] * df['UnitPrice']
    df.to_parquet(out, index=False)
    return out

if __name__ == '__main__':
    xlsx = extract_xlsx()
    print(convert_to_parquet(xlsx))
