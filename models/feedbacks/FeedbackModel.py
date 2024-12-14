from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EvaluationScore(BaseModel):
    score: str = Field(
        description="RAG score representing strictly evaluated performance level:\n"
        "- R (Red): Significant deficiencies or errors that would impact patient care. Reserved for clear performance failures\n"
        "- A (Amber): Good but not excellent performance. Shows competency but falls short of exemplary standards\n"
        "- G (Green): Outstanding performance only. Must demonstrate exceptional skill and no significant flaws\n"
        "Note: This is a stringent scoring system - 'G' scores should be rare and only awarded for truly exemplary performance. "
        "When in doubt, default to a lower score.\n"
        "Must be exactly one character: 'R', 'A', or 'G'. No other values permitted.",
        pattern="^[RAG]$",
    )
    supporting_phrase: Optional[str] = Field(
        description="Direct quote supporting the score BASED ONLY ON THE DOCTOR'S COMMUNICATION AND BEHAVIOR, CRITICAL EVALUATION GUIDELINES:\n\n"
        "🔍 SUPPORTING PHRASE RULES:\n"
        "- ONLY use quotes from the DOCTOR'S dialogue\n"
        "- The supporting phrase must directly demonstrate the skill being evaluated\n\n"
        "- If NO suitable doctor quote exists for a skill, mark the score but leave supporting_phrase as NULL\n"
        "- DO NOT use patient dialogue under ANY circumstances\n\n"
        "❌ INCORRECT Example:\n"
        'Patient says: "I\'m worried about my heart"\n'
        'Supporting Phrase: "I\'m worried about my heart" ❌ WRONG\n\n'
        "✅ CORRECT Example:\n"
        'Doctor says: "I understand your concerns about heart health. Let\'s discuss this together."\n'
        'Supporting Phrase: "I understand your concerns about heart health. Let\'s discuss this together." ✅ CORRECT\n\n'
        "Evaluation Steps:\n"
        "1. Read entire consultation transcript\n"
        "2. Assess ONLY the doctor's communication\n"
        "3. Select supporting phrases STRICTLY from doctor's dialogue\n"
        "4. Ensure phrases match the specific skill being evaluated"
    )


class GlobalSkills(BaseModel):
    """
    Detailed Scoring Guidance BASED ONLY ON THE DOCTOR'S COMMUNICATION AND BEHAVIOR:
    R (Red): Significant concerns, major improvements needed
    A (Amber): Partial performance, some areas for improvement
    G (Green): Excellent performance, meets all expected standards
    """

    structures_consultation: EvaluationScore = Field(
        description=" Assesses the doctor's ability to organize the consultation systematically. G: Clear logical flow, smooth transitions between stages. A: Some structure but occasional digressions. R: Disorganized, no clear consultation framework."
    )
    avoids_repetition: EvaluationScore = Field(
        description="Evaluates the doctor's communication efficiency and avoiding redundant questions. G: Asks each question purposefully, no unnecessary repetition. A: Some repeated or slightly overlapping inquiries. R: Frequently asks the same questions, shows poor information synthesis."
    )
    progresses_through_tasks: EvaluationScore = Field(
        description=" Measures the doctor's ability to move purposefully through consultation stages. G: Smooth, efficient progression, covers all necessary ground. A: Some hesitation or minor delays in task progression. R: Struggles to move forward, gets stuck or loses consultation direction."
    )
    recognises_ethical_implications: EvaluationScore = Field(
        description="Assesses the doctor's   awareness and consideration of ethical aspects. G: Proactively addresses potential ethical concerns, shows sensitivity. A: Partially acknowledges ethical dimensions. R: Fails to recognize or consider important ethical implications."
    )
    finishes_data_gathering: EvaluationScore = Field(
        description="Evaluates the doctor's time management in information collection. G: Completes comprehensive data gathering within 6-7 minutes efficiently. A: Slightly rushed or extended data gathering. R: Significantly over or under time, incomplete information collection."
    )
    uses_clear_language: EvaluationScore = Field(
        description="Measures the doctor's communication clarity and accessibility. G: Uses precise, understandable medical terminology, adapts language to patient's comprehension. A: Generally clear but occasional complex medical jargon. R: Consistently uses incomprehensible or overly technical language."
    )
    remains_responsive_to_patient: EvaluationScore = Field(
        description="Assesses the doctor's patient-centered communication and active listening. G: Consistently attentive, responds empathetically to patient's verbal and non-verbal cues. A: Partially responsive, some missed patient signals. R: Appears disengaged, minimal patient acknowledgment."
    )


