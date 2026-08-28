#!/usr/bin/env python

"""
The Malaria Data Specification Processing Tool
------------------------------------------------
Converts PHA4GE's "Malaria Standardised Terms" tabular (CSV) into a
machine-processable JSON Schema, mirroring the approach used by the
SARS-CoV-2 Data Specification Processing Tool (table_json.py).

Usage:
    python malaria_table_json.py PHA4GE_Malaria_Standardised_Terms_with_required_optional.csv
        -> writes PHA4GE_Malaria_Contextual_Data_Schema.json
"""

import argparse
import csv
import json
import re
import sys

# --- Input table configuration -------------------------------------------------
# NB: the malaria table uses a different column layout to the SARS-CoV-2 table
# (no separate "Values"/enum column, comma-delimited rather than semicolon-
# delimited) so the fieldnames/separator differ from table_json.py.
FIELDNAMES = ['Field', 'Required/Optional', 'Ontology ID', 'Type of Variable(s)',
              'Definition', 'Guidance', 'Example(s)']
SEPARATOR = ','
QUOTE = '"'


def interface_label_to_property_key(interface_label):
    """
    Turn a human-readable field label (the "Field" column value) into a
    snake_case JSON property key.

    Any character that isn't a word character, space, or curly brace is
    replaced with an underscore, spaces become underscores, repeated
    underscores are collapsed, and leading/trailing underscores are
    stripped. This also cleans up messy source data such as trailing
    whitespace or stray punctuation in field names (e.g. "geo_loc_latitude "
    -> "geo_loc_latitude", "sampling type?" -> "sampling_type").

    Args:
        interface_label: The raw "Field" value from the CSV.

    Returns:
        A lowercase snake_case string suitable for use as a JSON property key.
        Can be an empty string if the label contains no usable characters
        (e.g. a lone punctuation mark) - callers should handle that case.
    """
    property_key = re.sub(r'[^\w {}]', '_', interface_label).replace(' ', '_').replace('__', '_').lower()
    property_key = re.sub(r'_$', '', property_key)
    property_key = re.sub(r'^_', '', property_key)
    return property_key


def classify_value_type(raw_type, example):
    """
    Map the free-text 'Type of Variable(s)' column used in the malaria table
    to a JSON Schema type + optional format.

    Unlike the SARS-CoV-2 table (String/Int/Float/Enums/...), the malaria
    table's type column is a loosely-controlled vocabulary (e.g. 'Alphanumeric',
    'Free text', 'Permitted value(s), or Other (+ Free text)', 'Structured
    format', 'Numeric', ...). Most of these resolve to JSON Schema "string";
    only "Numeric" resolves to a number/integer, decided from the example value
    (a decimal point in the example means "number", otherwise "integer"; if
    the example can't be parsed as a number at all, it falls back to "string").

    Args:
        raw_type: The raw "Type of Variable(s)" value from the CSV row.
        example: The row's "Example(s)" value, used to disambiguate
            integer vs. number for "Numeric" fields.

    Returns:
        A (json_type, format) tuple, where json_type is one of
        "string" / "integer" / "number", and format is currently always
        None (reserved for future use; date formatting is applied
        separately by is_date_field).
    """
    t = (raw_type or '').strip().lower()

    if t == 'numeric':
        example = (example or '').strip()
        try:
            if '.' in example:
                float(example)
                return 'number', None
            else:
                int(example)
                return 'integer', None
        except ValueError:
            # Not actually parseable as a number - fall back to string
            return 'string', None

    # Everything else (Alphanumeric, Free text, Permitted value(s)..., Structured
    # format, NCBITaxon..., GAZ geography ontology..., etc.) is treated as string.
    return 'string', None


def is_multiselect(raw_type):
    """
    Check whether a "Type of Variable(s)" value marks the field as
    multiselect (e.g. 'Permitted value(s), or Other (Free text)- multiselect'),
    meaning multiple picklist values can be selected for that field.

    Args:
        raw_type: The raw "Type of Variable(s)" value from the CSV row.

    Returns:
        True if the field should be modelled as a JSON array of strings
        rather than a single string.
    """
    return 'multiselect' in (raw_type or '').lower()


def is_date_field(property_key, raw_type):
    """
    Decide whether a field should get JSON Schema's "date" format.

    The "Structured format" type covers several different kinds of values
    in the malaria table (dates, addresses, rates like "20 infectious
    bites/person/year"), so "Structured format" alone isn't a reliable
    signal. This combines it with a check for "date" in the property key
    (e.g. sample_collection_date, isolation_date) to only flag genuine
    date fields.

    Args:
        property_key: The sanitised snake_case property key for the field.
        raw_type: The raw "Type of Variable(s)" value from the CSV row.

    Returns:
        True if the field should be annotated with "format": "date".
    """
    return 'structured format' in (raw_type or '').lower() and (
        'date' in property_key
    )


