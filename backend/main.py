from fastapi import FastAPI, File, UploadFile
from PIL import Image
from typing import List, Optional, Union
import io, uvicorn, gc
import base64
from fastapi.responses import StreamingResponse
import torch
import time
from diffusers import StableDiffusionInpaintPipeline, DPMSolverMultistepScheduler
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel

class inPaintReq(BaseModel):
    prompt: str
    img: str
    mask: str

app = FastAPI()
app.POOL: ThreadPoolExecutor = None

@app.on_event("startup")
def startup_event():
    app.POOL = ThreadPoolExecutor(max_workers=1)
@app.on_event("shutdown")
def shutdown_event():
    app.POOL.shutdown(wait=False)

model_id = "stabilityai/stable-diffusion-2-inpainting"
pipe_nsd = StableDiffusionInpaintPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
# pipe_nsd.scheduler = DPMSolverMultistepScheduler.from_config(pipe_nsd.scheduler.config)
pipe_nsd = pipe_nsd.to("cuda")
pipe_nsd.enable_attention_slicing()


# @app.post("/getimage_nsd")
# def get_image_nsd(
#     #prompt: Union[str, List[str]],
#     prompt: Optional[str] = "dog",
#     height: Optional[int] = 512,
#     width: Optional[int] = 512,
#     num_inference_steps: Optional[int] = 50,
#     guidance_scale: Optional[float] = 7.5,
#     negative_prompt: Optional[str] = None,):

#     image = app.POOL.submit(pipe_nsd,prompt,height,width,num_inference_steps,guidance_scale,negative_prompt).result().images
#     gc.collect()
#     torch.cuda.empty_cache()
#     filtered_image = io.BytesIO()
#     image[0].save(filtered_image, "JPEG")
#     filtered_image.seek(0)
#     return StreamingResponse(filtered_image, media_type="image/jpeg")

@app.post("/inpaint")
def inpaint(
    body: inPaintReq
):
    # res = pipe_nsd(prompt=prompt, image=img, mask_image=mask).images[0]
    img_bytes = base64.b64decode(body.img)
    mask_bytes = base64.b64decode(body.mask)
    
    img_pil = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    mask_pil = Image.open(io.BytesIO(mask_bytes)).convert("RGB")
    print('img size', img_pil.size)
    print('mask size', mask_pil.size)

    res = app.POOL.submit(pipe_nsd, prompt=body.prompt, image=img_pil, mask_image=mask_pil, height=img_pil.height, width=img_pil.width).result().images[0]
    torch.cuda.empty_cache()
    filtered_image = io.BytesIO()
    res.save(filtered_image, "JPEG")
    filtered_image.seek(0)
    return StreamingResponse(filtered_image, media_type="image/jpeg")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)