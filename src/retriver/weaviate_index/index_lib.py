import sys
sys.path.append("/home/kosala/git-repos/contract_inspect/")  # add parent directory to the path for imports
import logging
from pathlib import Path
from weaviate.embedded import EmbeddedOptions
from unstructured.partition.pdf import partition_pdf
from src.retriver.config import WEAVIATE_SCHEMA

# logger config
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ContentExtractor:
    def __init__(self, document_path: Path):
        self.document_path = document_path
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
                data_struct = { # NOTE: this has to be changed according to the collection schema
                    "page_number": page_no,  
                    "document": self.document_path.name,  
                    "content": self.content()
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
    
def create_schema(client, schema: dict) -> None:
    """Create a Weaviate schema for the Document class.
    """
    client.collections.delete_all()
    client.collections.create_from_dict(schema)
    return None

def store_data_in_weaviate(client, data_objects: list[dict], collection: str) -> None:
    """Store the processed data objects in Weaviate.
    """
    pages = client.collections.get(collection)
    with pages.batch.fixed_size(batch_size=100) as batch:
        for data_object in data_objects:
            batch.add_object(data_object)