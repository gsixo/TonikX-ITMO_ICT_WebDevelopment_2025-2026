POST http://127.0.0.1:8000/api/auth/users/

{
  "username":"ivan",
  "email":"ivan@example.com",
  "password":"adminchmo123",
  "re_password":"adminchmo123"
}

response

{
    "email": "ivan@example.com",
    "username": "ivan",
    "id": 2
}

POST http://127.0.0.1:8000/api/auth/token/login/

{
  "username":"ivan",
  "password":"adminchmo123"
}

response

{
    "auth_token": "9fd2bd9ce864cb167aeddd3045b3dd34b4876003"
}

GET http://127.0.0.1:8000/api/items/

Authorization: Token: 9fd2bd9ce864cb167aeddd3045b3dd34b4876003

response 

{
    "count": 0,
    "next": null,
    "previous": null,
    "results": []
}

