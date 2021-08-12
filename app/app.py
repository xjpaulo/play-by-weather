#!/usr/bin/env python3
# -*- coding: utf-8 -*

import requests
import base64
import random
import datetime
import json
import config_propriedades
from cachetools import cached, TTLCache
from circuitbreaker import circuit
from pymongo import MongoClient
from flask import Flask, abort, make_response, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask('ingaia-challenge')
cache = TTLCache(maxsize=config_propriedades.cache_max_size, ttl=config_propriedades.cache_ttl)
limiter = Limiter(app, key_func=get_remote_address)

@cached(cache)
def retorna_genero(temperatura):
	if (temperatura > 25):
		genero = 'pop'
	elif (temperatura >= 10 and temperatura <= 25):
		genero = 'rock'
	else:
		genero = 'classical'
	return genero

@circuit(failure_threshold=5, expected_exception=KeyError)
@cached(cache)
def openweather_temperatura(cidade):
	query = {'q': cidade, 'units': 'metric', 'appid': config_propriedades.openweather}
	try:
		response = requests.get('http://api.openweathermap.org/data/2.5/weather', params=query)
		json_response = response.json()
		temperatura=json_response['main']['temp']
	except requests.exceptions.RequestException as e:
		retornar_erro(0, str(e))
	except KeyError:		
		retornar_erro('404', 'Cidade não encontrada!')
	return temperatura

@circuit(failure_threshold=5)
def spotify_autenticar():
	url = 'https://accounts.spotify.com/api/token'
	spotify_client_id = config_propriedades.spotify_client_id
	spotify_client_secret = config_propriedades.spotify_secret_id
	spotify_client = spotify_client_id + ':' + spotify_client_secret
	data = {
		'grant_type' : 'client_credentials'
	}
	
	try:
		response_spotify = requests.post(url, auth=(spotify_client_id, spotify_client_secret), data=data)
	except:
		retornar_erro(0, 'Ocorreu um erro ao autenticar no Spotify.')
	json_response_spotify = response_spotify.json()
	access_token = json_response_spotify.get('access_token')
	return access_token

@circuit(failure_threshold=5)
@cached(cache)
def spotify_playlists(access_token, genero):
	url = 'https://api.spotify.com/v1/browse/categories/' + genero + '/playlists'
	random_offset = random.randint(0,19)
	payload = {
		'country': 'BR',
		'limit': '1',
		'offset': random_offset
	}
	headers = {
        	'Authorization': "Bearer " + access_token
	}
	
	try:
		response_spotify = requests.get(url, params=payload, headers=headers)
	except:
		retornar_erro(0, 'Ocorreu um erro ao retornar as playlists do Spotify.')
	json_response_spotify = response_spotify.json()
	playlist_url = json_response_spotify['playlists']['items'][0]['tracks']['href']
	return playlist_url

@circuit(failure_threshold=5)
@cached(cache)
def spotify_musica(access_token, playlist_url):
	headers = {
		'Authorization': "Bearer " + access_token
	}

	try:
		response_spotify = requests.get(playlist_url, headers=headers)
		json_response_spotify = response_spotify.json()
		musicas_json = json_response_spotify["items"]
	except:
		retornar_erro(0, 'Ocorreu um erro ao coletar as músicas do Spotify.')
	musicas = { 'musicas': [] }
	x = 0
	for musica in musicas_json:
		artistas_json = json_response_spotify['items'][x]['track']['artists']
		musica_artistas = []
		for artista in artistas_json:
			musica_artistas.append(artista['name'])
		musica_nome = json_response_spotify['items'][x]['track']['name']
		musica_artistas_final = ', '.join(musica_artistas)
		musicas['musicas'].append({
				'musicaArtista': musica_artistas_final,
				'musicaNome': musica_nome
		})
		x += 1
	return musicas

def banco_config():
	mongo_client = MongoClient(config_propriedades.mongo_client_host, config_propriedades.mongo_client_port)
	banco = mongo_client[config_propriedades.mongo_db]
	return mongo_client, banco
	
def gravar_historico(cidade, temperatura, genero, playlist_url):
	(mongo_client, banco) = banco_config()
	datahora = str(datetime.datetime.now())
	dados = { 'cidade': cidade, 'temperatura': temperatura, 'genero': genero, 'playlist_url': playlist_url, 'datahora': datahora }
	colecao = banco['historico']
	try:
		colecao.insert_one(dados)
	except:
		retornar_erro(0, 'Ocorreu um erro com o banco de dados.')

@app.route('/api/v1/playlists/historico', methods=['GET'])
@limiter.limit("100/hour;5/minute")
def retornar_historico():
	(mongo_client, banco) = banco_config()
	colecao = banco['historico']
	musicas = []
	try:
		for musica in colecao.find({}, {'_id': False}):
			musicas.append(musica)
	except:
		retornar_erro(0, 'Ocorreu um erro com o banco de dados.')
	if not musicas:
		historico_json = { 'historico': 'Histórico vazio!' }
	else:
		historico_json = { 'historico': musicas }
	return historico_json

def retornar_erro(status, mensagem):
	if status != 0:
		abort(make_response(jsonify(status=status, erro_msg=mensagem), status))
	else:
		abort(make_response(jsonify(erro_msg=mensagem), 400))

@app.errorhandler(429)
def ratelimit_handler(e):
	e.description = e.description.replace('minute', 'minuto').replace('hour', 'hora').replace('per', 'por')
	return make_response(jsonify(error="Rate limit excedido! " + e.description), 429)

def validar(cidade):
	if not all(caracter.isalpha() or caracter.isspace() for caracter in cidade):
		retornar_erro('400', 'Cidade com caracteres inválidos! Utilize apenas letras e espaços.')

@app.route('/api/v1/playlists/cidades/<string:cidade>', methods=['GET'])
@limiter.limit("100/hour;5/minute")
def main(cidade):
	validar(cidade)
	temperatura = openweather_temperatura(cidade)
	access_token = spotify_autenticar()
	(playlist_url) = spotify_playlists(access_token, retorna_genero(temperatura))
	musicas = spotify_musica(access_token, playlist_url)

	output = {
		'resultado': {
			'cabecalho': {
				'cidade': cidade,
				'temperaturaCelcius': temperatura,
				'playlistGenero': retorna_genero(temperatura),
				},
			'musicas': None
			}
	}
	gravar_historico(cidade, temperatura, retorna_genero(temperatura), playlist_url)
	output['resultado'].update(musicas)	
	return output

@app.route('/')
def mensagem_padrao():
	return jsonify({"mensagem": "Utilize um dos endpoints para o funcionamento correto da aplicação."})

if __name__ == '__main__':
	app.run(host='0.0.0.0', port='8080')
