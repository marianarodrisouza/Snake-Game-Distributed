import pygame
import random
import socket
import pickle

# Inicializa o Pygame
pygame.init()

# Configurações da tela
LARGURA_TELA = 600
ALTURA_TELA = 600
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption('Jogo da Cobrinha')

# Cores
COR_FUNDO = (0, 0, 0)
COR_COBRA1 = (0, 255, 0)
COR_COBRA2 = (255, 0, 0)
COR_COMIDA = (255, 255, 0)
COR_TEXTO = (255, 255, 255)

# Configurações do jogo
NUM_CELULAS = 30
TAMANHO_CELULA = LARGURA_TELA // NUM_CELULAS

# Conectar ao servidor
IP_SERVIDOR = 'localhost'
PORTA_SERVIDOR = 8080

# Inicializa a conexão com o servidor
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente_socket.settimeout(10)  # Timeout de 10 segundos
cliente_socket.connect((IP_SERVIDOR, PORTA_SERVIDOR))

# Função para desenhar o tabuleiro
def desenhar_tabuleiro(estado_do_jogo):
    tela.fill(COR_FUNDO)
    
    # Desenha a cobra 1
    for parte in estado_do_jogo['cobra1']:
        pygame.draw.rect(tela, COR_COBRA1, (parte[1] * TAMANHO_CELULA, parte[0] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
    
    # Desenha a cobra 2
    for parte in estado_do_jogo['cobra2']:
        pygame.draw.rect(tela, COR_COBRA2, (parte[1] * TAMANHO_CELULA, parte[0] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
    
    # Desenha a comida
    pygame.draw.rect(tela, COR_COMIDA, (estado_do_jogo['comida'][1] * TAMANHO_CELULA, estado_do_jogo['comida'][0] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))

    pygame.display.flip()

# Função para exibir a mensagem de "Game Over"
def mostrar_game_over(vencedor):
    fonte = pygame.font.SysFont('Arial', 36)
    texto = fonte.render(f'Game Over! {vencedor} venceu!', True, COR_TEXTO)
    tela.blit(texto, (LARGURA_TELA // 2 - texto.get_width() // 2, ALTURA_TELA // 2 - texto.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(3000)  # Espera 3 segundos antes de encerrar

# Função para exibir o menu inicial
def exibir_menu():
    tela.fill(COR_FUNDO)
    fonte_titulo = pygame.font.SysFont('Arial', 36)
    fonte_iniciar = pygame.font.SysFont('Arial', 24)

    texto_titulo = fonte_titulo.render('Jogo da Cobrinha', True, COR_TEXTO)
    texto_iniciar = fonte_iniciar.render('Pressione qualquer tecla ou clique para iniciar', True, COR_TEXTO)
    
    tela.blit(texto_titulo, (LARGURA_TELA // 2 - texto_titulo.get_width() // 2, ALTURA_TELA // 3))
    tela.blit(texto_iniciar, (LARGURA_TELA // 2 - texto_iniciar.get_width() // 2, ALTURA_TELA // 2))
    
    pygame.display.flip()

# Loop principal para o menu
def menu():
    menu_rodando = True
    while menu_rodando:
        exibir_menu()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN or evento.type == pygame.MOUSEBUTTONDOWN:
                menu_rodando = False  # Sai do menu ao pressionar uma tecla ou clicar

# Loop principal do jogo
def iniciar_jogo():
    rodando = True
    relogio = pygame.time.Clock()

    # Direções dos jogadores
    direcao1 = 'direita'
    direcao2 = 'esquerda'

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        teclas = pygame.key.get_pressed()

        # Controles da cobra 1
        if teclas[pygame.K_w] and direcao1 != 'baixo':
            direcao1 = 'cima'
        elif teclas[pygame.K_s] and direcao1 != 'cima':
            direcao1 = 'baixo'
        elif teclas[pygame.K_a] and direcao1 != 'direita':
            direcao1 = 'esquerda'
        elif teclas[pygame.K_d] and direcao1 != 'esquerda':
            direcao1 = 'direita'

        # Controles da cobra 2
        if teclas[pygame.K_UP] and direcao2 != 'baixo':
            direcao2 = 'cima'
        elif teclas[pygame.K_DOWN] and direcao2 != 'cima':
            direcao2 = 'baixo'
        elif teclas[pygame.K_LEFT] and direcao2 != 'direita':
            direcao2 = 'esquerda'
        elif teclas[pygame.K_RIGHT] and direcao2 != 'esquerda':
            direcao2 = 'direita'

        # Envia as direções para o servidor
        direcoes = {'direcao1': direcao1, 'direcao2': direcao2}
        cliente_socket.sendall(pickle.dumps(direcoes))

        # Recebe o estado do jogo do servidor
        estado_do_jogo = pickle.loads(cliente_socket.recv(1024))

        # Verifica se o jogo terminou
        if isinstance(estado_do_jogo, str):
            mostrar_game_over(estado_do_jogo)
            rodando = False
        else:
            # Desenha o estado atualizado do jogo
            desenhar_tabuleiro(estado_do_jogo)

        # Controla a velocidade do jogo
        relogio.tick(5)  # Ajuste a taxa de quadros para um jogo mais fluido

    pygame.quit()

# Executa o menu e depois inicia o jogo
menu()
iniciar_jogo()

# Fecha a conexão com o servidor ao finalizar o jogo
cliente_socket.close()
