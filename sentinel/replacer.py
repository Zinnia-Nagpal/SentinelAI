def replace_secret_in_file(filepath: str, raw_value: str, reference: str) -> bool:
    """
    Replaces raw_value with reference in a given file.
    Returns True if replaced, False if not found.
    """
    try:
        # 1. Read the file contents
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        # 2. Check if raw_value exists in contents
        if raw_value not in content:
            return False

        # 3. Replace raw_value with reference
        new_content = content.replace(raw_value, reference)

        # 4. Write the file back
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(new_content)

        # 5. Return True if replaced
        return True

    except FileNotFoundError:
        print(f"Error: The file {filepath} was not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

         