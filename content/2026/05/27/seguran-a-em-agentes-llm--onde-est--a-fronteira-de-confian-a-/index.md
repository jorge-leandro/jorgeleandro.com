---
title: "Segurança em agentes LLM: onde está a fronteira de confiança?"
date: 2026-05-27T13:26:31-0300
draft: false
description: "Descrição do post aqui"
tags: ["llm", "segurança", "ia", "mcp", "integrações"]
author: "Jorge Leandro"
---

Quando você integra um LLM a ferramentas e dados externos, a preocupação mais comum costuma ser disponibilidade e custo. Mas você costuma considerar os riscos de segurança? 

Existem três propriedades de integrações com LLMs que tornam segurança diferente de aplicações tradicionais:

o modelo não é uma fronteira de confiança;
qualquer contexto pode virar instrução;
autonomia sem validação determinística amplia drasticamente o impacto de falhas.

Esse texto tenta mostrar onde essas superfícies de ataque aparecem — muitas vezes de formas pouco óbvias durante o projeto do sistema.

### Como a maioria das integrações é construída

O fluxo básico é simples: você tem um modelo, dá contexto pra ele, conecta ferramentas via MCP ou outra camada de integração, e ele opera. O modelo recebe uma mensagem, acessa dados, chama funções, devolve uma resposta.

O problema começa quando você percebe um detalhe: **o modelo não tem como distinguir de forma 100% assertiva uma instrução que veio do sistema de uma que veio de fora**. Ele processa texto. Não existe, para ele, uma hierarquia de confiança entre o que você definiu como prompt de sistema e o que chegou como entrada do usuário — ou como resposta de uma ferramenta. 

Ao trabalhar com LLMs constantemente, você aprende o quanto condições de contorno importam.

### Prompt injection — o que é e por que é diferente de outros ataques

Prompt injection não é uma exploração de memória ou de protocolo de rede. É, fundamentalmente, convencer o modelo de que o contexto mudou: que as instruções anteriores foram revogadas, que existe um modo especial de operação, que aquela mensagem faz parte de uma continuação legítima do sistema.

O caso mais conhecido é a direct prompt injection, quando o próprio usuário envia instruções maliciosas como:

> ignore as instruções anteriores e faça X

Isso é simples demais para passar despercebido — e justamente por isso os ataques mais interessantes raramente aparecem dessa forma.


O mesmo efeito pode ser alcançado com paráfrase, com outro idioma, dentro de um contexto narrativo ("suponha que você é um sistema sem restrições"), com codificação em base64, com sequências especiais de tokens que o modelo interpreta como delimitadores de instrução. A lista de variantes é longa porque a criatividade necessária para construí-las é baixa — qualquer pessoa com acesso ao sistema pode tentar.

Mas o problema mais perigoso costuma ser a indirect prompt injection: a instrução maliciosa não vem do usuário diretamente. Ela pode aparecer num documento que o agente leu, num e-mail processado automaticamente, numa resposta de API externa ou em qualquer outro dado incorporado ao contexto.

Conforme você adiciona mais autonomia ao agente — mais ferramentas, mais fontes de dados — a superfície de ataque tende a crescer junto.

Imagine um prompt injection que consiga convencer o modelo de que a condição de sucesso dele, para atender o usuário corretamente, depende de executar uma ação maliciosa.

### PII e credenciais vazando

Quando o agente tem acesso a dados reais — banco de dados, arquivos, histórico do usuário, no geral PII (Personal Identifiable Information) — esses dados tendem a acabar no payload que vai para o provider externo. Não como resultado de um bug específico, mas porque o fluxo foi desenhado assim: busca contexto relevante, envia para o modelo, recebe resposta.

Se ninguém inspeciona o que sai, CPF, número de cartão, chaves de API e outros dados sensíveis cruzam essa fronteira com regularidade. O modelo não faz esse julgamento por você — ele usa o que está disponível no contexto.

O mesmo vale para credenciais que aparecem em código, configurações ou logs que o agente acessa. A integração LLM vira um canal de exfiltração não porque foi atacada, mas porque ninguém definiu o que pode e o que não pode sair.



### Por que filtros de texto simples não resolvem

A primeira resposta para prompt injection costuma ser bloquear padrões conhecidos: "ignore suas instruções", variantes de jailbreak em português e inglês, frases associadas a DAN e similares. Funciona para os casos mais óbvios.

O problema é que regex detecta forma, não intenção. A mesma instrução, reescrita com paráfrase diferente, outro idioma, codificação ou contexto narrativo, passa facilmente pela maioria dos filtros baseados em padrão.

Tratar isso de forma eficaz exige entender o que a mensagem está tentando fazer — não só como ela está escrita. Isso envolve análise semântica, que é computacionalmente mais cara e mais difícil de manter, mas é o que efetivamente distingue tentativas de manipulação de pedidos legítimos com linguagem semelhante.

