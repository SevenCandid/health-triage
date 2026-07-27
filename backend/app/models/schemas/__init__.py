"""Pydantic v2 Schemas for the Domain Models Layer.

One schema file per model group, using model_config {"from_attributes": True}
so SQLAlchemy ORM instances can be directly serialized.

All schemas use strict Pydantic v2 syntax:
  - No .from_orm() — use .model_validate()
  - No class Config — use model_config = ConfigDict(...)
  - Annotated validators via @field_validator
"""

# Re-export all schema modules for convenient imports
from app.models.schemas.language import (  # noqa: F401
    LanguageCreate,
    LanguageRead,
    LanguageUpdate,
)
from app.models.schemas.user import (  # noqa: F401
    UserCreate,
    UserRead,
    UserUpdate,
    UserPublic,
)
from app.models.schemas.emergency_contact import (  # noqa: F401
    EmergencyContactCreate,
    EmergencyContactRead,
    EmergencyContactUpdate,
)
from app.models.schemas.symptom_category import (  # noqa: F401
    SymptomCategoryCreate,
    SymptomCategoryRead,
)
from app.models.schemas.symptom import (  # noqa: F401
    SymptomCreate,
    SymptomRead,
    SymptomWithTranslations,
)
from app.models.schemas.symptom_translation import (  # noqa: F401
    SymptomTranslationCreate,
    SymptomTranslationRead,
)
from app.models.schemas.health_concern import (  # noqa: F401
    HealthConcernCreate,
    HealthConcernRead,
)
from app.models.schemas.severity_level import (  # noqa: F401
    SeverityLevelCreate,
    SeverityLevelRead,
)
from app.models.schemas.triage_rule import (  # noqa: F401
    TriageRuleCreate,
    TriageRuleRead,
)
from app.models.schemas.recommendation import (  # noqa: F401
    RecommendationCreate,
    RecommendationRead,
)
from app.models.schemas.recommendation_translation import (  # noqa: F401
    RecommendationTranslationCreate,
    RecommendationTranslationRead,
)
from app.models.schemas.question import (  # noqa: F401
    QuestionCreate,
    QuestionRead,
)
from app.models.schemas.question_option import (  # noqa: F401
    QuestionOptionCreate,
    QuestionOptionRead,
)
from app.models.schemas.assessment_session import (  # noqa: F401
    AssessmentSessionCreate,
    AssessmentSessionRead,
    AssessmentSessionSummary,
)
from app.models.schemas.assessment_response import (  # noqa: F401
    AssessmentResponseCreate,
    AssessmentResponseRead,
)
from app.models.schemas.audit_log import (  # noqa: F401
    AuditLogCreate,
    AuditLogRead,
)
