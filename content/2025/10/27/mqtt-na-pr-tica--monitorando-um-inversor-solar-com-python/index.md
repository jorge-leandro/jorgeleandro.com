---
title: "MQTT na Prática: Monitorando um Inversor Solar com Python"
date: 2025-10-27T07:29:14-0300
tags: ["MQTT", "IoT", "Python", "Pub/Sub", "Protocolos", "Tutorial"]
---

O protocolo MQTT (Message Queuing Telemetry Transport), surgiu nos anos 90 com o objetivo de monitorar oleodutos via satélite. Essa demanda tinha como requisito **baixo consumo** de **banda** e de **bateria**.

Hoje existe um uso muito popular do protocolo MQTT em redes IoT (Internet das Coisas).
Mas você sabe como este protocolo funciona? Para entender o fluxo precisamos de 3 componentes principais:
![Protocolo MQTT](https://bucket.jorgeleandro.com/blog/mqtt.svg)

### O Broker

A base do MQTT é o uso de uma central de mensagens conhecida como Broker, que permite a aplicação do princípio de **Publicar/Inscrever-se** (Pub/Sub). Considere que o Broker é um centro de distribuição, onde cada dispositivo da rede vai se comunicar com ele e não diretamente entre si, como acontece no modelo de requisição/resposta (request/response).

Exemplos populares de Brokers são o Mosquitto e o HiveMQ.

### O Tópico

É o "endereço" ou "assunto" da mensagem. A escolha do assunto é livre, mas um exemplo de sua aplicação seria `inversores/id_001/telemetria` para dados de potência elétrica de um inversor de frequeência de um sistema solar.

### O Cliente

Um cliente é qualquer dispositivo que se conecta ao broker, ele pode assumir duas funções:

1. Publicador (Publisher): Envia dados (publica mensagens) no broker em um determinado tópico: nosso inversor [IoT Sensor], no exemplo anterior.

2. Inscrito (Subscriber): Recebe mensagens do broker de um tópico específico.

### Exemplo prático: monitorando um inversor solar

Para que você também possa testar, vou colocar um exemplo simulado, já que não posso deixar um equipamento disponível pra testes por aqui 😬.

> 💾 O código completo está disponível no GitHub: [Exemplo MQTT](https://github.com/jorge-leandro/mqtt-example).

Como já falamos de inversor de frequência, vamos supor que nosso inversor virtual envia os dados no seguinte formato:

```json
{
  "power_w": 3500.5,
  "energy_today_kwh": 10.2,
  "temperature_c": 45.8,
  "status": "Gerando"
}
```

Nosso cenário:

- Publicador: Um script (publisher.py) simulando o inversor.
- Inscrito: Outro script (subscriber.py) simulando um dashboard de monitoramento.
- Broker: Usaremos um broker público de testes: broker.hivemq.com.
- Tópico: inversores/id_001/telemetria

Código do Publicador (publisher.py)

```python
import paho.mqtt.client as mqtt
import json
import time
import random
[...]


# 2. Monta o payload (a mensagem)
payload_dict = {
    "power_w": round(power, 2),
    "energy_today_kwh": round(energy, 2),
    "temperature_c": round(temp, 1),
    "status": "Gerando",
}

# 3. Converte o dicionário para uma string JSON
json_payload = json.dumps(payload_dict)

# 4. Publica a mensagem no tópico
result = client.publish(TOPIC, json_payload)


[...]
```

Código do Inscrito (subscriber.py)

```python
import paho.mqtt.client as mqtt
import json

# --- Configurações do MQTT ---
BROKER_ADDRESS = "broker.hivemq.com"
BROKER_PORT = 1883
TOPIC = "inversores/id_001/telemetria"

def on_connect(client, userdata, flags, rc):
    """Callback chamado quando a conexão é estabelecida."""
    [...]

    client.subscribe(TOPIC)


[...]


payload_str = msg.payload.decode('utf-8')

# Converte a string JSON para um dicionário Python
dados = json.loads(payload_str)

# Exibe os dados de forma legível
print(f"  -> Potência: {dados['power_w']} W")
print(f"  -> Energia Hoje: {dados['energy_today_kwh']} kWh")
print(f"  -> Temperatura: {dados['temperature_c']} °C")
print(f"  -> Status: {dados['status']}")


[...]
```

Como Testar
Abra dois terminais.

No Terminal 1, execute o publicador:

```python
python publisher.py
```

No Terminal 2, execute o inscrito:

```python
python subscriber.py
```

Ele ficará aguardando mensagens.

Ele começará a enviar dados.

Observe o Terminal 2. Você verá os dados do inversor chegando em tempo real.


![Execução exemplo MQTT](https://bucket.jorgeleandro.com/blog/mqtt-exec.gif)

### Conclusão

É simples assim. O publicador (inversor) não tem ideia de quem está ouvindo, e o inscrito (dashboard) não precisa saber onde o inversor está. Ambos confiam no Broker para gerenciar a comunicação.

Esse desacoplamento é o que torna o MQTT muito eficaz para sistemas de IoT, desde simples sensores em casa até frotas de veículos conectados e até mesmo aplicacões industriais.

Quais outros casos de uso para o protocolo MQTT você imagina?
