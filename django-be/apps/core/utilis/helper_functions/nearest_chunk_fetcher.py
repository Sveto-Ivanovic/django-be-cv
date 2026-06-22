from apps.embed.models import VectorSearch1536, VectorSearch2048, VectorSearch3072


def fetch_nearest_chunks_supabase(
    vector_results,
    user_id,
    namespace,
    table_name,
    get_all_neighbor_chunks=False,
    nearest_chunks_n=2,
    nearest_page_or_array_members_n=0,
):

    if table_name not in [
        "vector_search_1536",
        "vector_search_2048",
        "vector_search_3072",
    ]:
        raise ValueError(
            f"Error in fetch_nearest_chunks_supabase: unsupported table name {table_name}, supported names: vector_search_1536, vector_search_2048, vector_search_3072."
        )

    if table_name == "vector_search_1536":
        model = VectorSearch1536
    elif table_name == "vector_search_2048":
        model = VectorSearch2048
    else:
        model = VectorSearch3072

    try:
        #'sourceless_text',

        full_array = []

        for result in vector_results:

            metadata_id = result.get("metadata", {}).get("id", None)
            page = result.get("metadata", {}).get("page", None)
            source = result.get("metadata", {}).get("source", None)
            file_type = result.get("metadata", {}).get("file_type", None)
            chunk_index = result.get("metadata", {}).get("chunk_index", None)
            type_of_flow = result.get("metadata", {}).get("type_of_flow", None)

            if file_type == "pdf" and page is not None:
                # we are dealing with file flow so it has pages and chunks

                if nearest_page_or_array_members_n >= 1:
                    # here we dont need to check chunks because we will just fetch entire page content
                    pages = list(
                        range(
                            page - nearest_page_or_array_members_n,
                            page + nearest_page_or_array_members_n + 1,
                        )
                    )
                    results = model.objects.filter(
                        user_id=user_id,
                        namespace=namespace,
                        metadata__source=source,
                        metadata__file_type=file_type,
                        metadata__page__in=pages,
                    )

                    result_array = list(
                        results.values(
                            "id",
                            "namespace",
                            "source",
                            "metadata",
                            "created_at",
                            "model",
                            "content",
                            "is_chunk",
                            "chunk_number",
                            "type",
                        )
                    )

                    full_array.extend(result_array)

                elif get_all_neighbor_chunks:
                    results = model.objects.filter(
                        user_id=user_id,
                        namespace=namespace,
                        metadata__source=source,
                        metadata__file_type=file_type,
                        metadata__page=page,
                    )

                    result_array = list(
                        results.values(
                            "id",
                            "namespace",
                            "source",
                            "metadata",
                            "created_at",
                            "model",
                            "content",
                            "is_chunk",
                            "chunk_number",
                            "type",
                        )
                    )

                    full_array.extend(result_array)

                elif nearest_chunks_n != 0 and chunk_index is not None:

                    n_chunks = list(
                        range(
                            chunk_index - nearest_chunks_n,
                            chunk_index + nearest_chunks_n + 1,
                        )
                    )
                    results = model.objects.filter(
                        user_id=user_id,
                        namespace=namespace,
                        metadata__source=source,
                        metadata__file_type=file_type,
                        metadata__page=page,
                        metadata__chunk_index__in=n_chunks,
                    )
                    result_array = list(
                        results.values(
                            "id",
                            "namespace",
                            "source",
                            "metadata",
                            "created_at",
                            "model",
                            "content",
                            "is_chunk",
                            "chunk_number",
                            "type",
                        )
                    )

                    full_array.extend(result_array)

                else:
                    full_array.append(result)

            elif file_type is None and page is None and chunk_index is not None:

                if get_all_neighbor_chunks:
                    results = model.objects.filter(
                        user_id=user_id,
                        namespace=namespace,
                        metadata__source=source,
                        metadata__file_type=file_type,
                        metadata__id=metadata_id,
                    )

                    result_array = list(
                        results.values(
                            "id",
                            "namespace",
                            "source",
                            "metadata",
                            "created_at",
                            "model",
                            "content",
                            "is_chunk",
                            "chunk_number",
                            "type",
                        )
                    )

                    full_array.extend(result_array)

                elif nearest_chunks_n != 0 and chunk_index is not None:

                    n_chunks = list(
                        range(
                            chunk_index - nearest_chunks_n,
                            chunk_index + nearest_chunks_n + 1,
                        )
                    )
                    results = model.objects.filter(
                        user_id=user_id,
                        namespace=namespace,
                        metadata__source=source,
                        metadata__file_type=file_type,
                        metadata__id=metadata_id,
                        metadata__chunk_index__in=n_chunks,
                    )
                    result_array = list(
                        results.values(
                            "id",
                            "namespace",
                            "source",
                            "metadata",
                            "created_at",
                            "model",
                            "content",
                            "is_chunk",
                            "chunk_number",
                            "type",
                        )
                    )

                    full_array.extend(result_array)

                else:
                    full_array.append(result)

        page_related_results = [
            {
                **result_element,
                "page": result_element.get("metadata", {}).get("page", None),
                "source": result_element.get("metadata", {}).get("source", None),
                "chunk_index": result_element.get("metadata", {}).get("chunk_index", None),
            }
            for result_element in full_array
            if result_element.get("metadata", {}).get("page", None) is not None
        ]
        id_related_results = [
            {**result_element,
              "chunk_index": result_element.get("metadata", {}).get("chunk_index", None),
              "metadata_id": result_element.get("metadata", {}).get("id", None),
            }
            for result_element in full_array
            if result_element.get("metadata", {}).get("page", None) is None
        ]

        sorted_page_data = sorted(
            page_related_results,
            key=lambda x: (
                x["source"] or "",
                x["page"] or 0,
                x["chunk_index"] if x["chunk_index"] is not None else 0,
            )
        )
        metadata_id_data = sorted(
            id_related_results,
            key=lambda x: (
                x["metadata_id"] if x["metadata_id"] is not None else "",
                x["chunk_index"] if x["chunk_index"] is not None else 0,
            )
        )

        sorted_page_data.extend(metadata_id_data)
        complete_results = sorted_page_data
        my_set = set()
        final_results = []

        for item in complete_results:
            key = item.get("id")
            if item.get("id") is None:
                raise ValueError("fetch_nearest_chunks_supabase id is None.")
            
            if key not in my_set:
                my_set.add(key)
                final_results.append(item)

        return final_results

    except Exception as e:
        print(f"Error in fetch_nearest_chunks_supabase: {e}")
        raise





