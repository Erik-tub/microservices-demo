FROM python:3.12.12-alpine@sha256:d82291d418d5c47f267708393e40599ae836f2260b0519dd38670e9d281657f5

RUN apk add --no-cache gcc musl-dev linux-headers g++

WORKDIR /popupservice

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY popup_main.py popup_pb2.py popup_pb2_grpc.py ./

ENV PORT="8080"
EXPOSE 8080

CMD ["python", "popup_main.py"]
