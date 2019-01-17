#!/usr/bin/env bash

function docker-login {
    echo ${HEROKU_API_KEY} | docker login --username=${HEROKU_LOGIN} --password-stdin registry.heroku.com
}
function build-push-heroku-images {
    echo "-------=---BUILDING IMAGE ${1}----------"
    docker build -t registry.heroku.com/${HEROKU_APP_NAME}/$1 . -f $2
    echo "-----------PUSHING IMAGE ${1}-----------"
    docker push registry.heroku.com/${HEROKU_APP_NAME}/$1:latest
    echo "-----------IMAGE ${1} DONE--------------"
}

function get-build-docker-image-id {
    echo $(docker inspect registry.heroku.com/${HEROKU_APP_NAME}/$1 --format={{.Id}})
}

function get-images-info {
    echo "{
        \"updates\" : [
            {
                \"type\": \"web\",
                \"docker_image\": \"$(get-build-docker-image-id web)\"
            },{
                \"type\": \"worker\",
                \"docker_image\": \"$(get-build-docker-image-id worker)\"
            },{
                \"type\": \"beat\",
                \"docker_image\": \"$(get-build-docker-image-id beat)\"
            },{
                \"type\": \"release\",
                \"docker_image\": \"$(get-build-docker-image-id release)\"
            }
        ]
    }"
}


function send_heroku_release {
    echo "Sending Release Command"
    curl -n -X PATCH --data "$(get-images-info)" https://api.heroku.com/apps/${HEROKU_APP_NAME}/formation \
     -H "Content-Type: application/json" -H "Accept: application/vnd.heroku+json; version=3.docker-releases" -H "Authorization: Bearer ${HEROKU_API_KEY}"
}

function build-all-images {
    build-push-heroku-images web Dockerfile
    build-push-heroku-images worker Dockerfile.worker
    build-push-heroku-images beat Dockerfile.beat
    build-push-heroku-images release Dockerfile.release
}

function main {
    docker-login
    build-all-images
    send_heroku_release
}

main
