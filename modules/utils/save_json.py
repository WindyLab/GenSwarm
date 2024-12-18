import json


def save_dict_to_json(data: dict, filename: str):
    """
    Saves a dictionary to a JSON file with the given filename.

    Parameters:
    data (dict): The dictionary to save.
    filename (str): The name of the JSON file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            # print("Saving dictionary as JSON file...")
            # print(f"Dictionary: {data}")
            json.dump(data, file, ensure_ascii=False, indent=4)
        # print(f"Dictionary successfully saved as JSON file: {filename}")
    except Exception as e:
        print(f"Failed to save file: {e}")
