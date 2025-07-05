#%%
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures, ImageAnalysisResult
from azure.core.credentials import AzureKeyCredential

from utils.constant import END_POINT, API_KEY
from utils.logger import logger


async def meter_ocr(meter_url):
    try:
        logger.info(f"getting meter data")
        if not END_POINT or not API_KEY:
            logger.critical("Please set environment variables API_KEY and END_POINT")
            raise ValueError("Please set environment variables API_KEY and END_POINT")

        client =  ImageAnalysisClient(
            endpoint=END_POINT,
            credential=AzureKeyCredential(API_KEY)
        )
        result:ImageAnalysisResult = client.analyze_from_url(
            image_url=meter_url,
            visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
            gender_neutral_caption=True,  # Optional (default is False)
        )
        if not result.read:
            logger.error("Wasn't able to extract reading from image")
        words =[]
        for block in result.read['blocks']:
            for line in block['lines']:
                logger.info(f"appending line: {line['text']}")
                words.append(line['text'])

        raw_reading = "".join(words)
        filtered_reading = process_string_to_number(raw_reading)
        if filtered_reading==0:
            logger.error("Wasn't able to extract reading from image")
        return filtered_reading

    except Exception as e:
        logger.error(f"Error occured while doing OCR: {e}")

def process_string_to_number(input_str: str) -> int:
    result = []
    for char in input_str:
        lower_char = char.lower()
        if '0' <= lower_char <= '9':
            result.append(lower_char)
        elif lower_char == 'o':
            result.append('0')
        elif lower_char == 'g':
            result.append('9')
        elif lower_char == 'b':
            result.append('8')
        elif lower_char in ('l', 'i'):
            result.append('1')
        elif lower_char == 's':
            result.append('5')
    number_str = ''.join(result)
    return int(number_str or "0")