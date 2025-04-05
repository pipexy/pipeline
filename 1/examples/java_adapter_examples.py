#!/usr/bin/env python3
# examples/java_adapter_example.py

from adapters.JavaAdapter import JavaAdapter


# Example 1: Simple Java program
def simple_java_example():
    print("\n--- Java Adapter Example 1: Simple program ---")
    adapter = JavaAdapter({})

    code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
    }
}
"""
    adapter.code(code)
    result = adapter.execute()
    print(f"Java execution result: {result}")


# Example 2: Java program with input processing
def input_processing_example():
    print("\n--- Java Adapter Example 2: Input processing ---")
    adapter = JavaAdapter({})

    code = """
import java.util.Scanner;
import org.json.JSONObject;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String input = scanner.nextLine();
        
        try {
            JSONObject json = new JSONObject(input);
            int value = json.getInt("value");
            System.out.println("Processed value: " + (value * 2));
        } catch (Exception e) {
            System.err.println("Error processing input: " + e.getMessage());
        }
    }
}
"""
    adapter.code(code)
    result = adapter.execute({"value": 21})
    print(f"Java processing result: {result}")


# Example 3: Java with collections and streams
def collections_streams_example():
    print("\n--- Java Adapter Example 3: Collections and streams ---")
    adapter = JavaAdapter({})

    code = """
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class Main {
    public static void main(String[] args) {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
        
        // Filter even numbers and calculate their sum
        int sum = numbers.stream()
                         .filter(n -> n % 2 == 0)
                         .mapToInt(Integer::intValue)
                         .sum();
        
        System.out.println("Numbers: " + numbers);
        System.out.println("Sum of even numbers: " + sum);
        
        // Transform to strings and join
        String joined = numbers.stream()
                              .map(n -> n.toString())
                              .collect(Collectors.joining(", "));
        
        System.out.println("Joined numbers: " + joined);
    }
}
"""
    adapter.code(code)
    result = adapter.execute()
    print(f"Java collections and streams result:\n{result}")


if __name__ == "__main__":
    print("Running JavaAdapter examples:")
    simple_java_example()
    input_processing_example()
    collections_streams_example()