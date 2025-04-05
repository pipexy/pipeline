#!/usr/bin/env python3
# examples/javascript_adapter_example.py

from adapters.JavaScriptAdapter import JavaScriptAdapter


# Example 1: Simple JavaScript code
def simple_js_example():
    print("\n--- JavaScript Adapter Example 1: Simple code ---")
    adapter = JavaScriptAdapter({})

    code = """
console.log('Hello from JavaScript!');
const result = 5 + 7;
console.log(`5 + 7 = ${result}`);
"""
    adapter.code(code)
    result = adapter.execute()
    print(f"JavaScript execution result:\n{result}")


# Example 2: Processing JSON input
def json_processing_example():
    print("\n--- JavaScript Adapter Example 2: JSON processing ---")
    adapter = JavaScriptAdapter({})

    code = """
// Read input
const input = JSON.parse(process.argv[2]);

// Process data
const processed = {
    original: input,
    doubled: input.value * 2,
    text: `Processed: ${input.text}`,
    timestamp: new Date().toISOString()
};

// Output result
console.log(JSON.stringify(processed, null, 2));
"""
    adapter.code(code)
    result = adapter.execute({"value": 21, "text": "Hello JS"})
    print(f"JavaScript JSON processing result:\n{result}")


# Example 3: Async operations
def async_js_example():
    print("\n--- JavaScript Adapter Example 3: Async operations ---")
    adapter = JavaScriptAdapter({})

    code = """
// Function that returns a promise
function delay(ms, value) {
    return new Promise(resolve => {
        console.log(`Waiting ${ms}ms for ${value}...`);
        setTimeout(() => {
            console.log(`Done waiting for ${value}`);
            resolve(value);
        }, ms);
    });
}

// Async function using promises
async function runSequence() {
    console.log('Starting async operations...');
    
    const result1 = await delay(1000, 'First operation');
    const result2 = await delay(500, 'Second operation');
    const result3 = await delay(300, 'Third operation');
    
    console.log('All operations completed!');
    console.log(`Results: ${result1}, ${result2}, ${result3}`);
}

// Run the async function
runSequence().then(() => {
    console.log('Async example finished.');
});
"""
    adapter.code(code)
    result = adapter.execute()
    print(f"JavaScript async operations result:\n{result}")


if __name__ == "__main__":
    print("Running JavaScriptAdapter examples:")
    simple_js_example()
    json_processing_example()
    async_js_example()