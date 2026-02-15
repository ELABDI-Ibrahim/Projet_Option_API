from langdetect import detect
from sentence_transformers import SentenceTransformer, util

# Load a multilingual sentence embedding model
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

def detect_language(text):
    lang = detect(text)
    if lang == 'fr':
        return 'french'
    elif lang == 'en':
        return 'english'
    else:
        return 'other'

def semantic_similarity(sent1, sent2):
    lang1 = detect_language(sent1)
    lang2 = detect_language(sent2)

    print(f"Sentence 1 detected as: {lang1}")
    print(f"Sentence 2 detected as: {lang2}")

    if lang1 == lang2:
        print("Both sentences are in the same language — expected cross‑language input.")
        return None

    # Encode both sentences into embeddings
    emb1 = model.encode(sent1, convert_to_tensor=True)
    emb2 = model.encode(sent2, convert_to_tensor=True)

    # Compute cosine similarity
    similarity = util.cos_sim(emb1, emb2)
    return float(similarity)

# Example usage
french_sentence = "Collaboration avec les équipes commerciales pour traduire les besoins."
english_sentence = "Collaborated with business teams to translate needs."

sim = semantic_similarity(french_sentence, english_sentence)
print(f"Semantic similarity: {sim:.4f}")
