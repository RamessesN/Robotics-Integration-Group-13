import os
import importlib.util

SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CV_PATH = os.path.join(SRC_PATH, "cv", "env_config.py")

spec = importlib.util.spec_from_file_location("env_config", CV_PATH)
cfg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cfg)