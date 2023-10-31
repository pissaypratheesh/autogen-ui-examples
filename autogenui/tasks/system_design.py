def extract_tasks():
    tasks = [
        """
        Assume you are building a system design for a company, give functional and non-functional requirements
        and brainstorm on all possible stuffs to keep in mind (highlight main ones) and
        also write the content in a markdown file by name functions.md. Question: Hotstar backend system design
        """,
        """
        For the same, give me the Requests Per Second, storage, bandwidth requirements assuming 1 billion DAUs with explanation,
        also give a generic Python code that takes in DAUs but don't execute it and prints other details
        and also write the content in a markdown file by name calc.md
        """,
        """
        For the same, give a simple intro of the top-level HLD with detailed data flow using the latest technologies with Mermaid code
        and also write the content in a markdown file by name hld.md
        """,
        """
        For the same, create an Entity-Relationship (ER) diagram with detailed DB schema with relationships,
        sample APIs (with data types) and major services
        and also write the content in a markdown file by name lld.md
        """,
        """
        For the same, explain the low-level design of critical services involved and possible algorithms
        and also write the content in a markdown file by name algos.md
        """,
        """
        For the same, list all possible single point of failures and solutions for the same
        and also write the content in a markdown file by name failures.md
        """,
        """
        Reflect on the sequence and create a recipe containing all the above steps necessary
        and name it. Suggest well-documented, generalized Python function(s) to perform similar tasks for coding steps in the future.
        Make sure coding steps and non-coding steps are never mixed in one function.
        In the docstring of the function(s), clarify what non-coding steps are needed to use the language skill of the assistant.
        """
    ]
    return tasks