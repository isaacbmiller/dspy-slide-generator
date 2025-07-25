
from enum import Enum

class Intent(Enum):
    ORIGINAL_QUESTION = "original_question"
    INFORMATION_REQUEST = "information_request"
    POTENTIAL_ANSWER = "potential_answer"
    FURTHER_DETAILS = "further_details"

    def is_question(self):
        return self == Intent.ORIGINAL_QUESTION or self == Intent.INFORMATION_REQUEST