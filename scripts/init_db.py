from newsapp.database import engine, SessionLocal
from newsapp.models import Base, Template

def main():
    # Tabellen anlegen
    Base.metadata.create_all(bind=engine)

    # Beispiel-Template (nur wenn noch nicht vorhanden)
    db = SessionLocal()
    try:
        if not db.query(Template).filter(Template.name == "Six Payments – Focused").first():
            t = Template(
                name="Six Payments – Focused",
                urls_csv="https://www.six-group.com/de/products-services/banking-services/payment-standardization/standards/qr-bill.html, https://www.six-group.com/de/products-services/banking-services/payment-standardization.html",
                keywords_csv="QR-Rechnung, ISO20022, IBAN, SEPA, EBICS",
                persona="Du bist Experte für Zahlungsverkehr/Cash Management.",
                assignment="Analysiere nur, was belegt ist. Keine Firmenbeschreibungen. Fokussiere auf QR-Rechnung, ISO20022, SEPA, IBAN, EBICS, Schnittstellen/Spec-Changes.",
                output_types=["summary","changes","action","risk","page_analysis"],
                scoring_rules={"weights":{"high":3,"med":2,"low":1},"trusted_boost":3,"allowed_boost":1,"max_passages_per_url":8}
            )
            db.add(t)
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    main()
