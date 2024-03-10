import streamlit as st
from fhirclient import client
import fhirclient.models.patient as p
from datetime import datetime
import uuid

def initialize_fhir_client():
    """Initialize and return a FHIR client configured for the HAPI FHIR server."""
    settings = {
        'app_id': 'my_test_app',
        'api_base': 'http://hapi.fhir.org/baseR4'
    }
    return client.FHIRClient(settings=settings)

def generate_mrn():
    """Generate a pseudo-random MRN for demonstration purposes."""
    return str(uuid.uuid4().int)[:9]  # Generate a 9-digit pseudo-random number

def create_and_post_patient(fhir_client, first_name, last_name, birthdate):
    """Create a new patient with the given details and post it to the server.

    Returns the MRN and resource ID if successful, otherwise returns None.
    """
    mrn = generate_mrn()
    system = "http://fhir.openclintech.com/r4"
    try:
        # Create a new patient resource with an MRN identifier
        patient = p.Patient(dict(
            identifier=[{
                "use": "official",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR",
                            "display": "Medical record number"
                        }
                    ]
                },
                "system": system,
                "value": mrn
            }],
            name=[{
                "use": "official",
                "family": last_name,
                "given": [first_name]
            }],
            birthDate=birthdate
        ))

        # Attempt to post the patient to the server
        result = patient.create(fhir_client.server)

        if result:
            resource_id = patient.id
            #print_details(resource_id, mrn, fhir_client.server.base_uri)
            return mrn, resource_id
        else:
            print("Patient creation failed.")
            return None
    except Exception as e:
        print(f"An error occurred during patient creation: {e}")
        return None

def print_details(resource_id, mrn, base_uri):
    """Print details of the successfully created patient using Streamlit."""
    full_url = f"{base_uri}/Patient/{resource_id}"
    st.success(f"Patient creation successful. Resource ID: {resource_id}, MRN: {mrn}")
    st.write(f"Full URL: {full_url}")

def verify_patient_creation(fhir_client, mrn, system):
    """Verify patient creation by searching for the patient using their MRN."""
    search = p.Patient.where(struct={'identifier': f"{system}|{mrn}"})
    patients = search.perform_resources(fhir_client.server)
    if patients:
        patient = patients[0]  # Assuming the MRN is unique, there should be only one match
        resource_id = patient.id
        base_uri = fhir_client.server.base_uri
        full_url = f"{base_uri}/Patient/{resource_id}"
        st.success(f"Verification successful. Found Patient with Resource ID: {resource_id}, MRN: {mrn}")
        st.write(f"Full URL: {full_url}")
    else:
        print("Verification failed. No patient found with the given MRN.")

def app():
    st.title('FHIR Patient Management')
    fhir_client = initialize_fhir_client()
    system = 'http://fhir.openclintech.com/r4'

    action = st.radio("Choose an action:", ('Create New Patient', 'View Existing Patient'))

    if action == 'Create New Patient':
        st.subheader("Create a New Patient")
        first_name = st.text_input("Enter the patient's first name:")
        last_name = st.text_input("Enter the patient's last name:")
        birthdate = st.text_input("Enter the patient's birthdate (YYYY-MM-DD):")

        if st.button('Create Patient'):
            if first_name and last_name and birthdate:
                mrn, resource_id = create_and_post_patient(fhir_client, first_name, last_name, birthdate)
                verify_patient_creation(fhir_client, mrn, system)  # Or print_details directly if preferred
            else:
                st.error("Please fill out all the fields.")

    elif action == 'View Existing Patient':
        st.subheader("View an Existing Patient")
        search_mrn = st.text_input("Enter the patient's MRN to search:")
        if st.button('Search'):
            if search_mrn:
                verify_patient_creation(fhir_client, search_mrn, system)
            else:
                st.error("Please enter an MRN.")

if __name__ == '__main__':
    app()
