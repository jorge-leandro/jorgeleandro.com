---
title: "Encurtador de URL escalável com Python"
date: 2025-11-15T20:02:14-0300
draft: false
description: "Descrição do post aqui"
tags: []
---

Esses dias eu estava assistindo o video do Renato Augusto, `Arquitetando um Encurtador de URL: O Maior Desafio dos Programadores em Entrevistas de System Design`, onde ele explica os desafios que você pode ter ao arquitetar um encuratador de URL escalável, destacando os impactos de não se pensar em um Design System adequado para o problema que você enfrenta.

No vídeo o objetivo não é desenvolver o encurtador de URL em si, mas sim pensar em como arquitetar um sistema que seja escalável, resiliente e eficiente. Mas após assistir o vídeo eu fiquei com aquela vontade de colocar a mão na massa e desenvolver o encurtador de URL de verdade.


Aí eu pensei, eu preciso fazer isso?

> Não.

Eu tenho tempo para isso?

> Não.

Vou fazer mesmo assim? **Com certeza 😬**


Obviamente eu não vou explicar os detalhes do *Design System* que o Renato fundamentou, ele já fez isso muito bem. Vai lá e assiste.

> 

{{< youtube id="m_anIoKW7Jg">}}

Mas basicamente o sistema tem como requisitos funcionais:
1. Encurtamento de URL: dado um URL longo => retornar um URL muito mais curto
2. Redirecionamento de URL: dado um URL mais curto => redirecionar para o URL original

E requisitos não funcionais:
1. O sistema deve suportar 100 milhões de URLs geradas por dia.
2. O tamanho da URL encurtada deve ser o mais curto possível.
3. Somente Números (0-9) e caracteres (az, AZ) são permitidos na URL
4. Para cada 1 operação de gravação no banco de dados, haverão 10 operações de leitura
5. O comprimento médio das URLs armazenadas é de 100 bytes
6. URLs devem ser armazenadas pelo período mínimo de 10 anos
7. O sistema deve operar em modo de alta disponibilidade (24/7)
