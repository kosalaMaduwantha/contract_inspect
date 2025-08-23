from unstructured.partition.pdf import partition_pdf

def partition_pdf_file(file_path: str) -> any:
    """Partitions a PDF file into its constituent elements.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        list: A list of partitioned elements from the PDF.
    """
    elements = partition_pdf(filename=file_path)
    return elements

if __name__ == "__main__":
    file_path = "/home/kosala/git-repos/contract_inspect/data/Oracle_contract.pdf"
    partitioned_elements = partition_pdf_file(file_path)
    print(partitioned_elements)