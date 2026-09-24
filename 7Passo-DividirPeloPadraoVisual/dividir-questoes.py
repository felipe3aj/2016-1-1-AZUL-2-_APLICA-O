"""
Propósito: Dividir as questões por padrão visual vertical.
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026
"""

from PIL import Image
import os

# Desativa o limite de tamanho para evitar o aviso/erro de DecompressionBomb
Image.MAX_IMAGE_PIXELS = None

def cor_proxima(cor_pixel, cor_alvo, tolerancia=15):
    """
    Verifica se uma cor RGB está dentro da tolerância em relação à cor alvo
    """
    r, g, b = cor_pixel[:3]
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def validar_faixa(pixels, altura_total, x, y_inicio, altura_esperada, cor_alvo, margem_erro=2, tolerancia=15):
    """
    Verifica se a partir de y_inicio existe um bloco contínuo da cor_alvo 
    com altura variando dentro de (altura_esperada +/- margem_erro)
    """
    contagem = 0
    y = y_inicio
    
    # Conta quantos pixels seguidos correspondem à cor alvo
    while y < altura_total:
        if cor_proxima(pixels[x, y], cor_alvo, tolerancia):
            contagem += 1
            y += 1
        else:
            break

    # Verifica se a altura contada está dentro da margem de erro
    if (altura_esperada - margem_erro) <= contagem <= (altura_esperada + margem_erro):
        return True, contagem
    return False, 0

def encontrar_padrao_vertical(imagem, tolerancia=15):
    """
    Encontra posições no último pixel da direita que correspondem ao padrão vertical:
    1. 4px de RGB(35, 31, 32)   [margem ±2]
    2. 7px de RGB(255, 255, 255) [margem ±2]
    3. 10px de RGB(189, 188, 188)[margem ±2]
    4. 4px de RGB(35, 31, 32)   [margem ±2]
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # Cores do padrão visual
    cor1 = (35, 31, 32)
    cor2 = (255, 255, 255)
    cor3 = (189, 188, 188)
    cor4 = (35, 31, 32)

    x = largura - 1  # Último pixel da direita
    posicoes_corte = []
    
    y = 0
    while y < altura:
        # Testa a 1ª faixa (4px)
        valido1, h1 = validar_faixa(pixels, altura, x, y, 4, cor1, margem_erro=2, tolerancia=tolerancia)
        if valido1:
            # Testa a 2ª faixa (7px)
            valido2, h2 = validar_faixa(pixels, altura, x, y + h1, 7, cor2, margem_erro=2, tolerancia=tolerancia)
            if valido2:
                # Testa a 3ª faixa (10px)
                valido3, h3 = validar_faixa(pixels, altura, x, y + h1 + h2, 10, cor3, margem_erro=2, tolerancia=tolerancia)
                if valido3:
                    # Testa a 4ª faixa (4px)
                    valido4, h4 = validar_faixa(pixels, altura, x, y + h1 + h2 + h3, 4, cor4, margem_erro=2, tolerancia=tolerancia)
                    if valido4:
                        # Padrão completo encontrado!
                        # Corta 12 pixels antes do padrão começar
                        posicao_corte = y - 12
                        if posicao_corte < 0:
                            posicao_corte = 0
                            
                        posicoes_corte.append((posicao_corte, y + h1 + h2 + h3 + h4))
                        print(f"Padrão encontrado em y={y}, cortando em y={posicao_corte}")
                        
                        # Salta o padrão inteiro para não detectar novamente
                        y += (h1 + h2 + h3 + h4)
                        continue
        y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente com base no padrão encontrado
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Retorna lista de tuplas (posicao_corte, fim_do_padrao)
    dados_corte = encontrar_padrao_vertical(imagem)
    
    if not dados_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontradas {len(dados_corte)} marcas do padrão para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, (posicao_corte, fim_padrao) in enumerate(dados_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    # Corta a seção final
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(dados_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "inteiras"  # Substitua pelo nome da pasta de saída desejada

    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")