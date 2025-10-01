"""Text processing utilities, especially for Thai language."""

import re
import unicodedata
from typing import List
import pythainlp
from pythainlp.tokenize import word_tokenize


def clean_thai_ocr(text: str) -> str:
    """Clean Thai OCR text by fixing common OCR errors and spacing issues.
    
    Args:
        text: Raw OCR text that may have spacing issues
        
    Returns:
        Cleaned text with proper Thai character spacing
    """
    # Normalize Unicode
    text = unicodedata.normalize("NFC", text)

    # Fix separated Thai characters (vowels, tone marks)
    # Join character + tone mark: ช า ระ → ชำระ
    text = re.sub(r'([ก-๙เแโใไ]{1})\s+([่-๋ัิุูำ])', r'\1\2', text)
    
    # Join leading vowel + consonant: เ ก า → เกา
    text = re.sub(r'([เแโใไ])\s+([ก-๙])', r'\1\2', text)
    
    # Join consecutive consonants: ก ร → กร
    text = re.sub(r'([ก-๙])\s+([ก-๙])', r'\1\2', text)

    # Common OCR word fixes (can be expanded)
    fixes = {
        # Add more common OCR mistakes here as needed
        # r'ช\s*า\s*ระ': 'ชำระ',
        # r'ท\s*า\s*การ': 'ทำการ',
    }
    
    for pattern, replacement in fixes.items():
        text = re.sub(pattern, replacement, flags=re.IGNORECASE)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def clean_and_tokenize_thai(text: str) -> str:
    """Clean and tokenize Thai text using PyThaiNLP.
    
    Args:
        text: Input text to tokenize
        
    Returns:
        Space-separated tokenized text
    """
    cleaned = clean_thai_ocr(text)
    tokens = word_tokenize(cleaned, keep_whitespace=False)
    return ' '.join(tokens)


def is_meaningful_text(text: str, min_length: int = 10) -> bool:
    """Check if text contains meaningful content.
    
    Args:
        text: Text to check
        min_length: Minimum length threshold
        
    Returns:
        True if text appears meaningful
    """
    if not text or len(text.strip()) < min_length:
        return False
    
    # Check if text is mostly special characters or numbers
    alpha_count = sum(1 for c in text if c.isalpha())
    return alpha_count > len(text) * 0.3  # At least 30% alphabetic characters
