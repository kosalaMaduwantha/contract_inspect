import sys
sys.path.append("/home/kosala/git-repos/contract_inspect/")  # add parent directory to the path for imports
import logging
from pathlib import Path
from datetime import datetime
from pathlib import Path
from weaviate.embedded import EmbeddedOptions
from unstructured.partition.pdf import partition_pdf
from src.core.config import WEAVIATE_SCHEMA
from typing import Any, Optional

# Module-level variable. Use get_vector_db_adapter() to access safely.
vector_db_adapter: Optional[Any] = None

# logger config
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ContentExtractor:
    def __init__(self, document_path: Path, metadata: dict):
        self.document_path = document_path
        self.metadata = metadata
        self.page_end = False  # Keep track of whether we've reached the end of a page
        self.texts = ""  # Keep track of the extracted content text
        self.text_list = []

    def process(self, element) -> bool:
        """Process a single element and extract its content.

        Args:
            element (Element): The element to process.

        Returns:
            bool: Whether the processing was successful.
        """
        if element.category == "Title" or element.category == "ListItem":
            self.concate_text(element.text)
            
        if element.category == "NarrativeText":
            if "Page" in element.text:
                self.page_end = True
            else:
                self.concate_text(element.text)

        return True
        
    def concate_text(self, text):
        self.texts += "\n" + text

    def consume_content_text(self, text):
        logger.info(f"Content part extracted: {text}")
        self.texts.append(text)

    def consume_elements(self, elements) -> None:
        """Consume a list of elements and extract their content.

        Args:
            elements (list): A list of elements to process.
        """
        page_no = 0
        for element in elements:
            self.process(element)

            if self.page_end:
                page_no += 1 # track the page number
                # dt = datetime.strptime(str(self.metadata.get("effective_date")), "%Y-%m-%d")
                data_struct = { # NOTE: this has to be changed according to the collection schema
                    "page_number": page_no,  
                    "document": self.document_path.name,  
                    "content": self.content(),
                    "effective_date": self.metadata.get("effective_date").strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                self.text_list.append(data_struct)
                self.reset_content() # reset the self.texts variable to store content for the next page
                self.page_end = False # reset page end flag
                continue

    def content(self) -> str:
        return self.texts
    
    def reset_content(self):
        self.texts = ""

    def get_processed_content(self) -> list[dict]:
        return self.text_list

def partition_pdf_file(file_path: str) -> any:
    """Partitions a PDF file into its constituent elements.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        list: A list of partitioned elements from the PDF.
    """
    elements = partition_pdf(filename=file_path)
    return elements

def init(adapter: Any) -> None:
    """Initialize the module-level vector DB adapter.

    Args:
        adapter: An object that implements the expected vector DB interface
                 (must provide the necessary methods for interaction).
    """
    global vector_db_adapter
    vector_db_adapter = adapter

def _get_vector_db_adapter() -> Any:
    """Return the initialized vector DB adapter or raise RuntimeError if missing."""
    if vector_db_adapter is None:
        raise RuntimeError("Vector DB adapter not initialized. Call init(adapter) first.")
    return vector_db_adapter

def clear_vector_db_adapter() -> None:
    """Clear the module-level adapter (useful for tests)."""
    global vector_db_adapter
    vector_db_adapter = None
    
def create_schema(schema: dict) -> None:
    """Create a Vector DB schema for the Document class.
    """
    vector_db_adapter = _get_vector_db_adapter()
    vector_db_adapter.drop_all_collections()
    vector_db_adapter.create_schema(schema)
    return None

def store_data_in_vector_db(data_objects: list[dict], collection: str) -> None:
    """Store the processed data objects in Vector DB.
    """
    vector_db_adapter = _get_vector_db_adapter()
    vector_db_adapter.insert_objects(collection, data_objects)
    return None