class Tasks(BaseModel):
    opens_consultation: EvaluationScore = Field(
        description="Evaluates the doctor's initial consultation approach. G: Warmly welcomes patient, clearly invites narrative, sets positive consultation tone. A: Standard opening, minimal personalization. R: Abrupt or impersonal start, fails to create comfortable environment."
    )
    discovers_psychosocial_context: EvaluationScore = Field(
        description="Measures the doctor's holistic understanding beyond medical symptoms. G: Comprehensively explores patient's life context, social determinants of health. A: Partial exploration of psychosocial factors. R: Focuses exclusively on medical symptoms, ignores broader context."
    )
    identifies_cues: EvaluationScore = Field(
        description="Assesses the doctor's ability to detect subtle patient communication signals. G: Expertly recognizes and follows up on explicit and implicit patient cues. A: Catches some, misses some important cues. R: Consistently misses or ignores patient's verbal and non-verbal signals."
    )
    discovers_ice: EvaluationScore = Field(
        description="Evaluates the doctor's exploration of patient's Ideas, Concerns, and Expectations. G: Thoroughly and sensitively explores patient's perspective on illness. A: Partially investigates ICE. R: Fails to explore patient's illness perception."
    )
    interprets_tests: EvaluationScore = Field(
        description="Measures the doctor's diagnostic reasoning and test interpretation. G: Precise, evidence-based interpretation, explains rationale clearly. A: Generally accurate interpretation with some uncertainty. R: Incorrect or unclear test interpretation."
    )
    generates_hypotheses: EvaluationScore = Field(
        description="Assesses the doctor's diagnostic reasoning complexity. G: Generates multiple nuanced diagnostic hypotheses, systematically evaluates. A: Develops basic hypotheses with some depth. R: Limited or overly simplistic diagnostic reasoning."
    )
    rules_in_out_disease: EvaluationScore = Field(
        description="Evaluates the doctor's systematic approach to differential diagnosis. G: Methodically and comprehensively rules in/out potential serious conditions. A: Partially considers differential diagnosis. R: Incomplete or superficial disease elimination process."
    )
    reaches_diagnosis: EvaluationScore = Field(
        description="Measures the doctor's diagnostic conclusion quality. G: Reaches well-reasoned, evidence-supported working diagnosis. A: Tentative or partially supported diagnosis. R: Premature or unsupported diagnostic conclusion."
    )
    offers_management_plan: EvaluationScore = Field(
        description="Assesses the doctor's patient-centered treatment strategy. G: Develops comprehensive, personalized management plan considering patient preferences. A: Standard management approach with minimal personalization. R: Generic or inappropriate management strategy."
    )
    manages_comorbidity: EvaluationScore = Field(
        description="Evaluates the doctor's ability to manage complex health conditions. G: Expertly navigates multiple health conditions, considers interactions. A: Partially addresses comorbidities. R: Fails to acknowledge or manage related health conditions."
    )
    provides_safety_net: EvaluationScore = Field(
        description="Measures the doctor's follow-up and contingency planning. G: Clear, comprehensive follow-up plan, explicit safety instructions. A: Basic follow-up guidance. R: Inadequate or absent follow-up and safety planning."
    )


