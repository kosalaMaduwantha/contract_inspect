import weaviate
from pathlib import Path
from index_lib import (
    ContentExtractor, 
    create_schema, 
    partition_pdf, 
    store_data_in_weaviate
)
from config import WEAVIATE_SCHEMA

if __name__ == "__main__":
    client = weaviate.connect_to_local()
    
    # create schema : delete the schema before creating it 
    create_schema(client, WEAVIATE_SCHEMA)
    data_folder = "../data"
    path = Path("/home/kosala/git-repos/contract_inspect/data/Oracle_contract.pdf")

    # partition the pdf to create a flexible data structure for indexing
    print(f"Processing {path.name}...")
    elements = partition_pdf(
        filename=path,
        infer_table_structure=True,
        include_page_breaks=False,
        unique_element_ids=True
    )

    # extract content from the partitioned elements
    content_extractor = ContentExtractor(path)
    content_extractor.consume_elements(elements)

    # store the extracted content in Weaviate
    store_data_in_weaviate(
        client,
        content_extractor.get_processed_content(),
        WEAVIATE_SCHEMA["class"]
    )   
    client.close()