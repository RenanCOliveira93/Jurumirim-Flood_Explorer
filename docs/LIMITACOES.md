# Limitações e o que NÃO pode ser inferido

> Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.

1. **Sem modelo hidráulico próprio.** A mancha é a do PAE, digitalizada. Comparar com a imagem de origem verifica fidelidade de digitalização, não física.
2. **Cenário único e extremo:** ruptura da barragem de concreto em dia seco com N.A. 568,00 m. Não extrapolar para outras cotas, nem escalar a mancha.
3. **Domínio do estudo termina na barragem da UHE Piraju (~33 km).** Nada se afirma além dela.
4. **Incerteza posicional:** registro 0,5 m; vetorização 3,5–10 m; simplificação 2,5 m; mais a incerteza do próprio PAE (escala 1:30.000). Sobreposições de poucas centenas de m² não são robustas.
5. **Cheia sem ruptura:** traçado azul de baixa confiança (cor alterada sob a ZAS; confunde-se com o reservatório) — apenas indicativo; o PAE não dá parâmetros hidráulicos desse cenário.
6. **Áreas urbanizadas IBGE 2019** não são perímetro urbano legal; OSM é colaborativo e incompleto.
7. **DEM** é MDS (inclui vegetação/edificações), ~30 m, erro vertical metros; perfis são descritivos. Não inferir alcance de inundação por cotas.
8. **Não estimar:** probabilidade de ruptura, risco de imóveis/endereços/rotas, profundidade ou velocidade por pixel/rua.
9. O PAE cita comparação de imagens 2019×2024 sem mudanças relevantes na ZAS; isso não substitui verificação atual de uso do solo.
10. **Vídeos GenAI** (opcionais, `STORYBOARD_GENAI.md`) são representação artística, não resultado científico.

## Barragens a jusante (Piraju e Paranapanema)
- **Ruptura em cascata: `not_modelled`.** Sem mancha, tempo ou probabilidade de cascata. O modo «Todas barragens selecionadas» sobrepõe cenários **isolados** com relógios independentes.
- **Tabelas 9/10 de Piraju são imagens**; foram lidas por OCR com checagens físicas (resíduo cota − fundo − profundidade de até 1,15 m na Tabela 10 e 1,37 m na Tabela 9, **não explicado**; pode ser arredondamento/fonte). Sem revisão por engenheiro.
- **Posição das seções de Piraju = ILUSTRAÇÃO** (km sobre eixo OSM; ±centenas de m; afastamento de 445–1070 m dos rótulos da Figura 17). Validada contra coordenadas oficiais (46 m e 45 m) e quilometragem (9,73 × 9,68 km), mas **não é georreferenciamento do PAE**.
- **Sem mancha** para Piraju (Apêndice 9 só listado) e Paranapanema (sem coordenadas nem tabela de tempos).
- Inconsistências **das próprias fontes** estão registradas, não corrigidas (`docs/SOURCE_REGISTRY.md`).
- PSB com «Sigilo: Interno»: derivados fora do Git e das exportações.
- Vazão de pico não é hidrograma; pico acima da descarga nominal não comprova falha; nenhuma inferência de segurança estrutural. Ver `docs/COMPARACAO_JURUMIRIM_PIRAJU.md`.
