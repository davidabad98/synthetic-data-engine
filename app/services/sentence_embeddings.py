import json
import os

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config.config import OPEN_SEARCH

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
FAISS_PATH = os.path.join(os.path.dirname(__file__), "..", "data/faiss")
INDEX_PATH = os.path.join(FAISS_PATH, "persisted_index.index")
METADATA_PATH = os.path.join(FAISS_PATH, "metadata.json")


class SentenceEmbeddingMatcher:
    def __init__(
        self,
        templates_dir=TEMPLATES_DIR,
        index_path=INDEX_PATH,
        metadata_path=METADATA_PATH,
    ):
        self.templates_dir = templates_dir
        self.index_path = index_path
        self.metadata_path = metadata_path

        # Load embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.templates = []
        self.filenames = []

        # Initialize by loading a persisted index if available; otherwise build it.
        if not OPEN_SEARCH:
            self._init_index()

    def _init_index(self):
        """Checks for persisted index and metadata. Loads them if available; otherwise, build and save."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            # Load persisted FAISS index
            self.index = faiss.read_index(self.index_path)
            # Load associated metadata
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                self.filenames = metadata.get("filenames", [])
                self.templates = metadata.get("templates", [])
        else:
            # Build the index since persisted data doesn't exist
            self._load_templates()

            # Creates dir if it doesn't exist
            os.makedirs(FAISS_PATH, exist_ok=True)

            # Persist the FAISS index
            if self.index is not None:
                faiss.write_index(self.index, self.index_path)
            # Save metadata (template filenames and content)
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump({"filenames": self.filenames, "templates": self.templates}, f)

    def _load_templates(self):
        """Loads JSON templates, extracts descriptions, and builds FAISS index."""
        template_files = [
            f for f in os.listdir(self.templates_dir) if f.endswith(".json")
        ]

        descriptions = []
        for filename in template_files:
            with open(
                os.path.join(self.templates_dir, filename), "r", encoding="utf-8"
            ) as f:
                template = json.load(f)
                if "description" in template:
                    self.templates.append(template)
                    self.filenames.append(filename)
                    descriptions.append(template["description"])

        if descriptions:
            # Convert descriptions to embeddings
            embeddings = self.model.encode(descriptions)

            # Store embeddings in FAISS
            embedding_dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(embedding_dim)
            self.index.add(np.array(embeddings))

    def match_template(self, user_request, threshold=0.40):
        """
        Finds the best matching template based on the user request.
        Computes the embedding for the user input, queries the persisted index,
        and returns the filename if the similarity score meets the threshold;
        otherwise, returns "NOT_FOUND".
        """
        if not self.index or not self.templates:
            return "NOT_FOUND"

        # Encode user request
        user_embedding = self.model.encode([user_request])
        distances, I = self.index.search(np.array(user_embedding), 1)  # Get top match

        best_match_idx = I[0][0]
        best_distance = distances[0][0]  # FAISS returns squared L2 distance

        # Normalize distance into a similarity score (1 - min-max scaled L2)
        similarity_score = 1 / (1 + best_distance)

        if similarity_score < threshold:
            return "NOT_FOUND"

        return self.filenames[best_match_idx]


# Example usage
if __name__ == "__main__":

    # Initialize matcher (loads and builds embeddings on first call)
    matcher = SentenceEmbeddingMatcher()

    # Example user request
    test_requests = [
        "burgers and fries i want to buy",
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
        # Get the matched template filename
        matched_template = matcher.match_template(req)
        print(f"User Request: '{req}' => Selected Template: {matched_template}")
