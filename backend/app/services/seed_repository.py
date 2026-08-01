import logging
from pathlib import Path
from sqlalchemy.orm import Session

from app.db.models import DocumentRecord, RepositorySource
from app.services.rag_engine import index_document
from app.services.status_inference import infer_document_relationships

logger = logging.getLogger("seed_repository")
UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SEED_DOCUMENTS = [
    {
        "filename": "GR_HigherEdu_2023_Scholarship.pdf",
        "title": "Maharashtra Higher & Technical Education Scholarship Policy 2023",
        "document_number": "उच्चशिसं-२०२३/प्र.क्र.४५/माशि-१",
        "department": "उच्च व तंत्र शिक्षण विभाग",
        "category": "Resolution",
        "language": "mr",
        "issue_date": "15 मे 2023",
        "source_key": "gr_maharashtra",
        "content": (
            "महाराष्ट्र शासन\n"
            "उच्च व तंत्र शिक्षण विभाग\n"
            "शासन निर्णय क्रमांक: उच्चशिसं-२०२३/प्र.क्र.४५/माशि-१\n"
            "मंत्रालय विस्तार भवन, मुंबई - ४०००३२.\n"
            "दिनांक: १५ मे २०२३.\n\n"
            "विषय: राज्यातील व्यावसायिक अभ्यासक्रमाच्या विद्यार्थ्यांना राजर्षी छत्रपती शाहू महाराज शिक्षण शुल्क शिष्यवृत्ती योजना लागू करण्याबाबत.\n\n"
            "प्रस्तावना:\n"
            "राज्यातील आर्थिकदृष्ट्या दुर्बल घटकातील (EWS) विद्यार्थ्यांना उच्च व तंत्र शिक्षण घेताना आर्थिक अडचणींचा सामना करावा लागू नये यासाठी "
            "वार्षिक उत्पन्न मर्यादा रु. ८,००,०००/- (आठ लाख) पर्यंत असलेल्या विद्यार्थ्यांना ५०% शिक्षण शुल्क प्रतिपूर्ती देण्यात येत आहे.\n\n"
            "शासन निर्णय:\n"
            "१. राज्यातील सर्व शासकीय, शासन अनुदानित व विनाअनुदानित व्यावसायिक महाविद्यालयांमध्ये प्रवेश घेणाऱ्या पात्र विद्यार्थ्यांना शिक्षण शुल्क आणि परीक्षा शुल्काची ५०% रक्कम थेट डीबीटी (DBT) द्वारे अदा करण्यात येईल.\n"
            "२. पदव्युत्तर पदवी (PG) आणि अभियांत्रिकी (Degree Engineering) अभ्यासक्रमासाठी ७५% उपस्थिती अनिवार्य राहील.\n"
            "३. सदर योजनेसाठी आधार संलग्न बँक खाते असणे बंधनकारक आहे.\n"
            "४. सदर शासन निर्णय मागील परिपत्रक क्रमांक उच्चशिसं-२०१९/प्र.क्र.१२ मधील तरतुदींमध्ये सुधारणा करतो (Amends GR 2019/12).\n\n"
            "महाराष्ट्राचे राज्यपाल यांच्या आदेशानुसार व नावाने."
        ),
    },
    {
        "filename": "GR_Finance_2022_PensionRevision.pdf",
        "title": "Finance Department Pension & Revised Pay Scale Resolution",
        "document_number": "वित्तवि-२०२२/प्र.क्र.१०२/सेवा-४",
        "department": "वित्त विभाग",
        "category": "Resolution",
        "language": "mr",
        "issue_date": "10 नोव्हेंबर 2022",
        "source_key": "gr_maharashtra",
        "content": (
            "महाराष्ट्र शासन\n"
            "वित्त विभाग\n"
            "शासन निर्णय क्रमांक: वित्तवि-२०२२/प्र.क्र.१०२/सेवा-४\n"
            "मंत्रालय, मुंबई - ४०००३२.\n"
            "दिनांक: १० नोव्हेंबर २०२२.\n\n"
            "विषय: राज्य शासकीय कर्मचारी व निवृत्तीवेतनधारकांना ७ व्या वेतन आयोगानुसार महागाई भत्ता वाढ व सुधारीत निवृत्तीवेतन मंजुरी.\n\n"
            "शासन निर्णय:\n"
            "१. दिनांक १ जुलै २०२२ पासून राज्य शासकीय कर्मचारी व जिल्हा परिषद कर्मचाऱ्यांना महागाई भत्ता (Dearness Allowance) ३४% वरून ३८% करण्यात येत आहे.\n"
            "२. सेवानिवृत्त कर्मचाऱ्यांचे निवृत्तीवेतन (Pension) व कुटुंब निवृत्तीवेतन सुधारित वेतनश्रेणीनुसार तात्काळ लागू करण्यात यावे.\n"
            "३. सदर आदेश थकीत रकमेसह (Arrears) कर्मचाऱ्यांच्या खात्यात वर्ग करण्यात येतील.\n"
            "४. संदर्भ: यापूर्वीचा शासन निर्णय क्र. वित्तवि-२०१९/प्र.क्र.४४/सेवा-४ पूर्णपणे अधिक्रमित (Supersedes) करण्यात आला आहे.\n\n"
            "नावाने व आदेशानुसार."
        ),
    },
    {
        "filename": "DTE_Circular_2024_AdmissionGuidelines.pdf",
        "title": "Directorate of Technical Education Centralized Admission Process (CAP) Circular 2024",
        "document_number": "DTE/CAP-2024/CR-88",
        "department": "Directorate of Technical Education (DTE)",
        "category": "Circular",
        "language": "en",
        "issue_date": "20 January 2024",
        "source_key": "dte_maharashtra",
        "content": (
            "DIRECTORATE OF TECHNICAL EDUCATION, MAHARASHTRA STATE\n"
            "3, Mahapalika Marg, Post Box No. 1967, Mumbai 400001\n"
            "Circular Reference: DTE/CAP-2024/CR-88\n"
            "Date: 20th January 2024\n\n"
            "Subject: Mandatory Verification Guidelines for Engineering & Polytechnic Admission 2024-25.\n\n"
            "Key Directives:\n"
            "1. All Facilitation Centres (FC) must verify Caste Validity, Non-Creamy Layer (NCL), and EWS certificates online before finalizing Option Forms.\n"
            "2. Tuition Fee Waiver Scheme (TFWS) seats are capped at 5% of total sanctioned intake per branch.\n"
            "3. Candidates claiming fee concession under Rajarshi Chhatrapati Shahu Maharaj Scheme must produce income certificate issued after 1st April 2023.\n"
            "4. References DTE Circular DTE/CAP-2023/CR-12 for procedural compliance.\n\n"
            "By Order of Director, DTE Maharashtra."
        ),
    },
]


