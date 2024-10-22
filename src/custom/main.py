from fastapi import Request, FastAPI
import asyncio
import uvicorn
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    title: str | None = None
    content: str | None = None

@app.get("/")
async def root():
    print("returning hello world")
    return {"message": "Hello World"}

@app.get("/say/")
async def say(message: str):
    print("received message:")
    print(message)
    return {"message": message}

@app.post("/generate")
async def generate(words: str):
    print("received words:")
    print(words)
    x, y = np.ogrid[:300, :300]

    mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
    mask = 255 * mask.astype(int)


    wc = WordCloud(background_color="white", repeat=True, mask=mask)
    wc.generate(words)

    plt.axis("off")
    plt.imshow(wc, interpolation="bilinear")
    plt.imsave(wc, "wordcloud.png")

@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down")

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8080)

print("starting server")