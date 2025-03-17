# app/services/template_selector.py

import spacy
from rapidfuzz import fuzz, process
from spacy.lang.en.stop_words import STOP_WORDS

# Load spaCy model (using a lightweight model)
nlp = spacy.load("en_core_web_sm")

# List of domain-specific filler phrases to remove
FILLER_PHRASES = [
    "synthetic data",
    "synth data",
    "mock data",
    "test data",
    "dummy data",
    "simulated data",
    "fabricated data",
    "artificial data",
    "generated data",
    "sample data",
    "synthetic records",
    "mock records",
    "test records",
    "dummy records",
    "simulated records",
    "fabricated records",
    "artificial records",
    "generated records",
    "fake data",
    "fake records",
    "data for testing",
    "data for simulation",
    "data for mockup",
    "data for example",
    "synthetic information",
    "mock information",
    "test information",
    "dummy information",
    "simulated information",
    "fabricated information",
    "artificial information",
    "generated information",
    "policy",
    "data",
    "records",
]


# Mapping of canonical template keys to descriptive category strings.
# This mapping can be updated regularly with domain-specific synonyms.
TEMPLATE_CANDIDATES = {}


def normalize_text(text: str) -> str:
    """
    Normalize text by:
      1. Lowercasing, removing punctuation, and filtering out stopwords.
      2. Removing filler phrases.
      3. Lemmatizing the text.
    """
    # Step 1: Lowercase, remove punctuation, and filter out stopwords.
    doc = nlp(text.lower())
    filtered_tokens = [
        token.text for token in doc if token.is_alpha and token.text not in STOP_WORDS
    ]
    filtered_text = " ".join(filtered_tokens)

    # Step 2: Remove filler phrases.
    filtered_text = remove_filler_phrases(filtered_text)

    # Step 3: Lemmatize the text.
    doc2 = nlp(filtered_text)
    lemmatized_tokens = [token.lemma_ for token in doc2 if token.is_alpha]
    return " ".join(lemmatized_tokens)


def extract_key_phrase(text: str) -> str:
    """
    Extract key noun chunks from the text after removing stopwords, punctuation and domain-specific filler phrases.
    This function normalizes the text, filters out common filler words, and then extracts the
    most domain-relevant noun chunk.
    """

    # Normalize text
    normalized = normalize_text(text)

    # Process the cleaned text to extract noun chunks
    doc_clean = nlp(normalized)
    noun_chunks = [
        chunk.text for chunk in doc_clean.noun_chunks if len(chunk.text.split()) > 1
    ]

    # Heuristic: choose the longest noun chunk as the key phrase
    if noun_chunks:
        key_phrase = max(noun_chunks, key=len)
        return remove_filler_phrases(key_phrase)
    # Fallback: if no noun chunks are found, return the cleaned text
    return remove_filler_phrases(normalized)


def remove_filler_phrases(text: str) -> str:
    """
    Remove common filler phrases from the text.
    """
    for phrase in FILLER_PHRASES:
        text = text.replace(phrase, "")
    return text


def select_template_rule_based(user_request: str, threshold: float = 85.0) -> str:
    """
    Select the appropriate template based on fuzzy matching of the normalized user request
    against a set of predefined category descriptions.

    Parameters:
      - user_request: The free-form natural language input from the user.
      - threshold: A similarity threshold (0-100) above which a match is considered acceptable.

    Returns:
      - The key for the selected template (e.g., "TFSA") or a default ("Life") if no match is confident.
    """
    normalized_request = extract_key_phrase(user_request)

    # Flatten the list of candidates since each value in TEMPLATE_CANDIDATES is a list of strings
    candidate_list = [
        desc for sublist in TEMPLATE_CANDIDATES.values() for desc in sublist
    ]

    # Use RapidFuzz to get the best matching candidate
    best_match, score, _ = process.extractOne(
        normalized_request, candidate_list, scorer=fuzz.token_sort_ratio
    )

    if score >= threshold:
        # Find the canonical key that maps to the best match
        for key, value_list in TEMPLATE_CANDIDATES.items():
            if best_match in value_list:
                return key
    # Fallback to a default template if none meets the threshold
    return "NOT_FOUND"


# Example usage:
if __name__ == "__main__":
    test_requests = [
        "Generate synthetic data for a tax free saving account",
        "I need data for a health insurance policy",
        "Produce synthetic records for dental insurances",
        "Mock data for TFSA",
        "Data generation for retirement savings",
        "Create data for a claim submission process",
        "Synthetic data for business owner insurance",
        "Generate records for critical illness coverage",
        "Mock data for disability insurance",
        "Data generation for life insurance policies",
        "Produce synthetic data for long-term care insurance",
        "Create mock records for mortgage protection",
        "Synthetic data for personal health insurance",
        "Generate data for travel insurance policies",
        "Mock data for a first home savings account",
        "Data generation for life income fund",
        "Produce synthetic records for locked-in retirement accounts",
        "Create data for registered education savings plans",
        "Synthetic data for registered retirement income funds",
        "Generate mock data for registered retirement savings plans",
        "Data generation for tax-free savings accounts",
        "I need synthetic data for a critical illness plan",
        "Produce mock records for a dental plan",
        "Create data for a disability coverage policy",
        "Generate synthetic data for a life protection plan",
        "Mock data for elder care insurance",
        "Data generation for home loan protection",
        "Synthetic data for individual health plans",
        "Produce records for trip protection insurance",
        "Create mock data for a first-time home buyer savings account",
        "Generate data for a retirement income fund",
        "Synthetic data for a pension income fund",
        "Mock data for a child education fund",
        "Data generation for a pension fund",
        "Produce synthetic records for a tax-free investment account",
    ]

    for req in test_requests:
        selected_template = select_template_rule_based(req)
        print(f"User Request: '{req}' => Selected Template: {selected_template}")
