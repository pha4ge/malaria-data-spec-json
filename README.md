# PHA4GE's Malaria Data Specification Processing Tool

## Motivation
In the face of the ongoing burden of malaria, [PHA4GE](https://pha4ge.org/) has identified a clear and present need for a fit-for-purpose, open source malaria contextual data standard. The specification is implementable via a collection template, as well as an array of protocols and tools to support the harmonisation and submission of sequence data and contextual information to public repositories.

The purpose of the [Malaria Community Metadata Standard (MCMS)](https://github.com/pha4ge/Malaria-Community-Metadata-Standard) is to provide a structure that enables consistent collection and formatting of malaria metadata, so that data held across disparate laboratory and epidemiological databases can be harmonised for different uses. It embraces FAIR data stewardship principles and emphasises machine-actionability and consistency of data.

PHA4GE's Malaria Data Specification Processing Tool converts the human-readable terms of the specification into a machine-processable JSON Schema.

## The Data Specification Processing Tool
This tool takes a simple tabular description of fields and converts it to JSON Schema, so that the information is machine-processable and can be harmonised for different uses.

### Repository contents
| File | Description |
|:--|:--|
| `malaria_table_json.py` | The processing tool. |
| `MalariaCommunityMetadataStandard_human_samples_v2_0_0_with_required_optional.csv` | MCMS v2.0.0 field table for human (clinical / One Health) samples. |
| `MalariaCommunityMetadataStandard_mosquito_samples_v2_0_0_with_required_optional.csv` | MCMS v2.0.0 field table for mosquito (vector) and environmental samples. |
| `PHA4GE_Malaria_Contextual_Data_Schema_Human.json` | JSON Schema generated from the human samples table. |
| `PHA4GE_Malaria_Contextual_Data_Schema_Mosquito.json` | JSON Schema generated from the mosquito samples table. |

### Installation
The tool is a single Python script with no third-party dependencies. You need Python 3.7 or later, and `git` to clone this repository:

```bash
git clone https://github.com/pha4ge/malaria-data-spec-json.git
cd malaria-data-spec-json
```

### Usage
```bash
python malaria_table_json.py <input.csv> [-o <output.json>]
```

If `-o`/`--output` is not given, the schema is written to `PHA4GE_Malaria_Contextual_Data_Schema.json`. The number of properties and required fields is printed when the script finishes.

To regenerate the schemas in this repository:

```bash
python malaria_table_json.py MalariaCommunityMetadataStandard_human_samples_v2_0_0_with_required_optional.csv \
  -o PHA4GE_Malaria_Contextual_Data_Schema_Human.json

python malaria_table_json.py MalariaCommunityMetadataStandard_mosquito_samples_v2_0_0_with_required_optional.csv \
  -o PHA4GE_Malaria_Contextual_Data_Schema_Mosquito.json
```

#### Input
The tool takes as input a CSV version of the **Field Reference Guide** sheet from an MCMS collection template ([human samples](https://github.com/pha4ge/Malaria-Community-Metadata-Standard/blob/v0.1/MalariaCommunityMetadataStandard_human_samples_v2_0_0.xlsx) or [mosquito samples](https://github.com/pha4ge/Malaria-Community-Metadata-Standard/blob/v0.1/MalariaCommunityMetadataStandard_mosquito_samples_v2_0_0.xlsx)). The CSV has one row per field, with section-header rows removed, and the columns described in Table 1.

The `Required/Optional` column is taken from the template's colour coding: field names in yellow are **Required**, purple are **Recommended** and white are **Optional**.

**Table 1** Columns of the input CSV.
| Column | Description |
|:--|:--|
| Field | Column header in the submission template. |
| Required/Optional | Requirement level according to the MCMS template. Limited to the values "Optional", "Recommended" and "Required". |
| Ontology ID | The ontology term identifier associated with the field. |
| Type of Variable(s) | Expected value type, e.g. "Alphanumeric", "Numeric", "Free text", or "Permitted value(s)" (optionally combined with "Other (+ Free text)" and/or "multiselect"). |
| Definition | Short description of the expected field value. |
| Guidance | Detailed description of the expected field value. |
| Example(s) | Example of the expected field value. |

#### Output
The tool creates a JSON Schema (draft 2019-09). Each field label is converted to a snake_case property key. Each property includes the field's description, guidance, ontology ID, original source value type, JSON Schema type (with format/items where applicable) and example value. Only fields marked **Required** are listed in the schema's `required` array.

Example outputs are available in this repository as `PHA4GE_Malaria_Contextual_Data_Schema_Human.json` and `PHA4GE_Malaria_Contextual_Data_Schema_Mosquito.json`.

## Contacts
For more information or assistance, contact `elulamba@pha4ge.org` or open an issue on this repository.

## Acknowledgements
This tool is adapted from PHA4GE's [SARS-CoV-2 Data Specification Processing Tool](https://github.com/pha4ge/sars-cov-2-data-spec-json), which pioneered this approach of converting a simple tabular description of fields into machine-processable JSON Schema. `malaria_table_json.py` builds on that tool's design, adapted to the column layout and value-type vocabulary of the MCMS field tables.
