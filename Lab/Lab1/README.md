## Workflow
### 1. Download dataset from [roboflow](universe.roboflow.com) website

<details open>
<summary> ⚠️ Warning </summary>

- The format of dataset is `yolov8`
- Each category needs at least **300** photos 
- Edit the num of categories in `data.yaml` and ensure the relation between each `img` and its `label`

</details>

### 2. Train model by [model_train.py](./src/model_train.py)

<details open>
<summary> ⚠️ Warning </summary>

- The part below is unique to ``mps`` based on `Apple Silicon` mac
<pre>
<code>max_det = 300,
conf = 0.5,
iou = 0.6,
plots = True,
save_period = 10</code>
</pre>

- `batch` is based on `VRAM`
- `workers` is based on the combination of `Core Num` ad `RAM` 

</details>

### 3. Run trained model on `jetson orin nx` by [video_process](./src/video_process.py)

<details open>
<summary> ⚠️ Warning </summary>

- [video_process.py](./src/video_process.py) is based on single `PyTorch` with only `gpu` acceleration
- [video_process_resize.py](./src/video_process_resize.py) is based on `frame-by-frame` compression strategy
- [engine_run.py](./src/engine_run.py) is based on `TensorRT` acceleration tech with better `gpu` scheduling than normal `PyTorch`

</details>

---

### Transfer `xxx.pt` into `xxx.onnx` and `xxx.engine`
> **Command Line Operation**
1. `Yolov8` -> `onnx`
<pre>
<code>yolo export \
model=weight/xxx.pt \
format=onnx \
imgsz=640 \
opset=12 \          # onnx operator set version
simplify=True \     # remove redundant operators
dynamic=False \     # dynamic input size
nms=True</code>     # avoid write NMS
</pre>
2. `onnx` -> `engine`
<pre>
<code>/usr/src/tensorrt/bin/trtexec \
--onnx=xxx.onnx \
--saveEngine=combined_v1.engine \
--fp16</code>       # [Optional] half-precision
</pre>