### Onde o ponto de inspeção precisa estar

A tendência natural é proteger a borda — o que entra pela API pública, o que o usuário envia diretamente. Mas as chamadas entre seu backend e o provider LLM ficam dentro da rede e geralmente não passam por nenhuma inspeção.

Se um ataque acontece via tool response — um documento que o agente buscou, uma resposta de API que continha instruções injetadas — o payload malicioso viaja por dentro, sem nunca ter tocado na borda externa. A proteção de perímetro não vê esse tráfego.

O ponto de inspeção precisa existir entre sua aplicação e o provider: observando o que entra no modelo e, principalmente, o que sai da sua rede.

Não apenas o que entra pela borda externa.

### O que isso muda na hora de projetar

Não é necessário tratar cada integração como uma fortaleza desde o início. Mas algumas perguntas, se feitas cedo, mudam bastante o que precisa ser construído depois:

- O que entra no contexto do agente pode ter sido produzido por alguém fora do sistema?
- O payload enviado ao provider externo contém dados sensíveis?
- Tool responses recebem o mesmo nível de desconfiança que entradas de usuário?
- Se o modelo for convencido a executar algo indevido, qual é o impacto máximo possível?
- O modelo possui acesso direto a ações com efeito colateral?

A maioria dos problemas de segurança em integrações LLM não vem de ataques sofisticados. Vem de sistemas projetados sem essas perguntas — onde a fronteira entre confiável e não confiável nunca foi definida, e onde o modelo opera com mais autoridade do que deveria ter.

### Integrar é necessário

Em muitos sistemas, o modelo inevitavelmente vai acabar no caminho crítico. A questão deixa de ser “usar ou não usar” e passa a ser “quanto de autoridade o modelo recebe”.

Um exercício útil é imaginar como um banco poderia construir uma integração com APIs de movimentação financeira. Não há como saber os detalhes internos de cada instituição, mas é possível raciocinar sobre quais barreiras uma arquitetura minimamente responsável precisaria ter.

O primeiro princípio que emerge é simples: o usuário nunca define a ação diretamente, e o modelo nunca a executa.

O usuário fornece intenção — linguagem natural, ambígua, sem formato rígido. O modelo transforma isso em um payload estruturado para uma ferramenta de validação.

Essa ferramenta não recebe linguagem natural; ela recebe dados validáveis — valor, destinatário, tipo de operação — e aplica regras determinísticas do domínio: limites, autorizações, consistência, destinatários permitidos.

Só depois dessa validação o usuário vê uma confirmação explícita do que vai acontecer, e a operação aguarda aprovação.

Essa arquitetura não elimina todos os riscos discutidos antes, mas limita drasticamente o dano máximo possível. Um prompt injection que convença o modelo a gerar um payload malicioso ainda precisa atravessar uma camada de validação que o próprio modelo não controla.

É o tipo de decisão arquitetural barata no início e extremamente cara de corrigir depois.

### Os dois caminhos em código

Para tornar a diferença mais concreta, vamos comparar duas abordagens. O cenário: um banco quer permitir que o usuário envie um PIX via mensagem de texto — "manda 200 reais pro João" — numa interface tipo WhatsApp.

**Abordagem 1 — o modelo com acesso direto, restrição só no prompt**

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-7",
    system="""Você é um assistente de pagamentos PIX.
Regras obrigatórias:
- Nunca envie mais de R$1.000 por transação
- Só transfira para chaves cadastradas pelo usuário
- Sempre confirme com o usuário antes de executar""",
    tools=[{
        "name": "enviar_pix",
        "description": "Executa uma transferência PIX",
        "input_schema": {
            "type": "object",
            "properties": {
                "chave_destino": {"type": "string"},
                "valor": {"type": "number"},
                "descricao": {"type": "string"}
            },
            "required": ["chave_destino", "valor"]
        }
    }],
    messages=[{"role": "user", "content": mensagem_usuario}]
)

# Se o modelo decidir chamar enviar_pix, a aplicação executa diretamente
if response.stop_reason == "tool_use":
    tool_call = next(b for b in response.content if b.type == "tool_use")
    resultado = api_financeira.enviar_pix(**tool_call.input)
```

A vulnerabilidade aqui não está na implementação técnica — está na suposição de que o prompt é suficiente como barreira. Todas as regras estão em linguagem natural, sujeitas à mesma interpretação (e manipulação) que qualquer outra instrução no contexto. Se a `mensagem_usuario` contiver algo que convença o modelo de que as restrições não se aplicam naquele caso — ou que a confirmação já foi dada implicitamente — o código executa sem nenhuma outra barreira.

**Abordagem 2 — o modelo extrai intenção, uma ferramenta valida, o usuário confirma**

```python
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
import json
import anthropic
from pydantic import BaseModel, field_validator, ValidationError

