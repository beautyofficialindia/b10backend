import logging

logger = logging.getLogger(__name__)


def flag_conversation_for_review(session_id, reason):
    logger.warning("conversation_flagged session_id=%s reason=%s", session_id, reason)
