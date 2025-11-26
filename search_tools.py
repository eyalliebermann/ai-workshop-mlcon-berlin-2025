from typing import Any, Dict, List


class SearchTools:
    """
    A collection of utilities for searching and modifying an index.

    This class wraps an index object and provides convenient methods
    for searching and adding entries with predefined metadata.
    """

    def __init__(self, index: Any) -> None:
        """
        Initialize the SearchTools instance.

        Args:
            index (Any): An index-like object that supports `search()` and `append()`.
        """
        self.index = index

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search the index for documents matching the given query.

        This function queries the index with a fixed course filter and 
        predefined boost weights for specific fields.

        Args:
            query (str): The search query string.

        Returns:
            List[Dict[str, Any]]: A list of search result objects returned 
            by `index.search()`. Each result is represented as a dictionary.
        """
        boost: Dict[str, float] = {"question": 3.0, "section": 0.5}

        results = self.index.search(
            query=query,
            filter_dict={"course": "data-engineering-zoomcamp"},
            boost_dict=boost,
            num_results=5,
        )

        return results

    def add_entry(self, question: str, answer: str) -> None:
        """
        Add a new question–answer entry to the index.

        This function constructs a document with the provided question
        and answer, tags it as user-added, and appends it to the index
        under the 'data-engineering-zoomcamp' course.

        Args:
            question (str): The question text to store.
            answer (str): The corresponding answer text.

        Returns:
            None
        """
        doc: Dict[str, Any] = {
            "question": question,
            "text": answer,
            "section": "user added",
            "course": "data-engineering-zoomcamp",
        }

        self.index.append(doc)
