import uuid
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from openai import OpenAI
from common.config import AppConfig
from apis.conversation.prompts import get_system_prompt
from pydantic import BaseModel, Field
import traceback


class LLMResponse(BaseModel):
  """Structured output schema for LLM response"""
  reply_text: str = Field(description="AI response text to the user")
  selected_screen_key: Optional[str] = Field(default=None, description="Screen key to navigate to, or null if no navigation needed")


class AudioProcessor:
  """
  Processor untuk handle speech-to-text, anonymization, LLM, dan text-to-speech
  """

  def __init__(self):
    self.openai_client = OpenAI(api_key=AppConfig.OPENAI_API_KEY)
    base_llm = ChatOpenAI(
      model="gpt-4o-mini",
      temperature=0.7,
      openai_api_key=AppConfig.OPENAI_API_KEY
    )
    # Create LLM with structured output
    self.llm = base_llm.with_structured_output(LLMResponse)
    self.analyzer = AnalyzerEngine()
    self.anonymizer = AnonymizerEngine()

  async def speech_to_text(self, audio_path: str) -> str:
    """
    Convert audio file to text using OpenAI Whisper

    Args:
        audio_path: Path to audio file

    Returns:
        Transcribed text
    """
    try:
      with open(audio_path, "rb") as audio_file:
        transcript = self.openai_client.audio.transcriptions.create(
          model="whisper-1",
          file=audio_file
        )
      return transcript.text
    except Exception as e:
      print(f"Error in speech_to_text: {e}")
      raise

  def anonymize_pii(self, text: str) -> Tuple[str, Dict[str, str]]:
    """
    Detect dan mask PII data dari text menggunakan Presidio

    Args:
        text: Original text

    Returns:
        Tuple of (anonymized_text, mapping_dict)
        mapping_dict format: {"<NAMA_USER>": "Eko Putra", "<EMAIL>": "eko@example.com"}
    """
    try:
      # Analyze text untuk detect PII
      analyzer_results = self.analyzer.analyze(
        text=text,
        language="id",
        entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION", "DATE_TIME"]
      )

      # Create mapping untuk unmasking nanti
      mapping = {}
      anonymized_text = text

      # Sort results by start position (descending) to avoid index shifting
      sorted_results = sorted(analyzer_results, key=lambda x: x.start, reverse=True)

      for i, result in enumerate(sorted_results):
        entity_type = result.entity_type
        original_value = text[result.start:result.end]

        # Generate placeholder based on entity type
        if entity_type == "PERSON":
          placeholder = f"<NAMA_USER_{i}>"
        elif entity_type == "EMAIL_ADDRESS":
          placeholder = f"<EMAIL_{i}>"
        elif entity_type == "PHONE_NUMBER":
          placeholder = f"<TELP_{i}>"
        elif entity_type == "LOCATION":
          placeholder = f"<LOKASI_{i}>"
        elif entity_type == "DATE_TIME":
          placeholder = f"<TANGGAL_{i}>"
        else:
          placeholder = f"<PII_{i}>"

        # Store mapping
        mapping[placeholder] = original_value

        # Replace in text
        anonymized_text = (
          anonymized_text[:result.start] +
          placeholder +
          anonymized_text[result.end:]
        )

      return anonymized_text, mapping

    except Exception as e:
      print(f"Error in anonymize_pii: {e}")
      # Fallback: return original text if error
      return text, {}

  def mask_screen_data(self, screens: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """
    Mask sensitive screen data (screen_id, deep_link, screen_name)

    Args:
        screens: List of screen objects

    Returns:
        Tuple of (masked_screens, mapping_dict)
        masked_screens: List dengan placeholder
        mapping_dict: {"SCREEN_0": {"screen_id": "...", "deep_link": "...", "screen_name": "..."}}
    """
    masked_screens = []
    mapping = {}

    for i, screen in enumerate(screens):
      screen_key = f"SCREEN_{i}"

      # Store original values
      mapping[screen_key] = {
        "screen_id": screen.get("screen_id"),
        "deep_link": screen.get("deep_link"),
        "screen_name": screen.get("screen_name")
      }

      # Create masked version dengan hanya placeholder
      masked_screen = {
        "screen_key": screen_key,
        "description": screen.get("description", ""),
      }

      masked_screens.append(masked_screen)

    return masked_screens, mapping

  async def get_llm_response(
      self,
      transcript: str,
      masked_screens: List[Dict[str, Any]],
      conversation_history: Optional[List[Dict[str, str]]] = None
  ) -> Dict[str, Any]:
      """
      Send transcript dan screen list ke LLM untuk mendapatkan response

      Args:
          transcript: Transcribed text (already anonymized)
          masked_screens: List of masked screens
          conversation_history: Optional list of previous conversations
                                [{"role": "user", "text": "..."}, {"role": "ai", "text": "..."}]

      Returns:
          Dict containing:
          - reply_text: AI response text
          - selected_screen_key: Screen key yang dipilih atau None
      """
      try:
        # Format screens list
        screens_text = "\n".join([
          f"- {screen['screen_key']}: {screen.get('description', 'No description')}"
          for screen in masked_screens
        ])

        # Get system prompt from prompts.py
        formatted_system_prompt = get_system_prompt(screens_text)

        # Build messages list
        messages = [SystemMessage(content=formatted_system_prompt)]

        # Add conversation history if available
        if conversation_history:
          for conv in conversation_history:
            if conv["role"] == "user":
              messages.append(HumanMessage(content=conv["text"]))
            elif conv["role"] == "ai":
              messages.append(AIMessage(content=conv["text"]))

        # Add current transcript
        messages.append(HumanMessage(content=transcript))

        # Invoke LLM with structured output
        response: LLMResponse = self.llm.invoke(messages)

        return {
          "reply_text": response.reply_text,
          "selected_screen_key": response.selected_screen_key
        }

      except Exception as e:
        print(f"❌ Error in get_llm_response: {e}")
        print(f"📝 Raw AI Response (if available):")
        
        traceback.print_exc()
        return {
          "reply_text": "Maaf, saya mengalami kesulitan memproses permintaan Anda.",
          "selected_screen_key": None
        }

  def unmask_response(
      self,
      reply_text: str,
      pii_mapping: Dict[str, str]
  ) -> str:
      """
      Unmask PII data in LLM response

      Args:
          reply_text: LLM response text with placeholders
          pii_mapping: Mapping dari placeholder ke original value

      Returns:
          Unmasked text
      """
      unmasked_text = reply_text

      for placeholder, original_value in pii_mapping.items():
        unmasked_text = unmasked_text.replace(placeholder, original_value)

      return unmasked_text

  def unmask_screen(
      self,
      screen_key: Optional[str],
      screen_mapping: Dict[str, Dict[str, Any]]
  ) -> Optional[Dict[str, Any]]:
      """
      Unmask screen data to get original screen info

      Args:
          screen_key: Screen key from LLM response
          screen_mapping: Mapping dari screen_key ke original data

      Returns:
          Original screen data atau None
      """
      if not screen_key or screen_key not in screen_mapping:
        return None

      return screen_mapping[screen_key]

  async def text_to_speech(self, text: str) -> str:
      """
      Convert text to speech using OpenAI TTS

      Args:
          text: Text to convert

      Returns:
          Path to generated audio file
      """
      try:
        # Generate unique filename
        audio_filename = f"reply_{uuid.uuid4()}.mp3"
        audio_path = str(Path(AppConfig.UPLOAD_DIR) / audio_filename)

        # Create directory if not exists
        Path(AppConfig.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

        tts_instructions = "Kamu adalah asisten virtual yang menjawab dengan suara yang ramah dan natural. Text yang disediakan ada 2 kemungkinan yaitu bahasa Indonesia atau bahasa Inggris"

        # Generate speech with streaming response
        with self.openai_client.audio.speech.with_streaming_response.create(
          model="gpt-4o-mini-tts",
          voice="nova",
          input=text,
          instructions=tts_instructions
        ) as response:
          response.stream_to_file(audio_path)

        return audio_path

      except Exception as e:
        print(f"Error in text_to_speech: {e}")
        raise
