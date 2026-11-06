# Publicar o dashboard em um link (ex.: subdomínio de rcodatasolutions.com)

> Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.
> **Status:** nenhum destes caminhos foi executado ainda; são instruções, não resultados verificados.

## 1. O que é preciso saber
- O dashboard é **Streamlit (Python)**: precisa de um **servidor que rode Python**. O Lovable hospeda front-ends estáticos/React, então **não roda este app**. Ele serve para o domínio/DNS, não para a aplicação.
- Um subdomínio (ex.: `enchentes.rcodatasolutions.com`) é só um registro **CNAME** que aponta para onde o app estiver hospedado.
- **Dados que não estão no GitHub:** por política do projeto, os PDFs dos PAEs/PSB e os derivados do PSB (documento com «Sigilo: Interno»), as tabelas de Piraju e alguns arquivos de `data/processed/` ficam fora do repositório (ver `.gitignore`). Um deploy feito só a partir do clone **ficará incompleto** nas páginas de Piraju/Paranapanema. Antes de publicar:
  1. decidir que dados podem ser públicos (**confirmar com a CBA se o PSB pode ser citado/derivado em público**);
  2. rodar `make setup` localmente e copiar os dados permitidos para a imagem de deploy, ou gerá-los no build.
- Os vídeos de drone (`outputs/*.mp4`, ~2,5 MB) também estão fora do git; a página «Visão de drone» pode renderizá-los com `ffmpeg` (já listado em `packages.txt`/`Dockerfile`).
- Memória: o DEM e as máscaras são raster grandes. Planos gratuitos (≈ 512 MB–1 GB) podem **estourar**; teste.

## 2. Opções (da mais simples à mais controlável)
| Opção | Custo | Subdomínio próprio | Observações |
|---|---|---|---|
| **Streamlit Community Cloud** | grátis | não (usa `*.streamlit.app`); domínio próprio só via redirecionamento | repositório precisa estar no GitHub; ler `packages.txt`; dados fora do git não irão |
| **Render** (Docker) | plano grátis dorme após inatividade; pago a partir de ~US$ 7/mês | sim (CNAME) | usa o `Dockerfile`; discos persistentes só em planos pagos |
| **Google Cloud Run** | paga por uso, camada gratuita | sim (domain mapping) | usa o `Dockerfile`; partida a frio de alguns segundos |
| **Fly.io** | pequeno custo | sim | `fly launch` com o `Dockerfile` |
| **Exportação estática** (imagens/HTML) | grátis | sim, até no Lovable | perde a interatividade; seria um trabalho à parte |

## 3. Passo a passo sugerido (Render ou Cloud Run + subdomínio)
1. Decida e prepare os dados (seção 1) e faça `docker build -t jurumirim .` e `docker run -p 8501:8501 jurumirim` localmente (**não testado**).
2. Publique a imagem no serviço escolhido; ele fornece uma URL do tipo `algo.onrender.com`.
3. No serviço, adicione o domínio personalizado `enchentes.rcodatasolutions.com` (o nome é só exemplo).
4. No **DNS do domínio** crie um registro `CNAME enchentes → <URL do serviço>` (o painel de DNS fica onde o domínio está gerenciado: no Lovable ou no registrador; confirme onde). O HTTPS é emitido pelo serviço.
5. Teste cada página (o mapa e a visão de drone são as mais pesadas) e confira o aviso fixo em todas.

## 4. Antes de divulgar
- Há conteúdo sensível? O projeto não classifica imóveis nem dá probabilidade, mas trata de rompimento de barragens: mantenha o aviso, as fontes e o texto «não é previsão».
- Não publique contatos pessoais dos PAEs (o projeto não os reproduz).
- Considere proteger com senha enquanto o PSB não for liberado.
