from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
from langdetect import detect
from gptzero import ZeroAccount, ZeroVerdict, ZeroVerdictData
from zeroGPT import zeroGPTVerdict
from paraphraser import paraphrase
from plagiarism import turnitinPlagaiarsimChecker
from enum import Enum

class ParaphraserModes(Enum):
    Creative = 3
    Smart = 4
    Shorten = 5

class Content(BaseModel):
    content: str

class ParaphraserContent(BaseModel):
    content: str
    mode: ParaphraserModes

app = FastAPI()

@app.post("/gptzero/scan/", response_model=ZeroVerdictData)
def gpt_zero_scan(content: Content):
    acc = ZeroAccount.get_from_local()
    if not acc:
        acc = ZeroAccount.create()
    
    res = ZeroVerdict.get(jsonable_encoder(content)["content"], acc)
    if res:
        return res
    raise HTTPException(status_code=500, detail="Something went wrong please check logs")

@app.post("/zerogpt/scan/")
def zero_gpt_scan(content: Content):

    res = zeroGPTVerdict(jsonable_encoder(content)["content"])
    if res:
        return res
    raise HTTPException(status_code=500, detail="Something went wrong please check logs")

@app.post("/turnitinPlagiarism/scan/")
def zero_gpt_scan(content: Content):

    inp = jsonable_encoder(content)["content"]
    res = turnitinPlagaiarsimChecker(inp, detect(inp))
    if res:
        return res
    raise HTTPException(status_code=500, detail="Something went wrong please check logs")

@app.post("/paraphrase/")
def paraphraser(content: ParaphraserContent):
    inp = jsonable_encoder(content)
    res = paraphrase(inp["content"], detect(inp["content"]), str(inp["mode"]))
    if res:
        return {"paraphraser": res}
    raise HTTPException(status_code=500, detail="Something went wrong please check logs")

