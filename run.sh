#!/usr/bin/with-contenv bashio

PAC_HOST=$(bashio::config 'pac_host')
PAC_PORT=$(bashio::config 'pac_port')
PROXY_PORT=$(bashio::config 'proxy_port')

bashio::log.info "Démarrage du proxy Arkteos"
bashio::log.info "PAC : ${PAC_HOST}:${PAC_PORT}"
bashio::log.info "Proxy en écoute sur port : ${PROXY_PORT}"

exec python3 /arkteos_proxy.py "${PAC_HOST}" "${PAC_PORT}" "${PROXY_PORT}"
