from pathlib import Path
import weaviate
from weaviate.embedded import EmbeddedOptions
import os
# import the WeaviateClient class here
from weaviate import WeaviateClient
from unstructured.partition.pdf import partition_pdf

import logging

logging.basicConfig(level=logging.INFO)




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
