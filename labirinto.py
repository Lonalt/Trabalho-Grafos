"""Labirinto com Entrante (DFS) e Minotauro (BFS) - Lógica de Movimento Restaurada e Otimizada."""

import random
import os 
import math
from collections import deque
import time
from heapq import heappush, heappop

# --- Configurações ---
LARGURA = 31
ALTURA = 31
PAREDE = "🔳"
CAMINHO = "⬜"
JOGADOR = "🏃"
MINOTAURO = "🐂"
ENTRADA = "🟩"
SAIDA = "❎"

PERCEPCAO = 5  # p(G): distância (em arestas) para o Minotauro detectar o entrante

ITENS_ATIVOS = True

# Consumíveis: energia
CONSUMIVEIS = {
    "🟥": 10,
    "🟠": 25,
    "🔴": 50
}

# Armas (força)
ARMAS = {
    "🟧": 10,
    "🟨": 25,
    "🔥": 50
}

# Armaduras (defesa)
ARMADURAS = {
    "🟦": 10,
    "🔵": 50
}

# --- Gera labirinto ---
def gerar_labirinto(largura, altura):
    """Gera um labirinto usando o algoritmo de Prim modificado com um centro livre."""
    # --- Inicializa matriz com paredes ---
    matriz = [[PAREDE for _ in range(largura)] for _ in range(altura)]
    visitado = [[False for _ in range(largura)] for _ in range(altura)]

    start_x, start_y = 1, 1
    matriz[start_y][start_x] = CAMINHO
    visitado[start_y][start_x] = True

    # Inicializa as paredes a partir dos vizinhos da entrada
    paredes = []
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        nx, ny = start_x+dx, start_y+dy
        if 0 <= nx < largura and 0 <= ny < altura:
            if not visitado[ny][nx]:
                paredes.append((nx, ny))


    # --- Loop do Prim ---
    while paredes:
        idx = random.randrange(len(paredes))
        x, y = paredes[idx]

        vizinhos_conectados = []
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < largura and 0 <= ny < altura and visitado[ny][nx]:
                vizinhos_conectados.append((nx, ny))

        if vizinhos_conectados:
            nx, ny = random.choice(vizinhos_conectados)

            px, py = (x+nx)//2, (y+ny)//2
            matriz[py][px] = CAMINHO

            matriz[y][x] = CAMINHO
            visitado[y][x] = True

            for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                nnx, nny = x+dx, y+dy
                if 0 <= nnx < largura and 0 <= nny < altura and not visitado[nny][nnx] and (nnx, nny) not in paredes:
                    paredes.append((nnx, nny))

        paredes.pop(idx)

    # --- Cria centro livre  ---
    cx, cy = largura // 2, altura // 2
    total = largura * altura
    area_livre = math.ceil(total * 0.05)
    raio = int(math.sqrt(area_livre / math.pi))

    for y in range(cy - raio, cy + raio + 1):
        for x in range(cx - raio, cx + raio + 1):
            if 0 <= x < largura and 0 <= y < altura:
                if (x - cx) ** 2 + (y - cy) ** 2 <= raio ** 2:
                    matriz[y][x] = CAMINHO

    matriz[altura-2][largura-2] = CAMINHO

    return matriz

def espalhar_itens(matriz, quantidade=20):
    """Espalha itens aleatórios no labirinto se ITENS_ATIVOS for True."""
    if not ITENS_ATIVOS:
        return

    altura = len(matriz)
    largura = len(matriz[0])
    # Incluindo os novos símbolos para CONSUMIVEIS, ARMAS e ARMADURAS
    itens = list(CONSUMIVEIS.keys()) * 1 + list(ARMAS.keys()) + list(ARMADURAS.keys())

    espalhados = 0
    tentativas = 0
    while espalhados < quantidade and tentativas < quantidade * 10:
        tentativas += 1
        x = random.randint(1, largura-2)
        y = random.randint(1, altura-2)

        # Evita colocar item na entrada e na saída
        if matriz[y][x] == CAMINHO and (x, y) != (1, 1) and (x, y) != (largura-2, altura-2):
            matriz[y][x] = random.choice(itens)
            espalhados += 1

