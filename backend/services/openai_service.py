"""
OpenAI API Service for Image Captioning

This module provides functionality to generate image captions (title + description)
using OpenAI's GPT-4o model.
"""

import base64
import os
from typing import Dict, Optional
from openai import OpenAI

class OpenAIService:
    """Service class for interacting with OpenAI API for image captioning."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI service.
        
        Args:
            api_key: OpenAI API key. If not provided, reads from OPENAI_API_KEY env var.
        
        Raises:
            ValueError: If API key is not provided and not found in environment.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it as an environment variable "
                "or pass it to the constructor."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"
        
        # System instruction for caption generation
        self.system_instruction = """You are an image captioning assistant. Generate a concise, relevant title (max 8 words) and a brief description (1–2 sentences) summarizing the main content and context of the image.

# Instructions

- Generate a title: Up to 8 words, clear and relevant to the image.
- Generate a description: 1–2 sentences highlighting the subject, context, and setting.
- Be factual and accurate. Do not hallucinate content not present in the image.
- If the image content is unclear, state so within the description.
- Do not include technical details or metadata in the output.
- Keep the tone neutral and factual.

# Output Format

Title: [Your generated title here]
Description: [Your generated description here]
"""
    
    def generate_caption(self, image_bytes: bytes) -> Dict[str, str]:
        """
        Generate a caption (title + description) for an image.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary with 'title' and 'description' keys
            
        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_instruction
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "Generate a title and description for this image."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200,
                temperature=0.7,
            )
            
            # Parse response
            caption_text = response.choices[0].message.content.strip()
            
            # Extract title and description
            title, description = self._parse_caption(caption_text)
            
            return {
                "title": title,
                "description": description
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate caption: {str(e)}")
    
    def _parse_caption(self, caption_text: str) -> tuple[str, str]:
        """
        Parse the OpenAI response to extract title and description.
        
        Args:
            caption_text: Raw text response from OpenAI
            
        Returns:
            Tuple of (title, description)
        """
        lines = caption_text.strip().split('\n')
        title = ""
        description = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
            elif line.startswith("Description:"):
                description = line.replace("Description:", "").strip()
        
        # Fallback if parsing fails
        if not title or not description:
            # Try to use the entire response as description
            if caption_text:
                parts = caption_text.strip().split('\n', 1)
                # Heuristic: First line title, rest description if labeled
                if len(parts) > 0 and not title:
                     possible_title = parts[0].replace("Title:", "").strip()
                     if len(possible_title.split()) <= 15: # Simple heuristic
                         title = possible_title
                
                if len(parts) > 1 and not description:
                    description = parts[1].replace("Description:", "").strip()
                elif not description:
                    description = caption_text

        # Final fallback
        if not title:
            title = "Image Caption"
        if not description:
            description = caption_text
        
        return title, description


# Global instance (initialized on first use)
_openai_service: Optional[OpenAIService] = None


def get_openai_service() -> OpenAIService:
    """
    Get or create the global OpenAI service instance.
    
    Returns:
        OpenAIService instance
        
    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    global _openai_service
    
    if _openai_service is None:
        _openai_service = OpenAIService()
    
    return _openai_service
