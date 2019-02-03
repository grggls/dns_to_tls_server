# Makefile

#___includes___

#___vars___
BREW_DEPS=docker git
NAME=dnstlsproxy
TAG=dns2dnstlsproxy

#___config___
.DEFAULT_GOAL := up

#___targets___

unprepare:
	brew uninstall --force $(BREW_DEPS)

prepare:
	brew update
	brew install $(BREW_DEPS)

reprepare: unprepare prepare

rm:
	docker stop $(NAME) || true && docker rm $(NAME) || true 2> /dev/null

build:
	docker build --tag $(TAG) .

build.curl:
	docker build --build-arg STUB=curl --tag $(TAG) .

build.kdig:
	docker build --build-arg STUB=kdig --tag $(TAG) .

script:
	python3 dnstotls_server.py --port 8053 --connections 3

run: build rm
	docker run --name dnstlsproxy -p 8053:8053/tcp $(TAG)

run.curl: build.curl rm
	docker run --name dnstlsproxy -p 8053:8053/tcp $(TAG)

run.kdig: build.kdig rm
	docker run --name dnstlsproxy -p 8053:8053/tcp $(TAG)

interactive: build rm
	docker run -it $(TAG):latest /bin/sh

up: run