# --- utilidades de grid ---
def vizinhos_livres(pos, matriz):
    """Gera vizinhos livres (não parede) de uma posição (x,y) na matriz."""
    x, y = pos
    for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
        nx, ny = x+dx, y+dy
        if 0 <= nx < len(matriz[0]) and 0 <= ny < len(matriz):
            if matriz[ny][nx] != PAREDE:
                yield (nx, ny)

def caminho_minimo(origem, destino, matriz):
    """BFS retorna lista de vértices do caminho (inclui origem e destino)"""
    if origem == destino:
        return [origem]
    fila = deque([origem])
    pai = {origem: None}

    altura = len(matriz)
    largura = len(matriz[0])

    while fila:
        atual = fila.popleft()
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nb = (atual[0]+dx, atual[1]+dy)
            nx, ny = nb

            celula = matriz[ny][nx]
            is_path = celula != PAREDE

            if 0 <= nx < largura and 0 <= ny < altura and is_path and nb not in pai:
                pai[nb] = atual
                if nb == destino:
                    path = [nb]
                    p = pai[nb]
                    while p is not None:
                        path.append(p)
                        p = pai[p]
                    path.reverse()
                    return path
                fila.append(nb)
    return []

def distancia_minima(origem, destino, matriz):
    """Distância em número de arestas pelo caminho mínimo."""
    path = caminho_minimo(origem, destino, matriz)
    return len(path)-1 if path else float('inf')

# --- Entrante (DFS com “novelo de lã”) ---
class Entrante:
    """Classe que representa o Entrante (jogador) no labirinto."""
    def __init__(self, inicio, saida, matriz, energia_max=500):
        self.pos = inicio
        self.saida = saida
        self.matriz = matriz
        self.visitado = set([inicio])
        self.trilha = [] # Pilha para DFS
        self.energia_max = energia_max
        self.energia = energia_max
        self.morto = False

        # Campos de Relatório
        self.trilha_final = [inicio]

        # Equipamentos (usados se ITENS_ATIVOS for True)
        self.arma = None
        self.armadura = None

        # Posição anterior para fins de rastro
        self.pos_anterior = inicio

    def coletar_item(self, item):
        """Coleta e aplica o efeito do item (se ITENS_ATIVOS for True)."""
        if not ITENS_ATIVOS:
            return

        # Consumível
        if item in CONSUMIVEIS:
            self.energia = min(self.energia_max, self.energia + CONSUMIVEIS[item])
        # Arma
        elif item in ARMAS:
            self.arma = item
        # Armadura
        elif item in ARMADURAS:
            self.armadura = item

    def bonus_combate_total(self):
        """Calcula a chance de vitória/sobrevivência baseada nos equipamentos."""
        if not ITENS_ATIVOS:
            return 0.0

        chance = 0
        if self.arma:
            chance += ARMAS[self.arma]
        if self.armadura:
            chance += ARMADURAS[self.armadura]
        return chance / 100

    def passo(self):
        """Faz um passo no labirinto usando DFS com trilha (novelo de lã)."""
        if self.energia <= 0:
            return self.pos, False, True

        if self.morto:
            return self.pos, False, False

        self.energia -= 1

        # 1. Restaura visualmente a célula anterior
        if self.pos_anterior != self.pos:

            if self.pos_anterior == (1, 1): # Entrada
                self.matriz[self.pos_anterior[1]][self.pos_anterior[0]] = ENTRADA
            elif self.pos_anterior == self.saida: # Saída
                self.matriz[self.pos_anterior[1]][self.pos_anterior[0]] = SAIDA
            else:
                self.matriz[self.pos_anterior[1]][self.pos_anterior[0]] = CAMINHO

        self.pos_anterior = self.pos

        if self.pos == self.saida:
            return self.pos, True, False

        vizs = list(vizinhos_livres(self.pos, self.matriz))
        random.shuffle(vizs)

        # 2. Tenta avançar (DFS)
        for nb in vizs:
            if nb not in self.visitado:
                # Movimento
                self.trilha.append(self.pos)
                self.pos = nb
                self.visitado.add(self.pos)

                # REGISTRO: Adiciona o novo vértice à trilha final
                self.trilha_final.append(self.pos)

                # Coleta item se houver
                if ITENS_ATIVOS:
                    celula = self.matriz[self.pos[1]][self.pos[0]]
                    if celula in CONSUMIVEIS or celula in ARMAS or celula in ARMADURAS:
                        self.coletar_item(celula)
                        self.matriz[self.pos[1]][self.pos[0]] = CAMINHO

                return self.pos, (self.pos == self.saida), False

        # 3. Backtrack
        if self.trilha:
            self.pos = self.trilha.pop()

            # REGISTRO: Adiciona o vértice de retorno à trilha final
            self.trilha_final.append(self.pos)

        return self.pos, (self.pos == self.saida), False

    def mostrar_energia(self):
        """Retorna uma string representando o status atual do Entrante."""
        base_status = f"--- 🏃 Entrante | 🍗 Energia: {self.energia}/{self.energia_max}"

        if ITENS_ATIVOS:
            arma = self.arma if self.arma else "Nenhuma"
            armadura = self.armadura if self.armadura else "Nenhuma"
            return f"{base_status} | Arma: {arma} | Armadura: {armadura} ---"
        else:
            return f"{base_status} | ITENS: DESATIVADOS ---"


