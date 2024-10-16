#FROM ultralytics/ultralytics:8.3.13-arm46
FROM ultralytics/ultralytics:8.3.13-cpu

COPY ./main.py /ultralytics
COPY ./cv_crop.py /ultralytics
COPY ./yolo_crop.py /ultralytics
COPY ./requirements.txt /
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /
RUN pip install -r /requirements.txt
WORKDIR /ultralytics
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]