import pandas as pd
import json

# Load the file
df = pd.read_csv('courtside.csv')

# Search terms
search_terms = ['PRE-GAME', '1ST HALF', 'HALFTIME', '2ND HALF', 'POST GAME']

pre_game_index = None
for idx, row in df.iterrows():
    if any(str(cell).strip().upper() == 'PRE-GAME' for cell in row):
        pre_game_index = idx
        break

if pre_game_index is not None:
    # Find the "CLOCK", "COURTSIDE", and "#" columns in the row immediately after PRE-GAME
    clock_column = None
    courtside_column = None
    sequence_column = None
    header_row = df.iloc[pre_game_index + 1]

    for col_idx, cell in enumerate(header_row):
        if str(cell).strip().upper() == 'CLOCK':
            clock_column = col_idx
        if str(cell).strip().upper() == 'COURTSIDE':
            courtside_column = col_idx
        if str(cell).strip() == '#':
            sequence_column = col_idx

    # Dictionary to store output in required format
    pre_game_data = {"PRE_GAME": {}}

    # Collect all values under the "CLOCK", "#", and "COURTSIDE" columns until the next segment (1ST HALF) starts
    for idx in range(pre_game_index + 2, len(df)):
        row = df.iloc[idx]
        if any(str(cell).strip().upper() in ['1ST HALF', 'HALFTIME', '2ND HALF', 'POST GAME'] for cell in row):
            break  # Stop when we hit the next segment

        # Ensure the clock value is not NaN
        if clock_column is not None and pd.notna(row.iloc[clock_column]):
            clock_value = str(row.iloc[clock_column]).strip("()")  # Remove parentheses
            courtside_value = str(row.iloc[courtside_column]) if courtside_column is not None else None
            sequence_value = row.iloc[sequence_column] if sequence_column is not None else None

            # Convert sequence_value to int if it's a number, otherwise None
            try:
                sequence_number = int(float(sequence_value)) if pd.notna(sequence_value) else None
            except (ValueError, TypeError):
                sequence_number = None

            # Create graphic object with number and graphic name
            graphic_object = {
                "number": sequence_number,
                "graphic": courtside_value
            }

            # Add to dictionary
            if clock_value not in pre_game_data["PRE_GAME"]:
                pre_game_data["PRE_GAME"][clock_value] = []
            pre_game_data["PRE_GAME"][clock_value].append(graphic_object)

    # Print structured output
    print(json.dumps(pre_game_data, indent=4))

else:
    print("PRE-GAME section not found.")
