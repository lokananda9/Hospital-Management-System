import os, django, random
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.dev")
django.setup()

from django.utils import timezone
from datetime import timedelta, date
from accounts.models import User
from doctors.models import Doctor
from patients.models import Patient
from appointments.models import Appointment
from prescriptions.models import Prescription, PrescriptionItem
from billing.models import Invoice
from medicines.models import Medicine, SystemSettings

# ── wipe everything except admin ──────────────────────────────
Invoice.objects.all().delete()
PrescriptionItem.objects.all().delete()
Prescription.objects.all().delete()
Appointment.objects.all().delete()
Doctor.objects.all().delete()
Patient.objects.all().delete()
User.objects.filter(is_superuser=False).delete()
print("Cleared old data")

# ── doctors ───────────────────────────────────────────────────
DOCTORS = [
    ("Dr. Priya Sharma",  "doctor@example.com",  "General Medicine", "MED001", 10, 500),
    ("Dr. Rahul Verma",   "doctor2@example.com", "Cardiology",       "MED002",  8, 600),
    ("Dr. Sneha Kapoor",  "doctor3@example.com", "Dermatology",      "MED003",  6, 450),
    ("Dr. Arjun Mehta",   "doctor4@example.com", "Orthopedics",      "MED004", 12, 700),
    ("Dr. Kavya Nair",    "doctor5@example.com", "Pediatrics",       "MED005",  5, 400),
]
doc_objs = []
for name, email, spec, lic, exp, fee in DOCTORS:
    u = User.objects.create_user(email=email, password="doctor123", full_name=name, role="DOCTOR")
    d = Doctor.objects.create(user=u, specialization=spec, license_number=lic,
                              years_experience=exp, consultation_fee=fee)
    doc_objs.append(d)
print(f"Created {len(doc_objs)} doctors")

# ── patients ──────────────────────────────────────────────────
PATIENTS = [
    ("Anita Patel",    "patient@example.com",  "1990-05-15", "FEMALE", "B+"),
    ("Rohan Gupta",    "patient2@example.com", "1985-08-22", "MALE",   "O+"),
    ("Meena Joshi",    "patient3@example.com", "1992-03-10", "FEMALE", "A+"),
    ("Kiran Singh",    "patient4@example.com", "1978-11-30", "MALE",   "AB+"),
    ("Sunita Reddy",   "patient5@example.com", "1995-07-18", "FEMALE", "B-"),
    ("Amit Kumar",     "patient6@example.com", "1988-01-25", "MALE",   "O-"),
    ("Divya Iyer",     "patient7@example.com", "2000-09-05", "FEMALE", "A-"),
    ("Prakash Tiwari", "patient8@example.com", "1975-12-14", "MALE",   "AB-"),
]
pat_objs = []
for name, email, dob, gender, blood in PATIENTS:
    u = User.objects.create_user(email=email, password="patient123", full_name=name, role="PATIENT")
    p = Patient.objects.create(user=u, date_of_birth=dob, gender=gender, blood_group=blood)
    pat_objs.append(p)
print(f"Created {len(pat_objs)} patients")

# ── medicines ─────────────────────────────────────────────────
Medicine.objects.all().delete()
MEDS_DATA = [
    ("Paracetamol 500mg",   "Acetaminophen",     "TABLET",   "GSK",          25,  5),
    ("Amoxicillin 250mg",   "Amoxicillin",       "CAPSULE",  "Cipla",        45, 12),
    ("Cetirizine 10mg",     "Cetirizine",        "TABLET",   "Sun Pharma",   15,  5),
    ("Azithromycin 500mg",  "Azithromycin",      "TABLET",   "Zydus",       120, 12),
    ("Omeprazole 20mg",     "Omeprazole",        "CAPSULE",  "Dr Reddy",     35, 12),
    ("Metformin 500mg",     "Metformin",         "TABLET",   "USV",          18,  5),
    ("Ibuprofen 400mg",     "Ibuprofen",         "TABLET",   "Cipla",        30, 12),
    ("Cough Syrup",         "Dextromethorphan",  "SYRUP",    "Dabur",        85, 18),
    ("Betadine Ointment",   "Povidone-Iodine",   "OINTMENT", "Win-Medicare", 65, 12),
    ("Eye Drops",           "Ofloxacin",         "DROPS",    "Alcon",        90, 12),
    ("Vitamin D3 1000IU",   "Cholecalciferol",   "TABLET",   "HealthKart",  150,  5),
    ("Insulin Injection",   "Insulin",           "INJECTION","Novo Nordisk", 450,  5),
    ("Salbutamol Inhaler",  "Salbutamol",        "INHALER",  "Cipla",       180, 12),
    ("Atorvastatin 10mg",   "Atorvastatin",      "TABLET",   "Ranbaxy",      55, 12),
    ("Aspirin 75mg",        "Aspirin",           "TABLET",   "Bayer",        20,  5),
]
med_objs = []
for name, gen, cat, mfg, price, tax in MEDS_DATA:
    m = Medicine.objects.create(name=name, generic_name=gen, category=cat,
                                manufacturer=mfg, price=price, tax_percent=tax)
    med_objs.append(m)
