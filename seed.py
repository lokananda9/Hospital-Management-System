import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.prod")
django.setup()

from accounts.models import User
from doctors.models import Doctor
from patients.models import Patient
from medicines.models import Medicine, SystemSettings


def seed():
    print("--- Seeding database ---")

    # --- Users ---
    if not User.objects.filter(email="admin@example.com").exists():
        admin = User.objects.create_superuser(
            email="admin@example.com", password="admin123",
            full_name="Admin User", role="ADMIN"
        )
        print(f"  Created admin: {admin.email}")
    else:
        print("  Admin already exists")

    if not User.objects.filter(email="doctor@example.com").exists():
        doc_user = User.objects.create_user(
            email="doctor@example.com", password="doctor123",
            full_name="Dr. Priya Sharma", role="DOCTOR"
        )
        Doctor.objects.create(
            user=doc_user, specialization="General Medicine",
            license_number="MED001", years_experience=10, consultation_fee=500
        )
        print(f"  Created doctor: {doc_user.email}")
    else:
        print("  Doctor already exists")

    if not User.objects.filter(email="doctor2@example.com").exists():
        doc_user2 = User.objects.create_user(
            email="doctor2@example.com", password="doctor123",
            full_name="Dr. Rahul Verma", role="DOCTOR"
        )
        Doctor.objects.create(
            user=doc_user2, specialization="Cardiology",
            license_number="MED002", years_experience=8, consultation_fee=600
        )
        print(f"  Created doctor: {doc_user2.email}")
    else:
        print("  Doctor2 already exists")

    if not User.objects.filter(email="patient@example.com").exists():
        pat_user = User.objects.create_user(
            email="patient@example.com", password="patient123",
            full_name="Anita Patel", role="PATIENT"
        )
        Patient.objects.create(user=pat_user)
        print(f"  Created patient: {pat_user.email}")
    else:
        print("  Patient already exists")

    # --- Medicines ---
    meds = [
        ("Paracetamol 500mg", "Acetaminophen", "TABLET", "GSK", 25, 5),
        ("Amoxicillin 250mg", "Amoxicillin", "CAPSULE", "Cipla", 45, 12),
        ("Cetirizine 10mg", "Cetirizine", "TABLET", "Sun Pharma", 15, 5),
        ("Azithromycin 500mg", "Azithromycin", "TABLET", "Zydus", 120, 12),
        ("Omeprazole 20mg", "Omeprazole", "CAPSULE", "Dr Reddy", 35, 12),
        ("Metformin 500mg", "Metformin", "TABLET", "USV", 18, 5),
        ("Ibuprofen 400mg", "Ibuprofen", "TABLET", "Cipla", 30, 12),
        ("Cough Syrup", "Dextromethorphan", "SYRUP", "Dabur", 85, 18),
        ("Betadine Ointment", "Povidone-Iodine", "OINTMENT", "Win-Medicare", 65, 12),
        ("Eye Drops", "Ofloxacin", "DROPS", "Alcon", 90, 12),
    ]
    created = 0
    for name, gen, cat, mfg, price, tax in meds:
        _, c = Medicine.objects.get_or_create(
            name=name,
            defaults={"generic_name": gen, "category": cat, "manufacturer": mfg, "price": price, "tax_percent": tax},
        )
        if c:
            created += 1
    print(f"  Medicines: {created} created, {Medicine.objects.count()} total")

    # --- Default discount ---
    s = SystemSettings.get_settings()
    if s.discount_percent == 0:
        s.discount_percent = 5
        s.save()
        print("  Set default discount to 5%")

    print("Seed complete!")


if __name__ == "__main__":
    seed()
