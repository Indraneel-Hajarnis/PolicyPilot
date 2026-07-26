class PolicyPilotError(Exception):
    """Base exception for PolicyPilot errors."""


class DocumentProcessingError(PolicyPilotError):
    """Raised when document processing fails."""
