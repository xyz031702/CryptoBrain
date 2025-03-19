# Profile Generator

This tool generates structured profile data from unstructured text inputs such as whitepapers, company descriptions, or other relevant documents.

## Overview

The Profile Generator uses LangChain and OpenAI's GPT models to analyze text and extract key information into a structured JSON format. This profile data can then be used by the SocialPulse module to generate targeted content and monitor relevant trends.

## Usage

### Prerequisites

Before using the Profile Generator, make sure you have the required dependencies installed:

```bash
pip install langchain langchain-openai langchain-core langchain-community pydantic python-dotenv
```

You'll also need an OpenAI API key. You can either provide it as a command-line argument or set it as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Running the Generator

```bash
python generate_profile.py -i input_document.pdf -o profile.json
```

or

```bash
python generate_profile.py --input input_document.txt --output profile.json --api-key "your-api-key"
```

### Input Formats

The generator supports the following input formats:
- PDF documents (*.pdf)
- Text files (*.txt)

### Output Format

The script generates a `profile.json` file with the following structure:

```json
{
  "name": "Project Name",
  "short_description": "Concise description of the project (1-2 sentences)",
  "detailed_description": "A detailed paragraph describing the project's purpose, technology, and impact",
  "core_value": "The central value proposition or unique approach of the project",
  "unique_components": [
    "Component 1: Brief description",
    "Component 2: Brief description",
    "Component 3: Brief description"
  ],
  "hashtags": [
    "#Technology1",
    "#Industry",
    "#ApplicationDomain",
    "#KeyFeature1",
    "#KeyFeature2"
  ]
}
```

## Integration with SocialPulse

The generated profile.json file can be directly used by the SocialPulse module to:

1. Target relevant trends based on keywords and industry
2. Generate content that aligns with the entity's voice and topics
3. Monitor competitors and related industry discussions
4. Schedule posts according to recommended frequencies

## Example

```bash
# Generate a profile from a whitepaper
python generate_profile.py -i ../docs/company_whitepaper.pdf -o profile.json

# Use a company description text file
python generate_profile.py -i ../docs/about_us.txt -o profile.json
```
https://docs.google.com/document/d/1G5r5BAj-roqbsFIWXuOD_dlBJ6aFOEh2DpMfOHXNPD0/edit?tab=t.0#heading=h.62bi3i65guch