"""Document loading and processing utilities."""

import os
import io
import requests
import tempfile
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# LangChain imports
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Unstructured imports
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.pptx import partition_pptx
from unstructured.partition.html import partition_html
from unstructured.partition.xlsx import partition_xlsx
from unstructured.partition.csv import partition_csv
from unstructured.partition.text import partition_text
from unstructured.partition.image import partition_image

# OCR imports
import pytesseract

from .text_processing import clean_thai_ocr, clean_and_tokenize_thai, is_meaningful_text
from .config import ProcessingConfig


class DocumentProcessor:
    """Main document processing class."""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        pytesseract.pytesseract.tesseract_cmd = config.tesseract_path
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            keep_separator=False
        )
    
    def elements_to_docs(self, elements, source: str) -> List[Document]:
        """Convert Unstructured elements to LangChain Documents."""
        docs = []
        for el in elements:
            text = (getattr(el, "text", "") or "").strip()
            if not text:
                if getattr(el, "category", "") in ("Table", "Image"):
                    text = f"[{el.category}]"
                else:
                    continue

            md = getattr(el, "metadata", None)
            metadata = {
                "source": source,
                "category": getattr(el, "category", None),
                "filename": getattr(md, "filename", None) if md else None,
                "page_number": getattr(md, "page_number", None) if md else None,
                "section": getattr(md, "section", None) if md else None,
                "links": getattr(md, "links", None) if md else None,
                "text_as_html": getattr(el, "text_as_html", None),
            }
            
            # Filter out None values
            metadata = {k: v for k, v in metadata.items() if v is not None}
            
            docs.append(Document(page_content=text, metadata=metadata))
        return docs

    def load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF document with OCR support."""
        docs: List[Document] = []

        # First pass: fast extraction
        elements = partition_pdf(
            filename=file_path,
            strategy="fast",
            include_metadata=True,
            infer_table_structure=False,
            extract_images_in_pdf=False,
            languages=["tha", "eng"],
            include_page_breaks=False,
        )

        total_chars = sum(len(getattr(e, "text", "") or "") for e in elements)

        # If very little text found, try OCR
        if total_chars < 500:
            elements = partition_pdf(
                filename=file_path,
                strategy="ocr_only",
                include_metadata=True,
                infer_table_structure=True,
                extract_images_in_pdf=False,
                languages=["tha", "eng"],
                include_page_breaks=False,
            )

        for e in elements:
            text = (getattr(e, "text", "") or "").strip()
            if not text or not is_meaningful_text(text):
                continue
                
            md = getattr(e, "metadata", None)
            page = getattr(md, "page_number", None) if md else None
            category = getattr(e, "category", None) or e.__class__.__name__
            
            docs.append(Document(
                page_content=text,
                metadata={
                    "source": file_path,
                    "page_number": page,
                    "category": category
                }
            ))
        return docs

    def load_docx(self, file_path: str) -> List[Document]:
        """Load DOCX document."""
        elements = partition_docx(filename=file_path, include_metadata=True)
        return self.elements_to_docs(elements, source=file_path)

    def load_pptx(self, file_path: str) -> List[Document]:
        """Load PPTX document."""
        elements = partition_pptx(filename=file_path, include_metadata=True)
        return self.elements_to_docs(elements, source=file_path)

    def load_xlsx(self, file_path: str) -> List[Document]:
        """Load XLSX document."""
        elements = partition_xlsx(filename=file_path, include_metadata=True)
        return self.elements_to_docs(elements, source=file_path)

    def load_csv(self, file_path: str) -> List[Document]:
        """Load CSV document."""
        elements = partition_csv(filename=file_path, include_metadata=True)
        return self.elements_to_docs(elements, source=file_path)

    def load_text(self, file_path: str) -> List[Document]:
        """Load text document."""
        elements = partition_text(filename=file_path, include_metadata=True, encoding="utf-8")
        return self.elements_to_docs(elements, source=file_path)

    def load_image(self, file_path: str) -> List[Document]:
        """Load image with OCR."""
        elements = partition_image(
            filename=file_path,
            include_metadata=True,
            strategy="ocr_only",
            languages=["tha", "eng"],
        )
        docs = self.elements_to_docs(elements, source=file_path)
        
        # Clean Thai text
        for doc in docs:
            doc.page_content = clean_and_tokenize_thai(doc.page_content)
        return docs

    def load_web_page(self, url: str, content_selector: str = "body") -> List[Document]:
        """Load web page with image OCR."""
        try:
            response = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ingest-bot/1.0)"
            })
            response.raise_for_status()
            response.encoding = response.apparent_encoding or response.encoding
        except Exception as e:
            print(f"[WEB] Failed to load {url}: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script/style/noscript tags
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        section = soup.select_one(content_selector) or soup

        # Fix lazy-loaded images
        for img_tag in section.find_all("img"):
            self._normalize_img_src(img_tag)

        html_str = str(section)

        # Process HTML content
        elements = partition_html(text=html_str, include_metadata=True)
        docs = self.elements_to_docs(elements, source=url)

        # OCR images on the page
        docs.extend(self._process_web_images(section, url))
        
        return docs

    def _normalize_img_src(self, tag):
        """Normalize image src attributes for lazy-loaded images."""
        for attr in ("data-src", "data-original", "data-lazy-src"):
            if tag.get(attr):
                tag["src"] = tag.get(attr)
                break
        
        # Extract from srcset if needed
        if not tag.get("src") and tag.get("srcset"):
            tag["src"] = tag["srcset"].split(",")[0].split()[0]

    def _process_web_images(self, section, base_url: str) -> List[Document]:
        """Process images from web page with OCR."""
        docs = []
        imgs = section.find_all("img")
        
        for img_tag in imgs:
            src = img_tag.get("src")
            if not src or src.startswith("data:"):
                continue
                
            full_url = urljoin(base_url, src)
            
            try:
                img_response = requests.get(full_url, timeout=10, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; ingest-bot/1.0)"
                })
                img_response.raise_for_status()

                # Skip large images
                if int(img_response.headers.get("Content-Length", 0)) > 8_000_000:
                    docs.append(Document(
                        page_content=f"[OCR skip: {full_url} - image too large]",
                        metadata={"source": base_url}
                    ))
                    continue

                elements_img = partition_image(
                    file=io.BytesIO(img_response.content),
                    include_metadata=True,
                    languages=["tha", "eng"],
                    strategy="ocr_only",
                )
                
                ocr_docs = self.elements_to_docs(elements_img, source=f"{base_url}#img:{full_url}")
                
                # Clean Thai text
                for doc in ocr_docs:
                    doc.page_content = clean_and_tokenize_thai(doc.page_content)
                    
                docs.extend(ocr_docs)
                
            except Exception as e:
                docs.append(Document(
                    page_content=f"[OCR fail: {full_url} - {e}]",
                    metadata={"source": base_url}
                ))
        
        return docs

    def load_documents_from_folders(self, folder_paths: List[str]) -> List[Document]:
        """Load documents from multiple folders."""
        import time
        
        docs: List[Document] = []
        
        for folder in folder_paths:
            if not os.path.exists(folder):
                print(f"Warning: Folder {folder} does not exist, skipping...")
                continue
                
            start = time.perf_counter()
            count_before = len(docs)

            print(f"--- Processing folder: {folder} ---")
            
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if not os.path.isfile(file_path):
                    continue
                    
                try:
                    docs.extend(self._load_file_by_extension(file_path))
                except Exception as e:
                    docs.append(Document(
                        page_content=f"[INGEST FAIL] {file_path}: {e}",
                        metadata={"source": file_path}
                    ))

            elapsed = time.perf_counter() - start
            count_added = len(docs) - count_before
            print(f"--- Completed folder: {folder} | {count_added} docs | {elapsed:.2f} sec ---")

        return docs

    def _load_file_by_extension(self, file_path: str) -> List[Document]:
        """Load file based on its extension."""
        filename = os.path.basename(file_path).lower()
        
        if filename.endswith(".pdf"):
            return self.load_pdf(file_path)
        elif filename.endswith(".docx"):
            return self.load_docx(file_path)
        elif filename.endswith(".pptx"):
            return self.load_pptx(file_path)
        elif filename.endswith(".xlsx"):
            return self.load_xlsx(file_path)
        elif filename.endswith(".csv"):
            return self.load_csv(file_path)
        elif filename.endswith((".jpg", ".jpeg", ".png", ".webp", ".tiff")):
            return self.load_image(file_path)
        elif filename.endswith((".txt", ".md")):
            return self.load_text(file_path)
        else:
            return []

    def process_documents_for_vector_store(self, docs: List[Document]) -> List[Document]:
        """Process documents for vector store by cleaning and splitting."""
        # Clean Thai text
        for doc in docs:
            doc.page_content = clean_thai_ocr(doc.page_content)

        # Separate table and text documents
        table_docs = []
        text_docs = []
        
        for doc in docs:
            if ("<table" in doc.page_content.lower() and 
                doc.metadata.get("category") == "Table"):
                table_docs.append(doc)  # Keep tables as single chunks
            else:
                text_docs.append(doc)

        # Split text documents
        splits = table_docs + self.text_splitter.split_documents(text_docs)
        
        return splits
