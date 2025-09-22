<div align="center">
    <h1> Robotics Integration Group Project </h1>
    <h2> Final Project </h2>
</div>

<img src="./doc/img/ouc.png" alt="ouc_alt" title="ouc_img">

<div align="center">
    <h3> Team ID: #13 </h3>
    <h4>
        Team member:
        <a href="https://github.com/RamessesN">Yuwei ZHAO</a>,
        <a href="https://github.com/aiCane">Yilin ZHANG</a>,
        <a href="https://github.com/Rossiga22">Shijia LUO</a>,
        <a href="https://github.com/SusanSun1001">Yingrui SUN</a>
    </h4>
</div>

---

## I. Project Abstract
This project is the final task of `Course @Robotics Integration Group Project` during the 2025 summer semester. 
We group achieves the goal of robot (robomaster) automatically detect, grab and place target (cola can).

> P.S. See ...

---

## II. Results Show
<p align="center">
    <img src="./doc/video/Screenshot.gif" width=600 alt="Screenshot">
</p>

---

## III. Struct of the Project
### 1. Mainbody Struct
<pre>
<code>Final_Lab/
├── src/
│   ├── cv/
│   │   └── ...
│   └── robot/
│       └── ...
├── LICENSE.txt
└── README.md</code>
</pre>

### 2. Submodule Struct
<details open>
<summary> Model Training Part </summary>
<pre>
<code>cv/
├── dataset/
│   └── coca-cola/
│       ├──  test/
│       ├──  train/
│       ├──  valid/
│       └── data.yaml
│
├── mlmodel/          # machine learning model
│   ├── engine/       # engine-format model
│   ├── onnx/         # onnx-format model
│   └── pt/           # pt-format model
│
├── runs/             # results of training the model
├── weight/           # pretrained model
├── env_config.py     # environment import
└── model_train.py    # model training</code>
</pre>
</details>

<details open>
<summary> Robot Control Part </summary>
<pre>
<code>robot/
├── movement/
│   ├── arm_ctrl.py      # arm control
│   ├── chassis_ctrl.py  # chassis control
│   └── gripper_ctrl.py  # gripper contrl
│
├── vision/
│   ├── marker_config.py # marker subscribe
│   └── video_capture.py # video stream and target annotation
│
├── other/
│   └── distance_sub.py  # distance subscribe
│
├── main.py              # running file
└── workflow.py          # finite-state machine</code>
</pre>
</details>

---

## IV. Workflow
### 1. Manually Shot the Dataset and Annotate
See Resources on [Cola_Dataset](https://app.roboflow.com/objdetect-tgixc/cola-yibcm/4) web

### 2. Train model by [model_train.py](./src/cv/model_train.py)
- The part below is unique to ``mps`` based on `Apple Silicon` mac
<pre>
<code>max_det = 300,
conf = 0.5,
iou = 0.6,
plots = True,
save_period = 10</code>
</pre>

### 3. Transfer the format of the model 
> `xxx.pt` -> `xxx.onnx` -> `xxx.engine`
- `pt` -> `onnx`
<pre>
<code>yolo export \
model=weight/xxx.pt \
format=onnx \
imgsz=640 \
opset=12 \          # onnx operator set version
simplify=True \     # remove redundant operators
dynamic=False \     # dynamic input size
nms=True            # avoid write NMS</code>     
</pre>

- `onnx` -> `engine` (It needs `cuda` device)
<pre>
<code>/usr/src/tensorrt/bin/trtexec \
--onnx=xxx.onnx \
--saveEngine=combined_v1.engine \
--fp16 </code>
</pre>

### 4. Build each Module and Organize the Workflow
- robot vision configuration
  1. [marker_config.py](./src/robot/vision/marker_config.py): information collection with the target of specified markers.
  2. [video_capture.py](./src/robot/vision/video_capture.py): annotate markers and objects on each frame. 
- robot action control
  1. [arm_ctrl.py](./src/robot/movement/arm_ctrl.py): automatic `alignment` of the arm with the target based on `PID`; `lift` or `lower`.
  2. [chassis_ctrl.py](./src/robot/movement/chassis_ctrl.py): automatic `center` and `close` of the chassis with the target based on `PID`; 
  automatically search the specified marker. 
  3. [gripper_ctrl.py](./src/robot/movement/gripper_ctrl.py): `close` and `open` of the gripper based on `status`.
- workflow
  1. [workflow.py](./src/robot/workflow.py): `finite-state machine` to manage the lifespan of each module.

### 5. Transplant to compatible with `Jetson` Device

---

## V. Innovation and Disadvantages
### 1. Innovation 
- Because the `Robomaster-SDK` isn't compatible with the later versions of python. 
Rather than yield to official sdk, we group choose to rewrite the sdk. For instance, we replace the `audioop` with a new method. 
See Resources on [Robomaster-SDK-Ultra](https://github.com/RamessesN/Robomaster-SDK-Ultra) web.
- There is no fixed path and fixed manipulator height. All our robot done is based on `Real-time Calculus`.
Meantime, because `dji` locked the binding of the arm control to `wait_for_completed()`, 
we modified the corresponding part of the source library to adapt to the `PID` dynamic adjustment of the manipulator height. 
See Resources on [sdk-action](https://github.com/RamessesN/Robomaster-SDK-Ultra/commit/d4d090f2d54ad706505507c18617ac395abbb8e1) web.
- Different from the highly coupled code that is difficult to develop again, we use the `finite-state machine` scheme to package each module separately, 
and to realize the project structure that can easily modify the process.
- We adopted the `multi-thread` parallel scheme, and the process unification of each thread is controlled based on `EVENT` and `finite-state machine`.

### 2. Disadvantages
- Because we group adopted a `Real-time Calculus` method thus the requirements for the robot to process information are high.
Therefore, we added some `time.sleep()` to increase the robustness of the robot in processing information, which causes robot to "look like" it has a high latency.
- Even though `multi-thread` of python is constrained by `GIL` from `CPython`, it still rarely causes `High-Concurrency`.

#### ⚠️ License: This project isn't open-source. See Details [LICENSE](./LICENSE.txt).

---

<img src="./doc/img/ouc2.png" alt="ouc2_alt" title="ouc2_img">