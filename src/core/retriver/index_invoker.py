import sys
sys.path.append("/home/kosala/git-repos/contract_inspect/")
import weaviate
from pathlib import Path
from src.core.retriver.util import index_lib 
from src.core.retriver.util.index_lib import ContentExtractor
from src.core.config import WEAVIATE_SCHEMA
from src.core.config import DATA_FOLDER, METADATA_CONFIG_PATH
from src.sp_adapters.weaviate_adapter import WeaviateVectorDBAdapter
import yaml

if __name__ == "__main__":
    # read yml file
    config = yaml.safe_load(open(METADATA_CONFIG_PATH))
    # initialize vector db client
    weaviate_adapter = WeaviateVectorDBAdapter()
    weaviate_adapter.connect()
    index_lib.init(adapter=weaviate_adapter)
    # create schema : delete the schema before creating it
    index_lib.create_schema(WEAVIATE_SCHEMA)

    for agreenment_metadata in config.get("service_agreements"):
        path = Path(DATA_FOLDER, agreenment_metadata.get("file_name"))

        # partition the pdf to create a flexible data structure for indexing
        print(f"Processing {path.name}...")
        elements = index_lib.partition_pdf(
            filename=path,
            infer_table_structure=True,
            include_page_breaks=False,
            unique_element_ids=True
        )

        # extract content from the partitioned elements
        content_extractor = ContentExtractor(path, agreenment_metadata)
        content_extractor.consume_elements(elements)

        # store the extracted content in Vector DB
        index_lib.store_data_in_vector_db(
            content_extractor.get_processed_content(),
            WEAVIATE_SCHEMA["class"]
        )   
    weaviate_adapter.close()
    index_lib.clear_vector_db_adapter()