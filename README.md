# System automatycznej korekty tekstu - Transfix

## Instalacja serwera 

Uruchomienie skryptu install.sh
```chmod u+x install.sh && ./install.sh
```

Utworzenie w katalogu ./backend pliku konfiguracyjnego .env

```
SECRET_KEY=secret_key
DEBUG=1
ALLOWED_HOSTS=localhost 127.0.0.1
TRANSLATION_WEBSOCKET=ws://150.254.78.132:443/translate
SCRIPT_PATH=/home/zary/Desktop/grammatical-error-correction-system
```

Uruchomienie serwera websocket na środowisku karty graficznej na porcie 443
```sudo ./tools/marian/build/marian-server --port 443 -m model/ens/model.npz -v model/ens/vocab.ende.yml model/ens/vocab.ende.yml```