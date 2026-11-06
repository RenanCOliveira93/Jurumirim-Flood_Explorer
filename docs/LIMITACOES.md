# Limitações e o que NÃO pode ser inferido

> Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.

1. **Sem modelo hidráulico próprio.** A mancha é a do PAE, digitalizada. Comparar com a imagem de origem verifica fidelidade de digitalização, não física.
2. **Cenário único e extremo:** ruptura da barragem de concreto em dia seco com N.A. 568,00 m. Não extrapolar para outras cotas, nem escalar a mancha.
3. **Domínio do estudo termina na barragem da UHE Piraju (~33 km).** Nada se afirma além dela.
4. **Incerteza posicional:** registro 0,5 m; vetorização 3,5–10 m; simplificação 2,5 m; mais a incerteza do próprio PAE (escala 1:30.000). Sobreposições de poucas centenas de m² não são robustas.
5. **Cheia sem ruptura:** traçado azul de baixa confiança (cor alterada sob a ZAS; confunde-se com o reservatório) — apenas indicativo; o PAE não dá parâmetros hidráulicos desse cenário.
6. **Áreas urbanizadas IBGE 2019** não são perímetro urbano legal; OSM é colaborativo e incompleto.
7. **DEM** é MDS (inclui vegetação/edificações), ~30 m, erro vertical metros; perfis são descritivos. Para Jurumirim não se infere alcance por cotas (a mancha é a do PAE). Para Piraju existe uma **estimativa exploratória separada**, rotulada (ver abaixo).
8. **Não estimar:** probabilidade de ruptura, risco de imóveis/endereços/rotas, profundidade ou velocidade por pixel/rua.
9. O PAE cita comparação de imagens 2019×2024 sem mudanças relevantes na ZAS; isso não substitui verificação atual de uso do solo.
10. **Vídeos GenAI** (opcionais, `STORYBOARD_GENAI.md`) são representação artística, não resultado científico.

## Barragens a jusante (Piraju e Paranapanema)
- **Ruptura em cascata hidráulica: `not_modelled`.** O modo «Todas barragens selecionadas» sobrepõe cenários **isolados** com relógios independentes; a opção de encadeamento é apenas uma hipótese de tempo (abaixo).
- **Tabelas 9/10 de Piraju são imagens**; foram lidas por OCR com checagens físicas (resíduo cota − fundo − profundidade de até 1,15 m na Tabela 10 e 1,37 m na Tabela 9, **não explicado**; pode ser arredondamento/fonte). Sem revisão por engenheiro.
- **Posição das seções de Piraju = ILUSTRAÇÃO** (km sobre eixo OSM; ±centenas de m; afastamento de 445–1070 m dos rótulos da Figura 17). Validada contra coordenadas oficiais (46 m e 45 m) e quilometragem (9,73 × 9,68 km), mas **não é georreferenciamento do PAE**.
- **Sem mancha OFICIAL** para Piraju (Apêndice 9 só listado) e Paranapanema (sem coordenadas nem tabela de tempos).
- **Estimativa exploratória de Piraju (`bathtub.py`, `make estimates`):** relevo Copernicus 30 m preenchido até a cota máxima tabelada no PAE, conectado ao rio, num corredor de 1,5 km. **Não é o mapa do PAE nem simulação hidráulica**; é enchimento estático (sem inércia, volume ou tempo). Limites: MDS com vegetação e erro vertical de metros, posição das seções ilustrativa, referenciais verticais possivelmente diferentes. Validação possível: cobre 95 % (99,7 % com tolerância de 36 m) da parte larga da mancha clara da Figura 17 (cenário **sem** ruptura, sem legenda própria). Isso mede cobertura, **não excesso**, e **não valida a ruptura** (sem mapa nos PDFs). Interseções com áreas urbanizadas IBGE não classificam endereços ou imóveis.
- **Paranapanema:** sem cotas por seção, **sem estimativa de mancha**; o PAE cita ≈ 3,4 km² só como ordem de grandeza. **ZAS** (Piraju 9,68 km, Paranapanema 10 km) é desenhada como **trecho de rio** com a extensão do PAE (posição ILUSTRATIVA). **ZSS:** Piraju «não definida»; Paranapanema só define ZAS.
- **Encadeamento no tempo (opcional, hipótese):** supõe que cada barragem rompe quando chega a onda da anterior (tempos dos PAEs: Jurumirim→Piraju 1 h 59 min; Piraju→Paranapanema = tempo da ST-11, km 9,65 ≈ 9,68). **Só desloca relógios**: não soma vazões, não calcula interação hidráulica nem altera mapas. Nenhum PAE estuda esse evento.
- Inconsistências **das próprias fontes** estão registradas, não corrigidas (`docs/SOURCE_REGISTRY.md`).
- PSB com «Sigilo: Interno»: derivados fora do Git e das exportações.
- Vazão de pico não é hidrograma; pico acima da descarga nominal não comprova falha; nenhuma inferência de segurança estrutural. Ver `docs/COMPARACAO_JURUMIRIM_PIRAJU.md`.

## Página «Altitude, força, extensão e duração» (`exposure.py`, `make exposure`)
- **Força:** pressão dinâmica ½ρv², carga v²/2g e h·v saem das velocidades/profundidades **máximas na seção do canal** (HEC-RAS). Não são valores no terreno nem sobre construções; sem detritos. Jurumirim não tabela profundidade.
- **Extensão lateral:** borda da mancha − borda da água normal (OSM), em transectos de 500 m. Jurumirim = mancha oficial; Piraju = **estimativa**. Largura de cenários diferentes não é comparável como «uma onda mais larga que a outra».
- **% de área urbana:** área urbanizada IBGE 2019 (≠ perímetro urbano) tocada ÷ total no município de Piraju. Mede área de mancha IBGE, **não** pessoas, imóveis ou endereços.
- **Altitude × nível da água:** MDS 30 m; cota do PAE da seção mais próxima do ponto central da mancha; «% do terreno abaixo da cota» não exige conexão com o rio (é teto). Referenciais verticais podem diferir.
- **Duração da inundação: NÃO calculável** (os PAEs não trazem hidrograma completo nem recessão). Só há chegada, pico e subida; o «teto de massa» V/Δ é um limite superior, não uma estimativa.
