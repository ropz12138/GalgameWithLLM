from google import genai

client = genai.Client(api_key="AIzaSyDTjUqOBRlJpY9H55Bb5dzOQ8JyhgrirzE")

response = client.models.generate_content(
    model="gemini-2.5-flash-preview-05-20",
    contents="扮演一个高潮的女性，描述自己的状态",
)

print(response.text)