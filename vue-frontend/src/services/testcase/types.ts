export type SupabaseMetadata = {
    namespace: string;
    top_k: number;
    mode: string;
    table_name: string;
    model: string;
    semantic_search_mode: string;
}

export type PineconeMetadata = {
    index_name: string;
    top_k: number;
    mode: string;
    index_name_lexical?: string;
    model: string;
}

export type EvalType = {
    question: string;
    reference_answer: string;
}

export type NearestNeighborSetting = {
    get_all_neighbor_chunks: boolean;
    nearest_chunks_n: number;
    nearest_page_or_array_members_n: number;
}


export type AggregateType = {
    faithfulness?: number;
    answer_relevancy?: number;
    answer_correctness?: number;
    context_recall?: number;
}

type EvaluationResult = {
    user_input: string | null;
    reference: string | null;
    retrieved_contexts: string[];
    response: string | null;
    retrieved_context_array: string;

    faithfulness: number | null;
    faithfulness_explanation: string | null;

    answer_relevancy: number | null;
    answer_relevancy_explanation: string | null;

    answer_correctness: number | null;
    answer_correctness_explanation: string | null;

    context_recall: number | null;
    context_recall_explanation: string | null;
};

export type ValidateTextRequest = {
    testcase_name: string;
    supabase_metadata?: SupabaseMetadata;
    pinecone_metadata?: PineconeMetadata;
    llm_model: string;
    eval_model: string;
    to_evaluate: EvalType[];
    nearest_neighbor_settings?: NearestNeighborSetting;
}

export type ValidateTextResponse = {
    status: string;
    response: string;
    aggregate: AggregateType;
    aggregate_id: string;
    total: number;
}

export type ValidateJsonRequest = {
    testcase_name: string;
    supabase_metadata?: SupabaseMetadata;
    pinecone_metadata?: PineconeMetadata;
    llm_model: string;
    eval_model: string;
    to_evaluate: File;
    nearest_neighbor_settings?: NearestNeighborSetting;
}


export type GetAggregateItem={
  id: string; 
  test_case_name: string | null;
  qa_model_used: string | null;
  validation_model_used: string | null;
  aggregate_metadata:   AggregateType | null;
  created_at: string;
  number_of_testcases: number | null;
}

export type GetAggregateResponse = GetAggregateItem[]


export type TestCaseListItem = {
  id: string; 
  aggregate_id: string; 
  test_case_name: string | null;
  qa_model_used: string | null;
  validation_model_used: string | null;
  aggregate_metadata: Record<string, unknown> | null;
  created_at: string; 

  user_input: string | null;
  retrieved_context_text: string | null;
  retrieved_context_array: any[] | null;
  response: string | null;
  reference: string | null;

  faithfulness: number | null;
  faithfulness_explanation: string | null;
  answer_relevancy: number | null;
  answer_relevancy_explanation: string | null;
  answer_correctness: number | null;
  answer_correctness_explanation: string | null;
  context_recall: number | null;
  context_recall_explanation: string | null;
}

export type TestCaseRequest = {
    aggregate_id: string;
}

export type TestCaseResponse = TestCaseListItem[]


export type DeleteTestCaseRequest = {
    aggregate_id: string;
}