# --- Minotauro (dois modos) ---
class Minotauro:
    """Classe que representa o Minotauro no labirinto."""
    def __init__(self, inicio):
        self.pos = inicio
        self.centro = inicio
        self.perseguindo = False
        self.ultimo = inicio
        self.passos_patrulha = 0
        self.passos_max = 15
        self.destino = None
        self.escondido = False

        # Campos de Estado da Patrulha Anterior
        self.voltando = False
        self.memoria = []
        self.memoria_max = 20

        # Campos de Relatório
        self.detectado_em = None
        self.alcancado_em = None
        self.caminho_perseguicao = []
        self.ultima_perseg_pos = inicio

    def _encontrar_destino_aleatorio(self, matriz):
        """Função auxiliar para escolher um ponto aleatório livre no mapa."""

        largura, altura = len(matriz[0]), len(matriz)
        livres = [(x, y) for y in range(altura) for x in range(largura) if matriz[y][x] != PAREDE and (x, y) != self.pos and (x, y) != self.centro]

        if not livres:
            return self.centro

        return random.choice(livres)


    def passo(self, alvo, matriz, percepcao, rodada_atual):
        """Faz um passo no labirinto baseado na lógica de perseguição/patrulha."""

        if self.escondido:
            return self.pos

        dist = distancia_minima(self.pos, alvo, matriz)
        perseg_anterior = self.perseguindo

        self.perseguindo = dist <= percepcao

        # Lógica de registro de detecção
        if self.perseguindo and not perseg_anterior and dist > 0:
            if self.detectado_em is None:
                self.detectado_em = rodada_atual

        # === MODO PERSEGUIÇÃO: Movimento de 2 em 2 (Ajustado) ===
        if self.perseguindo and dist > 0 and dist < float('inf'):
            path = caminho_minimo(self.pos, alvo, matriz)

            if len(path) >= 3:
                proxima_pos = path[2] 
            elif len(path) == 2:

                proxima_pos = path[1]
            else:
                proxima_pos = None

            if proxima_pos:
                self.ultimo = self.pos
                self.pos = proxima_pos

                # REGISTRO: Adiciona a posição à trilha de perseguição
                if self.ultima_perseg_pos != self.pos:
                    self.caminho_perseguicao.append(self.pos)
                    self.ultima_perseg_pos = self.pos
        
        # === MODO PATRULHA: Original com BFS (Otimizado) ===
        else:
            contador = 0
            if self.destino is None or self.pos == self.destino:
                if not self.voltando:
                    # escolhe ponto aleatório
                    self.destino = self._encontrar_destino_aleatorio(matriz)
                    contador += 1
                    if contador > 10:
                        self.voltando = True
                else:
                    # volta ao centro
                    self.destino = self.centro
                    self.voltando = False


            path = caminho_minimo(self.pos, self.destino, matriz)

            if len(path) >= 2:
                proxima_pos = path[1]

                self.ultimo = self.pos
                self.pos = proxima_pos
                self.passos_patrulha += 1
                self.memoria.append(self.pos)

                if len(self.memoria) > self.memoria_max:
                    self.memoria.pop(0)

            if self.passos_patrulha >= self.passos_max:
                self.passos_patrulha = 0
                self.destino = None

        return self.pos

