import random
import math
import time

# --- Configurações ---
LARGURA = 31
ALTURA = 31
# Definições de estados para a animação
PAREDE = "🔳"
CAMINHO = "⬜"
ENTRADA = "🟩"
SAIDA = "❎"
PAREDE_EM_PROCESSAMENTO = "🟨"
CAMINHO_RECENTE = "🟦"

# --- Funções de Impressão ---
def imprimir(matriz, x_proc=None, y_proc=None, delay=0.01):
    """
    Imprime o labirinto.
    x_proc, y_proc: Coordenadas da célula que está sendo processada para destaque.
    """
    print("\033c", end="") 
    
    largura_celula = 1
    for y in range(len(matriz)):
        linha = ""
        for x in range(len(matriz[0])):

            celula = matriz[y][x]
            
            if (x == x_proc and y == y_proc):
                celula = PAREDE_EM_PROCESSAMENTO
            elif (x, y) == (1, 1):
                celula = ENTRADA
            elif (x, y) == (len(matriz[0])-2, len(matriz)-2):
                celula = SAIDA

            linha += f"{celula}" 
        print(linha)
    
    time.sleep(delay)

# --- Gera labirinto (Modificada para animação) ---
def gerar_labirinto(largura, altura):
    """Gera um labirinto usando o algoritmo de Prim modificado com um centro livre e animação."""
    print("Iniciando geração animada...")
    
    # --- Inicializa matriz com paredes ---
    matriz = [[PAREDE for _ in range(largura)] for _ in range(altura)]
    visitado = [[False for _ in range(largura)] for _ in range(altura)]

    start_x, start_y = 1, 1
    matriz[start_y][start_x] = CAMINHO
    visitado[start_y][start_x] = True
    imprimir(matriz, delay=0.1)

    paredes = []
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        nx, ny = start_x+dx, start_y+dy
        if 0 <= nx < largura and 0 <= ny < altura and not visitado[ny][nx]:
            paredes.append((nx, ny))


    # --- Loop do Prim (Com Animação) ---
    while paredes:
        idx = random.randrange(len(paredes))
        x, y = paredes[idx]
        
        imprimir(matriz, x_proc=x, y_proc=y, delay=0.01)

        vizinhos_conectados = []
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < largura and 0 <= ny < altura and visitado[ny][nx]:
                vizinhos_conectados.append((nx, ny))

        if vizinhos_conectados:
            nx, ny = random.choice(vizinhos_conectados)

            px, py = (x+nx)//2, (y+ny)//2
            matriz[py][px] = CAMINHO_RECENTE

            matriz[y][x] = CAMINHO_RECENTE
            visitado[y][x] = True

            imprimir(matriz, delay=0.05)
            
            matriz[py][px] = CAMINHO
            matriz[y][x] = CAMINHO
            imprimir(matriz, delay=0.01)


            for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                nnx, nny = x+dx, y+dy
                if 0 <= nnx < largura and 0 <= nny < altura and not visitado[nny][nnx] and (nnx, nny) not in paredes:
                    paredes.append((nnx, nny))

        paredes.pop(idx)

    # --- Cria centro livre (Após o Prim) ---
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
    
    imprimir(matriz) 

    return matriz

# --- Execução Principal ---
labirinto = gerar_labirinto(LARGURA, ALTURA)
print("Labirinto gerado!")