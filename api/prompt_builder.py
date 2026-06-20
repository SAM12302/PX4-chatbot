modified_prompt = """
You are a PX4 autopilot expert assistant. You help drone developers and engineers 
understand PX4 configuration, flight modes, and development. Answer clearly and 
precisely. If the answer is not in the provided context, say so — do not make 
things up.

CONTEXT:
--- Chunk 1 ---
Section: {section_1}
{text_1}

--- Chunk 2 ---
Section: {section_2}
{text_2}

--- Chunk 3 ---
Section: {section_3}
{text_3}

--- Chunk 4 ---
Section: {section_4}
{text_4}

--- Chunk 5 ---
Section: {section_5}
{text_5}

CONVERSATION HISTORY:
User: {history_user_1}
Assistant: {history_assistant_1}
User: {history_user_2}
Assistant: {history_assistant_2}

CURRENT QUESTION:
{question}

ANSWER:
"""

def build_prompt(chunks: list, history: list, question: str) -> str:
    
    context_blocks = ""
    section = ""
    count = 0
    chunk = chunks[0]
    for c in chunk:
        context_blocks += f"--- Chunk {count} ---\n"
        section += c['entity']['current_section']

        context_blocks += f"Section: {section}\n"
        # print("Context Blocks after adding section\n", context_blocks)
        context_blocks += f"{c['entity']['text']}\n\n"
        count += 1
        section = ""

    history_block = ""
    for message in history:
        role = message["role"].capitalize()
        history_block += f"{role}: {message['content']}\n"

    print("Final Context Blocks\n", context_blocks)

    prompt = f"""You are a PX4 autopilot expert assistant. You help drone developers and engineers 
understand PX4 configuration, flight modes, and development. Answer clearly and 
precisely. If the answer is not in the provided context, say so — do not make 
things up.

CONTEXT:
{context_blocks}
CONVERSATION HISTORY:
{history_block}
CURRENT QUESTION:
{question}

ANSWER:"""

    return prompt


if __name__ == "__main__":
    from api.retriever import search_embedding
    test_history = [
        {"role": "user", "content": "What is PX4?"},
        {"role": "assistant", "content": "PX4 is an open source autopilot."}
    ]
    test_question = "How do I activate offboard mode?"
    test_chunks = search_embedding(test_question)

    print(build_prompt(test_chunks, test_history, test_question))