# backend/services/ai_agents/ocr_agent.py

import os
from backend.utils.logger import logger


class OCRAgent:
    """
    Lightweight OCR handler with a future-proof interface.

    Designed to plug in:
    - Google Vision API
    - AWS Textract
    - Azure Cognitive Services
    - Tesseract (local)
    - PaddleOCR / EasyOCR

    For now, returns a structured placeholder.
    """

    async def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image file.

        Returns:
            str: Extracted text (placeholder for now)
        """
        try:
            logger.info(f"OCR process started for: {image_path}")

            # -------------------------------------------------------
            # CHECK IF FILE EXISTS
            # -------------------------------------------------------
            if not os.path.exists(image_path):
                logger.error(f"OCR error: File not found → {image_path}")
                return (
                    "OCR Error: File not found. Verify image path before processing."
                )

            # -------------------------------------------------------
            # PLACEHOLDER IMPLEMENTATION
            # -------------------------------------------------------
            # Real OCR integration will replace this block.
            # -------------------------------------------------------

            logger.info("Returning placeholder OCR output. "
                        "Integrate real OCR engine in future.")

            placeholder_text = (
                "OCR Placeholder Output:\n"
                "- Real text extraction will appear here.\n"
                "- You can integrate Google Vision, AWS Textract, or Tesseract.\n"
                "- Ensure the image is clear, upright, and readable.\n"
            )

            return placeholder_text

        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return "OCR Error: Failed to extract text due to an internal error."
