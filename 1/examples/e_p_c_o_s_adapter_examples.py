#!/usr/bin/env python3
# examples/epcos_adapter_example.py

from adapters.epcos_adapter import EPCOSAdapter


# Example 1: Basic EPCOS document
def basic_epcos_example():
    print("\n--- EPCOS Adapter Example 1: Basic document ---")
    adapter = EPCOSAdapter({})

    adapter.document_begin()
    adapter.add_text("EPCOS Test Document")
    adapter.add_line()
    adapter.add_text("This is a simple test of the EPCOS adapter.")
    adapter.document_end()

    result = adapter.execute()
    print(f"EPCOS output:\n{result}")


# Example 2: Document with formatting
def formatted_document_example():
    print("\n--- EPCOS Adapter Example 2: Formatted document ---")
    adapter = EPCOSAdapter({})

    adapter.document_begin()
    adapter.add_text("EPCOS Formatted Document", bold=True, size=14)
    adapter.add_line()
    adapter.add_text("This text is ", bold=False)
    adapter.add_text("bold", bold=True)
    adapter.add_text(" and this is ", bold=False)
    adapter.add_text("italic", italic=True)
    adapter.add_line()
    adapter.add_text("This is a different size", size=12)
    adapter.document_end()

    result = adapter.execute()
    print(f"Formatted EPCOS output:\n{result}")


# Example 3: Document with tables and structure
def structured_document_example():
    print("\n--- EPCOS Adapter Example 3: Structured document ---")
    adapter = EPCOSAdapter({})

    adapter.document_begin()
    adapter.add_text("EPCOS Document With Structure", bold=True, size=16)
    adapter.add_line(2)

    adapter.add_text("Section 1: Introduction", bold=True, size=12)
    adapter.add_line()
    adapter.add_text("This is the introduction section of our document.")
    adapter.add_line(2)

    adapter.add_text("Section 2: Data Table", bold=True, size=12)
    adapter.add_line()

    adapter.table_begin(3)
    adapter.table_header(["Name", "Value", "Description"])
    adapter.table_row(["Item 1", "10.5", "First test item"])
    adapter.table_row(["Item 2", "20.7", "Second test item"])
    adapter.table_row(["Item 3", "15.3", "Third test item"])
    adapter.table_end()

    adapter.add_line(2)
    adapter.add_text("End of document", italic=True)
    adapter.document_end()

    result = adapter.execute()
    print(f"Structured EPCOS output:\n{result}")


if __name__ == "__main__":
    print("Running EPCOSAdapter examples:")
    basic_epcos_example()
    formatted_document_example()
    structured_document_example()