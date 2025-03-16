#!/usr/bin/env python3
"""
ChatGPT SQL Anonymizer Client

A simple client program to demonstrate masking and demasking SQL statements
for secure sharing with ChatGPT and other AI assistants.
"""

import argparse
import json
import os
from queryanonymizer import anonymize, deanonymize

def main():
    parser = argparse.ArgumentParser(
        description="Anonymize and deanonymize SQL queries for secure sharing with ChatGPT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Anonymize a SQL file
  python chatgpt_sql_anonymizer.py --anonymize --input query.sql --output anonymized.sql
  
  # Anonymize a SQL file with a custom prompt
  python chatgpt_sql_anonymizer.py --anonymize --input query.sql --output anonymized.sql --prompt "Help me optimize this query"
  
  # Deanonymize a SQL file
  python chatgpt_sql_anonymizer.py --deanonymize --input anonymized.sql --output original.sql
"""
    )
    
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--anonymize", action="store_true", help="Anonymize a SQL query")
    action_group.add_argument("--deanonymize", action="store_true", help="Deanonymize a SQL query")
    
    parser.add_argument("--input", required=True, help="Input file containing SQL query")
    parser.add_argument("--output", help="Output file for the processed query")
    parser.add_argument("--dialect", default="SQL", choices=["SQL", "TSQL", "MySQL", "PLSQL", "DAX", "CUSTOM_ONLY"],
                        help="SQL dialect to use for keyword recognition")
    parser.add_argument("--prompt", help="Prompt to include with the query for ChatGPT")
    parser.add_argument("--prompt-file", help="File containing prompt for ChatGPT")
    parser.add_argument("--decoder-file", default="decoder_dictionary.json", 
                        help="File to store/read the decoder dictionary")
    parser.add_argument("--min-word-length", type=int, default=3, 
                        help="Minimum word length to anonymize")
    parser.add_argument("--no-anonymize-numbers", action="store_false", dest="anonymize_numbers",
                        help="Don't anonymize numbers")
    parser.add_argument("--no-anonymize-dates", action="store_false", dest="anonymize_dates",
                        help="Don't anonymize dates")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.isfile(args.input):
        print(f"Error: Input file '{args.input}' does not exist")
        return 1
    
    # Set default output file if not provided
    if not args.output:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}_{'anonymized' if args.anonymize else 'deanonymized'}{ext}"
    
    # Process the query
    if args.anonymize:
        # Read prompt from file if specified
        prompt = ""
        if args.prompt_file and os.path.isfile(args.prompt_file):
            with open(args.prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()
        elif args.prompt:
            prompt = args.prompt
            
        # Anonymize the query
        anonymized_query, decoder_dict, anonymized_prompt = anonymize(
            path_to_query_file=args.input,
            keywords_group=args.dialect,
            prompt=prompt,
            min_word_length=args.min_word_length,
            anonymize_numbers=args.anonymize_numbers,
            anonymize_dates=args.anonymize_dates,
            path_to_decoder_dictionary_file=args.decoder_file,
            path_to_anonymized_file=args.output,
            print_result=True
        )
        
        print(f"\nQuery anonymized successfully!")
        print(f"Anonymized query saved to: {args.output}")
        print(f"Decoder dictionary saved to: {args.decoder_file}")
        print("\nIMPORTANT: Keep the decoder dictionary secure and private.")
        print("It contains the mapping between anonymized and original values.")
        
    else:  # deanonymize
        # Deanonymize the query
        deanonymized_text = deanonymize(
            path_to_anonymized_file=args.input,
            path_to_decoder_dictionary_file=args.decoder_file,
            path_to_deanonymized_file=args.output,
            print_result=True
        )
        
        print(f"\nQuery deanonymized successfully!")
        print(f"Deanonymized query saved to: {args.output}")

    return 0

if __name__ == "__main__":
    exit(main())
