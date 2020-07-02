# ingaia-challenge

Um micro-serviço web que retorna playlists específicas de música baseadas na temperatura da cidade fornecida. Esta API foi desenvolvida em Python, utilizando Flask, uWSGI, MongoDB e Docker.

## Pré-requisitos

 - [docker](https://docs.docker.com/)
 - [docker-compose](https://docs.docker.com/compose/)

## Infraestrutura

 - Gateway - Foi utilizado o uWSGI para permitir e controlar processos simultâneos;
 - API - Aplicação constrúida em Python junto com o framework Flask para criação de endpoints. Utiliza cache em algumas funções e possui circuit breaker.
 - Banco de dados - Grava o histórico de chamadas da API dentro de um banco MongoDB;
 - Docker - Utiliza dois containers: um para a API e para o serviço web, e outro para o banco de dados.

## Configuração
Para iniciar as aplicações, execute o docker-compose na pasta raiz:
```
$ docker-compose up --detach --build
```
Os logs podem ser acompanhados pelo comando:  
```
$ docker-compose logs --folow
```
## Funcionamento

Após a instalação, a API ficará disponível através do endereço, onde a cidade para requisição deverá substituir \<cidade\>:

``http://localhost:8080/musica/sugerir/<cidade>``

**Endpoints:**

 - Retornar sugestões de músicas pelo nome da cidade:
```
GET localhost:8080/musica/sugerir/<cidade>
```
 - Retornar o histórico de chamadas:
``` 
GET localhost:8080/musica/historico
```
