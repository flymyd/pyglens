FROM python:3.10-alpine3.19
COPY ./main.py /
COPY ./requirements.txt /
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]