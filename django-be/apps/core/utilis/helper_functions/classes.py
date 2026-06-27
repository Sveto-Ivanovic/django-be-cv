from pydantic import BaseModel, Field

class FaithfulnessResult(BaseModel):
    reasoning: str = Field(description="Overall reasoning summary for the faithfulness score")
    score: float = Field(description="Faithfulness score between 0.0 and 1.0", ge=0.0, le=1.0)


class AnswerRelevancyResult(BaseModel):
    reasoning: str = Field(description="Overall reasoning summary for the relevance score")
    score: float = Field(description="Answer relevance score between 0.0 and 1.0", ge=0.0, le=1.0)


class ContextRecallResult(BaseModel):
    reasoning: str = Field(description="Overall reasoning summary for the context recall score")
    score: float = Field(description="Context recall score between 0.0 and 1.0", ge=0.0, le=1.0)


class AnswerCorrectnessResult(BaseModel):
    reasoning: str = Field(description="Overall reasoning summary for the answer correctness score")
    score: float = Field(description="Answer correctness score between 0.0 and 1.0", ge=0.0, le=1.0)


class RAGEvaluationResult(BaseModel):
    faithfulness: FaithfulnessResult
    answer_relevancy: AnswerRelevancyResult
    context_recall: ContextRecallResult


class RAGEvaluationResultReference(BaseModel):
    faithfulness: FaithfulnessResult
    answer_relevancy: AnswerRelevancyResult
    context_recall: ContextRecallResult
    answer_correctness: AnswerCorrectnessResult
