import numpy as np
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models import MemoryEntry

class SemanticMemoryManager:
    def __init__(self, embedding_dimension: int = 1536):
        self.dimension = embedding_dimension

    def _generate_mock_embedding(self, text: str) -> List[float]:
        np.random.seed(abs(hash(text)) % (2**32))
        vec = np.random.randn(self.dimension)
        vec = vec / np.linalg.norm(vec)
        return vec.tolist()

    def get_embedding(self, text: str) -> List[float]:
        return self._generate_mock_embedding(text)

    def add_memory(self, db: Session, content: str, category: str = "general") -> MemoryEntry:
        embedding = self.get_embedding(content)
        memory = MemoryEntry(
            content=content,
            embedding=embedding,
            category=category
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    def search_memories(self, db: Session, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_embedding = np.array(self.get_embedding(query))
        all_memories = db.query(MemoryEntry).all()

        results = []
        for memory in all_memories:
            mem_embedding = np.array(memory.embedding)
            dot_product = np.dot(query_embedding, mem_embedding)
            norm_q = np.linalg.norm(query_embedding)
            norm_m = np.linalg.norm(mem_embedding)
            similarity = float(dot_product / (norm_q * norm_m)) if norm_q > 0 and norm_m > 0 else 0.0

            results.append({
                "id": memory.id,
                "content": memory.content,
                "category": memory.category,
                "similarity": similarity,
                "created_at": memory.created_at.isoformat()
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]

memory_manager = SemanticMemoryManager()
