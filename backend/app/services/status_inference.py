import re
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.db.models import DocumentRecord, DocumentRelationship

logger = logging.getLogger("status_inference")

GR_NUM_PATTERNS = [
    r'(?:शासन\s+निर्णय\s+क्रमांक|क्र\.|क्रमांक|GR\s+No\.?|No\.?)\s*[:\-]?\s*([A-Za-z0-9\/\-\.अभिसकवतपफबभमयरलवशषसहणळज्ञ\s]{4,40})',
    r'([A-Z0-9]{2,10}\-[0-9]{4}\/[0-9]+\/[A-Z0-9\-]+)',
]


def extract_gr_metadata(text: str) -> Dict[str, Optional[str]]:
    """Extract document number, date, and department from document text preview."""
    if not text:
        return {"document_number": None, "issue_date": None, "department": None}

    doc_num = None
    for pattern in GR_NUM_PATTERNS:
        match = re.search(pattern, text[:2500])
        if match:
            extracted = match.group(1).strip()
            if len(extracted) > 3 and not extracted.startswith("http"):
                doc_num = extracted[:60]
                break

    date_match = re.search(
        r'(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4}|\d{1,2}\s+(?:जानेवारी|फेब्रुवारी|मार्च|एप्रिल|मे|जून|जुलै|ऑगस्ट|सप्टेंबर|ऑक्टोबर|नोव्हेंबर|डिसेंबर|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        text[:3000],
        re.IGNORECASE,
    )
    issue_date = date_match.group(1) if date_match else None

    dept_match = re.search(r'([^\n\r]+विभाग)', text[:1500])
    department = dept_match.group(1).strip()[:100] if dept_match else None

    return {
        "document_number": doc_num,
        "issue_date": issue_date,
        "department": department,
    }


def infer_document_relationships(doc: DocumentRecord, text: str, db: Session) -> List[DocumentRelationship]:
    """
    Scan text for references to existing database documents, create DocumentRelationship records,
    and update target document statuses if superseded/amended.
    """
    if not text:
        return []

    created_rels = []
    text_sample = text[:5000].lower()

    existing_docs = db.query(DocumentRecord).filter(DocumentRecord.id != doc.id).all()

    for other in existing_docs:
        match_found = False
        rel_type = "references"
        evidence = ""

        if other.document_number and len(other.document_number) > 3:
            num_clean = other.document_number.lower()
            if num_clean in text_sample:
                match_found = True
                evidence = f"Text references GR number '{other.document_number}'"

        if not match_found and other.original_name and len(other.original_name) > 6:
            base_name = other.original_name.rsplit('.', 1)[0].lower()
            if len(base_name) > 5 and base_name in text_sample:
                match_found = True
                evidence = f"Text references document '{other.original_name}'"

        if match_found:
            if "रद्द" in text_sample or "supersed" in text_sample or "अधिक्रमण" in text_sample:
                rel_type = "supersedes"
            elif "सुधारणा" in text_sample or "amend" in text_sample or "सुधारित" in text_sample:
                rel_type = "amends"

            existing_rel = (
                db.query(DocumentRelationship)
                .filter(
                    DocumentRelationship.source_document_id == doc.id,
                    DocumentRelationship.target_document_id == other.id,
                    DocumentRelationship.relation_type == rel_type,
                )
                .first()
            )

            if not existing_rel:
                rel = DocumentRelationship(
                    source_document_id=doc.id,
                    target_document_id=other.id,
                    relation_type=rel_type,
                    evidence_text=evidence,
                )
                db.add(rel)
                created_rels.append(rel)

                if rel_type == "supersedes" and other.status != "superseded":
                    other.status = "superseded"
                    other.status_reason = f"Superseded by Document #{doc.id} ({doc.original_name or doc.filename})"
                    logger.info("Auto-updated Doc #%d status to 'superseded'", other.id)
                elif rel_type == "amends" and other.status == "active":
                    other.status = "amended"
                    other.status_reason = f"Amended by Document #{doc.id} ({doc.original_name or doc.filename})"
                    logger.info("Auto-updated Doc #%d status to 'amended'", other.id)

    if created_rels:
        db.commit()

    return created_rels