# --- Renderização ---
def imprimir(matriz, entrante_pos, minotauro_pos, minotauro: Minotauro=None):
    largura_celula = 1
    for y in range(len(matriz)):
        linha = ""
        for x in range(len(matriz[0])):

            celula = matriz[y][x]
            is_explosion = False
            if (x, y) == entrante_pos and entrante.morto:
                celula = "💥"
                is_explosion = True

            if (x, y) == entrante_pos and not is_explosion:
                celula = JOGADOR
            elif (x, y) == minotauro_pos and not minotauro.escondido:
                celula = MINOTAURO

            elif (x, y) == (1, 1):
                celula = ENTRADA
            elif (x, y) == (len(matriz[0])-2, len(matriz)-2):
                celula = SAIDA

            linha += f"{celula:<{largura_celula}}"
        print(linha)


# --- Regras de encontro ---
def resolver_encontro():
    """Resolve o encontro entre Entrante e Minotauro. Retorna True se o Entrante sobrevive."""
    # 1. Chance base
    chance = 0.01

    if ITENS_ATIVOS:
        # 2. Adiciona bônus de equipamentos se existirem
        bonus_equipamento = entrante.bonus_combate_total()
        chance += bonus_equipamento

    # 3. Garante que não ultrapasse 99%
    chance = min(chance, 0.99)

    return random.random() < chance

# Função para checar se o Minotauro está adjacente ou sobre o Entrante
def checar_combate_imediato(minotauro_pos, entrante_pos, matriz):
    """Checa se o Minotauro está na mesma posição ou adjacente ao Entrante."""
    if minotauro_pos == entrante_pos:
        return True
    dist = distancia_minima(minotauro_pos, entrante_pos, matriz)
    return dist == 1

# --- Geração de Relatório ---
def gerar_relatorio(jogador: Entrante, minotauro: Minotauro, status_final: str):
    """Gera um relatório final do jogo e salva em 'relatorio.txt'."""
    # global ITENS_ATIVOS

    report = "======== RELATÓRIO DO LABIRINTO (MINOTAURO) ========\n"
    report += f"STATUS FINAL: {status_final}\n"
    report += f"Rodada final: {minotauro.alcancado_em if minotauro.alcancado_em else 'N/A'}\n"
    report += "----------------------------------------------------\n"

    # Tempo restante de comida
    report += f"TEMPO RESTANTE DE ENERGIA (Comida): {jogador.energia} passos (Inteiros)\n"

    if ITENS_ATIVOS:
        report += f"Arma do Entrante: {jogador.arma if jogador.arma else 'Nenhuma'}\n"
        report += f"Armadura do Entrante: {jogador.armadura if jogador.armadura else 'Nenhuma'}\n"
    else:
        report += "[INFO] A coleta, uso e rastreamento de Itens/Equipamentos estão DESATIVADOS.\n"

    report += "----------------------------------------------------\n"
    trilha = jogador.trilha_final
    # Sequência de vértices do prisioneiro (Entrante)
    report += f"SEQUÊNCIA DE VÉRTICES VISITADOS PELO PRISIONEIRO ({len(jogador.trilha_final)} vértices):\n"
    report += "-> ["
    for i, vertice in enumerate(trilha):
        report += str(vertice)

        if i < len(trilha) - 1:
            report += ", "
        if (i + 1) % 8 == 0 and i < len(trilha) - 1:
            report += "\n   "

    report += "]\n"
    report += "----------------------------------------------------\n"

    # Detecção e Perseguição
    report += "RASTREAMENTO DO MINOTAURO:\n"

    if minotauro.detectado_em:
        report += f" - Detecção do Prisioneiro: Rodada {minotauro.detectado_em}\n"
    else:
        report += " - O prisioneiro não foi detectado pelo Minotauro.\n"

    if minotauro.alcancado_em:
        report += f" - Encontro (Alcançado): Rodada {minotauro.alcancado_em}\n"
    else:
        report += " - O encontro não ocorreu.\n"

    if minotauro.caminho_perseguicao:
        report += " - Caminho Percorrido pelo Minotauro (durante a perseguição):\n"
        report += str(minotauro.caminho_perseguicao) + "\n"
    else:
        report += " - Nenhuma perseguição significativa ocorreu ou foi registrada.\n"

    report += "====================================================\n"

    with open("relatorio.txt", "w", encoding="utf-8") as f:
        f.write(report)

    print("\n[INFO] Relatório salvo em 'relatorio.txt'")


