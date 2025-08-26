from pathlib import Path
import weaviate
from weaviate.embedded import EmbeddedOptions
import os
# import the WeaviateClient class here
from weaviate import WeaviateClient
from unstructured.partition.pdf import partition_pdf

import logging

logging.basicConfig(level=logging.INFO)


class ContentExtractor:
    def __init__(self, document_path: Path):
        self.document_path = document_path
        self.current_section = None  # Keep track of the current section being processed
        self.have_extracted_content = (
            False  # Keep track of whether the content has been extracted
        )
        self.in_content_section = (
            False  # Keep track of whether we're inside the Content section
        )
        self.page_end = False  # Keep track of whether we've reached the end of a page
        self.texts = ""  # Keep track of the extracted content text
        self.text_list = []

    def process(self, element) -> bool:
        if element.category == "Title" or element.category == "ListItem":
            self.concate_text(element.text)

            # if self.current_section == "NarrativeText":
            #     self.in_content_section = True
            #     return True

            # if self.in_content_section:
            #     return False

        if element.category == "NarrativeText":
            if "Page" in element.text:
                self.page_end = True
            else:
                self.in_content_section = True
                self.concate_text(element.text)

        return True

    def set_section(self, text):
        self.current_section = text
        logging.info(f"Current section: {self.current_section}")
        
    def concate_text(self, text):
        self.texts += "\n" + text

    def consume_content_text(self, text):
        logging.info(f"Content part extracted: {text}")
        self.texts.append(text)

    def consume_elements(self, elements):
        page_no = 0
        for element in elements:
            should_continue = self.process(element)

            if self.page_end:
                page_no += 1
                data_struct = {
                    "page_number": page_no,  # Store the current page number
                    "document": self.document_path.name,  # Store the document name
                    "content": self.content()
                }
                self.text_list.append(data_struct)
                self.reset_content()
                self.page_end = False
                continue

    def content(self) -> str:
        return self.texts
    
    def reset_content(self):
        self.texts = ""

    def get_processed_content(self) -> list[dict]:
        return self.text_list

weaviate_schema = {
    "class": "Page",
    "properties": [
        {
            "name": "document",
            "dataType": ["text"],
            "description": "Original file name or URL",
            # "moduleConfig": {
            #     "text2vec-ollama": {
            #         "skip": False,
            #         "vectorizePropertyName": False
            #     }
            # }
        },
        {
            "name": "page_number",
            "dataType": ["int"],
            "description": "Page number in the original document"
        },
        {
            "name": "content",
            "dataType": ["text"],
            "description": "Main content of the file"
        }
    ],
    "moduleConfig": {
        "generative-ollama": {
            "model": "llama3.2",
            "api_endpoint": "http://host.docker.internal:11434",
            "type": "text"
        },
        "text2vec-ollama": {
            "model": "nomic-embed-text",
            "api_endpoint": "http://host.docker.internal:11434",
            "type": "text"
        }
    }
}

def partition_pdf_file(file_path: str) -> any:
    """Partitions a PDF file into its constituent elements.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        list: A list of partitioned elements from the PDF.
    """
    elements = partition_pdf(filename=file_path)
    return elements
    
def create_schema(client) -> None:
    """Create a Weaviate schema for the Document class.
    """
    client.collections.delete_all()
    client.collections.create_from_dict(weaviate_schema)
    return None

def store_data_in_weaviate(client, data_objects: list[dict]) -> None:
    """Store the processed data objects in Weaviate.
    """
    pages = client.collections.get("Page")
    with pages.batch.fixed_size(batch_size=100) as batch:
        for data_object in data_objects:
            batch.add_object(data_object)

if __name__ == "__main__":
    
    client = weaviate.connect_to_local()
    # create_schema(client)
    # data_folder = "../data"
    # path = Path("/home/kosala/git-repos/contract_inspect/data/Oracle_contract.pdf")

    # print(f"Processing {path.name}...")
    # elements = partition_pdf(
    #     filename=path,
    #     infer_table_structure=True,
    #     include_page_breaks=False,
    #     unique_element_ids=True
    # )
    
    # content_extractor = ContentExtractor(path)
    # content_extractor.consume_elements(elements)
    
    # store_data_in_weaviate(
    #     client,
    #     content_extractor.get_processed_content()
    # )   
    pages = client.collections.get("Page")
    response = pages.query.bm25(
        query="oracle",
        limit=2,
    )
    print(response)
    client.close()
