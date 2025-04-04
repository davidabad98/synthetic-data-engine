import json
import logging
import re
from typing import Any, Dict, List, Optional

import spacy
from rapidfuzz import fuzz, process
from spacy.lang.en.stop_words import STOP_WORDS

from app.services.open_search import get_best_matching_schema
from app.services.sentence_embeddings import SentenceEmbeddingMatcher
from app.utils.template_loader import load_template_mappings
from config.config import (
    DEFAULT_FORMAT,
    DEFAULT_RECORD_COUNT,
    FILLER_PHRASES,
    OPEN_SEARCH,
    SUPPORTED_FORMATS,
)

logger = logging.getLogger(__name__)


class PromptProcessor:
    """
    Processes natural language prompts for synthetic data generation.
    Extracts parameters and identifies the appropriate template.
    """

    def __init__(self, template_matcher: SentenceEmbeddingMatcher):
        """
        Initialize the processor with template matching functionality.

        Args:
            template_matcher: An object with a match_template method that finds the
                             appropriate template based on the query.
        """
        self.nlp = spacy.load("en_core_web_sm")
        self.template_matcher = template_matcher

        # Mapping of canonical template keys to descriptive category strings.
        # The mapping can be updated regularly with domain-specific synonyms in the templates.
        self.template_mappings = load_template_mappings()

        # Patterns for extraction
        self.record_count_patterns = [
            r"(\d+)\s+(?:record|records|rows?|entries?)",
            r"(?:generate|create|produce)\s+(\d+)",
            r"(?:set of|total of|about)\s+(\d+)",
        ]

        # Words to numbers mapping for text numbers
        self.word_to_number = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
            "twenty": 20,
            "twenty-five": 25,
            "thirty": 30,
            "thirty-five": 35,
            "forty": 40,
            "forty-five": 45,
            "fifty": 50,
            "fifty-five": 55,
            "sixty": 60,
            "sixty-five": 65,
            "seventy": 70,
            "seventy-five": 75,
            "eighty": 80,
            "eighty-five": 85,
            "ninety": 90,
            "ninety-five": 95,
            "hundred": 100,
            "thousand": 1000,
        }

    def process(self, user_input: str) -> Dict[str, Any]:
        """
        Process the user input and extract parameters.

        Args:
            user_input: The natural language prompt from the user.

        Returns:
            Dict containing extracted parameters and template information.
        """
        # Start with original input for reference
        original_input = user_input

        # Basic normalization
        normalized_input = user_input.strip()

        # Extract parameters
        record_count = self._extract_record_count(normalized_input)
        data_format = self._extract_data_format(normalized_input)
        template_success = True

        # Find matching template
        try:
            if OPEN_SEARCH:
                # Use OpenSearch for template selection
                schema, schema_name = get_best_matching_schema(user_input)

                if schema is None:
                    logger.error("No matching schema found using OpenSearch.")
                    template_name = "NOT_FOUND"
                    template_success = False
                else:
                    template_name = json.dumps(schema)
            else:
                # Use NLP for template selection
                if self.template_mappings == "NOT_FOUND":
                    logger.error("Unable to load template mappings")
                    template_name = "NOT_FOUND"
                    template_success = False

                if template_success:
                    # Step 1: Rule-Based Template Selection
                    template_name = self._select_template_rule_based(user_input)
                    if template_name == "NOT_FOUND":
                        # Step 2: Embedding-Based Template Selection
                        template_name = self.template_matcher.match_template(user_input)
                        if template_name == "NOT_FOUND":
                            # No template found by either method
                            template_name = "NOT_FOUND"
                            template_success = False

        except Exception as e:
            logger.error(f"Template matching error: {str(e)}")
            template_name = None
            template_success = False

        # Prepare result
        result = {
            "original_input": original_input,
            "record_count": record_count,
            "data_format": data_format,
            "template": template_name if template_name else None,
            "error": None,
        }

        # Handle case where no template is found
        if template_name is None or template_name == "NOT_FOUND":
            if not template_success:
                result["error"] = "Template matching system error."
            else:
                result["error"] = "No matching template found."

        # Log the processing results
        logger.info(f"Processed request: {result}")

        return result

    def _extract_record_count(self, text: str) -> int:
        """Extract the number of records requested."""
        # Check for numeric patterns
        for pattern in self.record_count_patterns:
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches:
                return int(matches.group(1))

        # Check for text number representations
        words = text.lower().split()
        for i, word in enumerate(words):
            if word in self.word_to_number:
                # Check if this word is actually referring to records
                context_words = ["record", "records", "entries", "rows", "examples"]
                if i < len(words) - 1 and any(
                    cw in words[i + 1] for cw in context_words
                ):
                    return self.word_to_number[word]

        return DEFAULT_RECORD_COUNT

    def _extract_data_format(self, text: str) -> str:
        """Extract the requested data format."""
        text_upper = text.upper()
        for fmt in SUPPORTED_FORMATS:
            if fmt in text_upper:
                return fmt

        return DEFAULT_FORMAT

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text by:
        1. Lowercasing, removing punctuation, and filtering out stopwords.
        2. Removing filler phrases.
        3. Lemmatizing the text.
        """
        # Step 1: Lowercase, remove punctuation, and filter out stopwords.
        doc = self.nlp(text.lower())
        filtered_tokens = [
            token.text
            for token in doc
            if token.is_alpha and token.text not in STOP_WORDS
        ]
        filtered_text = " ".join(filtered_tokens)

        # Step 2: Remove filler phrases.
        filtered_text = self._remove_filler_phrases(filtered_text)

        # Step 3: Lemmatize the text.
        doc2 = self.nlp(filtered_text)
        lemmatized_tokens = [token.lemma_ for token in doc2 if token.is_alpha]
        return " ".join(lemmatized_tokens)

    def _remove_filler_phrases(self, text: str) -> str:
        """
        Remove common filler phrases from the text.
        """
        for phrase in FILLER_PHRASES:
            text = text.replace(phrase, "")
        return text

    def _extract_key_phrase(self, text: str) -> str:
        """
        Extract key noun chunks from the text after removing stopwords, punctuation and domain-specific filler phrases.
        This function normalizes the text, filters out common filler words, and then extracts the
        most domain-relevant noun chunk.
        """

        # Normalize text
        normalized = self._normalize_text(text)

        # Process the cleaned text to extract noun chunks
        doc_clean = self.nlp(normalized)
        noun_chunks = [
            chunk.text for chunk in doc_clean.noun_chunks if len(chunk.text.split()) > 1
        ]

        # Heuristic: choose the longest noun chunk as the key phrase
        if noun_chunks:
            key_phrase = max(noun_chunks, key=len)
            return self._remove_filler_phrases(key_phrase)
        # Fallback: if no noun chunks are found, return the cleaned text
        return self._remove_filler_phrases(normalized)

    def _select_template_rule_based(
        self, user_request: str, threshold: float = 85.0
    ) -> str:
        """
        Select the appropriate template based on fuzzy matching of the normalized user request
        against a set of predefined category descriptions.

        Parameters:
        - user_request: The free-form natural language input from the user.
        - threshold: A similarity threshold (0-100) above which a match is considered acceptable.

        Returns:
        - The key for the selected template (e.g., "TFSA") or a default ("Life") if no match is confident.
        """
        normalized_request = self._extract_key_phrase(user_request)

        # Flatten the list of candidates since each value in TEMPLATE_CANDIDATES is a list of strings
        candidate_list = [
            desc for sublist in self.template_mappings.values() for desc in sublist
        ]

        # Use RapidFuzz to get the best matching candidate
        best_match, score, _ = process.extractOne(
            normalized_request, candidate_list, scorer=fuzz.token_sort_ratio
        )

        if score >= threshold:
            # Find the canonical key that maps to the best match
            for key, value_list in self.template_mappings.items():
                if best_match in value_list:
                    return key
        # Fallback to a default template if none meets the threshold
        return "NOT_FOUND"
