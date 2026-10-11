from retriever import retrieve


def evaluate_retrieval(eval_cases, k=3):
    hits = 0
    reciprocal_ranks = []

    for case in eval_cases:
        results = retrieve(case["query"], limit=k)

        retrieved_headings = [
            row[1] for row in results
        ]

        rank = None

        for i, heading in enumerate(retrieved_headings):
            if heading.startswith(case["expected_section"]):
                rank = i + 1
                break

        if rank is not None:
            hits += 1
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0)

        print(f"\nQuery: {case['query']}")
        print(f"Expected: {case['expected_section']}")
        print(f"Retrieved: {retrieved_headings}")
        print(f"Rank: {rank if rank else 'NOT FOUND'}")

    total = len(eval_cases)

    hit_rate = hits / total
    mrr = sum(reciprocal_ranks) / total

    print("\n===== EVALUATION RESULTS =====")
    print(f"Hit Rate @{k}: {hit_rate:.2%}")
    print(f"MRR @{k}: {mrr:.4f}")

def inspect_similarity_scores(positive_cases, negative_queries):
    print("\n=== POSITIVE QUERIES ===")

    for case in positive_cases:
        results = retrieve(case["query"], limit=3)

        print(f"\nQuery: {case['query']}")

        for row in results:
            _, heading, _, similarity = row
            print(f"  {similarity:.4f} | {heading}")

    print("\n=== NEGATIVE QUERIES ===")

    for query in negative_queries:
        results = retrieve(query, limit=3)

        print(f"\nQuery: {query}")

        for row in results:
            _, heading, _, similarity = row
            print(f"  {similarity:.4f} | {heading}")



eval_cases = [
    {
        "query": "My company laptop is damaged. What should I do?",
        "expected_section": "8."
    },
    {
        "query": "How much leave can employees take?",
        "expected_section": "5."
    },
    {
        "query": "What happens when an employee resigns?",
        "expected_section": "9."
    },
    {
        "query": "What are the rules around workplace harassment?",
        "expected_section": "3."
    },
    {
        "query": "How do I request a new company laptop?",
        "expected_section": "7."
    },
    {
        "query": "What are the company's core values?",
        "expected_section": "1."
    },
    {
        "query": "What are the rules for professional conduct?",
        "expected_section": "4."
    },
    {
        "query": "How does the company handle employee compensation?",
        "expected_section": "6."
    }
]

negative_queries = [
    "What is the refund policy for business class flights to Japan?",
    "How do I apply for a tourist visa to Australia?",
    "What is the company's policy on cryptocurrency trading?",
    "How much does a Tesla Model 3 cost?",
    "What is the recipe for chicken biryani?",
    "Does the company provide free gym memberships?",
    "What are the parking charges at Bangalore airport?",
    "Can employees bring their pets to the office?"
]

# evaluate_retrieval(eval_cases, k=3)

inspect_similarity_scores(eval_cases, negative_queries)
