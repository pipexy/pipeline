#!/usr/bin/env python3
# examples/ml_adapter_example.py

from adapters.ml_adapter import MLAdapter
import numpy as np
import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris

# Helper function to create a sample model
def create_sample_model(model_path):
    # Load Iris dataset
    iris = load_iris()
    X = iris.data
    y = iris.target
    
    # Train a simple model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save the model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Sample model saved to {model_path}")
    return model_path

# Example 1: Basic prediction
def basic_prediction_example():
    print("\n--- ML Adapter Example 1: Basic prediction ---")
    
    # Create a sample model if it doesn't exist
    model_path = "examples/models/iris_rf.pkl"
    if not os.path.exists(model_path):
        model_path = create_sample_model(model_path)
    
    # Initialize the adapter
    adapter = MLAdapter({})
    adapter.model(model_path)
    
    # Prepare input data (single iris flower measurements)
    input_data = np.array([[5.1, 3.5, 1.4, 0.2]])  # Should be a setosa
    
    # Make prediction
    adapter.input(input_data)
    result = adapter.execute()
    
    # Map result to iris species
    species = ["setosa", "versicolor", "virginica"]
    print(f"Input features: {input_data[0]