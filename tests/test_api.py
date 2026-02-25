from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from appointments.models import Appointment
from billing.models import Invoice
from doctors.models import Doctor
from patients.models import Patient

User = get_user_model()


class HospitalAPITestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="adminpass123",
            full_name="Admin User",
            role=User.Role.ADMIN,
            is_staff=True,
        )
        self.doctor_user = User.objects.create_user(
            email="doctor@example.com",
            password="doctorpass123",
            full_name="Doctor User",
            role=User.Role.DOCTOR,
        )
        self.patient_user = User.objects.create_user(
            email="patient@example.com",
            password="patientpass123",
            full_name="Patient User",
            role=User.Role.PATIENT,
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialization="Cardiology",
            license_number="LIC-001",
            years_experience=8,
            consultation_fee=500,
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            blood_group="O+",
            emergency_contact="9999999999",
        )

    def auth(self, email, password):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return response.data

    def test_auth_login_refresh_me(self):
        token_data = self.auth("admin@example.com", "adminpass123")
        me_response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.data["email"], "admin@example.com")

        refresh_response = self.client.post("/api/v1/auth/refresh/", {"refresh": token_data["refresh"]}, format="json")
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn("access", refresh_response.data)

    def test_admin_creates_doctor_and_patient(self):
        self.auth("admin@example.com", "adminpass123")

        new_doctor_user = self.client.post(
            "/api/v1/users/",
            {
                "email": "doctor2@example.com",
                "password": "doctor2pass123",
                "full_name": "Doctor Two",
                "role": "DOCTOR",
            },
            format="json",
        )
        self.assertEqual(new_doctor_user.status_code, 201, new_doctor_user.data)

        doctor_profile = self.client.post(
            "/api/v1/doctors/",
            {
                "user": new_doctor_user.data["id"],
                "specialization": "Neurology",
                "license_number": "LIC-002",
                "years_experience": 5,
                "consultation_fee": "750.00",
            },
            format="json",
        )
        self.assertEqual(doctor_profile.status_code, 201, doctor_profile.data)

        new_patient_user = self.client.post(
            "/api/v1/users/",
            {
                "email": "patient2@example.com",
                "password": "patient2pass123",
                "full_name": "Patient Two",
                "role": "PATIENT",
            },
            format="json",
        )
        self.assertEqual(new_patient_user.status_code, 201, new_patient_user.data)

        patient_profile = self.client.post(
            "/api/v1/patients/",
            {
                "user": new_patient_user.data["id"],
                "blood_group": "A+",
                "emergency_contact": "8888888888",
            },
            format="json",
        )
        self.assertEqual(patient_profile.status_code, 201, patient_profile.data)

    def test_patient_books_appointment_and_overlap_rejected(self):
        self.auth("patient@example.com", "patientpass123")
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(minutes=30)

        first = self.client.post(
            "/api/v1/appointments/",
            {
                "doctor": self.doctor.id,
                "patient": self.patient.id,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "reason": "Consultation",
            },
            format="json",
        )
        self.assertEqual(first.status_code, 201, first.data)

        overlapping = self.client.post(
            "/api/v1/appointments/",
            {
                "doctor": self.doctor.id,
                "patient": self.patient.id,
                "start_time": (start + timedelta(minutes=10)).isoformat(),
                "end_time": (end + timedelta(minutes=10)).isoformat(),
                "reason": "Overlap check",
            },
            format="json",
        )
        self.assertEqual(overlapping.status_code, 400)

    def test_doctor_completes_appointment_and_creates_prescription(self):
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=30),
            reason="Follow up",
        )

        self.auth("doctor@example.com", "doctorpass123")
        status_update = self.client.patch(
            f"/api/v1/appointments/{appointment.id}/status/",
            {"status": "COMPLETED"},
            format="json",
        )
        self.assertEqual(status_update.status_code, 200, status_update.data)

        prescription = self.client.post(
            "/api/v1/prescriptions/",
            {
                "appointment": appointment.id,
                "diagnosis": "Hypertension",
                "medicines_json": [{"name": "MedA", "dose": "1/day"}],
                "instructions": "Take after food",
            },
            format="json",
        )
        self.assertEqual(prescription.status_code, 201, prescription.data)

    def test_admin_generates_invoice_and_marks_paid(self):
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=30),
            reason="Billing test",
        )
        self.auth("admin@example.com", "adminpass123")

        invoice = self.client.post(
            "/api/v1/invoices/",
            {
                "appointment": appointment.id,
                "amount": "1000.00",
                "tax": "100.00",
                "discount": "50.00",
                "payment_method": "CASH",
            },
            format="json",
        )
        self.assertEqual(invoice.status_code, 201, invoice.data)
        self.assertEqual(Decimal(invoice.data["total_amount"]), Decimal("1050.00"))

        paid = self.client.patch(
            f"/api/v1/invoices/{invoice.data['id']}/status/",
            {"status": "PAID", "payment_method": "CASH"},
            format="json",
        )
        self.assertEqual(paid.status_code, 200, paid.data)
        self.assertEqual(paid.data["status"], "PAID")

    def test_dashboard_overview_returns_aggregates(self):
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=30),
            reason="Dashboard test",
            status=Appointment.Status.COMPLETED,
        )
        Invoice.objects.create(appointment=appointment, amount=1000, tax=100, discount=100, status="PAID")

        self.auth("admin@example.com", "adminpass123")
        first = self.client.get("/api/v1/dashboard/overview/")
        self.assertEqual(first.status_code, 200, first.data)
        self.assertIn("users_by_role", first.data)
        self.assertIn("appointments_by_status", first.data)
        self.assertIn("revenue_paid_total", first.data)

        second = self.client.get("/api/v1/dashboard/overview/")
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data, second.data)

    def test_patient_cannot_create_invoice(self):
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=30),
            reason="Permission test",
        )
        self.auth("patient@example.com", "patientpass123")
        response = self.client.post(
            "/api/v1/invoices/",
            {"appointment": appointment.id, "amount": "100.00", "tax": "10.00", "discount": "0.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
