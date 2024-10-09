使用方法
```shell
docker build -t pyglens .
docker run -d --name pyglens -p 10241:8000 pyglens
```
POST请求
```shell
curl --location 'http://IP:10241/glens' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'pic_url=https://raw.githubusercontent.com/kitUIN/PicImageSearch/main/demo/images/test03.jpg'
```