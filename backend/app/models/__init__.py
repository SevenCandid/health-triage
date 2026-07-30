"""Domain Models Package.

This package contains the canonical SQLAlchemy 2.0 ORM model definitions
for the FirstAid+ persistence layer.

Import order matters for Alembic autogenerate discovery:
All models must be imported here so Base.metadata is fully populated.
"""

from app.models.base import Base  # noqa: F401 — must be first
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin  # noqa: F401
from app.models.language import LanguageModel  # noqa: F401
from app.models.user import UserModel  # noqa: F401
from app.models.emergency_contact import EmergencyContactModel  # noqa: F401
from app.models.symptom_category import SymptomCategoryModel  # noqa: F401
from app.models.symptom import SymptomModel  # noqa: F401
from app.models.symptom_translation import SymptomTranslationModel  # noqa: F401
from app.models.health_concern import HealthConcernModel  # noqa: F401
from app.models.symptom_concern import SymptomConcernModel  # noqa: F401
from app.models.severity_level import SeverityLevelModel  # noqa: F401
from app.models.triage_rule import TriageRuleModel  # noqa: F401
from app.models.recommendation import RecommendationModel  # noqa: F401
from app.models.recommendation_translation import RecommendationTranslationModel  # noqa: F401
from app.models.question import QuestionModel  # noqa: F401
from app.models.question_option import QuestionOptionModel  # noqa: F401
from app.models.health_conversation import HealthConversationModel, ConversationSymptomModel  # noqa: F401
from app.models.assessment_response import AssessmentResponseModel  # noqa: F401
from app.models.audit_log import AuditLogModel  # noqa: F401

__all__ = [
    "Base",
    "SoftDeleteMixin",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "LanguageModel",
    "UserModel",
    "EmergencyContactModel",
    "SymptomCategoryModel",
    "SymptomModel",
    "SymptomTranslationModel",
    "HealthConcernModel",
    "SymptomConcernModel",
    "SeverityLevelModel",
    "TriageRuleModel",
    "RecommendationModel",
    "RecommendationTranslationModel",
    "QuestionModel",
    "QuestionOptionModel",
    "HealthConversationModel",
    "ConversationSymptomModel",
    "AssessmentResponseModel",
    "AuditLogModel",
]
