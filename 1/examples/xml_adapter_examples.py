#!/usr/bin/env python3
# examples/xml_adapter_example.py

from adapters.xml_adapter import XMLAdapter

# Example 1: Simple XML document
def simple_xml_example():
    print("\n--- XML Adapter Example 1: Simple document ---")
    adapter = XMLAdapter({})
    
    # Start building the XML document
    adapter.document("inventory")
    
    # Add some items
    adapter.element("item", attributes={"id": "1001"})
    adapter.element("name", "Laptop")
    adapter.element("category", "Electronics")
    adapter.element("price", "999.99")
    adapter.element("quantity", "15")
    adapter.end_element()  # Close item
    
    adapter.element("item", attributes={"id": "1002"})
    adapter.element("name", "Smartphone")
    adapter.element("category", "Electronics")
    adapter.element("price", "699.99")
    adapter.element("quantity", "28")
    adapter.end_element()  # Close item
    
    adapter.element("item", attributes={"id": "1003"})
    adapter.element("name", "Headphones")
    adapter.element("category", "Accessories")
    adapter.element("price", "149.99")
    adapter.element("quantity", "35")
    adapter.end_element()  # Close item
    
    # Get the resulting XML
    result = adapter.execute()
    print(f"Simple XML Document:\n{result}")

# Example 2: XML with namespaces and advanced structure
def advanced_xml_example():
    print("\n--- XML Adapter Example 2: Namespaces and advanced structure ---")
    adapter = XMLAdapter({})
    
    # Define namespaces
    namespaces = {
        "urn:books": "bk",
        "urn:authors": "auth",
        "http://www.w3.org/2001/XMLSchema-instance": "xsi"
    }
    
    # Start building XML with namespaces
    adapter.document("bk:library", namespaces=namespaces, attributes={
        "xsi:schemaLocation": "urn:books books.xsd"
    })
    
    # Add a section for books
    adapter.element("bk:books")
    
    # Book 1
    adapter.element("bk:book", attributes={"id": "B001", "format": "hardcover"})
    adapter.element("bk:title", "The Great Adventure")
    adapter.element("bk:publication")
    adapter.element("bk:publisher", "Global Books")
    adapter.element("bk:year", "2022")
    adapter.element("bk:isbn", "978-3-16-148410-0")
    adapter.end_element()  # Close publication
    
    adapter.element("auth:author", attributes={"id": "A101"})
    adapter.element("auth:name", "John Smith")
    adapter.element("auth:nationality", "American")
    adapter.end_element()  # Close author
    
    adapter.element("bk:price", "24.99", attributes={"currency": "USD"})
    adapter.end_element()  # Close book
    
    # Book 2
    adapter.element("bk:book", attributes={"id": "B002", "format": "paperback"})
    adapter.element("bk:title", "Mystery in Paris")
    adapter.element("bk:publication")
    adapter.element("bk:publisher", "European Press")
    adapter.element("bk:year", "2021")
    adapter.element("bk:isbn", "978-1-23-456789-0")
    adapter.end_element()  # Close publication
    
    adapter.element("auth:author", attributes={"id": "A202"})
    adapter.element("auth:name", "Marie Dubois")
    adapter.element("auth:nationality", "French")
    adapter.end_element()  # Close author
    
    adapter.element("bk:price", "18.50", attributes={"currency": "EUR"})
    adapter.end_element()  # Close book
    
    adapter.end_element()  #