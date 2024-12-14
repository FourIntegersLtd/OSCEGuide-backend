from pydantic import BaseModel, Field

from typing import List, Optional


class PatientInformationModel(BaseModel):
    patient_biodata: str = (Field(description="patient biodata "),)
    gender: str = (Field(description="gender of the patient "),)
    opening_sentence: str = (
        Field(
            description="The presenting complaint the patient opens the station with",
        ),
    )
    expanded_history: str = (
        Field(description="Detailed information about the concern "),
    )
    family_social_history: List[str] = (
        Field(description="Detailed information about any relevant family history "),
    )
    past_med_history_allergies: List[str] = (
        Field(
            description="Detailed information about any relevant past medical history ",
        ),
    )

    idea: List[str] = (
        Field(description="Patient's thoughts about the presenting complaint "),
    )
    concerns: List[str] = (
        Field(description="Patient's worries about the presenting complaint "),
    )
    expectation: List[str] = (
        Field(description="Patient's expectations from the consultation "),
    )
    persona: str = Field(
        description="The personality to adopt during the consultation "
    )


class DoctorInformationModel(BaseModel):
    patient_biodata: str = (Field(description="patient biodata "),)
    recent_notes: List[str] = (
        Field(description="recent notes from previous consultations "),
    )
    current_medications: List[str] = (Field(description="current medications "),)
    past_medical_history: List[str] = (Field(description="past medical history  "),)
    recent_investigations: List[str] = (Field(description="recent investigations "),)
    social_history: List[str] = (Field(description="social history "),)


class ManagementPlanModel(BaseModel):
    explanation: str = Field(
        description="Explanation of the diagnosis or condition to the patient"
    )
    assessment: List[str] = Field(
        description="Steps taken to assess the patient's condition (e.g., physical exams, investigations)"
    )
    social_concerns: Optional[List[str]] = Field(
        description="Social concerns or challenges identified during the consultation (e.g., housing, employment, family support)"
    )
    ice: Optional[List[str]] = Field(
        description=("Patient's Ideas, Concerns, and Expectations. ")
    )
    immediate_actions: List[str] = Field(
        description="Actions taken immediately to manage the condition (e.g., urgent medications, referrals)"
    )
    pharmacological_treatment: Optional[List[str]] = Field(
        description="Details of medications prescribed, including drug name, dose, and duration"
    )
    non_pharmacological_treatment: Optional[List[str]] = Field(
        description="Details of non-drug interventions (e.g., lifestyle advice, physiotherapy, counseling)"
    )
    follow_up: Optional[str] = Field(
        description="Follow-up plan, including timeframes and criteria for review"
    )
    health_education: Optional[List[str]] = Field(
        description="Patient education points, lifestyle advice, and preventive measures"
    )
    safety_netting: Optional[str] = Field(
        description="Safety-netting advice for the patient, including red flags to look out for"
    )
    additional_notes: Optional[str] = Field(
        description="Any additional notes or comments about the management plan"
    )


class StationModel(BaseModel):
    station_id: str = (Field(description="ID of the station/scenario"),)
    station_name: str = (Field(description="Name of the station/scenario"),)
    created_at: str = (Field(description="Created at"),)
    created_by: str = (Field(description="Created by"),)
    patient_information: PatientInformationModel = Field(descripton="Patient details")
    doctor_information: DoctorInformationModel = Field(descripton="Doctor details")
    management_plan: ManagementPlanModel = Field(descripton="Management plan")
    tags: List[str] = Field(descripton="Tags for the station")
