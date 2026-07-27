"""Question Engine module.

Dynamically determines the next question in the decision tree traversal.
"""

import logging
from typing import Any, Dict, List, Optional
from app.models.question import QuestionModel

logger = logging.getLogger(__name__)


class QuestionEngine:
    """Determines decision tree progression and missing question identification."""

    def determine_next_question(
        self,
        questions: List[QuestionModel],
        answers: Dict[str, Any]
    ) -> Optional[QuestionModel]:
        """Finds the next unanswered required question in order of display index.

        Returns None if all relevant questions have been answered.
        """
        sorted_questions = sorted(questions, key=lambda q: q.order_index)

        for question in sorted_questions:
            # If the node_id is not in patient's provided answers, this is the next question
            if question.node_id not in answers:
                logger.debug(f"Next question identified: node_id={question.node_id}")
                return question

        return None
