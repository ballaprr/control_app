import pandas as pd
import json

# Load the file
df = pd.read_csv('courtside.csv')

# Search terms
search_terms = ['PRE-GAME', '1ST HALF', 'HALFTIME', '2ND HALF', 'POST GAME']

# Initialize data dictionary
game_data = {}

# Process PRE-GAME section
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

    # Dictionary to store PRE-GAME output
    game_data["PRE_GAME"] = {}

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
            if clock_value not in game_data["PRE_GAME"]:
                game_data["PRE_GAME"][clock_value] = []
            game_data["PRE_GAME"][clock_value].append(graphic_object)

# Process 1ST HALF section
first_half_index = None
for idx, row in df.iterrows():
    if any(str(cell).strip().upper() == '1ST HALF' for cell in row):
        first_half_index = idx
        break

if first_half_index is not None:
    
    # Find the column indices for the 1ST HALF section
    first_half_header = df.iloc[first_half_index]
    clock_column = 1  # Clock is in column 1 for 1ST HALF
    courtside_column = 10  # COURTSIDE is in column 10
    sequence_column = 3  # # is in column 3
    
    # Dictionary to store 1ST HALF output
    game_data["1ST_HALF"] = {
        "16:00": [],
        "12:00": [],
        "8:00": [],
        "4:00": []
    }

    # Process the data rows
    current_time = None
    start_idx = first_half_index + 1
    for idx in range(start_idx, len(df)):
        row = df.iloc[idx]
        
        # Check if we've reached the next section
        if any(str(cell).strip().upper() in ['HALFTIME', '2ND HALF', 'POST GAME'] for cell in row):
            break

        # Process clock value
        if pd.notna(row.iloc[clock_column]):
            clock_text = str(row.iloc[clock_column]).strip()
            
            # Extract time from format "1:1 (Under 16:00)"
            if clock_text:  # Process any non-empty clock text
                time_str = None
                if ':' in clock_text:  # Check if it contains a play number (e.g., "1:1")
                    parts = clock_text.split('(')
                    if len(parts) > 1:
                        time_part = parts[1].strip(')')
                        if 'Under' in time_part:
                            time_str = time_part.replace('Under', '').strip()
                
                if time_str and time_str in game_data["1ST_HALF"]:
                    current_time = time_str
                else:
                    print(f"Debug: Time string not valid or not found in expected times: '{time_str}'")

        # Process courtside value and sequence number
        if current_time and pd.notna(row.iloc[courtside_column]):
            courtside_value = str(row.iloc[courtside_column]).strip()
            sequence_value = row.iloc[sequence_column] if pd.notna(row.iloc[sequence_column]) else None

            # Convert sequence_value to int if possible
            try:
                sequence_number = int(float(sequence_value)) if sequence_value is not None else None
            except (ValueError, TypeError):
                sequence_number = None

            if courtside_value != 'nan':
                graphic_object = {
                    "number": sequence_number,
                    "graphic": courtside_value
                }
                game_data["1ST_HALF"][current_time].append(graphic_object)

# Process HALFTIME section
halftime_index = None
for idx, row in df.iterrows():
    if any(str(cell).strip().upper() == 'HALFTIME' for cell in row):
        halftime_index = idx
        break

if halftime_index is not None:
    # Find the column indices for the HALFTIME section
    clock_column = 1  # Clock is in column 1
    courtside_column = 10  # COURTSIDE is in column 10
    sequence_column = 3  # # is in column 3
    
    # Dictionary to store HALFTIME output
    game_data["HALFTIME"] = {}

    # Process the data rows
    start_idx = halftime_index + 1
    for idx in range(start_idx, len(df)):
        row = df.iloc[idx]
        
        # Check if we've reached the next section
        if any(str(cell).strip().upper() in ['2ND HALF', 'POST GAME'] for cell in row):
            break

        # Process clock value and courtside value
        if pd.notna(row.iloc[clock_column]) and pd.notna(row.iloc[courtside_column]):
            clock_text = str(row.iloc[clock_column]).strip()
            courtside_value = str(row.iloc[courtside_column]).strip()
            
            # Extract time from clock text
            if ':' in clock_text:
                # If the time is in parentheses, extract it
                if '(' in clock_text:
                    time_str = clock_text.split('(')[1].strip(')')
                else:
                    time_str = clock_text
                
                # Clean up the time string
                time_str = time_str.strip()
                if courtside_value != 'nan':
                    game_data["HALFTIME"][time_str] = courtside_value

# Process 2ND HALF section
second_half_index = None
for idx, row in df.iterrows():
    if any(str(cell).strip().upper() == '2ND HALF' for cell in row):
        second_half_index = idx
        break

if second_half_index is not None:
    # Find the column indices for the 2ND HALF section
    clock_column = 1  # Clock is in column 1
    courtside_column = 10  # COURTSIDE is in column 10
    sequence_column = 3  # # is in column 3
    
    # Dictionary to store 2ND HALF output with same time slots as 1ST HALF
    game_data["2ND_HALF"] = {
        "16:00": [],
        "12:00": [],
        "8:00": [],
        "4:00": []
    }

    # Process the data rows
    current_time = None
    start_idx = second_half_index + 1
    for idx in range(start_idx, len(df)):
        row = df.iloc[idx]
        
        # Check if we've reached the next section
        if any(str(cell).strip().upper() in ['POST GAME'] for cell in row):
            break

        # Process clock value
        if pd.notna(row.iloc[clock_column]):
            clock_text = str(row.iloc[clock_column]).strip()
            
            # Extract time from format "2:1 (Under 16:00)"
            if clock_text:  # Process any non-empty clock text
                time_str = None
                if ':' in clock_text:  # Check if it contains a play number (e.g., "2:1")
                    parts = clock_text.split('(')
                    if len(parts) > 1:
                        time_part = parts[1].strip(')')
                        if 'Under' in time_part:
                            time_str = time_part.replace('Under', '').strip()
                
                if time_str and time_str in game_data["2ND_HALF"]:
                    current_time = time_str
                else:
                    print(f"Debug: Time string not valid or not found in expected times: '{time_str}'")

        # Process courtside value and sequence number
        if current_time and pd.notna(row.iloc[courtside_column]):
            courtside_value = str(row.iloc[courtside_column]).strip()
            sequence_value = row.iloc[sequence_column] if pd.notna(row.iloc[sequence_column]) else None

            # Convert sequence_value to int if possible
            try:
                sequence_number = int(float(sequence_value)) if sequence_value is not None else None
            except (ValueError, TypeError):
                sequence_number = None

            if courtside_value != 'nan':
                graphic_object = {
                    "number": sequence_number,
                    "graphic": courtside_value
                }
                game_data["2ND_HALF"][current_time].append(graphic_object)

# Print structured output
print(json.dumps(game_data, indent=4))
