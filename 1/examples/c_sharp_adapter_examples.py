#!/usr/bin/env python3
# examples/csharp_adapter_example.py

from adapters.CSharpAdapter import CSharpAdapter


# Example 1: Simple C# code execution
def simple_csharp_example():
    print("\n--- CSharp Adapter Example 1: Simple code execution ---")
    adapter = CSharpAdapter({})

    code = """
using System;

public class Program {
    public static void Main() {
        Console.WriteLine("Hello from C#!");
        return 0;
    }
}
"""
    adapter.code(code)
    result = adapter.execute()
    print(f"C# execution result: {result}")


# Example 2: C# code with input processing
def input_processing_example():
    print("\n--- CSharp Adapter Example 2: Input processing ---")
    adapter = CSharpAdapter({})

    code = """
using System;
using System.Text.Json;

public class Program {
    public static void Main() {
        string input = Console.ReadLine();
        var data = JsonSerializer.Deserialize<dynamic>(input);
        int value = data.GetProperty("value").GetInt32();
        Console.WriteLine($"Processed value: {value * 2}");
        return 0;
    }
}
"""
    adapter.code(code)
    result = adapter.execute({"value": 21})
    print(f"C# processing result: {result}")


# Example 3: C# with external dependencies
def external_dependencies_example():
    print("\n--- CSharp Adapter Example 3: External dependencies ---")
    adapter = CSharpAdapter({})

    code = """
using System;
using System.Linq;
using System.Collections.Generic;

public class Program {
    public static void Main() {
        List<int> numbers = new List<int> { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
        
        var evenNumbers = numbers.Where(n => n % 2 == 0).ToList();
        Console.WriteLine($"Even numbers: {string.Join(", ", evenNumbers)}");
        
        var sum = numbers.Sum();
        Console.WriteLine($"Sum: {sum}");
        
        return 0;
    }
}
"""
    adapter.code(code)
    result = adapter.execute()
    print(f"C# with LINQ result: {result}")


if __name__ == "__main__":
    print("Running CSharpAdapter examples:")
    simple_csharp_example()
    input_processing_example()
    external_dependencies_example()