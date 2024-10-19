# Tutorial início api Flask

### 1 Iniciar Virtual Environment

```bash
// Windows
python -m venv venv
venv\Scripts\activate

Linux & macOs
python -m venv venv
source venv/bin/activate
```


### 2 Instalar pacotes

```bash
pip install -r requirements.txt
pip install mysqlclient
pip install PyPDF2
```


### 3 Rodar servidor web

```bash
// Para rodar na porta padrão
flask run --host=0.0.0.0

// Para escolher a porta http
flask run --host=0.0.0.0 --port 5001
```


# Endpoint de usuários

### Listar todos usuários

**Definição/Request**

`GET /v1/users`

**Response**

- `200 OK` ao ter sucesso

```json
{
    "data": [ ],
    "message": "successfully fetched"
}
```
### Listar usuários filtrando por nome

**Definição/Request**

`GET /v1/users?name=a`

**Response**

- `200 OK` ao ter sucesso

```json
{
    "data": [ ],
    "message": "successfully fetched"
}
```


## Retornar um usuário especifico

`GET /v1/users/<id>`

**Response**

- `404 Not Found` usuário não existe

```json
{
    "data": {},
    "message": "user don't exist"
}
```

- `200 OK` ao ter sucesso

```json
{
    "data": { },
    "message": "successfully fetched"
}
```


### Registrando novo usuário

**Definição/Request**

`POST /v1/users`

**Argumentos**

- `"username":string` usuário que será mostrado e feito para usar a api
- `"password":string` senha que será encriptada antes de ir para o banco
- `"name":string` nome do usuário
- `"email":string` email que será usado para comunicação

**Response**

- `201 Created` ao ter sucesso

```json
{
    "data": { },
    "message": "successfully registered"
}
```

- `200 Created` ao ter erro com usuário ou email existente

```json
{
    "data": {
        },
    "message": "user already exists"
}
```

- `500 Internal error` ao ter erro com o servidor ou sistema

```json
{
    "data": {},
    "message": "unable to create"
}
```


### Atualizando usuário

**Definição/Request**

`PUT /v1/users/<id>`

**Argumentos**

- `"username":string` usuário que será mostrado e feito para usar a api(eventualmente)
- `"password":string` senha que será encriptada antes de ir para o banco(eventualmente)
- `"name":string` nome do usuário
- `"email":string` email que será usado para comunicação(caso necessário)

**Response**

- `201 Created` ao ter sucesso

```json
{
    "data": { },
    "message": "successfully updated"
}
```

- `404 Not Found` usuário não existe

```json
{
    "data": {},
    "message": "user don't exist"
}
```

- `500 Internal error` ao ter erro com servidor ou sistema

```json
{
    "data": {},
    "message": "unable to update"
}
```

## Deletar usuário

**Definição**

`DELETE /v1/users/<id>`

**Response**

- `200 No Content` ao ter sucesso

```json
{
    "data": { },
    "message": "successfully deleted"
}
```

- `404 Not Found` usuário não existente

```json
{
    "data": {},
    "message": "user don't exist"
}
```

- `500 Internal error` erro com servidor ou sistema

```json
{
    "data": {},
    "message": "unable to delete"
}
```

## Autenticação do token com servidor JWT

`POST /v1/auth`

**No header do seu JavaScript será necessário passar os dados do usuário.**

***Authorization: 'Basic ' + btoa(username + ':' + password)***

**Response**

- `401 Not Found` caso não exista
- `200 OK` ao ter sucesso

```json
{
 "token": "QIHWEUkoqwe8291j1ioe2j12jjw9218.JASJA.WQIUH3uijs0a",
 "exp": "Mon, 20 May 2019 10:45:50 GMT"
}
```


https://github.com/openai/openai-quickstart-python/tree/master