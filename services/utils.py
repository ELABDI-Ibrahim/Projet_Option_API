"""Utility functions for text processing and similarity."""

import re
from datetime import datetime

# =============================================================================
# LAZY LOADING - Models loaded only when needed
# =============================================================================

_tfidf_vectorizer = None


def _get_tfidf():
    """Lazy load TF-IDF vectorizer."""
    global _tfidf_vectorizer
    if _tfidf_vectorizer is None:
        from sklearn.feature_extraction.text import TfidfVectorizer
        _tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
    return _tfidf_vectorizer


# =============================================================================
# TEXT PROCESSING
# =============================================================================

def normalize_text(text: str) -> str:
    """Normalize text: lowercase, strip, remove extra spaces."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.lower().strip())


def clean_encoding(text: str) -> str:
    """Clean common encoding artifacts (mojibake)."""
    if not text:
        return ""
    replacements = [
        ("â€¢", "•"), ("Ã©", "é"), ("Ã¨", "è"), ("Ã ", "à"),
        ("Ã®", "î"), ("Ã‰", "É"), ("Â·", "·"), ("Ã§", "ç"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


# =============================================================================
# DATE HANDLING
# =============================================================================

def parse_date(date_str: str) -> datetime | None:
    """Parse date string. Returns current date for 'Present'."""
    if not date_str:
        return None
    
    date_str = date_str.strip()
    if date_str.lower() == "present":
        return datetime.now()
    
    formats = ["%b %Y", "%B %Y", "%Y", "%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def months_difference(date1: datetime, date2: datetime) -> int:
    """Absolute difference in months between two dates."""
    if not date1 or not date2:
        return 0
    return abs((date1.year - date2.year) * 12 + (date1.month - date2.month))


# =============================================================================
# SIMILARITY METHODS
# =============================================================================

def similarity_tfidf(text1: str, text2: str) -> float:
    """
    TF-IDF + Cosine Similarity.
    
    Fast, lightweight similarity based on word overlap and frequency.
    Perfect for comparing job descriptions, education details, etc.
    
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not text1 or not text2:
        return 0.0
    
    text1 = clean_encoding(text1)
    text2 = clean_encoding(text2)
    
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        vectorizer = _get_tfidf()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity)
    except Exception:
        return 0.0


def semantic_similarity(text1: str, text2: str) -> float:
    """
    Semantic similarity using TF-IDF + Cosine Similarity.
    
    Simple, fast, and effective for comparing text descriptions.
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score between 0.0 and 1.0
    
    Example:
        >>> semantic_similarity("Software Engineer at Google", "Engineer at Google Inc")
        0.85
    """
    return similarity_tfidf(text1, text2)