from pinecone import Pinecone


def fetch_nearest_chunks_pinecone(
    vector_results,
    index_name,
    pinecone_api_key,
    get_all_neighbor_chunks=False,
    nearest_chunks_n=2,
    nearest_page_or_array_members_n=0,
):
    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(index_name)
    index_description=pc.describe_index(name=index_name)
    index_size = index_description.dimension
    full_array = []

    for result in vector_results:
        metadata = result.get("metadata", {})
        metadata_id = metadata.get("id", None)
        page = metadata.get("page", None)
        source = metadata.get("source", None)
        file_type = metadata.get("file_type", None)
        chunk_index = metadata.get("chunk_index", None)

        def build_filter(extra_filters=None):
            f = {
                "source":    {"$eq": source},
                "file_type": {"$eq": file_type},
            }
            if extra_filters:
                f.update(extra_filters)
            return f

        def fetch_by_filter(filter_dict):
            dummy_vector = [0.0] * index_size
            response = index.query(
                vector=dummy_vector,
                filter=filter_dict,
                top_k=200,
                include_metadata=True,
            )
            return [
                {
                    "id":           m["id"],
                    "source":       m["metadata"].get("source"),
                    "metadata":     m["metadata"],
                    "model":        m["metadata"].get("model"),
                    "content":      m["metadata"].get("content"),
                    "is_chunk":     m["metadata"].get("is_chunk"),
                    "chunk_number": m["metadata"].get("chunk_number"),
                    "type":         m["metadata"].get("type"),
                    "score":        m["score"],
                }
                for m in response["matches"]
            ]

        if file_type == "pdf" and page is not None:

            if nearest_page_or_array_members_n >= 1:
                pages = list(range(
                    page - nearest_page_or_array_members_n,
                    page + nearest_page_or_array_members_n + 1,
                ))
                f = build_filter({"page": {"$in": pages}})
                full_array.extend(fetch_by_filter(f))

            elif get_all_neighbor_chunks:
                f = build_filter({"page": {"$eq": page}})
                full_array.extend(fetch_by_filter(f))

            elif nearest_chunks_n != 0 and chunk_index is not None:
                n_chunks = list(range(
                    chunk_index - nearest_chunks_n,
                    chunk_index + nearest_chunks_n + 1,
                ))
                f = build_filter({
                    "page":        {"$eq": page},
                    "chunk_index": {"$in": n_chunks},
                })
                full_array.extend(fetch_by_filter(f))

            else:
                full_array.append(result)

        elif file_type is None and page is None and chunk_index is not None:

            if get_all_neighbor_chunks:
                f = build_filter({"id": {"$eq": metadata_id}})
                full_array.extend(fetch_by_filter(f))

            elif nearest_chunks_n != 0:
                n_chunks = list(range(
                    chunk_index - nearest_chunks_n,
                    chunk_index + nearest_chunks_n + 1,
                ))
                f = build_filter({
                    "id":          {"$eq": metadata_id},
                    "chunk_index": {"$in": n_chunks},
                })
                full_array.extend(fetch_by_filter(f))

            else:
                full_array.append(result)

    page_related_results = [
        {
            **r,
            "page":        r.get("metadata", {}).get("page"),
            "source":      r.get("metadata", {}).get("source"),
            "chunk_index": r.get("metadata", {}).get("chunk_index"),
        }
        for r in full_array
        if r.get("metadata", {}).get("page") is not None
    ]
    id_related_results = [
        {
            **r,
            "chunk_index": r.get("metadata", {}).get("chunk_index"),
            "metadata_id": r.get("metadata", {}).get("id"),
        }
        for r in full_array
        if r.get("metadata", {}).get("page") is None
    ]

    sorted_page_data = sorted(
            page_related_results,
            key=lambda x: (
                x["source"] or "",
                x["page"] or 0,
                x["chunk_index"] if x["chunk_index"] is not None else 0,
            )
        )
    sorted_id_data = sorted(
            id_related_results,
            key=lambda x: (
                x["metadata_id"] if x["metadata_id"] is not None else "",
                x["chunk_index"] if x["chunk_index"] is not None else 0,
            )
        )


    seen = set()
    final_results = []
    for item in sorted_page_data + sorted_id_data:
        key = item.get("id")
        if key is None:
            raise ValueError("fetch_nearest_chunks_pinecone: id is None.")
        if key not in seen:
            seen.add(key)
            final_results.append(item)

    return final_results
