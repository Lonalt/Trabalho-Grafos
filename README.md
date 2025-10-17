# **📄 Análise e Documentação: Labirinto com Entrante (DFS) e Minotauro (BFS)**

Este documento descreve a arquitetura e a lógica de programação do jogo de labirinto em Python, onde o Entrante (jogador) tenta escapar enquanto é caçado pelo Minotauro.

## **1\. Visão Geral do Jogo**

O jogo simula um labirinto gerado proceduralmente onde o Entrante deve ir da **Entrada (🟩)** até a **Saída (❎)**. A complexidade reside na gestão de recursos (Energia) e na ameaça constante do **Minotauro (🐂)**, que utiliza algoritmos de busca de caminho ótimos (BFS) para perseguição.

## **2\. Estrutura e Configurações**

As constantes abaixo definem as propriedades e a jogabilidade da simulação:

| Constante | Descrição | Valor Padrão |
| :---- | :---- | :---- |
| LARGURA/ALTURA | Dimensões do labirinto (devem ser ímpares para o Algoritmo de Prim). | 31 |
| PERCEPCAO | Distância máxima (em arestas) para o Minotauro iniciar a perseguição. | 5 |
| ITENS\_ATIVOS | Define se itens de consumo e equipamento estão habilitados. | False |

**Itens Disponíveis (se ITENS\_ATIVOS \= True):**

| Categoria | Símbolos | Efeito Principal |
| :---- | :---- | :---- |
| **CONSUMIVEIS** | 🟥, 🟠, 🔴 | Restaura energia. |
| **ARMAS** | 🟧, 🟨, 🔥 | Aumenta a chance de sobrevivência em combate. |
| **ARMADURAS** | 🟦, 🔵 | Aumenta a chance de sobrevivência em combate. |

## **3\. Geração do Labirinto (gerar\_labirinto)**

O labirinto é gerado utilizando uma variação do **Algoritmo de Prim** para garantir que a maior parte do mapa seja acessível.

* **Inicialização:** O mapa é preenchido inteiramente com paredes (🔳).  
* **Centro Livre:** Uma área circular central é forçada a ser caminho (⬜) para garantir que o Minotauro inicie em uma área acessível, prevenindo o isolamento do caçador.  
* **Geração (Prim):** O algoritmo de Prim (usando uma lista de paredes aleatória) é executado, garantindo um caminho contínuo na maioria das células.  
* **Validação:** Após a geração, a função caminho\_minimo (utilizando BFS) verifica se existe solução entre (Entrada, Saída) e se o centro está conectado a ambos. Labirintos sem solução são descartados.  
* **Itens Opcionais:** A função espalhar\_itens coloca consumíveis e equipamentos de forma aleatória nas células de caminho, se habilitado.

## **4\. Agentes Inteligentes**

### **A. Entrante (Entrante) \- Estratégia DFS**

O Entrante simula um explorador usando a lógica de **Busca em Profundidade (DFS)** com a metáfora do "novelo de lã" (self.trilha):

* **Avanço (Exploração):** A cada passo, o Entrante verifica vizinhos não visitados. Se houver, ele avança para um deles aleatoriamente, empilhando a posição atual (self.trilha.append()).  
* **Backtracking (Retorno):** Se o Entrante estiver em uma célula onde todos os vizinhos foram visitados ou são paredes, ele faz *backtrack*, retornando para a posição anterior na pilha (self.trilha.pop()).  
* **Recurso:** Cada passo consome 1 ponto de energia (self.energia \-= 1). O esgotamento da energia resulta em morte por fome.  
* **Coleta de Itens:** Se ITENS\_ATIVOS for True, ao se mover para uma célula de item, ele o coleta e a célula volta a ser um caminho.

### **B. Minotauro (Minotauro) \- Estratégia BFS**

O Minotauro utiliza a **Busca em Largura (BFS)**, através da função caminho\_minimo, para encontrar a rota mais curta e se move em dois modos mutuamente exclusivos:

1. **Modo Patrulha (Padrão):**  
   * Escolhe um destino aleatório no labirinto e usa BFS para se mover em direção a ele.  
   * Após atingir o destino, ou após um número máximo de passos (self.passos\_max), ele redefine um novo destino ou volta ao seu ponto de *spawn* (self.centro).  
2. **Modo Perseguição (self.perseguindo):**  
   * **Ativação:** É ativado quando a distância mínima (distancia\_minima) até o Entrante é menor ou igual ao valor de PERCEPCAO.  
   * **Movimento:** O Minotauro calcula a rota mais curta até a posição atual do Entrante usando BFS e avança um passo nessa rota.  
   * O modo perseguição tem prioridade total sobre a patrulha.

## **5\. Lógica de Encontro e Combate**

A verificação de encontro (checar\_combate\_imediato) ocorre **após o movimento do Minotauro**, mas antes do movimento do Entrante.

* **Condição:** O Minotauro está adjacente (distância 1\) ou na mesma célula que o Entrante.  
* **Resolução (resolver\_encontro):**  
  * A chance base de sobrevivência do Entrante é de **1%**.  
  * Se ITENS\_ATIVOS for True, a chance é aumentada pelos equipamentos equipados (Arma e Armadura).  
  * Um sorteio define o resultado (random.random() \< chance).  
* **Resultado:**  
  * **Entrante Sobrevive:** O Minotauro fica "escondido" (minotauro.escondido \= True) e para de se mover/ser renderizado (simulando a derrota/fuga do Minotauro). O Entrante continua.  
  * **Entrante Morre:** O jogo termina imediatamente, e a célula do Entrante é renderizada como uma explosão (💥).

## **6\. Fluxo Principal do Jogo (main)**

O loop principal (while True) coordena os passos de cada rodada:

1. **Minotauro Move:** minotauro.passo(...)  
2. **Verificação de Combate:** checar\_combate\_imediato e resolver\_encontro. Se o Entrante morrer, o loop para.  
3. **Entrante Move:** entrante.passo() (se não estiver morto).  
4. **Renderização:** Limpa o console (os.system) e imprime o novo estado do labirinto (imprimir).  
5. **Verificação de Fim:** O loop é interrompido se uma das três condições for atingida:  
   * O Entrante alcançou a saída (vitória).  
   * O Entrante morreu de fome.  
   * O Entrante morreu pelo Minotauro.

Ao final, a função gerar\_relatorio salva um registro completo do jogo, incluindo a trilha de vértices percorrida pelo Entrante e o histórico de perseguição do Minotauro, no arquivo relatorio.txt.

## **7\. Link do vídeo Demonstrativo**

[![Link do vídeo Demonstrativo](https://img.youtube.com/vi/9RGFy7A-v00/0.jpg)](https://youtu.be/9RGFy7A-v00)