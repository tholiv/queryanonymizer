__all__ = ['anonymize','deanonymize','keywords_list']

import json
import re
from os import path
from random import sample, randint, choice
from string import ascii_uppercase, digits as st_digits
from datetime import datetime, timedelta
from typing import List, Literal
from unidecode import unidecode

keywords_groups_list = ["SQL", "TSQL", "MySQL", "PLSQL", "DAX"]

def keywords_list(keywords_group: Literal["CUSTOM_ONLY", "SQL", "TSQL", "MySQL", "PLSQL", "DAX"] = "SQL",
                  custom_keywords: List[str] = [],
                  print_keywords: bool = True) -> list:
    """
    Generates a list of keywords based on a specified group and custom keywords.

    Args:
    keywords_group: An enumeration representing the group of keywords to be used.
    custom_keywords (List[str]): A list of custom keywords to be added.
    print_keywords (bool): If True, prints the list of keywords.

    Returns:
    list: A combined list of keywords from the specified group and custom keywords.

    Raises:
    FileNotFoundError: If the keywords JSON file is not found.
    json.JSONDecodeError: If the JSON file cannot be parsed.
    """
    if keywords_group == 'CUSTOM_ONLY':
        query_keywords = []
    else:
        try:
            current_file_path = path.abspath(__file__)
            current_directory = path.dirname(current_file_path)
            json_file_path = path.join(current_directory, 'keywords.json')
        
            with open(json_file_path, 'r') as file:
                keywords = json.load(file)
                query_keywords = keywords[keywords_group]
        except FileNotFoundError as e:
            _print_info(f"Keywords JSON file not found at {json_file_path}")
            raise e
        except json.JSONDecodeError as e:
            _print_info(f"Error decoding JSON file at {json_file_path}")
            raise e

    query_keywords = set(item.upper() for item in query_keywords)
    custom_keywords = set(item.upper() for item in custom_keywords)
    combined_keywords = list(query_keywords.union(custom_keywords))

    if print_keywords and combined_keywords:
        print(f"Keywords list has {len(combined_keywords)} elements:\n===========================")
        for keyword in sorted(combined_keywords):
            print(keyword)

    return combined_keywords

def anonymize(query: str = "",
              keywords_group: Literal["CUSTOM_ONLY", "SQL", "TSQL", "MySQL", "PLSQL", "DAX"] = "SQL",
              custom_keywords: List[str] = [],
              custom_tokens: List[str] = [],
              custom_encoder_dictionary: dict = {},
              prompt: str = "",
              print_result: bool = True,
              anonymize_strings_inside_apostrophes: bool = True,
              anonymize_strings_inside_quotation_marks: bool = False,
              anonymize_strings_inside_square_brackets: bool = False,
              anonymize_strings_inside_curly_brackets: bool = False,
              anonymize_numbers: bool = True,
              anonymize_dates: bool = True,
              min_word_length: int = 3,
              path_to_query_file: str = "",
              path_to_custom_keywords_file: str = "",
              path_to_custom_tokens_file: str = "",
              path_to_custom_encoder_dictionary_file: str = "",
              path_to_prompt_file: str = "",
              path_to_anonymized_file: str = "",
              path_to_decoder_dictionary_file: str = "",
              custom_date_format: str = 'YYYY-MM-DD',
              custom_time_format: str = 'HH:mm:ss',
              custom_datetime_format: str = 'YYYY-MM-DD HH:mm:ss'):
    """
    Performs anonymization of a given text based on specified criteria and custom settings.

    The function anonymizes strings, numbers, and dates in the provided query and prompt text,
    using custom rules, a list of keywords, and various anonymization options. It can handle
    different formats and enclosures like apostrophes, quotation marks, square brackets, and curly brackets.

    Parameters:
    - query (str): The query string to be anonymized.
    - keywords_group: An enumeration representing the group of keywords to be used.
    - custom_keywords (List[str]): A list of custom keywords to be included in anonymization.
    - custom_tokens (List[str]): Custom tokens to be anonymized.
    - custom_encoder_dictionary (dict): Dictionary for custom encoding.
    - prompt (str): Additional prompt text for anonymization.
    - print_result (bool): Flag to print the anonymization result.
    - anonymize_strings_inside_apostrophes (bool): Flag to anonymize strings inside apostrophes.
    - anonymize_strings_inside_quotation_marks (bool): Flag to anonymize strings inside quotation marks.
    - anonymize_strings_inside_square_brackets (bool): Flag to anonymize strings inside square brackets.
    - anonymize_strings_inside_curly_brackets (bool): Flag to anonymize strings inside curly brackets.
    - anonymize_numbers (bool): Flag to anonymize numeric values.
    - anonymize_dates (bool): Flag to anonymize date values.
    - min_word_length (int): Minimum length of words to consider for anonymization.
    - path_to_query_file (str): File path for an external query file.
    - path_to_custom_keywords_file (str): File path for a custom keywords file.
    - path_to_custom_tokens_file (str): File path for a custom tokens file.
    - path_to_custom_encoder_dictionary_file (str): File path for a custom encoder dictionary file.
    - path_to_prompt_file (str): File path for an external prompt file.
    - path_to_anonymized_file (str): File path to save the anonymized text.
    - path_to_decoder_dictionary_file (str): File path for a decoder dictionary file.
    - custom_date_format (str): Custom format for date anonymization.
    - custom_time_format (str): Custom format for time anonymization.
    - custom_datetime_format (str): Custom format for datetime anonymization.

    Returns:
    tuple: A tuple containing the anonymized query, decoder dictionary, and anonymized prompt.

    This function integrates several internal helper functions to achieve the anonymization process,
    including the identification of dates, floats, and different types of enclosures. The function
    also supports loading data from external files and saving the anonymization results to specified file paths.
    """

