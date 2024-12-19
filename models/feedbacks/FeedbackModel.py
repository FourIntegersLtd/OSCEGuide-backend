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
        description="Direct quote supporting the score with additional cultural/linguistic considerations:\n\n"
        "🔍 STRICT QUOTE UNIQUENESS REQUIREMENTS:\n"
        "1. Each quote MUST BE COMPLETELY UNIQUE across ALL domains and categories\n"
        "2. Even partial overlaps or similar phrases are NOT permitted\n"
        "3. System should reject any duplicate or similar quotes\n\n"
        "🔍 SUPPORTING PHRASE RULES:\n"
        "1. ONLY use quotes from the DOCTOR'S dialogue\n"
        "2. Maximum length: 2-3 sentences to ensure distinctiveness\n"
        "3. AUTOMATIC RED SCORE TRIGGERS:\n"
        "   - Use of informal phrases (e.g., 'yeah', 'okay', 'alright then')\n"
        "   - Use of idioms or colloquialisms\n"
        "   - Unexplained complex medical terminology\n"
        "   - Rushed or unclear pronunciation\n"
        "   - Culture-specific references\n\n"
        "✅ CORRECT Example:\n"
        'Instead of: "Yeah, that sounds about right" (RED SCORE)\n'
        'Better: "I understand your concerns and would like to explain further"\n\n'
        "❌ STRICTLY PROHIBITED (ALL RESULT IN RED SCORE):\n"
        "- ANY repeated quotes across ALL domains\n"
        "- Similar phrases with minor variations\n"
        "- Informal/casual language\n"
        "- Culture-specific references\n"
        "- Unexplained medical terms\n"
        "- Quotes longer than 3 sentences"
    )


class GlobalSkills(BaseModel):
    """
    Detailed Scoring Guidance BASED ONLY ON THE DOCTOR'S COMMUNICATION AND BEHAVIOR:
    R (Red): Significant concerns, major improvements needed
    A (Amber): Partial performance, some areas for improvement
    G (Green): Excellent performance, meets all expected standards
    """

    structures_consultation: EvaluationScore = Field(
        description="G: Must do ALL: clear opening/introduction, systematic history, focused examination, structured closing, "
        "explicit signposting between ALL stages, completes within appropriate timeframes.\n"
        "A: Misses ONE element but maintains overall structure.\n"
        "R: Misses multiple elements OR unclear framework OR poor time management."
    )
    
    avoids_repetition: EvaluationScore = Field(
        description="G: Zero repetition of questions/statements AND demonstrates perfect information retention.\n"
        "A: ONE justified clarification with clear purpose.\n"
        "R: ≥2 repeated questions OR asks for previously provided information."
    )

    progresses_through_tasks: EvaluationScore = Field(
        description="G: Completes ALL consultation stages in sequence WITH clear transitions AND within 10 minutes.\n"
        "A: Completes most stages with ≤2 minor delays OR slight time overrun.\n"
        "R: >2 delays OR significant time overrun OR incomplete stages."
    )

    recognises_ethical_implications: EvaluationScore = Field(
        description="G: Identifies ALL ethical issues AND addresses confidentiality, consent, AND autonomy explicitly.\n"
        "A: Addresses 2 of 3: confidentiality, consent, autonomy.\n"
        "R: Addresses ≤1 ethical element OR misses major ethical concerns."
    )

    finishes_data_gathering: EvaluationScore = Field(
        description="G: Completes comprehensive history AND examination within 6-7 minutes.\n"
        "A: Complete data gathering in 5-6 OR 7-8 minutes.\n"
        "R: <5 or >8 minutes OR incomplete essential information."
    )

    uses_clear_language: EvaluationScore = Field(
        description="G: Uses layperson terms throughout AND checks understanding ≥3 times.\n"
        "A: ≤2 instances of medical jargon with explanation.\n"
        "R: >2 instances of unexplained jargon OR no understanding checks."
    )

    remains_responsive_to_patient: EvaluationScore = Field(
        description="G: Acknowledges ALL verbal/non-verbal cues AND provides ≥3 empathetic responses.\n"
        "A: Acknowledges ≥70% of cues with 1-2 empathetic responses.\n"
        "R: Misses >30% of cues OR no empathetic responses."
    )


