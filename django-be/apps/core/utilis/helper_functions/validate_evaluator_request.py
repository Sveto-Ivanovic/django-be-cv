def validate_request_for_evaluation(data_to_evaluate):

    all_has_question = all(item.get("question") is not None for item in data_to_evaluate)
    all_has_reference = all(item.get("reference_answer") is not None for item in data_to_evaluate)

    if not all_has_question:
        raise ValueError("All objects must have a 'question' property.")

    # Metrics that don't need reference_answer
    metrics = ["faithfulness", "answer_relevance", "context_recall"]

    # Metrics that require reference_answer
    if all_has_reference:
        metrics += ["answer_correctness"]

    return metrics