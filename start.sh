#!/bin/sh

usage () {
    echo '[start] : Usage'
    echo '  - $1 -> launching mode (dev|prod)'
    exit 1
}

launch_prod() {
    echo "Launching the server..."
    echo "selected production mod..."

    uv run fastapi dev server.py
}

launch_dev() {
    echo "Launching the server..."
    echo "selected developpement mod..."

    uv dev fastapi dev server.py
}

main() {
    echo $1
    if [ "$1" = "dev" ]; then
        launch_dev
    else if [ "$1" = "prod" ]; then
        launch_prod
    else 
        usage
    fi
    fi
}

if [ $# -lt 1 ]; then
    usage
else if [ $# -gt 1 ]; then
    usage
fi
fi

main $1