class Tasks(BaseModel):
    opens_consultation: EvaluationScore = Field(
        description="G: Must do ALL: introduces self, confirms patient identity, obtains consent, establishes agenda. "
        "A: Misses one element but maintains professionalism. "
        "R: Misses multiple elements or appears unprofessional."
    )
    discovers_psychosocial_context: EvaluationScore = Field(
        description="G: Explores occupation, living situation, support systems, and impact on daily life. "
        "A: Explores 2-3 psychosocial elements. "
        "R: Fails to explore any psychosocial context."
    )
    identifies_cues: EvaluationScore = Field(
        description="G: Spots and explores >3 verbal/non-verbal cues with appropriate follow-up. "
        "A: Identifies 1-2 cues with some follow-up. "
        "R: Misses obvious cues or inappropriate response."
    )
    discovers_ice: EvaluationScore = Field(
        description="G: Explicitly explores all three: ideas, concerns, AND expectations. "
        "A: Explores two ICE elements. "
        "R: Explores one or no ICE elements."
    )
    interprets_tests: EvaluationScore = Field(
        description="G: Explains results, significance, and implications with complete accuracy. "
        "A: Minor inaccuracies in explanation but core message correct. "
        "R: Major inaccuracies or unclear explanation."
    )
    generates_hypotheses: EvaluationScore = Field(
        description="G: Generates ≥3 relevant differential diagnoses with clear reasoning. "
        "A: 2 reasonable differentials considered. "
        "R: Single or incorrect differential."
    )
    rules_in_out_disease: EvaluationScore = Field(
        description="G: Systematically excludes red flags and serious conditions with specific questions. "
        "A: Partial assessment of serious conditions. "
        "R: Fails to consider serious diagnoses."
    )
    reaches_diagnosis: EvaluationScore = Field(
        description="G: Evidence-based diagnosis with clear explanation of reasoning. "
        "A: Reasonable diagnosis but incomplete reasoning. "
        "R: Incorrect or unsupported diagnosis."
    )
    offers_management_plan: EvaluationScore = Field(
        description="G: Specific plan with medication details, lifestyle changes, AND follow-up timing. "
        "A: Basic plan missing one key element. "
        "R: Vague or inappropriate plan."
    )
    manages_comorbidity: EvaluationScore = Field(
        description="G: Addresses all comorbidities with specific medication/interaction considerations. "
        "A: Acknowledges comorbidities with partial management. "
        "R: Ignores relevant comorbidities."
    )
    provides_safety_net: EvaluationScore = Field(
        description="G: Specific red flags, timeframes, AND action plan for deterioration. "
        "A: General safety advice without specifics. "
        "R: No safety-netting or inappropriate advice."
    )


class RelatingToOthers(BaseModel):
    generates_rapport: EvaluationScore = Field(
        description="G: Must do ALL: maintains eye contact, uses patient's name, acknowledges emotions, demonstrates empathy ≥3 times.\n"
        "A: Achieves 2-3 elements but misses some opportunities.\n"
        "R: Achieves ≤1 element OR appears disinterested/dismissive."
    )
    uses_open_questions: EvaluationScore = Field(
        description="G: Uses ≥3 effective open questions AND allows complete responses without interruption.\n"
        "A: Uses 1-2 open questions with adequate follow-up.\n"
        "R: No open questions OR consistently interrupts responses."
    )
    clarifies_cues: EvaluationScore = Field(
        description="G: Identifies AND explores ≥3 verbal/non-verbal cues with specific follow-up questions.\n"
        "A: Explores 1-2 cues with some follow-up.\n"
        "R: Misses obvious cues OR inappropriate/no follow-up."
    )
    listens_curiosity: EvaluationScore = Field(
        description="G: Demonstrates ALL: active listening, appropriate silences, meaningful follow-ups, summarizes ≥2 times.\n"
        "A: Demonstrates 2-3 elements but inconsistent.\n"
        "R: ≤1 element OR appears disinterested."
    )
    uses_closed_questions: EvaluationScore = Field(
        description="G: Uses closed questions ONLY for specific clarification AND limits to ≤3 consecutive.\n"
        "A: Occasional overuse but maintains narrative flow.\n"
        "R: Dominates with closed questions OR creates interrogative atmosphere."
    )
    explains_rationale: EvaluationScore = Field(
        description="G: Explains reasoning for ALL: questions, examinations, AND investigations clearly.\n"
        "A: Explains reasoning for 2 of 3 elements.\n"
        "R: Minimal/no explanation of clinical reasoning."
    )
    verbalises_diagnosis: EvaluationScore = Field(
        description="G: Explains diagnosis with ALL: clear language, specific evidence, patient understanding check.\n"
        "A: Includes 2 elements but lacks completeness.\n"
        "R: Unclear explanation OR no understanding check."
    )
    shares_ice_plan: EvaluationScore = Field(
        description="G: Explicitly addresses ALL: ideas, concerns, AND expectations in management plan.\n"
        "A: Addresses 2 ICE elements in plan.\n"
        "R: Addresses ≤1 ICE element OR ignores patient perspective."
    )
    negotiates_psychosocial_plan: EvaluationScore = Field(
        description="G: Addresses ALL: work impact, social support, lifestyle changes, AND practical constraints.\n"
        "A: Addresses 2-3 psychosocial elements.\n"
        "R: Addresses ≤1 element OR purely medical focus."
    )
    shares_risks: EvaluationScore = Field(
        description="G: Discusses ALL: benefits, risks, alternatives, AND obtains informed consent.\n"
        "A: Covers 2-3 elements but lacks detail.\n"
        "R: Inadequate risk discussion OR no clear consent."
    )
    supports_decision_making: EvaluationScore = Field(
        description="G: Offers ALL: clear options, balanced information, time to decide, AND respects choice.\n"
        "A: Provides 2-3 elements of decision support.\n"
        "R: Directive approach OR inadequate support."
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
    cultural_linguistic_considerations: list[str] = Field(
        description="Specific feedback on cultural and linguistic appropriateness",
        default_factory=list
    )
    language_adaptations: list[str] = Field(
        description="Suggestions for clearer communication with non-native English speakers",
        default_factory=list
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