# --- Principal ---
def main():
    """Função principal que executa o jogo do labirinto."""
    global entrante

    os.system('cls' if os.name == 'nt' else 'clear')

    entrada = (1, 1)
    saida = (LARGURA-2, ALTURA-2)

    lab = gerar_labirinto(LARGURA, ALTURA)

    espalhar_itens(lab, quantidade=30)
    lab[entrada[1]][entrada[0]] = ENTRADA
    lab[saida[1]][saida[0]] = SAIDA


    # Encontra ponto de spawn do Minotauro
    cx, cy = len(lab[0])//2, len(lab)//2
    mino_start = None
    if lab[cy][cx] == PAREDE:
        pq = []
        seen = set()
        heappush(pq, (0, (cx, cy)))
        while pq:
            _, (x, y) = heappop(pq)
            if (x, y) in seen:
                continue
            seen.add((x, y))
            if lab[y][x] != PAREDE:
                mino_start = (x, y)
                break
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                if 0 <= nx < len(lab[0]) and 0 <= ny < len(lab):
                    heappush(pq, (abs(nx-cx)+abs(ny-cy), (nx, ny)))
    else:
        mino_start = (cx, cy)

    if mino_start is None:
        mino_start = (LARGURA-2, ALTURA-2)


    entrante = Entrante(entrada, saida, lab)
    minotauro = Minotauro(mino_start)
    minotauro.centro = mino_start

    time.sleep(1.0)
    os.system('cls' if os.name == 'nt' else 'clear')

    rodada = 0
    status_final = "INCOMPLETO"

    while True:

        rodada += 1

        # 1. MINOTAURO SE MOVE
        mpos = minotauro.passo(entrante.pos, lab, PERCEPCAO, rodada)

        # 2. VERIFICAÇÃO DE COMBATE E RESOLUÇÃO
        if checar_combate_imediato(mpos, entrante.pos, lab):

            minotauro.alcancado_em = rodada
            sobreviveu = resolver_encontro()

            if not sobreviveu:
                print(f"\n💀 O Minotauro eliminou o prisioneiro na Rodada {rodada}!")
                entrante.morto = True
                status_final = "MORREU PELO MINOTAURO"
            else:
                print(f"\n⚔️ Batalha! O prisioneiro sobreviveu na Rodada {rodada} e continua sua jornada.")

            minotauro.escondido = True

            if entrante.morto:
                break


        # 3. ENTRANTE SE MOVE (Se não estiver morto)
        epos, salvou, morreu_fome = entrante.passo()

        # 4. LIMPEZA E RENDERIZAÇÃO
        os.system('cls' if os.name == 'nt' else 'clear')
        imprimir(lab, epos, mpos, minotauro)

        destino_str = minotauro.destino if minotauro.destino else "Nenhum"
        estado_mino = '🐂 PERSEGUINDO 🏃' if minotauro.perseguindo and not minotauro.escondido else ('Patrulha para ' + str(destino_str) if not minotauro.escondido else "Desativado")

        print(f"\nRodada {rodada} | Estado do Minotauro: {estado_mino} | Percepção (Distância): {PERCEPCAO}")
        print(entrante.mostrar_energia())

        # 5. CONDIÇÕES DE FIM DE JOGO
        if morreu_fome:
            print("\n💀 O prisioneiro não aguentou mais andar. Morreu de fome!")
            status_final = "MORREU DE FOME"
            minotauro.alcancado_em = rodada
            break

        if salvou:
            print("\n🎉 O prisioneiro encontrou a saída!")
            status_final = "ESCAPOU"
            minotauro.alcancado_em = rodada
            break

        time.sleep(0.05)

    # RENDERIZAÇÃO FINAL
    os.system('cls' if os.name == 'nt' else 'clear')
    imprimir(lab, entrante.pos, minotauro.pos, minotauro)
    print(f"\n--- FIM DE JOGO: {status_final} na Rodada {rodada} ---")

    # GERAÇÃO FINAL DO RELATÓRIO
    gerar_relatorio(entrante, minotauro, status_final)


if __name__ == "__main__":
    main()
