#!/usr/bin/env bash

function docker-login{
    echo ${HEROKU_API_KEY} | docker login --username=${HEROKU_LOGIN} --password-stdin registry.heroku.com
}

function get-build-docker-image{
    docker build -t registry.heroku.com/${HEROKU_APP_NAME}/$1 . -f $2
    docker push registry.heroku.com/${HEROKU_APP_NAME}/$1:latest
    docker inspect registry.heroku.com/${HEROKU_APP_NAME}/$1 --format={{.Id}} > "${1}_DOCKER_IMAGE_ID_FILE"

    echo $(cat "${1}_DOCKER_IMAGE_ID_FILE")
}

function get-images-info{
    echo "{
        \"updates\" : [
            {
                \"type\": \"web\",
                \"docker_image\": \"$(get-build-docker-image web Dockerfile)\"
            },{
                \"type\": \"worker\",
                \"docker_image\": \"$(get-build-docker-image worker Dockerfile.worker)\"
            },{
                \"type\": \"beat\",
                \"docker_image\": \"$(get-build-docker-image beat Dockerfile.beat)\"
            },{
                \"type\": \"release\",
                \"docker_image\": \"$(get-build-docker-image release Dockerfile.release)\"
            }
        ]
    }"
}

function send_heroku_release{
    curl -n -X PATCH --data "$(get-images-info)" https://api.heroku.com/apps/${HEROKU_APP_NAME}/formation \
     -H "Content-Type: application/json" -H "Accept: application/vnd.heroku+json; version=3.docker-releases" -H "Authorization: Bearer ${HEROKU_API_KEY}"
}

function main{
    docker-login
    send_heroku_release
}

main
