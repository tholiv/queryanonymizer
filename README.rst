QueryAnonymizer
===============


Description
-----------

`queryanonymizer` is a Python library designed to anonymize SQL, DAX or others languages queries. It allows safe sharing of queries for debugging, documentation, or educational purposes without the risk of exposing sensitive data. The library provides functions for both anonymizing and deanonymizing queries, with support for various SQL dialects and allows using also custom keywords.


Installation
------------

To install `queryanonymizer`, run the following command:


    pip install queryanonymizer

Usage
-----

Import `queryanonymizer` in your Python project and use the provided functions to anonymize or deanonymize your queries/prompts.


    from queryanonymizer import anonymize, deanonymize, keywords_list

    query = """
    SELECT order_id
        , customer_id
        , order_date
        , employee_id
        , customer_name
        , order_value
    FROM order
    WHERE order_date >= '2023-01-01'
        AND order_value >= 1000
    """

    anonymized_query, decoder_dictionary, _ = anonymize(query)

    # Example of deanonymizing a query
    deanonymize(anonymized_query, decoder_dictionary)

More Examples
-------------

Visit [QueryAnonymizer Documentation](https://queryanonymizer.com) for more comprehensive examples and use cases.


Features
--------

- **Anonymization of SQL, DAX and other types of queries**: Replace sensitive data in your queries with randomized, case sensitive equivalents.
- **Support for Multiple SQL Dialects**: Customize the anonymization process based on different SQL dialects including T-SQL, MySQL, and others.
- **Customization Options**: Offers various customization options for the anonymization process, such as handling of string literals, numbers, dates, and more.
- **Decoding Dictionary**: Generate a decoding dictionary that allows you to revert your anonymized queries back to their original form.
- **Advanced Anonymization**: Tailor the anonymization process with numerous parameters.
- **File Support**: Anonymize queries directly from and to files.
- **Reversible Process**: Capabilities to both anonymize and deanonymize queries.
- **Customizable**: Fine-tune settings to fit your specific requirements.
- **AI Integration**: Unique features for integrating with AI tools like ChatGPT.


License
-------

`queryanonymizer` is licensed under the MIT License. See the LICENSE file for more details.

Authors
-------

`queryanonymizer` was created by [DataTeam.pl](https://datateam.pl) (Mariusz & Mateusz Cieciura).
