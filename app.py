from flask import Flask, request, render_template, send_from_directory
from comfy_api_simplified import ComfyApiWrapper, ComfyWorkflowWrapper
import asyncio
import nest_asyncio

nest_asyncio.apply()

app = Flask(__name__)


@app.route("/")  # ruta: página principal
def index():
    return render_template("index.html")


filenamez = ""


@app.route(
    "/generate", methods=["POST"]
)  
def generate():

    async def async_generate():
        api = ComfyApiWrapper("http://127.0.0.1:8188/")
        print(request.get_json())
        style = request.get_json()["style_id"]
        if(request.get_json()["highQ"] == True):
            wf = ComfyWorkflowWrapper("highQ_workflow_api.json")
        else:
            wf = ComfyWorkflowWrapper("normalQ_workflow_api.json")

        positivePrompt = request.get_json()["positivePrompt"]
        # negative prompt is optional
        negativePrompt = request.get_json().get("negativePrompt", "") 
        if(negativePrompt == None):
            negativePrompt = ""
        seed = request.get_json()["seed"]
        ratio = request.get_json()["ratio"]



        # Checkpoint and ksampler parameters
        wf.set_node_param("Loader","ckpt_name", request.get_json()["checkpoint"])

        wf.set_node_param("steps", "number", request.get_json()["ksampler"]["steps"])
        wf.set_node_param("cfg", "number", request.get_json()["ksampler"]["cfg"])
        wf.set_node_param("sampler_name", "sampler_name", request.get_json()["ksampler"]["sampler_name"])
        wf.set_node_param("scheduler", "scheduler_name", request.get_json()["ksampler"]["scheduler"])

        # Loras
        for i, lora in enumerate(request.get_json()["loras"], start=1):
            print(lora)
            wf.set_node_param("LoRA Stacker", f"lora_name_{i}", lora["lora"])
            wf.set_node_param("LoRA Stacker", f"lora_wt_{i}", lora["weight"])
        
        wf.set_node_param("LoRA Stacker", "lora_count", len(request.get_json()["loras"]))
        
        print(wf.get_node_param("LoRA Stacker", "lora_count"))
        print(wf.get_node_param("LoRA Stacker", "lora_name_1"))
        print(wf.get_node_param("LoRA Stacker", "lora_wt_1"))

        # Embeddings
        for i, emb in enumerate(request.get_json()["embeddings"], start=1):
            print(emb)
            if(emb["prompt_target"] == "positive"):
                if(emb["weight"] != 1):
                    positivePrompt = positivePrompt + f",(embedding:{emb['embedding']}:{emb['weight']})"
                else:
                    positivePrompt = positivePrompt + f",embedding:{emb['embedding']}"
            else:
                if(emb["weight"] != 1):
                    negativePrompt = negativePrompt + f",(embedding:{emb['embedding']}:{emb['weight']})"
                else:
                    negativePrompt = negativePrompt + f",embedding:{emb['embedding']}"
        
        # Positive and negative prompts
        wf.set_node_param("UserInputPositive", "text", positivePrompt)
        wf.set_node_param("UserInputNegative", "text", negativePrompt)
        
        print(wf.get_node_param("UserInputPositive", "text"))
        print(wf.get_node_param("UserInputNegative", "text"))
        
        # Seed
        wf.set_node_param("User seed", "seed", seed)
        
        # Resolution
        if ratio == "1:1":
            wf.set_node_param("width", "number", 512)
            wf.set_node_param("height", "number", 512)
        else:
            wf.set_node_param("width", "number", 512)
            wf.set_node_param("height", "number", 768)
        
        # Send request and save the image
        results = api.queue_and_wait_images(wf, "Result")
        for filename, image_data in results.items():
            with open("generated/generated.png", "wb+") as f:
                f.write(image_data)
        pass

    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    asyncio.get_event_loop().run_until_complete(async_generate())
    response = send_from_directory("generated/", "generated.png", as_attachment=True)
    return response


if __name__ == "__main__":
    app.run(debug=True)