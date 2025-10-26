#!/bin/bash

set -e

print_message() {
    echo "[INFO] $1"
}

print_error() {
    echo "[ERROR] $1"
}

generate_index() {
    print_message "Gerando índice..."
    python3 scripts/generate_index.py
}


new_post() {
    if [ -z "$1" ]; then
        print_error "Título do post não especificado"
        print_message "Uso: ./scripts/dev.sh new-post 'Título do Post'"
        exit 1
    fi
    
    DATE_PATH=$(date +%Y/%m/%d)
    POST_DIR="content/${DATE_PATH}/$(echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-\|-$//g')"
    
    print_message "Criando post: $POST_DIR"
    
    mkdir -p "$POST_DIR"
    
    cat > "$POST_DIR/index.md" << EOF
---
title: "$1"
date: $(date +%Y-%m-%dT%H:%M:%S%z)
draft: false
description: "Descrição do post aqui"
tags: []
---

Conteúdo do post aqui...

EOF
    
    print_message "Post criado em: $POST_DIR/index.md"
}

show_help() {
    echo "Comandos:"
    echo "  generate-index - Gera o índice de posts"
    echo "  new-post <title> - Cria um novo post"
    echo "  help           - Mostra esta ajuda"
}

main() {

    
    case "${1:-help}" in
  
        generate-index)
            generate_index
            ;;
        new-post)
            shift
            new_post "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Comando desconhecido: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
