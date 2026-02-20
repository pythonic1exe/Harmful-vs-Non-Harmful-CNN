"""
Gemini API Service for Image Captioning

This module provides functionality to generate image captions (title + description)
using Google's Gemini API. It should ONLY be called for images that have already
been classified as NON-HARMFUL by the CNN model.

IMPORTANT: This service does NOT perform safety detection. The CNN handles that.
"""

import base64
import os
from typing import Dict, Optional
from google import genai
from google.genai import types


class GeminiService:
    """Service class for interacting with Gemini API for image captioning."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini service.
        
        Args:
            api_key: Gemini API key. If not provided, reads from GEMINI_API_KEY env var.
        
        Raises:
            ValueError: If API key is not provided and not found in environment.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it as an environment variable "
                "or pass it to the constructor."
            )
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash-exp"
        
        # System instruction for caption generation (NO safety detection)
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

# Example

Input: [Image of a sunset over mountains]

Output:
Title: Sunset Over Mountain Range
Description: A vibrant sunset casts warm colors across a mountain landscape. The scene captures the peaceful transition from day to night in a natural setting."""
    
    def generate_caption(self, image_bytes: bytes) -> Dict[str, str]:
        """
        Generate a caption (title + description) for an image.
        
        This method should ONLY be called for images already classified as NON-HARMFUL.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary with 'title' and 'description' keys
            
        Raises:
            Exception: If Gemini API call fails
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Prepare the content with image
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type="image/jpeg"
                        ),
                        types.Part.from_text(
                            text="Generate a title and description for this image."
                        ),
                    ],
                ),
            ]
            
            # Configure generation
            generate_content_config = types.GenerateContentConfig(
                system_instruction=[
                    types.Part.from_text(text=self.system_instruction),
                ],
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=200,
            )
            
            # Generate caption
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )
            
            # Parse response
            caption_text = response.text.strip()
            
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
        Parse the Gemini response to extract title and description.
        
        Args:
            caption_text: Raw text response from Gemini
            
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
                parts = caption_text.split('\n', 1)
                title = parts[0][:50] if parts else "Image Caption"
                description = parts[1] if len(parts) > 1 else caption_text
        
        return title, description


# Global instance (initialized on first use)
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """
    Get or create the global Gemini service instance.
    
    Returns:
        GeminiService instance
        
    Raises:
        ValueError: If GEMINI_API_KEY is not set
    """
    global _gemini_service
    
    if _gemini_service is None:
        _gemini_service = GeminiService()
    
    return _gemini_service
