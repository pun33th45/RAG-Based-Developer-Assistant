import re


API_KEY_PATTERN = re.compile(r"AIza[0-9A-Za-z_\-]{20,}")


def safe_error_message(error: Exception) -> str:
    message = str(error)
    message = API_KEY_PATTERN.sub("[redacted-api-key]", message)

    if "CONSUMER_SUSPENDED" in message or "has been suspended" in message:
        return "Gemini API key is suspended. Create a new key in Google AI Studio, update backend/.env, and restart the backend."

    if "PERMISSION_DENIED" in message or "403" in message:
        return "Gemini permission denied. Check that your API key is valid and enabled for the Gemini API."

    return message
