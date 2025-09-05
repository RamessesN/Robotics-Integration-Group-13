# Robotics-Integration-Group-13

---

## Our `jetson orin nx` system config
- JetPack 6.2.1
- Ubuntu 22.04 Jammy
- CUDA 12.6.68
- cuDNN 9.3.0.75
- VPI 3.2.4
- Vulkan 1.3.204
- Python 3.10.12
- OpenCV 4.11.0 with CUDA: YES
- PyTorch 2.8.0 (torchvision 0.23.0)
- TensorRT 10.3.0

> Suggest to use `jtop` to check system config

---

## Jetson Orin NX Configuration

> Run `sudo apt-get update` `sudo apt-get upgrade` first

<details open>
<summary> 1. Python </summary>

- Use `miniconda` to manage `python` version. 
- Run `conda create --name xxx python=3.10` to create virtual env

</details>

<details open>
<summary> 2. Ultralytics (YOLO) </summary>

- Install ultralytics dependencies: `pip install ultralytics`
- Uninstall `torch` and `torchvision` for they're `cpu` version: `pip uninstall torch torchvision` (See belows)
- Reinstall `numpy` for its too-high version: `pip install "numpy<2" --force-reinstall`

</details>

<details open>
<summary> 3. OpenCV </summary>

- Install **nano / orin**: `sudo apt-get install nano` \
    > Don't worry it's also compatible with `orin nx`
- Install **dphys-swapfile**: `sudo apt-get install dphys-swapfile`
- Enlarge the boundary of **CONF_MAXSWAP**: `sudo nano /sbin/dphys-swapfile`
- Restart the **nano / orin**: `sudo reboot`
- Check memory: `free -m`
- Run automator script [OpenCV-4-11-0.sh](./doc/guide/OpenCV-4-11-0.sh):
  - Grant permissions: `sudo chmod 755 ./OpenCV-4-11-0.sh`
  - Run: `./OpenCV-4-11-0.sh`
- Then check the installation of `opencv-cuda-version` is okay

    > Thanks to [Q-engineering](https://qengineering.eu/install-opencv-on-jetson-nano.html) I finally did it!

</details>

---

## YOLO Official Web

See [Ultralytics YOLO Docs](https://docs.ultralytics.com)

---

## Robomaster Support

See [Robomaster SDK Ultra](https://github.com/RamessesN/Robomaster-SDK-Ultra) for `python-3.10` compatibility.

---

## YOLOv8 Training on Intel Arc GPU

See [intel-extension-for-pytorch](https://github.com/intel/intel-extension-for-pytorch).

See [ultralytics issue #19821](https://github.com/ultralytics/ultralytics/issues/19821) for `Intel Arc` compatibility.
