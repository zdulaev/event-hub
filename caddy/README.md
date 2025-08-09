Создай тут файл Caddyfile с содержимым:
{your.domain.tld} {
    tls internal
    basicauth /* {
        {user} {# docker run --rm caddy:2-alpine caddy hash-password --plaintext '{your_pass}'}
    }

    handle_path /logger* {
        reverse_proxy logger:8999
    }

    handle_path /pgweb* {
        reverse_proxy pgweb:8081
    }
}