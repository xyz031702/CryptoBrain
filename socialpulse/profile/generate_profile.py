#!/usr/bin/env python3
"""
Profile Generator - Uses LangChain to extract structured profile information from text input.

This script takes a text input (whitepaper, company description, etc.) and generates
a structured profile.json file containing key information about the entity.
"""

import os
import json
import argparse
from typing import Dict, List, Any, Optional
import logging

# LangChain imports
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the profile schema using Pydantic
class ProjectProfile(BaseModel):
    """Schema for a project profile extracted from text."""
    
    name: str = Field(description="Name of the project/entity")
    
    short_description: str = Field(
        description="A concise description (1-2 sentences) of what the project does"
    )
    
    detailed_description: str = Field(
        description="A detailed paragraph describing the project's purpose, technology, and impact"
    )
    
    core_value: str = Field(
        description="The central value proposition or unique approach of the project"
    )
    
    unique_components: List[str] = Field(
        description="5-7 unique features, components, or technologies that define the project"
    )
    
    hashtags: List[str] = Field(
        description="7-10 relevant hashtags that represent the project's tech stack and vision"
    )
    
    @validator('hashtags', pre=True, each_item=True)
    def clean_hashtags(cls, v):
        """Clean hashtags by ensuring they have # prefix."""
        if isinstance(v, str):
            # Ensure hashtag has # prefix
            v = v.strip()
            if not v.startswith('#'):
                return f"#{v}"
            return v
        return v

def load_document(file_path: str) -> str:
    """Load a document from a file path."""
    logger.info(f"Loading document from {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == '.pdf':
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            return "\n".join([doc.page_content for doc in docs])
        else:  # Assume text file
            loader = TextLoader(file_path)
            docs = loader.load()
            return docs[0].page_content
    except Exception as e:
        logger.error(f"Error loading document: {str(e)}")
        raise

def chunk_text(text: str, chunk_size: int = 4000) -> List[str]:
    """Split text into manageable chunks."""
    logger.info(f"Splitting text into chunks of ~{chunk_size} characters")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=200,
        length_function=len
    )
    
    return text_splitter.split_text(text)

def create_profile_prompt() -> PromptTemplate:
    """Create the prompt template for profile generation."""
    parser = PydanticOutputParser(pydantic_object=ProjectProfile)
    
    template = """
    You are an expert technology analyst with expertise in creating detailed project profiles.
    
    Analyze the following content and extract key information to create a comprehensive project profile.
    Focus on understanding the project's name, core value proposition, key features, and technologies used.
    
    Your task is to extract:
    1. The name of the project/entity
    2. A short description (1-2 sentences) that captures its essence
    3. A detailed description explaining how it works and its impact
    4. The core value proposition that makes it unique
    5. A list of unique components or technologies it incorporates
    6. Relevant hashtags that represent the project's technology stack and vision
    
    If the information provided is incomplete, make reasonable inferences based on the available text.
    For any fields where information is completely absent, provide sensible defaults that would apply
    to a project in the described domain.
    
    CONTENT:
    {text}
    
    {format_instructions}
    """
    
    return PromptTemplate(
        template=template,
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

def extract_profile_from_chunk(chunk: str, llm: ChatOpenAI) -> Dict[str, Any]:
    """Extract profile information from a text chunk."""
    parser = PydanticOutputParser(pydantic_object=ProjectProfile)
    prompt = create_profile_prompt()
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    try:
        logger.info("Extracting profile information from text chunk")
        result = chain.run(text=chunk)
        return parser.parse(result)
    except Exception as e:
        logger.error(f"Error extracting profile: {str(e)}")
        logger.error(f"Raw LLM output: {result if 'result' in locals() else 'No output'}")
        raise

def merge_profiles(profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple profile chunks into a consolidated profile."""
    logger.info(f"Merging {len(profiles)} profile chunks")
    
    if not profiles:
        return {}
    
    # For single chunk, just return it
    if len(profiles) == 1:
        return profiles[0]
    
    # Start with the first profile
    merged = profiles[0].copy()
    
    # For list fields, combine and deduplicate
    list_fields = [
        'unique_components', 'hashtags'
    ]
    
    for field in list_fields:
        all_items = []
        for profile in profiles:
            if field in profile and profile[field]:
                all_items.extend(profile[field])
        
        # Remove duplicates while preserving order
        seen = set()
        merged[field] = [x for x in all_items if not (x in seen or seen.add(x))]
    
    # No dictionary fields in our new profile structure
    
    # For string fields, use the first non-empty value
    string_fields = ['name', 'short_description', 'detailed_description', 'core_value']
    for field in string_fields:
        for profile in profiles:
            if field in profile and profile[field] and not merged.get(field):
                merged[field] = profile[field]
                break
    
    return merged

def generate_profile(input_file: str, output_file: str, openai_api_key: Optional[str] = None):
    """Generate a profile from an input file and save to output file."""
    # Setup the LLM
    if not openai_api_key:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OpenAI API key is required. Either provide it as an argument or set OPENAI_API_KEY environment variable."
            )
    
    llm = ChatOpenAI(
        temperature=0.2,
        model="gpt-4",
        api_key=openai_api_key
    )
    
    # Load and process the document
    text = load_document(input_file)
    
    # If text is short, process it as a single chunk
    if len(text) < 6000:
        chunks = [text]
    else:
        chunks = chunk_text(text)
    
    logger.info(f"Processing {len(chunks)} text chunks")
    
    # Process each chunk
    profiles = []
    for i, chunk in enumerate(chunks):
        logger.info(f"Processing chunk {i+1}/{len(chunks)}")
        profile = extract_profile_from_chunk(chunk, llm)
        profiles.append(profile.dict())
    
    # Merge profiles from different chunks
    merged_profile = merge_profiles(profiles)
    
    # Save to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_profile, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Profile saved to {output_file}")
    return merged_profile

def main():
    """Main function to parse arguments and run the profile generator."""
    parser = argparse.ArgumentParser(description="Generate a profile.json from input text")
    
    parser.add_argument(
        "-i", "--input", 
        required=True, 
        help="Path to input file (PDF or TXT)"
    )
    
    parser.add_argument(
        "-o", "--output", 
        default="profile.json", 
        help="Path to output JSON file (default: profile.json)"
    )
    
    parser.add_argument(
        "-k", "--api-key", 
        help="OpenAI API key (optional, can also use OPENAI_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    try:
        generate_profile(args.input, args.output, args.api_key)
        print(f"✅ Profile successfully generated and saved to {args.output}")
    except Exception as e:
        logger.error(f"Error generating profile: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()
