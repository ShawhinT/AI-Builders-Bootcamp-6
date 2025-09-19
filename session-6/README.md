---
title: YT Agent Streamlit
emoji: 🤖
sdk: docker
app_port: 8501
tags:
  - streamlit
license: apache-2.0
short_description: Example Space for running YT agent Streamlit app.
---
# yt-agent-streamlit
Example code for creating a YouTube agent with Streamlit and hosting via Hugging Face Spaces.

Resources:
- [HF Spaces app](https://huggingface.co/spaces/shawhin/yt-agent-streamlit)

## How to Run This Example

1. Clone this repo

    ```
    git clone https://github.com/ShawhinT/yt-agent-streamlit.git
    ```
2. Open repo directory

    ```
    cd yt-agent-streamlit
    ```
3. Install dependencies

    ```
    uv sync
    ```
4. Run Streamlit app

    ```
    uv run streamlit run main.py
    ```

## Hosting on HF Space

1. [Create new](https://huggingface.co/new-space) Hugging Face Space

    ```
    Name: yt-agent-streamlit
    Description: Example Space for running YT agent Streamlit app.
    Space SDK: Docker
    Docker Template: Blank
    Space Hardware: CPU
    ```
2. Add another remote to git repo

    ```
    # In your yt-agent-streamlit directory
    git remote add hf https://huggingface.co/spaces/{your_hr_username}/yt-agent-streamlit.git
    ```
3. Push code to HF spaces (may need to force first push)

    ```
    git push --force hf
    ```

### Secret Variables
For the [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) to work via hosted endpoint, a proxy service (e.g. [Decodo](https://decodo.com/lp/hellodecodo)) is required. This can be configured following the steps below.

1. Navigate to your Hugging Face Space
2. Open "Settings"
3. Scroll down to "Variables and secrets" and click "New secret"
4. Add the following secret env variables.

    ```
    PROXY_USERNAME=XXX
    PROXY_PASSWORD=XXX
    PROXY_URL=XXX
    ```