print(f"Created {len(med_objs)} medicines")

# ── system settings ───────────────────────────────────────────
s = SystemSettings.get_settings()
s.discount_percent = 5
s.save()

# ── appointments + prescriptions + invoices ───────────────────
DIAGNOSES = [
    ("Viral Fever", "Take rest and stay hydrated"),
    ("Hypertension", "Avoid salt, take medicines regularly"),
    ("Diabetes Type 2", "Monitor blood sugar daily"),
    ("Migraine", "Avoid bright light and noise"),
    ("Common Cold", "Steam inhalation, warm fluids"),
    ("Back Pain", "Physiotherapy recommended, avoid lifting"),
    ("Skin Allergy", "Avoid allergen, apply cream as directed"),
    ("Chest Infection", "Complete the full antibiotic course"),
    ("Stomach Infection", "Oral rehydration, bland diet"),
    ("Anxiety Disorder", "Breathing exercises, follow up in 2 weeks"),
    ("Knee Arthritis", "Low-impact exercise, weight management"),
    ("Asthma", "Carry inhaler always, avoid triggers"),
]

REASONS = [
    "Regular checkup", "Follow-up visit", "Severe headache",
    "Chest pain", "Fever and cough", "Joint pain",
    "Skin rash", "Stomach ache", "High BP monitoring", "Diabetes review",
]

DOSAGES = ["250mg", "500mg", "10mg", "5ml", "1 tablet", "2 tablets", "once daily dose"]
FREQUENCIES = ["Once daily", "Twice daily", "Thrice daily", "Every 8 hours", "SOS", "At bedtime"]

now = timezone.now()
appt_count = 0
rx_count = 0
inv_count = 0

# Create ~20 appointments spread across past 30 days
for i in range(22):
    doc = random.choice(doc_objs)
    pat = random.choice(pat_objs)
    diag, instr = random.choice(DIAGNOSES)
    reason = random.choice(REASONS)

    # Spread over last 30 days (some past, some upcoming)
    days_offset = random.randint(-25, 5)
    start = now + timedelta(days=days_offset, hours=random.randint(9, 17))
    end = start + timedelta(minutes=30)
    status = "COMPLETED" if days_offset < 0 else ("SCHEDULED" if days_offset > 0 else "COMPLETED")

    appt = Appointment.objects.create(
        doctor=doc, patient=pat,
        start_time=start, end_time=end,
        reason=reason, status=status,
    )
    appt_count += 1

    # Only completed appointments get prescriptions + invoices
    if status == "COMPLETED":
        # Create prescription
        rx = Prescription.objects.create(
            appointment=appt,
            diagnosis=diag,
            instructions=instr,
            created_by=doc.user,
        )
        rx_count += 1

        # Pick 2-3 random medicines for this prescription
        chosen_meds = random.sample(med_objs, random.randint(2, 3))
        med_total = Decimal("0")
        tax_total = Decimal("0")
        for med in chosen_meds:
            qty = random.randint(1, 3)
            dosage = random.choice(DOSAGES)
            freq = random.choice(FREQUENCIES)
            duration = random.randint(3, 10)
            PrescriptionItem.objects.create(
                prescription=rx,
                medicine=med,
                quantity=qty,
                dosage=dosage,
                frequency=freq,
                duration_days=duration,
                unit_price=med.price,
                tax_percent=med.tax_percent,
            )
            line_total = Decimal(str(med.price)) * qty
            line_tax = line_total * Decimal(str(med.tax_percent)) / 100
            med_total += line_total
            tax_total += line_tax

        # Create invoice
        consult_fee = Decimal(str(doc.consultation_fee))
        disc_pct = Decimal("5.00")
        subtotal = consult_fee + med_total + tax_total
        disc_amt = (subtotal * disc_pct / 100).quantize(Decimal("0.01"))
        total = subtotal - disc_amt

        inv_status = random.choice(["PAID", "PAID", "PENDING"])  # 2/3 paid
        inv = Invoice(
            appointment=appt,
            consultation_fee=consult_fee,
            medicine_total=med_total,
            tax=tax_total,
            discount_percent=disc_pct,
            discount_amount=disc_amt,
            total_amount=total,
            status=inv_status,
        )
        if inv_status == "PAID":
            inv.payment_method = random.choice(["UPI", "CARD", "CASH", "NET_BANKING"])
            inv.paid_at = start + timedelta(hours=random.randint(1, 24))
        inv.save()
        inv_count += 1

print(f"Created {appt_count} appointments")
print(f"Created {rx_count} prescriptions")
print(f"Created {inv_count} invoices")

# Summary
paid = Invoice.objects.filter(status="PAID").count()
pending = Invoice.objects.filter(status="PENDING").count()
from django.db.models import Sum
revenue = Invoice.objects.filter(status="PAID").aggregate(t=Sum("total_amount"))["t"] or 0
print(f"  PAID={paid}  PENDING={pending}  Revenue=Rs{revenue}")
print("DONE! Database is full.")
