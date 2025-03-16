# ChatGPT SQL Anonymizer Usage Guide

## Overview

This guide demonstrates how to use the QueryAnonymizer library to safely share SQL queries with ChatGPT and other AI assistants without exposing sensitive data. The provided client program simplifies the process of anonymizing queries before sharing and deanonymizing them after receiving assistance.

## Why Anonymize SQL Queries for ChatGPT?

1. **Data Privacy**: Prevents exposure of sensitive information like customer IDs, emails, and personal data
2. **Security**: Reduces risk of data breaches when sharing queries with external systems
3. **Regulatory Compliance**: Helps meet GDPR, HIPAA, and other data protection requirements
4. **Confidentiality**: Protects proprietary database structures and naming conventions

## Installation

```bash
# Install the QueryAnonymizer library
pip install queryanonymizer

# Make the client script executable (Unix/Linux/macOS)
chmod +x chatgpt_sql_anonymizer.py
```

## Basic Usage

### Anonymizing a SQL Query

```bash
./chatgpt_sql_anonymizer.py --anonymize --input your_query.sql --output anonymized.sql
```

This will:
1. Read your SQL query from `your_query.sql`
2. Replace sensitive data with anonymized placeholders
3. Save the anonymized query to `anonymized.sql`
4. Create a decoder dictionary file (`decoder_dictionary.json`)

### Adding a Prompt for ChatGPT

```bash
./chatgpt_sql_anonymizer.py --anonymize --input your_query.sql --prompt "Please optimize this query for better performance"
```

### Deanonymizing a Response

After receiving assistance from ChatGPT, you may need to deanonymize the query:

```bash
./chatgpt_sql_anonymizer.py --deanonymize --input chatgpt_response.sql --output final_query.sql
```

## Workflow Example

1. **Prepare your SQL query** in a file (e.g., `original_query.sql`)

2. **Anonymize the query**:
   ```bash
   ./chatgpt_sql_anonymizer.py --anonymize --input original_query.sql --output anonymized_query.sql --prompt "Help me optimize this query for better performance"
   ```

3. **Copy the anonymized query** from `anonymized_query.sql` and paste it into ChatGPT along with the anonymized prompt

4. **Copy ChatGPT's response** to a new file (e.g., `chatgpt_response.sql`)

5. **Deanonymize the response**:
   ```bash
   ./chatgpt_sql_anonymizer.py --deanonymize --input chatgpt_response.sql --output optimized_query.sql
   ```

6. **Review and implement** the optimized query from `optimized_query.sql`

## Advanced Options

- **SQL Dialect**: Specify the SQL dialect to use the appropriate keyword list
  ```bash
  ./chatgpt_sql_anonymizer.py --anonymize --input query.sql --dialect TSQL
  ```

- **Minimum Word Length**: Set minimum length for words to be anonymized
  ```bash
  ./chatgpt_sql_anonymizer.py --anonymize --input query.sql --min-word-length 4
  ```

- **Selective Anonymization**: Control what gets anonymized
  ```bash
  ./chatgpt_sql_anonymizer.py --anonymize --input query.sql --no-anonymize-numbers
  ```

## Security Considerations

- **Protect the decoder dictionary**: The `decoder_dictionary.json` file contains the mapping between original and anonymized values. Keep it secure.
- **Review before sharing**: Always review anonymized queries to ensure no sensitive data remains.
- **Use with caution**: While anonymization helps protect sensitive data, it doesn't guarantee complete security. Use judgment when sharing queries.

## Limitations

- Very short identifiers (below the minimum word length) may not be anonymized
- Complex or non-standard SQL constructs might not be properly anonymized
- The anonymization process may occasionally alter query semantics

For more comprehensive options and details, refer to the QueryAnonymizer library documentation.
