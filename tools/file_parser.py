import pandas as pd
import PyPDF2
from pathlib import Path

def parse_csv(file_path: str) -> dict:
    """
    Parse CSV file and return structured data.
    """
    try:
        df = pd.read_csv(file_path)
        
        return {
            "type": "csv",
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(10).to_dict('records'),
            "summary": df.describe().to_dict() if df.select_dtypes(include=['number']).shape[1] > 0 else None,
            "data": df.to_csv(index=False)
        }
    except Exception as e:
        return {"error": f"Failed to parse CSV: {str(e)}"}


def parse_excel(file_path: str) -> dict:
    """
    Parse Excel file and return structured data.
    """
    try:
        # Read all sheets
        excel_file = pd.ExcelFile(file_path)
        sheets = {}
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            sheets[sheet_name] = {
                "rows": len(df),
                "columns": list(df.columns),
                "preview": df.head(10).to_dict('records'),
                "data": df.to_csv(index=False)
            }
        
        return {
            "type": "excel",
            "sheets": list(sheets.keys()),
            "data": sheets
        }
    except Exception as e:
        return {"error": f"Failed to parse Excel: {str(e)}"}


def parse_pdf(file_path: str) -> dict:
    """
    Extract text from PDF file.
    """
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            for page_num in range(min(num_pages, 10)):  # Limit to first 10 pages
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        
        return {
            "type": "pdf",
            "pages": num_pages,
            "text": text[:5000],  # First 5000 chars
            "full_text": text
        }
    except Exception as e:
        return {"error": f"Failed to parse PDF: {str(e)}"}


def parse_uploaded_file(file_path: str) -> dict:
    """
    Parse uploaded file based on extension.
    
    Args:
        file_path: Path to uploaded file
    
    Returns:
        Dictionary with parsed data and metadata
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    
    if extension == '.csv':
        return parse_csv(file_path)
    elif extension in ['.xlsx', '.xls']:
        return parse_excel(file_path)
    elif extension == '.pdf':
        return parse_pdf(file_path)
    else:
        return {"error": f"Unsupported file type: {extension}"}


def summarize_file_for_llm(parsed_data: dict) -> str:
    """
    Create a concise summary of file contents for LLM context.
    
    Args:
        parsed_data: Output from parse_uploaded_file
    
    Returns:
        Text summary suitable for LLM prompt
    """
    if "error" in parsed_data:
        return f"Error: {parsed_data['error']}"
    
    file_type = parsed_data.get("type", "unknown")
    
    if file_type == "csv":
        summary = f"CSV file with {parsed_data['rows']} rows and {len(parsed_data['columns'])} columns.\n"
        summary += f"Columns: {', '.join(parsed_data['columns'])}\n\n"
        summary += "First 5 rows:\n"
        for i, row in enumerate(parsed_data['preview'][:5], 1):
            summary += f"{i}. {row}\n"
        return summary
    
    elif file_type == "excel":
        summary = f"Excel file with {len(parsed_data['sheets'])} sheet(s): {', '.join(parsed_data['sheets'])}\n\n"
        for sheet_name, sheet_data in parsed_data['data'].items():
            summary += f"Sheet '{sheet_name}': {sheet_data['rows']} rows, columns: {', '.join(sheet_data['columns'])}\n"
        return summary
    
    elif file_type == "pdf":
        summary = f"PDF document with {parsed_data['pages']} pages.\n\n"
        summary += f"Content preview:\n{parsed_data['text'][:1000]}..."
        return summary
    
    return "Unknown file type"
