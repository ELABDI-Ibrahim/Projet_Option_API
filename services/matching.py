"""Simple TF-IDF matching utilities for experience and education."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from services.utils import normalize_text


def tfidf_match(text1: str, text2: str) -> int:
    """
    Match texts using TF-IDF + Cosine Similarity.
    
    Args:
        text1: First text to compare
        text2: Second text to compare
    
    Returns:
        Match score 0-100
    """
    if not text1 or not text2:
        return 0
    
    text1 = normalize_text(text1)
    text2 = normalize_text(text2)
    
    if not text1 or not text2:
        return 0
    
    try:
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),  # Use unigrams and bigrams
            max_features=100
        )
        
        # Fit and transform both texts
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Convert to 0-100 scale
        return int(similarity * 100)
    
    except Exception:
        # Fallback to simple word overlap if TF-IDF fails
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return int((intersection / union) * 100) if union > 0 else 0


def fuzzy_company_match(company1: str, company2: str) -> int:
    """
    Match company names using TF-IDF.
    Handles abbreviations, extra words, etc.
    
    Returns:
        Match score 0-100
    """
    return tfidf_match(company1, company2)


def fuzzy_title_match(title1: str, title2: str) -> int:
    """
    Match job titles using TF-IDF.
    
    Returns:
        Match score 0-100
    """
    return tfidf_match(title1, title2)


def find_matching_experience(target_exp: dict, experiences: list) -> dict:
    """
    Find the best matching experience from a list.
    
    Args:
        target_exp: Experience to match
        experiences: List of experiences to search
        
    Returns:
        Best matching experience or None
    """
    if not experiences:
        return None
    
    best_match = None
    best_score = 0
    
    target_company = target_exp.get("institution_name", "")
    target_title = target_exp.get("position_title", "")
    
    for exp in experiences:
        exp_company = exp.get("institution_name", "")
        exp_title = exp.get("position_title", "")
        
        # Calculate combined score
        company_score = fuzzy_company_match(target_company, exp_company)
        title_score = fuzzy_title_match(target_title, exp_title)
        
        # Weighted average (company is more important)
        combined_score = (company_score * 0.6) + (title_score * 0.4)
        
        if combined_score > best_score:
            best_score = combined_score
            best_match = exp
    
    # Only return if score is above threshold
    return best_match if best_score >= 50 else None