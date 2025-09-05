import sys
sys.path.append("/home/kosala/git-repos/contract_inspect/")
import weaviate
from pathlib import Path
from retriver.util.index_lib import (
    create_schema, 
    partition_pdf, 
    store_data_in_weaviate
)
from src.core.retriver.util.index_lib import ContentExtractor
from core.config import WEAVIATE_SCHEMA
from core.config import DATA_FOLDER, METADATA_CONFIG_PATH
import yaml

if __name__ == "__main__":
    # read yml file
    config = yaml.safe_load(open(METADATA_CONFIG_PATH))
    client = weaviate.connect_to_local()
    # create schema : delete the schema before creating it 
    create_schema(client, WEAVIATE_SCHEMA)
    
    for agreenment_metadata in config.get("service_agreements"):
        path = Path(DATA_FOLDER, agreenment_metadata.get("file_name"))

        # partition the pdf to create a flexible data structure for indexing
        print(f"Processing {path.name}...")
        elements = partition_pdf(
            filename=path,
            infer_table_structure=True,
            include_page_breaks=False,
            unique_element_ids=True
        )

        # extract content from the partitioned elements
        content_extractor = ContentExtractor(path, agreenment_metadata)
        content_extractor.consume_elements(elements)

        # store the extracted content in Weaviate
        store_data_in_weaviate(
            client,
            content_extractor.get_processed_content(),
            WEAVIATE_SCHEMA["class"]
        )   
    client.close()