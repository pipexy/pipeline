#!/usr/bin/env python3
# examples/go_adapter_example.py

from adapters.GoAdapter import GoAdapter


# Example 1: Simple Go program
def simple_go_example():
    print("\n--- Go Adapter Example 1: Simple program ---")
    adapter = GoAdapter({})

    code = """
package main

import "fmt"

func main() {
    fmt.Println("Hello from Go!")
}
"""
    adapter.code(code)
    result = adapter.execute()
    print(f"Go execution result: {result}")


# Example 2: Go program with input
def input_go_example():
    print("\n--- Go Adapter Example 2: Processing input ---")
    adapter = GoAdapter({})

    code = """
package main

import (
    "encoding/json"
    "fmt"
    "io/ioutil"
    "os"
)

func main() {
    // Read input from stdin
    input, err := ioutil.ReadAll(os.Stdin)
    if err != nil {
        fmt.Println("Error reading input:", err)
        return
    }
    
    // Parse JSON input
    var data map[string]interface{}
    if err := json.Unmarshal(input, &data); err != nil {
        fmt.Println("Error parsing JSON:", err)
        return
    }
    
    // Process the input
    if val, ok := data["value"].(float64); ok {
        result := val * 2
        fmt.Printf("Processed value: %.2f", result)
    } else {
        fmt.Println("Invalid input format")
    }
}
"""
    adapter.code(code)
    result = adapter.execute({"value": 21.5})
    print(f"Go input processing result: {result}")


# Example 3: Go with concurrent processing
def concurrent_go_example():
    print("\n--- Go Adapter Example 3: Concurrent processing ---")
    adapter = GoAdapter({})

    code = """
package main

import (
    "fmt"
    "sync"
    "time"
)

func worker(id int, wg *sync.WaitGroup) {
    defer wg.Done()
    fmt.Printf("Worker %d starting\\n", id)
    time.Sleep(time.Second)
    fmt.Printf("Worker %d done\\n", id)
}

func main() {
    const numWorkers = 3
    
    var wg sync.WaitGroup
    wg.Add(numWorkers)
    
    fmt.Println("Starting concurrent workers...")
    
    for i := 1; i <= numWorkers; i++ {
        go worker(i, &wg)
    }
    
    wg.Wait()
    fmt.Println("All workers completed")
}
"""
    adapter.code(code)
    result = adapter.execute()
    print(f"Go concurrent execution result:\n{result}")


if __name__ == "__main__":
    print("Running GoAdapter examples:")
    simple_go_example()
    input_go_example()
    concurrent_go_example()