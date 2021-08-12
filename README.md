# play-by-weather

Um serviço web que retorna playlists específicas de música baseadas na temperatura da cidade fornecida. Esta API foi desenvolvida em Python, utilizando Flask, uWSGI, MongoDB e Docker.

## Introdução

A API recebe uma cidade como entrada, e retorna em JSON playlists aleatórias com base na temperatura atual da cidade fornecida.
- Caso a temperatura seja maior que 25 graus Celsius, deverá retornar playlists de músicas pop;
- Caso esteja entre 10 e 25 graus Celsius, deverá retornar playlists de músicas de rock;
- Caso esteja abaixo de 10 graus Celsius, deverá retornar playlists de música clássica.

São utilizadas a API do OpenWeather para consultar a temperatura atual, e a API do Spotify para retornar as informações sobre as músicas.

O serviço também possui um histórico de chamadas e estatísticas que é armazenado em um banco de dados.

## Pré-requisitos

 - [docker](https://docs.docker.com/)
 - [docker-compose](https://docs.docker.com/compose/)

## Infraestrutura

 - Gateway - Foi utilizado o uWSGI para permitir e controlar processos simultâneos;
 - API - Aplicação construída em Python junto com o framework Flask para criação de endpoints. Utiliza cache em algumas funções, possui rate limit e circuit breaker.
 - Banco de dados - Grava o histórico de chamadas da API dentro de um banco MongoDB;
 - Docker - Utiliza dois containers: um para a API e para o serviço web, e outro para o banco de dados.

## Configuração
Para iniciar a aplicação, execute o docker-compose na pasta raiz:
```
$ docker-compose up --detach --build
```
Os logs podem ser acompanhados pelo comando:  
```
$ docker-compose logs --follow
```
## Funcionamento

Após a instalação a API ficará disponível através do endereço abaixo, onde a cidade para requisição deverá substituir \<cidade\>:

``http://localhost:8080/musicas/<cidade>``

**Endpoints:**

 - Retornar sugestões de músicas pelo nome da cidade:
```
GET localhost:8080/api/v1/playlists/cidades/<cidade>
```
 - Retornar o histórico de chamadas:
``` 
GET localhost:8080/api/v1/playlists/historico
```

## Heroku
Foi realizado um deploy dessa aplicação na plataforma Heroku, que pode ser consultada utilizando um dos endpoints acima:

https://play-by-weather.herokuapp.com/