class RelatingToOthers(BaseModel):
    generates_rapport: EvaluationScore = Field(
        description="Assesses the doctor's interpersonal connection quality. G: Builds strong, immediate empathetic connection. A: Polite but somewhat distant interaction. R: Fails to establish any meaningful patient rapport."
    )
    uses_open_questions: EvaluationScore = Field(
        description="Evaluates the doctor's questioning technique breadth. G: Masterfully uses open questions to encourage comprehensive patient narrative. A: Some effective open questioning. R: Predominantly closed or leading questions."
    )
    clarifies_cues: EvaluationScore = Field(
        description="Measures the doctor's depth of patient cue exploration. G: Systematically and sensitively explores and clarifies patient cues. A: Partially investigates patient signals. R: Consistently overlooks or dismisses patient cues."
    )
    listens_curiosity: EvaluationScore = Field(
        description="Assesses the doctor's active and engaged listening. G: Demonstrates genuine curiosity, active listening, meaningful follow-ups. A: Intermittent attentiveness. R: Appears disinterested, minimal genuine listening."
    )
    uses_closed_questions: EvaluationScore = Field(
        description="Evaluates the doctor's targeted information gathering. G: Precisely uses closed questions to gather specific, necessary information. A: Some effective closed questioning. R: Overuses closed questions, restricts patient narrative."
    )
    explains_rationale: EvaluationScore = Field(
        description="Measures the doctor's transparency in clinical reasoning. G: Clearly explains reasoning behind questions and actions. A: Partial explanation of clinical approach. R: Provides no context or rationale for clinical actions."
    )
    verbalises_diagnosis: EvaluationScore = Field(
        description="Assesses the doctor's ability to communicate diagnosis clearly, compassionately, and comprehensibly in a patient-friendly manner. G: Articulates diagnosis clearly, compassionately, and comprehensibly. A: Basic diagnostic explanation. R: Unclear or insensitive diagnostic communication."
    )
    shares_ice_plan: EvaluationScore = Field(
        description="Evaluates the doctor's ability to integrate patient's Ideas, Concerns, and Expectations into management plan. G: Explicitly incorporates patient's perspective into management plan. A: Partial integration of patient perspective. R: Ignores patient's perspective in planning."
    )
    negotiates_psychosocial_plan: EvaluationScore = Field(
        description="Measures the doctor's holistic care approach. G: Comprehensively negotiates plan considering broader life context. A: Partially considers psychosocial factors. R: Exclusively biomedical approach, ignores social context."
    )
    shares_risks: EvaluationScore = Field(
        description="Assesses the doctor's ability to inform consent process. G: Transparently and compassionately discusses all potential risks and options. A: Provides basic risk information. R: Inadequate or unclear risk communication."
    )
    supports_decision_making: EvaluationScore = Field(
        description="Evaluates how the doctor supports patient's empowerment in healthcare decisions. G: Fully supports patient's autonomous decision-making process. A: Provides some decision support. R: Paternalistic or dismissive approach to patient choices."
    )


class DomainFeedback(BaseModel):
    score: str = Field(description="Overall domain score (R/A/G)")
    strengths: list[str] = Field(
        description="Specific strengths identified from Green scores and supporting phrases",
        default_factory=list
    )
    improvements: list[str] = Field(
        description="Specific improvements needed based on Red/Amber scores and supporting phrases",
        default_factory=list
    )
    suggested_actions: list[str] = Field(
        description="Concrete actions to improve performance in this area",
        default_factory=list
    )


class PriorityAction(BaseModel):
    area: str = Field(
        description="The specific skill or competency area needing attention"
    )
    current_level: str = Field(
        description="Brief description of current performance level and why it's a priority"
    )
    improvement_steps: list[str] = Field(
        description="Specific, actionable steps to improve in this area",
        min_items=1,
        max_items=4
    )
    expected_outcome: str = Field(
        description="Clear description of what successful improvement looks like"
    )


class ActionableFeedback(BaseModel):
    global_skills_feedback: DomainFeedback = Field(
        description="Analysis and recommendations for global consultation skills"
    )
    tasks_feedback: DomainFeedback = Field(
        description="Analysis and recommendations for clinical tasks"
    )
    relating_feedback: DomainFeedback = Field(
        description="Analysis and recommendations for interpersonal skills"
    )
    overall_priorities: list[PriorityAction] = Field(
        description="2-3 highest priority areas across all domains with detailed improvement plans",
        min_items=3,
        max_items=6
    )


class FeedbackResponse(BaseModel):
    global_skills: GlobalSkills = Field(
        description="Comprehensive evaluation of overall consultation skills OF THE DOCTOR with RAG scoring."
    )
    tasks: Tasks = Field(
        description="Detailed assessment of clinical task performance OF THE DOCTOR with RAG scoring."
    )
    relating_to_others: RelatingToOthers = Field(
        description="Interpersonal and communication skill analysis OF THE DOCTOR   with RAG scoring."
    )
    actionable_feedback: ActionableFeedback


class ExtendedFeedbackResponse(FeedbackResponse):
    feedback_id: str = Field(description="Unique identifier for the feedback")
    user_id: str = Field(description="ID of the user receiving the feedback")
    mock_id: str = Field(description="ID of the mock consultation session")
    station_id: str = Field(description="ID of the station/scenario")
    evaluated_by: str = Field(description="ID or name of the evaluator")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the feedback was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the feedback was last updated"
    )
