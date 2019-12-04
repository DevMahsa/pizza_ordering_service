# pizza_ordering_service
pizza_ordering_service(pos)
## Getting started

To start project, run:

```
docker-compose up
```

The API will then be available at http://127.0.0.1:8000.
All migrations and models are in core app. 35 Tests have been written for this project. Authentication is handled. Docker, Travis-ci, flake8. 

| description  | route |  test |
|----------|:-------------:|------:|
| api for create user as customer|    http://127.0.0.1:8000/api/user/create/   | email password name |
| token create for user  | http://127.0.0.1:8000/api/user/token/ | for test better option is using ModHeader extension for chrome |
| send token| http://127.0.0.1:8000/user/me/| now you are authenticated |
| api root for order| http://127.0.0.1:8000/api/order/| after authentication you could see the process on browser in debug mode True|
| api root for order| http://127.0.0.1:8000/api/order/| after authentication |
| api root for order detail | http://127.0.0.1:8000/api/order/detail/ | list && create |
| api root for order detail | http://127.0.0.1:8000/api/order/detail/id/| retrieve, update && delete |
| create retrieve list  order  | http://127.0.0.1:8000/api/order/order/ | filter is also here |
| delete update order | http://127.0.0.1:8000/api/order/order/id/ | retrieve, update && delete |
| retrieve update status | http://127.0.0.1:8000/api/order/order/id/status| retrieve && update |
| validate status | http://127.0.0.1:8000/api/order/order/id | you cannot update an order if status is in 3,4,5 (out for delivery, delivered, returned) |





