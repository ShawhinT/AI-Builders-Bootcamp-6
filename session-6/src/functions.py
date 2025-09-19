from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig
import re
import os
from agents import function_tool

@function_tool
def fetch_video_transcript(url: str) -> str:
    """
    Extract transcript with timestamps from a YouTube video URL and format it for LLM consumption
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: Formatted transcript with timestamps, where each entry is on a new line
             in the format: "[MM:SS] Text"
    """
    # Extract video ID from URL
    video_id_pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    video_id_match = re.search(video_id_pattern, url)
    
    if not video_id_match:
        raise ValueError("Invalid YouTube URL")
    
    video_id = video_id_match.group(1)
    
    def format_transcript(transcript):
        """Format transcript entries with timestamps"""
        formatted_entries = []
        for entry in transcript:
            # Convert seconds to MM:SS format
            minutes = int(entry.start // 60)
            seconds = int(entry.start % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"

            formatted_entry = f"{timestamp} {entry.text}"
            formatted_entries.append(formatted_entry)

        # Join all entries with newlines
        return "\n".join(formatted_entries)

    # First attempt: Try without proxy
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        return format_transcript(transcript)
    except Exception as e:
        # Second attempt: Try with proxy if credentials are available
        proxy_username = os.getenv("PROXY_USERNAME")
        proxy_password = os.getenv("PROXY_PASSWORD")
        proxy_url_base = os.getenv("PROXY_URL")

        if proxy_username and proxy_password:
            try:
                # Construct proxy URLs with credentials
                http_proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_url_base}"
                https_proxy_url = f"https://{proxy_username}:{proxy_password}@{proxy_url_base}"

                proxy_config = GenericProxyConfig(
                    http_url=http_proxy_url,
                    https_url=https_proxy_url
                )

                ytt_api_with_proxy = YouTubeTranscriptApi(proxy_config=proxy_config)
                transcript = ytt_api_with_proxy.fetch(video_id)
                return format_transcript(transcript)
            except Exception as proxy_error:
                raise Exception(f"Error fetching transcript (tried with and without proxy): {str(proxy_error)}")
        else:
            raise Exception(f"Error fetching transcript: {str(e)}. Proxy credentials not available.")

@function_tool
def fetch_intstructions(prompt_name: str) -> str:
    """
    Fetch instructions for a given prompt name from the prompts/ directory

    Args:
        prompt_name (str): Name of the prompt to fetch instructions for
        Available prompts: 
            - write_blog_post
            - write_social_post
            - write_video_chapters

    Returns:
        str: Instructions for the given prompt
    """
    import os
    script_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(script_dir, "prompts", f"{prompt_name}.md")
    with open(prompt_path, "r") as f:
        return f.read()