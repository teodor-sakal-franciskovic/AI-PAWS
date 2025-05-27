import os
import tempfile

# https://pypi.org/project/pymupdf4llm/
import pymupdf4llm
from fastapi import HTTPException, UploadFile


def extract_pdf_to_markdown(file: UploadFile):
  if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

  with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_path = temp_file.name
        temp_file.write(file.file.read())
        temp_file.flush()

  try:
      markdown_text = pymupdf4llm.to_markdown(temp_path)
  except Exception as e:
      raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")
  finally:
      if os.path.exists(temp_path):
          os.remove(temp_path)

  if not markdown_text:
      raise HTTPException(status_code=500, detail="No content was extracted from the document.")

  return markdown_text