# Internal functions:
    def _is_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False
        
    def _create_encryptor() -> str:
        letters = ''.join(sample(ascii_uppercase, 26))
        digits = ''.join(sample(st_digits, 10))
        return letters + digits
    
    def _recreate_encryptor(key_val, val_val) -> str:
        mapped_dict = {key_val[i]: val_val[i] for i in range(len(key_val))}
        key_str = ''.join(mapped_dict.keys())
        val_str = ''.join(mapped_dict.values())
        return key_str + '/' + val_str
    
    def _convert_arrow_to_dateutil(arrow_format):
        conversion_dict = {
            'YYYY': '%Y', 'YY': '%y', # Year
            'MMMM': '%B', 'MMM': '%b', 'MM': '%m', 'M': '%m', # Month
            'DDDD': '%j', 'DDD': '%j', # Day of year
            'DD': '%d', 'D': '%d', 'Do': '%d', # Day of month
            'dddd': '%A', 'ddd': '%a', 'd': '%w', # Day of week
            'W': '%W', # ISO week date
            'HH': '%H', 'H': '%H', 'hh': '%I', 'h': '%I', # Hour
            'A': '%p', 'a': '%p', # AM/PM
            'mm': '%M', 'm': '%M', # Minute
            'ss': '%S', 's': '%S', # Second
            'S…': '%f', # Sub-second
            'ZZZ': '%Z', 'ZZ': '%z', 'Z': '%z' # Timezone
        }

        dateutil_format = arrow_format
        for arrow_token, dateutil_token in conversion_dict.items():
            dateutil_format = re.sub(f'(?<!%){arrow_token}', dateutil_token, dateutil_format)

        return dateutil_format
    
    def _identify_date_format_time(text: str):
        if not re.search(r'\d', text):
            return None

        for format_str in [custom_datetime_format, custom_date_format, custom_time_format]:
            if format_str:
                try:
                    if '%' not in format_str:
                        format_str =_convert_arrow_to_dateutil(format_str)
                    datetime.strptime(text, format_str)
                    return format_str
                except ValueError as e:
                    _print_info(f"ERROR!!!: Date conversion error: {e}")
                    continue

        return None

    def _anonymize_date(text):
        format_str = _identify_date_format_time(text)
        try:
            if '%' not in format_str:
                format_str =_convert_arrow_to_dateutil(format_str)

            date_obj = datetime.strptime(text, format_str)

        except ValueError as e:
            _print_info(f"ERROR!!!: Date conversion error: {e}")
            return text

        if "Y" in format_str and "H" in format_str:
            delta = timedelta(minutes=randint(1, 10000))
        elif "Y" in format_str:
            delta = timedelta(days=randint(1, 100))
        elif "H" in format_str:
            delta = timedelta(minutes=randint(1, 700))
        else:
            delta = timedelta(minutes=0)
        
        modified_date = date_obj + delta if choice([True, False]) else date_obj - delta

        return modified_date.strftime(format_str)

    def _anonymize_number(text):
        try:
            number = int(text)

            if number > 99:
                current_year = datetime.now().year
                ranges = [
                    (1950, current_year - 6),
                    (current_year - 5, current_year),
                    (current_year + 1, current_year + 10),
                    (current_year + 11, current_year + 30)
                ]

                for start, end in ranges:
                    if start <= number <= end:
                        return str(randint(start, end))

                length = len(str(number))
                min_value = 10**(length - 1)
                max_value = 10**length - 1
                return str(randint(min_value, max_value))

            return text

        except ValueError:
            return text

    def _anonymize_string(to_anonymize: str, code: str) -> str:
        if "/" in code:
            key_val, val_val = code.split("/")
            def _custom_replace(match):
                char = match.group(0)
                index = key_val.upper().find(char.upper())
                if index != -1:
                    replacement = val_val[index]
                    return replacement.lower() if char.islower() else replacement.upper()
                return char

            anonymized = re.sub(f"[{key_val}]", _custom_replace, to_anonymize, flags=re.IGNORECASE)
        else:
            letters = ascii_uppercase
            letters_code = code[:26]
            numbers_code = code[26:]

            anonymized = ''
            to_anonymize = unidecode(to_anonymize)
            for char in to_anonymize:
                if char.isalpha():
                    char_index = letters.index(char.upper())
                    replacement_char = letters_code[char_index]
                    anonymized += replacement_char
                elif char.isdigit():
                    anonymized += numbers_code[int(char)]
                else:
                    anonymized += char
            anonymized = anonymized.replace('"', '_').replace("'", "_")

        return anonymized

    def _identify_enclosure(token):
        if token.startswith("'") and token.endswith("'"):
            return 'apostrophes'
        elif token.startswith('"') and token.endswith('"'):
            return 'quotation_marks'
        elif token.startswith('[') and token.endswith(']'):
            return 'square_brackets'
        elif token.startswith('{') and token.endswith('}'):
            return 'curly_brackets'
        else:
            return ''
    
    def _remove_enclosure(token):
        if token.startswith("'") and token.endswith("'"):
            return token[1:-1]
        elif token.startswith('"') and token.endswith('"'):
            return token[1:-1]
        elif token.startswith('[') and token.endswith(']'):
            return token[1:-1]
        elif token.startswith('{') and token.endswith('}'):
            return token[1:-1]
        else:
            return token

    def _create_pattern(token):
        if _identify_enclosure(token) in ('apostrophes', 'quotation_marks', 'square_brackets', 'curly_brackets'):
            return re.escape(token)
        else:
            return r"(?:'{}'|\"{}\"|\[{}\]|\{{{}\}})".format(
                re.escape(token),
                re.escape(token),
                re.escape(token),
                re.escape(token)
            )
    
    def _tokens_list():
        query_text = ' '.join(re.findall(r'<query>(.*?)</query>', prompt, flags=re.IGNORECASE | re.DOTALL))
        query_text += ' ' + re.sub(r'<prompt>.*?</prompt>', '', query, flags=re.IGNORECASE | re.DOTALL)

        prompt_text = ' '.join(re.findall(r'<prompt>(.*?)</prompt>', query, flags=re.IGNORECASE | re.DOTALL))
        prompt_text += ' ' + re.sub(r'<query>.*?</query>', '', prompt, flags=re.IGNORECASE | re.DOTALL)

        data = []

        pattern = r"'(.*?)'|\"(.*?)\"|\[([^\]]*)\]|\{([^}]*)\}|([\w-]+)"
        query_tokens = re.findall(pattern, query_text)
        for match in query_tokens:
            if match[0] and anonymize_strings_inside_apostrophes:
                data.append((match[0].upper(), 'apostrophes'))
            elif match[1] and anonymize_strings_inside_quotation_marks:
                data.append((match[1].upper(), 'quotation_marks'))
            elif match[2] and anonymize_strings_inside_square_brackets:
                data.append((match[2].upper(), 'square_brackets'))
            elif match[3] and anonymize_strings_inside_curly_brackets:
                data.append((match[3].upper(), 'curly_brackets'))
            elif match[4]:
                data.append((match[4].upper(), ''))

        pattern = r"'(.*?)'|\"(.*?)\"|\[([^\]]*)\]|\{([^}]*)\}"
        prompt_tokens = re.findall(pattern, prompt_text)
        for match in prompt_tokens:
            if match[0] and anonymize_strings_inside_apostrophes:
                data.append((match[0].upper(), 'apostrophes'))
            elif match[1] and anonymize_strings_inside_quotation_marks:
                data.append((match[1].upper(), 'quotation_marks'))
            elif match[2] and anonymize_strings_inside_square_brackets:
                data.append((match[2].upper(), 'square_brackets'))
            elif match[3] and anonymize_strings_inside_curly_brackets:
                data.append((match[3].upper(), 'curly_brackets'))
        
        data = list(set(data))
        data = [element for element in data if len(element[0]) >= min_word_length]

        if custom_tokens:
            pattern = '|'.join(_create_pattern(token) for token in custom_tokens)

            prompt_tokens = re.finditer(pattern, prompt_text, re.IGNORECASE)
            for match in prompt_tokens:
                token = match.group(0)
                enclosure = _identify_enclosure(token)
                if enclosure in ('apostrophes', 'quotation_marks', 'square_brackets', 'curly_brackets'):
                    data.append((token[1:-1].upper(), enclosure))
                else:
                    data.append((token.upper(), ''))

        unique_tokens_list = list(set(data))
        unique_tokens_list = [element for element in unique_tokens_list if not (element[1] == '' and element[0] in query_keywords_upper)]
        new_unique_tokens_list = []
        for element in unique_tokens_list:
            token = element[0]
            if element[1]=='apostrophes':
                if _identify_date_format_time(token) is None:
                    new_unique_tokens_list.append((element[0], element[1], 'string'))
                else:
                    if anonymize_dates:
                        new_unique_tokens_list.append((element[0], element[1], 'datetime'))
            elif _is_float(token):
                if anonymize_numbers:
                    new_unique_tokens_list.append((element[0], element[1], 'number'))
            else:
                new_unique_tokens_list.append((element[0], element[1], 'string'))

        return new_unique_tokens_list

    def _replace_with_case(match, replacement):
        current = match.group()
        new_replacement = ''.join(b.upper() if a.isupper() else b.lower() for a, b in zip(current, replacement))
        return new_replacement
    
    def _clean_key(key):
        return re.sub(r'[\"\'\{\}\[\]]', '', key)
    
