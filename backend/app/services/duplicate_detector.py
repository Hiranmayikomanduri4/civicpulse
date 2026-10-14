"""
Explainable Duplicate Issue Detection Service for CivicPulse AI.
Detects potential duplicate civic complaints using a composite score of:
1. Geographical proximity (Haversine distance)
2. Category match
3. Textual similarity (Token Jaccard & N-gram overlap)
"""
import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models import Report
from backend.app.utils.geo import calculate_haversine_distance, format_distance


def tokenize_text(text: str) -> set[str]:
    """Normalize and tokenize text into unique cleaned words, removing common stop words."""
    stop_words = {
        "the", "a", "an", "in", "on", "at", "of", "to", "for", "is", "are", 
        "and", "or", "it", "this", "that", "there", "with", "by", "from", "be"
    }
    words = re.findall(r"\b[a-zA-Z0-9]{3,}\b", text.lower())
    return {w for w in words if w not in stop_words}


def calculate_jaccard_similarity(set1: set[str], set2: set[str]) -> float:
    """Compute Jaccard similarity index between two token sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0


def find_potential_duplicates(
    db: Session,
    category: str,
    title: str,
    description: str,
    latitude: float,
    longitude: float,
    max_distance_meters: float = 300.0,
    similarity_threshold: float = 0.35,
    exclude_report_id: str = None
) -> List[Dict[str, Any]]:
    """
    Find potentially duplicate reports within geographical proximity 
    and matching text/category characteristics.
    Only checks active/unresolved issues (or recently resolved issues).
    """
    # Query candidate reports (not resolved or resolved in the past 14 days)
    query = db.query(Report).filter(Report.status.in_(["Reported", "Acknowledged", "In Progress"]))
    if exclude_report_id:
        query = query.filter(Report.id != exclude_report_id)
        
    candidates = query.all()
    duplicates = []
    
    input_tokens = tokenize_text(f"{title} {description}")

    for candidate in candidates:
        # 1. Geographic distance
        distance = calculate_haversine_distance(latitude, longitude, candidate.latitude, candidate.longitude)
        if distance > max_distance_meters:
            continue

        # Proximity score (1.0 at 0m, decaying to 0 at max_distance_meters)
        proximity_score = max(0.0, 1.0 - (distance / max_distance_meters))

        # 2. Category score
        category_score = 1.0 if candidate.category == category else 0.2

        # 3. Textual similarity
        candidate_tokens = tokenize_text(f"{candidate.title} {candidate.description}")
        text_similarity = calculate_jaccard_similarity(input_tokens, candidate_tokens)

        # Composite match score:
        # 45% Geo proximity + 30% Category + 25% Description
        composite_score = (
            (proximity_score * 0.45) +
            (category_score * 0.30) +
            (text_similarity * 0.25)
        )

        if composite_score >= similarity_threshold:
            duplicates.append({
                "id": candidate.id,
                "title": candidate.title,
                "category": candidate.category,
                "status": candidate.status,
                "priority": candidate.priority,
                "distance_meters": distance,
                "distance_formatted": format_distance(distance),
                "similarity_score": round(composite_score, 2),
                "similarity_percentage": int(composite_score * 100),
                "created_at": candidate.created_at,
                "image_url": candidate.image_url,
                "address": candidate.address
            })

    # Sort duplicates by highest similarity score first
    duplicates.sort(key=lambda x: x["similarity_score"], reverse=True)
    return duplicates
