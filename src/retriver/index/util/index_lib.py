import sys
sys.path.append("/home/kosala/git-repos/contract_inspect/")  # add parent directory to the path for imports
import logging
from datetime import datetime
from pathlib import Path
from weaviate.embedded import EmbeddedOptions
from unstructured.partition.pdf import partition_pdf
from src.retriver.config import WEAVIATE_SCHEMA

# logger config
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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