# Main code:
    if path_to_query_file:
        text_from_file, _ = _load_text_with_fallback_encodings(path_to_query_file)
        if query:
            query += "\n"
        query += text_from_file
    
    if path_to_prompt_file:
        text_from_file, _ = _load_text_with_fallback_encodings(path_to_prompt_file)
        if prompt:
            prompt += "\n"
        prompt += text_from_file

    try:
        if path_to_custom_keywords_file:
            with open(path_to_custom_keywords_file, 'r') as file:
                try:
                    data = json.load(file)
                    if custom_keywords:
                        custom_keywords.extend(data)
                except json.JSONDecodeError as e:
                    _print_info(f"ERROR!!!: Could not decode JSON from {path_to_custom_keywords_file}")
                    raise e

    except FileNotFoundError as e:
        _print_info(f"ERROR!!!: File not found - {path_to_custom_keywords_file}")
        raise e
    except IOError as e:
        _print_info(f"ERROR!!!: IO error occurred: {e}")
        raise e

    try:
        if path_to_custom_tokens_file:
            with open(path_to_custom_tokens_file, 'r') as file:
                try:
                    data = json.load(file)
                    if custom_tokens:
                        custom_tokens.extend(data)
                except json.JSONDecodeError:
                    _print_info(f"ERROR!!!: Could not decode JSON from {path_to_custom_tokens_file}")
                    raise e

    except FileNotFoundError as e:
        _print_info(f"ERROR!!!: File not found - {path_to_custom_tokens_file}")
        raise e
    except IOError as e:
        _print_info(f"ERROR!!!: IO error occurred: {e}")
        raise e
    
    custom_tokens = set([token.upper() for token in custom_tokens]) 
    # Loading additional encoder dictionary entries from a file if provided
    if path_to_custom_encoder_dictionary_file:
        encoder_dictionary_from_file = _load_dict_with_fallback_encodings(path_to_custom_encoder_dictionary_file)
        custom_encoder_dictionary = {k: v for d in [custom_encoder_dictionary, encoder_dictionary_from_file] for k, v in d.items() if v not in custom_encoder_dictionary.values() or v == custom_encoder_dictionary.get(k)}

    custom_codes_dictionary = {_remove_enclosure(key.upper()): _remove_enclosure(value.upper()) 
                            for key, value in custom_encoder_dictionary.items() 
                            if not _is_float(key)}

    if query or path_to_query_file:
        query_keywords = keywords_list(keywords_group=keywords_group, custom_keywords=custom_keywords, print_keywords=False)
        query_keywords_upper = set([keyword.upper() for keyword in query_keywords])   
        query_keywords_upper = [keyword for keyword in query_keywords_upper if keyword not in custom_tokens]
    else:
        query_keywords_upper = []

    unique_tokens_list = _tokens_list()

    query = re.sub(r'</?prompt>', '', query, flags=re.IGNORECASE)
    prompt = re.sub(r'</?query>', '', prompt, flags=re.IGNORECASE)
    
    codes_list = set(element[0] for element in unique_tokens_list if element[2] == 'string')
    codes_dict = {element: _create_encryptor() for element in codes_list}
    for key, value in custom_codes_dictionary.items():
        if key in codes_dict:
            codes_dict[key] = _recreate_encryptor(key, value)

    new_unique_token_list = []
    for token in unique_tokens_list:
        if token[2] == 'string' and token[0] in codes_dict:
            if len(codes_dict[token[0]]) < 22:
                new_element = _anonymize_string(token[0], codes_dict[token[0]])
            else:
                new_element = _anonymize_string(token[0], codes_dict[token[0]])
        elif token[2] == 'datetime':
            new_element = _anonymize_date(token[0])
        elif token[2] == 'number':
            new_element = _anonymize_number(token[0])
        new_unique_token_list.append(token + (new_element,))
    
    dictionary_list = []
    for key, value in custom_encoder_dictionary.items():
        enclosure = _identify_enclosure(key)
        token_type = 'string'
        new_key = key
        new_value = value
        if enclosure in ['apostrophes','quotation_marks','square_brackets','curly_brackets']:
            new_key = key[1:-1]
            new_value = value[1:-1]
        
        if enclosure == 'apostrophes':
            if _identify_date_format_time(key) is None:
                token_type = 'string'
            else:
                token_type = 'datetime'
        elif _is_float(key):
            token_type = 'number'
        
        dictionary_list.append((new_key, enclosure, token_type, new_value))
        
    for new_token in new_unique_token_list:
        if not any(new_token[:3] == existing_token[:3] for existing_token in dictionary_list):
            dictionary_list.append(new_token)

    for element in dictionary_list:
        if element[1] == 'apostrophes':
            pattern = rf"'{re.escape(element[0])}'"
            new_token = rf"'{element[3]}'"
        elif element[1] == 'quotation_marks':
            pattern = rf'"{re.escape(element[0])}"'
            new_token = rf'"{element[3]}"'
        elif element[1] == 'square_brackets':
            pattern = r'\[' + re.escape(element[0]) + r'\]'
            new_token = rf'[{element[3]}]'
        elif element[1] == 'curly_brackets':
            pattern = r'\{' + re.escape(element[0]) + r'\}'
            new_token = r'{' + element[3] + r'}'
        else:
            pattern = r"(?<!['\"\[\]{])\b" + re.escape(element[0]) + r"\b(?!['\"\[\]{])"
            new_token = element[3]

        pattern = re.compile(pattern, re.IGNORECASE)
        query = pattern.sub(lambda match: _replace_with_case(match, new_token), query)
        prompt = pattern.sub(lambda match: _replace_with_case(match, new_token), prompt)
    
    decoder_dictionary = {}
    for item in dictionary_list:
        if item[1] == 'apostrophes':
            key = f"'{item[0]}'"
            value = f"'{item[3]}'"
        elif item[1] == 'quotation_marks':
            key = f'"{item[0]}"'
            value = f'"{item[3]}"'
        elif item[1] == 'square_brackets':
            key = f'[{item[0]}]'
            value = f'[{item[3]}]'
        elif item[1] == 'curly_brackets':
            key = f'{{{item[0]}}}'
            value = f'{{{item[3]}}}'
        else:
            key = item[0]
            value = item[3]

        decoder_dictionary[key] = value

    if print_result:
        if prompt:
            print(prompt + "\n\n")
        if query:
            print(query + "\n\n")
        if len(decoder_dictionary) > 0:
            print(f"Decoder dictionary has {len(decoder_dictionary)} elements:\n===========================")
            sorted_items = sorted(decoder_dictionary.items(), key=lambda item: _clean_key(item[0]))
            decoder_dictionary = {key: value for key, value in sorted_items}
            for key, value in sorted_items:
                print(f'{key} -> {value}')
    
    anonymized_query = query
    anonymized_prompt = prompt

    if path_to_decoder_dictionary_file:
        with open(path_to_decoder_dictionary_file, 'w', encoding='utf-8') as file:
            json.dump(decoder_dictionary, file, indent=4)
    
    if path_to_anonymized_file:
        with open(path_to_anonymized_file, 'w', encoding='utf-8') as file:
            file.write(f"{anonymized_prompt}\n{anonymized_query}")

    return anonymized_query, decoder_dictionary, anonymized_prompt