def parse_properties_table(path_to_properties_table):
    """
    Read the malaria properties CSV and build the JSON Schema "properties"
    object, one entry per row.

    For each row this:
      1. Derives a snake_case property key from the "Field" label, falling
         back to an ontology-ID-based key (with a warning) if the label
         sanitises to an empty or duplicate key.
      2. Carries over the Definition, Guidance, and Ontology ID columns.
      3. Classifies the JSON Schema type (string/integer/number/array) from
         the "Type of Variable(s)" column via classify_value_type and
         is_multiselect.
      4. Adds a "date" format when is_date_field says the field is a date.
      5. Records the example value (coerced to int/float when the field
         is numeric), kept as a single-item list rather than being split
         on commas (see inline note below on why).

    Args:
        path_to_properties_table: Path to the malaria CSV file.

    Returns:
        A dict mapping property_key -> JSON Schema property definition,
        suitable for use as the "properties" value in a JSON Schema.
    """
    properties = {}
    seen_keys = set()

    with open(path_to_properties_table, newline='') as f:
        reader = csv.DictReader(f, delimiter=SEPARATOR, quotechar=QUOTE)
        for row in reader:
            raw_label = row.get('Field', '') or ''
            property_key = interface_label_to_property_key(raw_label)

            # Guard against rows whose Field label sanitises to an empty/duplicate
            # key (a data-quality issue in the source table, e.g. a lone '/').
            if not property_key or property_key in seen_keys:
                ontology_id = (row.get('Ontology ID') or '').strip()
                fallback = re.sub(r'[^\w]', '_', ontology_id).strip('_').lower()
                property_key = 'field_' + fallback if fallback else f'unnamed_field_{len(properties) + 1}'
                print(
                    f"Warning: could not derive a usable property key from Field "
                    f"'{raw_label}'. Falling back to '{property_key}'.",
                    file=sys.stderr,
                )
            seen_keys.add(property_key)

            raw_type = row.get('Type of Variable(s)', '') or ''
            example_raw = (row.get('Example(s)', '') or '').strip()

            prop = {}
            prop['description'] = (row.get('Definition', '') or '').strip()
            prop['guidance'] = (row.get('Guidance', '') or '').strip()
            prop['ontology'] = (row.get('Ontology ID', '') or '').strip()
            prop['source_value_type'] = raw_type.strip()

            json_type, fmt = classify_value_type(raw_type, example_raw)

            if is_multiselect(raw_type):
                prop['type'] = 'array'
                prop['items'] = {'type': 'string'}
            else:
                prop['type'] = json_type

            if fmt:
                prop['format'] = fmt
            elif is_date_field(property_key, raw_type):
                prop['format'] = 'date'

            # Examples: the malaria table's example values frequently contain
            # commas that are NOT list separators (addresses, dates, free text
            # descriptions), unlike the SARS-CoV-2 table which reliably used
            # ';' as a multi-example separator. So examples are kept as a
            # single value here rather than being split.
            if example_raw:
                if json_type == 'integer':
                    try:
                        example_value = int(example_raw)
                    except ValueError:
                        example_value = example_raw
                elif json_type == 'number':
                    try:
                        example_value = float(example_raw)
                    except ValueError:
                        example_value = example_raw
                else:
                    example_value = example_raw
                prop['examples'] = [example_value]
            else:
                prop['examples'] = []

            properties[property_key] = prop

    return properties


def get_required_fields(path_to_properties_table):
    """
    Read the malaria properties CSV and collect the property keys of every
    field marked "Required" in the "Required/Optional" column (fields marked
    "Recommended" or "Optional" are not included).

    Re-derives property keys the same way as parse_properties_table
    (including the ontology-ID fallback for empty/duplicate keys) so the
    returned keys line up with the ones used in the "properties" object.

    Args:
        path_to_properties_table: Path to the malaria CSV file.

    Returns:
        A list of property_key strings for all required fields, suitable
        for use as the "required" value in a JSON Schema.
    """
    required_fields = []
    seen_keys = set()
    with open(path_to_properties_table, newline='') as f:
        reader = csv.DictReader(f, delimiter=SEPARATOR, quotechar=QUOTE)
        for row in reader:
            raw_label = row.get('Field', '') or ''
            property_key = interface_label_to_property_key(raw_label)
            if not property_key or property_key in seen_keys:
                ontology_id = (row.get('Ontology ID') or '').strip()
                fallback = re.sub(r'[^\w]', '_', ontology_id).strip('_').lower()
                property_key = 'field_' + fallback if fallback else None
            if property_key:
                seen_keys.add(property_key)
            if property_key and (row.get('Required/Optional', '') or '').strip() == 'Required':
                required_fields.append(property_key)

    return required_fields


def main(args):
    """
    Entry point: build the full JSON Schema (properties + required list)
    from the input CSV and write it to the output path, then print a short
    summary (property/required counts) to stderr.

    Args:
        args: Parsed command-line arguments with `input` (CSV path) and
            `output` (JSON output path) attributes.
    """
    schema = {
        "$schema": "http://json-schema.org/draft/2019-09/schema#",
        "title": "PHA4GE Malaria Contextual Data Schema",
        "type": "object",
        "properties": {},
        "required": [],
    }

    schema["properties"] = parse_properties_table(args.input)
    schema["required"] = get_required_fields(args.input)

    output_path = args.output
    with open(output_path, "w") as fh:
        json.dump(schema, fh, indent=2)

    print(f"Wrote schema with {len(schema['properties'])} properties "
          f"({len(schema['required'])} required) to {output_path}", file=sys.stderr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert the PHA4GE Malaria Standardised Terms CSV into a JSON schema.'
    )
    parser.add_argument('input', help='Input malaria properties table (CSV)')
    parser.add_argument(
        '-o', '--output',
        default='PHA4GE_Malaria_Contextual_Data_Schema.json',
        help='Output JSON schema file path (default: %(default)s)'
    )

    args = parser.parse_args()
    main(args)
