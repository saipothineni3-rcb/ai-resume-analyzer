import google.generativeai as genai

genai.configure(
    api_key="AIzaSyC1SxDypMz4JXIXwtx6UUkggfHwPIS5ftk"
)

model = genai.GenerativeModel(
    "models/gemini-1.5-flash"
)

for m in genai.list_models():
    print(m.name)