def deanonymize(anonymized_text: str = "",
                decoder_dictionary: dict = {},
                path_to_decoder_dictionary_file: str = "",
                path_to_anonymized_file: str = "",
                path_to_deanonymized_file: str = "",
                print_result: bool = True) -> str:
    """
    The 'deanonymize' function is used to reverse the anonymization of text using a decoder dictionary.

    Parameters:
    - anonymized_text (str): A string containing the text to be deanonymized.
    - decoder_dictionary (dict): A dictionary where keys represent anonymized strings and values their original form.
    - path_to_decoder_dictionary_file (str): File path to load additional decoder dictionary entries.
    - path_to_anonymized_file (str): File path to load the anonymized text.
    - path_to_deanonymized_file (str): File path to save the deanonymized text.
    - print_result (bool): If True, prints the deanonymized text.

    Returns:
    - str: The deanonymized text.

    Inner Functions:
    - _replace_with_case: Replaces a regex match with a replacement text, maintaining the original case.

    The function can either use the provided text and dictionary or load them from the specified file paths.
    The deanonymization process involves replacing anonymized strings with their original counterparts 
    from the decoder dictionary, respecting the original text's casing.
    """

    def _replace_with_case(match, replacement):
        # Inner function to match the case of the original text
        current = match.group()
        new_replacement = ''.join(b.upper() if a.isupper() else b.lower() for a, b in zip(current, replacement))
        return new_replacement
    
    # Loading additional decoder dictionary entries from a file if provided
    if path_to_decoder_dictionary_file:
        decoder_dictionary_from_file = _load_dict_with_fallback_encodings(path_to_decoder_dictionary_file)
        decoder_dictionary = {k: v for d in [decoder_dictionary, decoder_dictionary_from_file] for k, v in d.items() if v not in decoder_dictionary.values() or v == decoder_dictionary.get(k)}

    # Loading anonymized text from a file if provided
    if path_to_anonymized_file:
        anonymized_text, file_encoding = _load_text_with_fallback_encodings(path_to_anonymized_file)

    # Processing the decoder dictionary and performing the deanonymization
    if _check_decoder_dictionary(decoder_dictionary):
        decoder_dictionary = dict(sorted(decoder_dictionary.items(), key=lambda item: len(item[0]), reverse=True))
        for key, value in decoder_dictionary.items():
            if key.startswith(("'", '"', '[', '{')) and key.endswith(("'", '"', ']', '}')):
                escaped_value = re.escape(value)
                pattern = rf"{escaped_value}"
            else:
                pattern = rf"(?<!['\"\[\]{{}}])\b{re.escape(value)}\b(?!['\"\[\]{{}}])"
            
            anonymized_text = re.sub(pattern, lambda match: _replace_with_case(match, key), anonymized_text, flags=re.IGNORECASE)
    
        deanonymized_text = anonymized_text
    else:
        deanonymized_text = ''

    # Printing the deanonymized text if requested
    if print_result:
        print(deanonymized_text)

    # Saving the deanonymized text to a file if specified
    if path_to_deanonymized_file:
        try:
            with open(path_to_deanonymized_file, 'w', encoding=file_encoding) as file:
                file.write(deanonymized_text)

        except IOError as e:
            _print_info(f"Error writing to deanonymized text file: {path_to_deanonymized_file}")
            raise e

    return deanonymized_text