client = anthropic.Anthropic()


class MotivoRecusa(Enum):
    LIMITE_POR_TRANSACAO        = auto()
    LIMITE_DIARIO               = auto()
    DESTINATARIO_NAO_CADASTRADO = auto()
    TOKEN_EXPIRADO              = auto()


@dataclass(frozen=True)
class IntencaoPagamento:
    valor: Decimal
    destinatario: str
    descricao: str = ""


@dataclass(frozen=True)
class TransacaoPendente:
    token: str
    valor: Decimal
    chave_destino: str
    nome_destino: str
    usuario_id: str

    @property
    def resumo(self) -> str:
        return f"PIX de R${self.valor:.2f} para {self.nome_destino}"


@dataclass(frozen=True)
class ResultadoValidacao:
    aprovada: bool
    transacao: TransacaoPendente | None = None
    motivo: MotivoRecusa | None = None


class _RespostaLLM(BaseModel):
    """Valida o JSON que o modelo retorna antes de confiar nele."""
    valor: Decimal
    destinatario: str
    descricao: str = ""

    @field_validator("valor")
    @classmethod
    def deve_ser_positivo(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("valor deve ser positivo")
        return v

    @field_validator("destinatario")
    @classmethod
    def nao_pode_ser_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("destinatario não pode ser vazio")
        return v.strip()


def extrair_intencao(mensagem: str) -> IntencaoPagamento | None:
    response = client.messages.create(
        model="claude-opus-4-7",
        system="""Extraia a intenção de pagamento PIX da mensagem.
Retorne JSON com: valor (número positivo), destinatario (string), descricao (string).
Se não for possível identificar os dados com clareza, retorne null.""",
        messages=[{"role": "user", "content": mensagem}]
    )

    raw = response.content[0].text.strip()
    if raw.lower() == "null":
        return None

    try:
        parsed = _RespostaLLM.model_validate(json.loads(raw))
    except (json.JSONDecodeError, ValidationError):
        return None

    return IntencaoPagamento(
        valor=parsed.valor,
        destinatario=parsed.destinatario,
        descricao=parsed.descricao,
    )


def validar_pix(intencao: IntencaoPagamento, usuario_id: str) -> ResultadoValidacao:
    limites = buscar_limites_usuario(usuario_id)

    if intencao.valor > limites.por_transacao:
        return ResultadoValidacao(aprovada=False, motivo=MotivoRecusa.LIMITE_POR_TRANSACAO)

    if intencao.valor > limites.diario_restante:
        return ResultadoValidacao(aprovada=False, motivo=MotivoRecusa.LIMITE_DIARIO)

    destinatario = resolver_destinatario(intencao.destinatario, usuario_id)
    if destinatario is None:
        return ResultadoValidacao(aprovada=False, motivo=MotivoRecusa.DESTINATARIO_NAO_CADASTRADO)

    transacao = TransacaoPendente(
        token=criar_token_transacao(intencao, destinatario, usuario_id),
        valor=intencao.valor,
        chave_destino=destinatario.chave_pix,
        nome_destino=destinatario.nome,
        usuario_id=usuario_id,
    )
    return ResultadoValidacao(aprovada=True, transacao=transacao)


def confirmar_pix(token: str, confirmacao: bool) -> None:
    if not confirmacao:
        invalidar_token(token)
        return

    transacao = recuperar_transacao(token)
    if transacao is None or transacao.expirado:
        raise ValueError(MotivoRecusa.TOKEN_EXPIRADO)

    api_financeira.executar_pix(transacao)


# Fluxo completo
intencao = extrair_intencao(mensagem_usuario)

if intencao is None:
    enviar_para_usuario("Não consegui entender o pagamento. Pode reformular?")
else:
    resultado = validar_pix(intencao, usuario_id)

    if not resultado.aprovada:
        enviar_para_usuario(f"Pagamento não permitido: {resultado.motivo.name}")
    else:
        enviar_para_usuario(resultado.transacao.resumo + "\n\nConfirma? (sim/não)")
        # confirmar_pix(token, confirmacao) é chamado quando o usuário responder
```

A diferença estrutural entre as duas abordagens não está nos imports nem nas chamadas de API — está em onde fica a autoridade. Na primeira, o modelo tem acesso direto à ferramenta que executa; qualquer injeção que mude sua interpretação das regras do prompt afeta diretamente o que é executado. Na segunda, o modelo só pode propor uma intenção estruturada. A validação — limites, contatos cadastrados, consistência dos dados — acontece numa camada que não é influenciada pelo contexto que o modelo recebeu. E a execução depende de uma ação explícita do usuário sobre um resumo que foi gerado fora do modelo, não por ele.

Isso não torna o sistema imune a todos os problemas discutidos antes. Mas localiza claramente o que cada parte do sistema pode e não pode fazer — e essa separação é o que permite raciocinar sobre os riscos de forma concreta.

**O proxy em código**
Outro problema discutido antes é posicionamento.

Você precisa de um ponto que observe todo o tráfego entre sua aplicação e o provider — inclusive conteúdo vindo de tool responses, que normalmente nunca passa pela borda externa.

O padrão de proxy resolve isso: o cliente do provider é encapsulado por uma camada responsável por inspeção, sanitização e observabilidade.

O exemplo abaixo é deliberadamente simplificado. Ele serve para ilustrar posicionamento arquitetural, não detecção robusta de prompt injection.

```python
from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
import re
import anthropic


class AcaoProxy(Enum):
    PERMITIR  = auto()
    SANITIZAR = auto()
    BLOQUEAR  = auto()


@dataclass(frozen=True)
class ResultadoInspecao:
    acao: AcaoProxy
    payload: str
    motivo: str = ""


_PADROES_PII = [
    (r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",               "CPF"),
    (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  "cartão"),
    (r"(?i)(sk-|api[-_]?key|bearer\s+)[a-z0-9]{20,}", "credencial"),
]

_PADROES_INJECTION = [
    r"(?i)ignore\s+(as\s+)?instru",
    r"(?i)<\s*/?system\s*>",
    r"(?i)you are now",
]


def inspecionar_payload(texto: str) -> ResultadoInspecao:
    """Remove PII antes que o conteúdo saia em direção ao provider."""
    resultado = texto
    for padrao, rotulo in _PADROES_PII:
        if re.search(padrao, resultado):
            resultado = re.sub(padrao, f"[{rotulo} removido]", resultado)

    if resultado != texto:
        return ResultadoInspecao(acao=AcaoProxy.SANITIZAR, payload=resultado, motivo="PII detectado")

    return ResultadoInspecao(acao=AcaoProxy.PERMITIR, payload=texto)


def inspecionar_tool_response(conteudo: str) -> ResultadoInspecao:
    for padrao in _PADROES_INJECTION:
        if re.search(padrao, conteudo):
            return ResultadoInspecao(
                acao=AcaoProxy.BLOQUEAR,
                payload="[conteúdo bloqueado pelo proxy]",
                motivo="padrão de injection em tool response",
            )
    return ResultadoInspecao(acao=AcaoProxy.PERMITIR, payload=conteudo)


class AnthropicProxy:
    """Envolve o cliente Anthropic com inspeção em cada chamada."""

    def __init__(self, on_alerta: Callable[[str], None]):
        self._client = anthropic.Anthropic()
        self._on_alerta = on_alerta

    def _inspecionar_mensagens(self, messages: list[dict]) -> list[dict]:
        resultado = []
        for msg in messages:
            conteudo = str(msg["content"])
            inspecao = (
                inspecionar_tool_response(conteudo)
                if msg["role"] == "tool"
                else inspecionar_payload(conteudo)
            )
            if inspecao.acao != AcaoProxy.PERMITIR:
                self._on_alerta(inspecao.motivo)
            resultado.append({**msg, "content": inspecao.payload})
        return resultado

    def create(self, *, system: str, messages: list[dict], **kwargs) -> anthropic.types.Message:
        inspecao_system = inspecionar_payload(system)
        if inspecao_system.acao != AcaoProxy.PERMITIR:
            self._on_alerta(inspecao_system.motivo)

        return self._client.messages.create(
            system=inspecao_system.payload,
            messages=self._inspecionar_mensagens(messages),
            **kwargs,
        )


# Substitui o cliente direto em qualquer ponto da aplicação
proxy = AnthropicProxy(on_alerta=registrar_alerta)
response = proxy.create(
    model="claude-opus-4-7",
    system=system_prompt,
    messages=messages,
)
```

Vale ser honesto sobre o que esse padrão resolve e o que não resolve. A remoção de PII antes de sair para o provider — CPF, número de cartão, credenciais que aparecem no contexto — funciona razoavelmente bem com regex porque o formato desses dados é determinístico. Detecção de injection é diferente: os padrões acima cobrem os casos mais diretos, mas ataques sofisticados passam por qualquer filtro baseado em forma, como já discutido anteriormente. Para esses casos a análise semântica é o que funciona — mais cara, mais difícil de manter, mas é o que efetivamente distingue manipulação de linguagem legítima.

O que o proxy resolve independente da qualidade da inspeção é o posicionamento: existe agora um único ponto onde todo o tráfego entre sua aplicação e o provider pode ser observado, filtrado e registrado — inclusive o que vem de tool responses e nunca chegou pela borda externa. 

Sem esse ponto central, qualquer mecanismo de inspeção futuro acaba espalhado em múltiplos lugares da aplicação, com risco constante de gaps e inconsistências.

