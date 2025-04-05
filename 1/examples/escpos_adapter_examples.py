#!/usr/bin/env python3
# examples/escpos_adapter_example.py

from adapters.escpos_adapter import ESCPOSAdapter


# Example 1: Basic receipt
def basic_receipt_example():
    print("\n--- ESCPOS Adapter Example 1: Basic receipt ---")
    adapter = ESCPOSAdapter({})

    adapter.text_center()
    adapter.text_bold(True)
    adapter.text("SAMPLE RECEIPT")
    adapter.text_bold(False)
    adapter.line_feed()
    adapter.text_left()
    adapter.text("Date: 2023-06-15 10:30 AM")
    adapter.line_feed(2)

    adapter.text_left()
    adapter.text("Item 1               $10.00")
    adapter.text("Item 2                $5.50")
    adapter.text("Item 3               $15.75")
    adapter.line_feed()

    adapter.text_right()
    adapter.text_bold(True)
    adapter.text("Total:              $31.25")
    adapter.text_bold(False)
    adapter.line_feed(2)

    adapter.text_center()
    adapter.text("Thank you for your purchase!")
    adapter.line_feed(3)
    adapter.cut()

    result = adapter.execute()
    print(f"ESCPOS commands generated:\n{result}")


# Example 2: Receipt with barcode and QR code
def barcode_receipt_example():
    print("\n--- ESCPOS Adapter Example 2: Receipt with barcode ---")
    adapter = ESCPOSAdapter({})

    adapter.text_center()
    adapter.text_bold(True)
    adapter.text("SAMPLE RECEIPT WITH CODES")
    adapter.text_bold(False)
    adapter.line_feed(2)

    adapter.text_left()
    adapter.text("Product: Sample Product")
    adapter.text("SKU: ABC123")
    adapter.line_feed()

    adapter.text_center()
    adapter.text("Barcode:")
    adapter.barcode("1234567890", "CODE39")
    adapter.line_feed()

    adapter.text("QR Code:")
    adapter.qr_code("https://example.com/product/ABC123")
    adapter.line_feed(2)

    adapter.text_center()
    adapter.text("Scan for more information")
    adapter.line_feed(3)
    adapter.cut()

    result = adapter.execute()
    print(f"ESCPOS commands with codes:\n{result}")


# Example 3: Receipt with image and formatting
def formatted_receipt_example():
    print("\n--- ESCPOS Adapter Example 3: Formatted receipt ---")
    adapter = ESCPOSAdapter({})

    adapter.text_center()
    adapter.image("/path/to/logo.png")  # Path would be updated to actual image
    adapter.line_feed()

    adapter.text_bold(True)
    adapter.text_double_height(True)
    adapter.text("COMPANY NAME")
    adapter.text_double_height(False)
    adapter.text_bold(False)
    adapter.line_feed()

    adapter.text("123 Main Street")
    adapter.text("Anytown, ST 12345")
    adapter.text("Tel: (555) 123-4567")
    adapter.line_feed(2)

    adapter.text_left()
    adapter.text_underline(True)
    adapter.text("ORDER SUMMARY")
    adapter.text_underline(False)
    adapter.line_feed()

    adapter.text("Item 1               $10.00")
    adapter.text("Item 2               $15.00")
    adapter.text("Discount             -$5.00")
    adapter.line_feed()

    adapter.text_right()
    adapter.text_bold(True)
    adapter.text("Total:              $20.00")
    adapter.text_bold(False)
    adapter.line_feed(2)

    adapter.text_center()
    adapter.barcode("ORDER123456", "CODE39")
    adapter.line_feed(3)
    adapter.cut()

    result = adapter.execute()
    print(f"Formatted ESCPOS commands:\n{result}")


if __name__ == "__main__":
    print("Running ESCPOSAdapter examples:")
    basic_receipt_example()
    barcode_receipt_example()
    formatted_receipt_example()