# Internal functions:
def _load_dict_with_fallback_encodings(file_path):
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
            try:
                data = json.loads(file_content.decode('utf-8'))
            except UnicodeDecodeError:
                try:
                    data = json.loads(file_content.decode('latin-1'))
                except UnicodeDecodeError as e:
                    _print_info(f"Failed to decode {file_path} with any of the supported encodings: utf-8, latin-1.")
                    raise e
    except FileNotFoundError as e:
        _print_info(f"File not found: {file_path}")
        raise e
    except json.JSONDecodeError as e:
        _print_info(f"Error processing the JSON file: {file_path}")
        raise e

    return {key.upper(): (value.upper() if isinstance(value, str) else value) for key, value in data.items()}

def _load_text_with_fallback_encodings(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read(), 'utf-8'
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read(), 'utf-8'
        except UnicodeDecodeError as e:
            _print_info(f"Failed to decode {file_path} with UTF-8 and Latin-1 encodings.")
            raise e
    except FileNotFoundError as e:
        _print_info(f"File not found: {file_path}")
        raise e
    except IOError as e:
        _print_info(f"IO error occurred while reading the file: {e}")
        raise e

def _check_decoder_dictionary(decoder_dictionary):
    if len(decoder_dictionary) != len(set(decoder_dictionary.keys())):
        _print_info("ERROR!!!: Not all keys in the decoder dictionary are unique.")
        return False

    if len(set(decoder_dictionary.values())) != len(decoder_dictionary.values()):
        _print_info("ERROR!!!: Not all values in the decoder dictionary are unique.")
        return False

    for key, value in decoder_dictionary.items():
        if len(key) != len(value):
            _print_info(f"ERROR!!!: Key-value pair ({key}, {value}) does not meet the validity criteria.")
            return False

    return True

def _print_info(info: str = ''):
    asterisks = '*' * (len(info) + 4)
    print(f"\n{asterisks}\n* {info} *\n{asterisks}\n")