def seed_central_repository(db: Session) -> dict:
    """Seed central repository corpus if empty."""
    # Ensure source records exist
    sources_data = [
        {"source_key": "gr_maharashtra", "name": "Maharashtra GR Portal", "source_type": "portal", "base_url": "https://gr.maharashtra.gov.in"},
        {"source_key": "dte_maharashtra", "name": "DTE Maharashtra", "source_type": "portal", "base_url": "https://dte.maharashtra.gov.in"},
        {"source_key": "github_mahgrs", "name": "Maharashtra GRs (GitHub)", "source_type": "github", "base_url": "https://github.com/orgpedia/mahGRs"},
    ]

    for sdata in sources_data:
        existing_src = db.query(RepositorySource).filter(RepositorySource.source_key == sdata["source_key"]).first()
        if not existing_src:
            src = RepositorySource(
                source_key=sdata["source_key"],
                name=sdata["name"],
                source_type=sdata["source_type"],
                base_url=sdata["base_url"],
                auth_trusted=True,
                sync_status="active",
            )
            db.add(src)
    db.commit()

    existing_count = db.query(DocumentRecord).filter(DocumentRecord.is_repository_document == True).count()
    if existing_count > 0:
        return {"seeded_count": 0, "message": f"Central repository already populated ({existing_count} documents)."}

    seeded_records = []
    for item in SEED_DOCUMENTS:
        # Save sample file to disk
        file_path = UPLOAD_DIR / item["filename"]
        file_path.write_text(item["content"], encoding="utf-8")

        src = db.query(RepositorySource).filter(RepositorySource.source_key == item["source_key"]).first()
        record = DocumentRecord(
            filename=item["filename"],
            original_name=item["filename"],
            title=item["title"],
            content_type="text/plain",
            file_size=len(item["content"].encode("utf-8")),
            page_count=2,
            language=item["language"],
            text_preview=item["content"][:2000],
            department=item["department"],
            document_number=item["document_number"],
            category=item["category"],
            issue_date=item["issue_date"],
            status="active",
            is_repository_document=True,
            source_key=item["source_key"],
            source_id=src.id if src else None,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # Index document into FAISS with full page & document metadata
        page_tuples = [(1, item["content"][:1500]), (2, item["content"][1500:])]
        doc_meta = {
            "filename": record.filename,
            "document_number": record.document_number,
            "department": record.department,
            "category": record.category,
            "issue_date": record.issue_date,
        }
        index_document(item["content"], record.id, page_tuples=page_tuples, doc_meta=doc_meta)
        infer_document_relationships(record, item["content"], db)
        seeded_records.append(record.id)

    return {
        "seeded_count": len(seeded_records),
        "message": f"Successfully seeded central repository with {len(seeded_records)} policy documents.",
    }
