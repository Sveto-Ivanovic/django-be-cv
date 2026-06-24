def validate_request_for_evaluation(data_to_evaluate):

    all_has_reference_answer = True
    all_has_question = True
    
    count_has_reference_answer = 0
    count_has_question = 0

    for item in data_to_evaluate:
        
        question = item.get("question", None)
        if question is None:
            all_has_question = False
        else:
            count_has_question = count_has_question + 1


        reference_answer = item.get("reference_answer", None)
        if reference_answer is None:
            all_has_reference_answer = False
        else:
            count_has_reference_answer = count_has_reference_answer + 1

    if not all_has_reference_answer and  not all_has_question:
        raise ValueError(f"Structure of the request to evaluate isn't uniform, the supported types are objects with properties: '{'question'}' or '{'question', 'reference_answer'}'")

    elif all_has_reference_answer and all_has_question:
        return ["completness", "correctness"]
    
    elif all_has_question:
         return ["completness"]
    
    elif not all_has_question:
        raise ValueError(f"All objects must have question property.")


