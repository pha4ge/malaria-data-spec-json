# PHA4GE's Malaria Data Specification Processing Tool

## Motivation
In the face of the ongoing burden of malaria, [PHA4GE](https://pha4ge.org/) has identified a clear and present need for a fit-for-purpose, open source malaria contextual data standard. The specification is implementable via a collection template, as well as an array of protocols and tools to support the harmonisation and submission of sequence data and contextual information to public repositories.

The purpose of the [PHA4GE Malaria specification](https://github.com/pha4ge/Malaria-Community-Metadata-Standard) is to provide a structure that enables consistent collection and formatting of malaria metadata in order to structure data consistently across disparate laboratory and epidemiological databases so that they can be harmonised for different uses. It embraces FAIR data stewardship principles and emphasises machine-actionability and consistency of data.

The PHA4GE's Malaria Data Specification Processing Tool aims to collect the human readable terms and convert them to the machine processable formats in JSON schema language.

## The Data Specification Processing Tool
The aim of this tool is to take a simple tabular description of fields and convert it to JSON schema language so that the information is machine processable and therefore possible to be harmonised for different uses.

### Installation
The Malaria Data Specification Processing Tool is a simple Python script that automatically converts a tabular to JSON schema language. To install you simply require `python >= 3.7.*` and `git` to clone this repository.

### Usage
`python malaria_table_json.py PHA4GE_Malaria_Standardised_Terms_with_required_optional.csv`

This writes the schema to `PHA4GE_Malaria_Contextual_Data_Schema.json` by default. An alternate output path can be given with `-o`/`--output`:

`python malaria_table_json.py PHA4GE_Malaria_Standardised_Terms_with_required_optional.csv -o schema.json`

#### Input
Currently, the Data Specification Processing Tool takes as input PHA4GE's "Malaria Standardised Terms" tabular. This table lists the terms for the malaria submission template according to the PHA4GE contextual data collection specification and it's structure is described in Table 1.

**Table 1** Field description of the "Malaria Standardised Terms" tabular.
| Column 	| Description 	|
|:-:	|:-:	|
| Field 	| Column headers in the submission template 	|
| Required/Optional 	| Type of requirement according to PHA4GE's template specification. Limited to the values "Optional", "Recommended" and "Required".  	|
| Ontology ID 	| The ontology term identifier associated with the field. 	|
| Type of Variable(s) 	| Expected field's value type, e.g. "Alphanumeric", "Numeric", "Free text", or "Permitted value(s)" (optionally combined with "Other (+ Free text)" and/or "multiselect"). 	|
| Definition 	| Short description for the expected field value. 	|
| Guidance 	| Detailed description for the expected field value. 	|
| Example(s) 	| Example for the expected field value. 	|

#### Output
Currently, only JSON schema format is being created by this tool. Each property in the schema includes the field's description, guidance, ontology ID, original source value type, JSON Schema type (and format/items where applicable), and example value. An example output is available at `PHA4GE_Malaria_Contextual_Data_Schema.json` in this repository.

## Contacts
For more information and/or assistance, contact `elulamba@pha4ge.org` or the issue page of this repository.

## Acknowledgements
This tool is adapted from PHA4GE's [SARS-CoV-2 Data Specification Processing Tool](https://github.com/pha4ge/sars-cov-2-data-spec-json), which pioneered this approach of converting a simple tabular description of fields into machine-processable JSON schema language. `malaria_table_json.py` builds on that tool's design, adapted to the column layout and value-type vocabulary of the Malaria Standardised Terms tabular.

