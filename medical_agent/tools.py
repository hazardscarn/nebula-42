from typing import Dict, Any
import random
from datetime import date

# Patient database (same as your original)
patient_database = {
    "P001": {
        "name": "Lisa Cuddy",
        "allergies": ["Penicillin"],
        "prescriptions": ["Lisinopril", "Metformin", "Ibuprofen"],
        "conditions": ["Hypertension", "Type 2 Diabetes", "Occasional migraines"],
        "notes": "Dean of Medicine. Monitor blood pressure and blood sugar regularly."
    },
    "P002": {
        "name": "Robert Chase",
        "allergies": ["None known"],
        "prescriptions": ["Ibuprofen", "Albuterol inhaler", "Naproxen", "Vicodin"],
        "conditions": ["Seasonal Allergies", "Asthma", "Shoulder strain from surgery", "Leg surgery done recently"],
        "notes": "Surgeon. Monitor asthma triggers and allergy seasons."
    },
    "P003": {
        "name": "Eric Foreman",
        "allergies": ["Shellfish"],
        "prescriptions": ["Aspirin", "Atorvastatin"],
        "conditions": ["High cholesterol", "Family history of heart disease"],
        "notes": "Neurologist. Annual cardiac screening recommended."
    }
}

doctors = {
    "Lisa Cuddy": "LIC-1001",
    "James Wilson": "LIC-1004",
    "Gregory House": "LIC-1002",
    "Eric Foreman": "LIC-1003"
}

def patient_ehr_lookup(patient_id: str) -> Dict[str, Any]:
    """Access all electronic health records of a specific patient, including allergies, medications, prescriptions, conditions, and notes.
    
    Args:
        patient_id: Patient ID (e.g., P001)
        
    Returns:
        A dictionary with patient data or error message
    """
    if patient_id in patient_database:
        return {
            "patient_id": patient_id,
            "patient_data": patient_database[patient_id]
        }
    return {"error": f"Patient ID '{patient_id}' not found."}

def search_patients_by_name(name: str) -> Dict[str, Any]:
    """Search for patients by name - requires authorization. Case-insensitive search.
    
    Args:
        name: Patient name (partial or full) to search for
        
    Returns:
        A dictionary with matching patients or no matches message
    """
    name_lower = name.lower()
    matches = []
    for patient_id, data in patient_database.items():
        if name_lower in data["name"].lower():
            matches.append({
                "patient_id": patient_id,
                "name": data["name"],
                "last_visit": "2024-12-10"
            })
    
    if matches:
        return {"patients": matches}
    return {"message": f"No patients found matching '{name}'."}

def list_all_patients() -> Dict[str, Any]:
    """List all patients in the system - ADMINISTRATIVE FUNCTION ONLY. Returns basic patient info including last visit date.
    
    Returns:
        A dictionary with all patients basic info
    """
    patients = []
    for patient_id, data in patient_database.items():
        patients.append({
            "patient_id": patient_id,
            "name": data["name"],
            "last_visit": "2024-12-10"
        })
    return {"patients": patients}

def search_doctors_by_name(name: str) -> Dict[str, Any]:
    """Search registered doctors in hospital system. Used for verifying and assigning prescriptions.
    
    Args:
        name: Doctor name (partial or full) to search for
        
    Returns:
        A dictionary with matching doctors or no matches message
    """
    name_lower = name.lower()
    matches = []
    for doctor_name, license_id in doctors.items():
        if name_lower in doctor_name.lower():
            matches.append({
                "name": doctor_name,
                "license_id": license_id,
                "department": "Internal Medicine"
            })
    
    if matches:
        return {"doctors": matches}
    return {"message": f"No doctors found matching '{name}'."}

def create_prescription(prescription_note: str, doctor_name: str) -> Dict[str, Any]:
    """Generate a prescription note for a patient on hospital notepad. Includes prescription number, doctor info, date, and signature.
    
    Args:
        prescription_note: The prescription instructions for the patient, including medication, dosage, and frequency
        doctor_name: Full name of the prescribing doctor (must exist in system)
        
    Returns:
        A dictionary with prescription details or error message
    """
    if doctor_name not in doctors:
        return {"error": f"Doctor '{doctor_name}' not found in system."}
    
    prescription_number = f"RX{random.randint(100000, 999999)}"
    date_issued = date.today().isoformat()
    license_id = doctors[doctor_name]
    
    prescription = {
        "prescription_number": prescription_number,
        "date": date_issued,
        "doctor_name": doctor_name,
        "doctor_license_id": license_id,
        "prescription_note": prescription_note,
        "hospital_notepad": "Houston Medical Center",
        "signature": f"Dr. {doctor_name} (Signature)"
    }
    
    return prescription