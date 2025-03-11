import json
import os

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


class SentenceEmbeddingMatcher:
    def __init__(self, templates_dir=TEMPLATES_DIR):
        self.templates_dir = templates_dir

        # Load embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.templates = []
        self.filenames = []
        self._load_templates()

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
        """Finds the best matching template and returns the filename, or 'NOT FOUND' if none match."""
        if not self.index or not self.templates:
            return "NOT FOUND"

        user_embedding = self.model.encode([user_request])
        distances, I = self.index.search(np.array(user_embedding), 1)  # Get top match

        best_match_idx = I[0][0]
        best_distance = distances[0][0]  # FAISS returns squared L2 distance

        # Normalize distance into a similarity score (1 - min-max scaled L2)
        similarity_score = 1 / (1 + best_distance)

        if similarity_score < threshold:
            return "NOT FOUND"

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
