import numpy as np
import pandas as pd

# Load the .npz file
data = np.load('training/trained_dnn.npz')

# Iterate over each array and save it with a descriptive name
for key in data.files:
    array = data[key]
    
    # Determine a descriptive name based on the key
    if 'W' in key:
        name = key.replace('/', '_') + '_weights'
    elif 'b' in key:
        name = key.replace('/', '_') + '_biases'
    else:
        name = key.replace('/', '_')
    
    # Flatten the array for simplicity
    flattened_array = array.flatten()
    # Create a DataFrame
    df = pd.DataFrame(flattened_array)
    
    # Save to CSV with the descriptive name
    csv_filename = f"{name}.csv"
    df.to_csv(csv_filename, index=False, header=False)

print("All data has been exported to descriptive CSV files.")
