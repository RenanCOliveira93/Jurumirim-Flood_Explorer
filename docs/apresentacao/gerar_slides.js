// Gera docs/apresentacao/Jurumirim_Flood_Explorer.pptx  ->  node gerar_slides.js   (requer: npm i pptxgenjs)
const pptxgen = require("pptxgenjs");
const path = require("path");
const IMG = (f) => path.join(__dirname, "..", "img", f);
const AUTOR = path.join(__dirname, "..", "..", "app", "assets", "autor.jpg");
const sizeOf = require("fs").existsSync;

const DISC = "Estudo educacional independente; não substitui o PAE oficial, a Defesa Civil ou laudo de engenharia.";
const C = { navy: "0B2A3C", teal: "1C7293", ice: "E8F1F5", orange: "E07A2F", ink: "1B2B34", mute: "5B6B75", white: "FFFFFF", green: "3C8D5A", purple: "7A4FA3" };
const HF = "Cambria", BF = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.title = "Jurumirim Flood Explorer — Piraju seria alagada?";
pres.author = "Renan Cunha de Oliveira";

// proporção das imagens (largura/altura) para encaixar sem distorcer
const AR = { "3d_piraju.png": 1315 / 760, "3d_corredor.png": 1423 / 760, "relevo_piraju.png": 1119 / 884, "relevo_corredor.png": 1128 / 761, "relevo_paranapanema.png": 1128 / 808 };
function fit(slide, file, x, y, w, h, name) {
  const ar = AR[file]; let iw = w, ih = w / ar;
  if (ih > h) { ih = h; iw = h * ar; }
  slide.addImage({ path: IMG(file), x: x + (w - iw) / 2, y: y + (h - ih) / 2, w: iw, h: ih, altText: name || file });
}
function base(title, opts = {}) {
  const s = pres.addSlide();
  const dark = !!opts.dark;
  s.background = { color: dark ? C.navy : C.white };
  if (title) s.addText(title, { x: 0.5, y: 0.3, w: 9, h: 0.8, fontFace: HF, fontSize: 28, bold: true, color: dark ? C.white : C.navy, margin: 0, isTextBox: true, valign: "top" });
  s.addText(DISC, { x: 0.5, y: 5.25, w: 9, h: 0.25, fontFace: BF, fontSize: 9, italic: true, color: dark ? "B8CAD3" : C.mute, margin: 0, isTextBox: true });
  if (opts.tag) tag(s, opts.tag);
  return s;
}
const TAGS = { O: ["DADO OFICIAL", C.teal], D: ["DERIVADO DO PAE", C.green], E: ["ESTIMATIVA EXPLORATÓRIA", C.purple], I: ["ILUSTRAÇÃO", C.mute] };
function tag(s, k) {
  const [t, col] = TAGS[k];
  s.addText(t, { x: 7.0, y: 0.05, w: 2.5, h: 0.26, fontFace: BF, fontSize: 9, bold: true, color: C.white, align: "center", valign: "middle", fill: { color: col }, margin: 0, isTextBox: true });
}
function stat(s, x, y, w, big, small, color) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 1.35, fill: { color: C.ice }, line: { color: C.ice }, rectRadius: 0.12 });
  s.addText(big, { x: x + 0.1, y: y + 0.12, w: w - 0.2, h: 0.65, fontFace: HF, fontSize: 30, bold: true, color: color || C.teal, align: "center", margin: 0, isTextBox: true });
  s.addText(small, { x: x + 0.1, y: y + 0.78, w: w - 0.2, h: 0.5, fontFace: BF, fontSize: 12.5, color: C.ink, align: "center", valign: "top", margin: 0, isTextBox: true });
}
function para(s, text, x, y, w, h, size) {
  s.addText(text, { x, y, w, h, fontFace: BF, fontSize: size || 16, color: C.ink, margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 8 });
}
function bullets(s, items, x, y, w, h, size, color) {
  const arr = items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } }));
  s.addText(arr, { x, y, w, h, fontFace: BF, fontSize: size || 16, color: color || C.ink, margin: 0, valign: "top", isTextBox: true, paraSpaceAfter: 10 });
}

// 1 ------------------------------------------------------------
let s = base(null, { dark: true });
fit(s, "3d_piraju.png", 4.9, 0.5, 4.7, 3.6, "Vista 3D do relevo de Piraju");
s.addText("Piraju seria alagada?", { x: 0.5, y: 1.2, w: 4.3, h: 1.4, fontFace: HF, fontSize: 38, bold: true, color: C.white, margin: 0, isTextBox: true, valign: "top" });
s.addText("O que os planos oficiais de emergência de três barragens realmente dizem, e o que ninguém sabe.", { x: 0.5, y: 2.75, w: 4.2, h: 1.1, fontFace: BF, fontSize: 16, color: "CADCE6", margin: 0, isTextBox: true, valign: "top" });
s.addText("Jurumirim Flood Explorer", { x: 0.5, y: 4.3, w: 4.3, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: C.orange, margin: 0, isTextBox: true });
s.addNotes("Abra com a pergunta e não responda ainda. O objetivo é tirar o alarmismo e mostrar de onde vêm os números. Perfil: todos.");

// 2 ------------------------------------------------------------
s = base("Três barragens em sequência", { tag: "O" });
stat(s, 0.5, 1.15, 2.8, "7.007", "milhões de m³: Jurumirim (a maior)");
stat(s, 0.5, 2.45, 2.8, "105,6", "milhões de m³: Piraju (≈ 66 vezes menor)", C.orange);
stat(s, 0.5, 3.75, 2.8, "12,2", "milhões de m³: Paranapanema");
fit(s, "relevo_corredor.png", 3.6, 1.2, 6.0, 3.9, "Relevo do corredor Jurumirim-Piraju-Paranapanema");
s.addNotes("O tamanho do reservatório muda tudo: Jurumirim guarda cerca de 66 vezes mais água que Piraju. Fonte: PAEs de cada barragem.");

// 3 ------------------------------------------------------------
s = base("O que é um PAE?", { tag: "O" });
para(s, "PAE = Plano de Ação de Emergência.", 0.5, 1.3, 5, 0.5, 20);
bullets(s, ["Cada barragem tem o seu, por lei.", "Ele descreve um cenário hipotético de acidente para preparar alertas e evacuação.", "É um exercício de preparo, não uma previsão.", "Ninguém está dizendo que uma barragem vai romper."], 0.5, 2.0, 5.2, 3, 17);
s.addShape(pres.shapes.OVAL, { x: 6.5, y: 1.4, w: 2.8, h: 2.8, fill: { color: C.ice }, line: { color: C.teal, width: 3 } });
s.addText("NÃO é\nprevisão", { x: 6.5, y: 1.4, w: 2.8, h: 2.8, fontFace: HF, fontSize: 28, bold: true, color: C.teal, align: "center", valign: "middle", margin: 0, isTextBox: true });
s.addNotes("Evite alarmismo. Explique que o PAE é um plano de preparo. Perfil: público em geral.");

// 4 ------------------------------------------------------------
s = base("Como ler as imagens", { tag: "I" });
const leg = [["Verde-escuro", "fundo do vale", "2F6B3F"], ["Marrom e branco", "morros", "8B6B4A"], ["Azul", "água de hoje", "2E78C7"], ["Laranja", "área urbanizada", "E07A2F"], ["Roxo", "estimativa de Piraju", C.purple], ["Vermelho", "mancha do PAE de Jurumirim", "C0392B"]];
leg.forEach((l, i) => {
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.35 + i * 0.6, w: 0.4, h: 0.4, fill: { color: l[2] }, line: { color: l[2] } });
  s.addText([{ text: l[0] + ": ", options: { bold: true } }, { text: l[1] }], { x: 1.05, y: 1.35 + i * 0.6, w: 3.4, h: 0.4, fontFace: BF, fontSize: 14, color: C.ink, valign: "middle", margin: 0, isTextBox: true });
});
para(s, "Altura exagerada 4× para o relevo aparecer.", 0.5, 4.95, 4, 0.25, 11);
fit(s, "relevo_piraju.png", 4.6, 1.2, 5.0, 3.9, "Relevo de Piraju");
s.addNotes("Explique cada cor. Destaque que o exagero vertical de 4 vezes é só para visualização. Perfil: leigo e morador.");

// 5 ------------------------------------------------------------
s = base("O que o PAE de Jurumirim mostra", { tag: "D" });
stat(s, 0.5, 1.4, 2.8, "30,4 km²", "área da mancha da ruptura (mapa do PAE)");
stat(s, 3.6, 1.4, 2.8, "5,3 %", "do município de Piraju, quase tudo rural", C.green);
stat(s, 6.7, 1.4, 2.8, "1 h 59", "para a onda chegar à barragem de Piraju", C.orange);
para(s, "Origem: mapa e tabelas do PAE de Jurumirim (p. 38). Cenário hipotético com a barragem rompendo no nível 568,00 m.", 0.5, 3.3, 9, 1, 16);
s.addNotes("Todos os números vêm do PAE (derivados da mancha oficial georreferenciada). Cenário hipotético, não previsão.");

// 6 ------------------------------------------------------------
s = base("A cidade e a mancha", { tag: "D" });
fit(s, "3d_corredor.png", 0.4, 1.2, 5.6, 3.8, "Vista 3D do corredor");
stat(s, 6.3, 1.4, 3.2, "2,0 km", "da mancha até a maior área urbanizada");
stat(s, 6.3, 3.0, 3.2, "0,04 %", "da área urbanizada tocada (3.326 m², duas áreas pequenas)", C.orange);
s.addNotes("Área urbanizada: IBGE 2019, que não é o perímetro legal da cidade. Diga isso em voz alta.");

// 7 ------------------------------------------------------------
s = base("E se fosse a barragem de Piraju?", { tag: "O" });
bullets(s, ["O PAE de Piraju não traz o mapa da mancha nos PDFs.", "Traz tabelas: altura da água, velocidade e tempo em cada seção do rio, a cerca de 9,7 km de extensão (ZAS).", "Traz também 84 edificações na zona de autossalvamento.", "Sem mapa oficial, só dá para fazer uma estimativa, e ela precisa estar bem rotulada."], 0.5, 1.4, 9, 3.5, 18);
s.addNotes("Oficial versus estimativa. O mapa de ruptura de Piraju não existe nos PDFs obtidos; tudo o que vem a seguir é estimativa.");

// 8 ------------------------------------------------------------
s = base("Estimativa para Piraju", { tag: "E" });
fit(s, "relevo_piraju.png", 0.4, 1.2, 4.6, 3.9, "Estimativa em roxo sobre o relevo de Piraju");
stat(s, 5.3, 1.3, 4.2, "≈ 11,5 km²", "área estimada (roxo)", C.purple);
stat(s, 5.3, 2.75, 2.0, "≈ 1 %", "da área urbanizada", C.purple);
stat(s, 7.5, 2.75, 2.0, "17 min", "para a água ir 9 km", C.purple);
para(s, "Método: preencher o terreno até a altura de água informada no PAE. Não é o mapa oficial nem simulação.", 5.3, 4.25, 4.2, 0.9, 12.5);
s.addNotes("Rótulo ESTIMATIVA EXPLORATÓRIA. A estimativa foi comparada com a Figura 17 do PAE: cobre 94,6% dela. Isso mede cobertura, não excesso.");

// 9 ------------------------------------------------------------
s = base("Até onde a água chegaria?", { tag: "E" });
stat(s, 0.5, 1.4, 4.2, "56 m", "além da margem normal do rio, em média (mediana)", C.purple);
stat(s, 5.3, 1.4, 4.2, "161 m", "além da margem em 9 de cada 10 pontos", C.purple);
para(s, "Ou seja: a água se espalha para os lados, mas a maior parte fica perto do rio.", 0.5, 3.3, 9, 1, 18);
s.addNotes("Medido em cortes perpendiculares ao eixo do rio. O eixo vem do OpenStreetMap, então é ilustração.");

// 10 -----------------------------------------------------------
s = base("Altos e baixos da cidade", { tag: "E" });
fit(s, "relevo_piraju.png", 5.3, 1.2, 4.3, 3.9, "Relevo de Piraju");
stat(s, 0.5, 1.3, 4.5, "491–653 m", "altitude do terreno na cidade");
stat(s, 0.5, 2.8, 2.1, "≈ 517 m", "altura da água nessa região", C.purple);
stat(s, 2.9, 2.8, 2.1, "3,3 %", "da área urbana está abaixo disso", C.orange);
para(s, "Estar abaixo da altura não significa que a água chegaria lá: o terreno precisa estar conectado ao rio.", 0.5, 4.3, 4.6, 0.8, 12.5);
s.addNotes("Teto sem conexão hidráulica. Resolução do relevo: 30 metros.");

// 11 -----------------------------------------------------------
s = base("E a minha casa?", { tag: "O" });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.4, w: 9, h: 2.2, fill: { color: C.ice }, line: { color: C.orange, width: 3 }, rectRadius: 0.12 });
s.addText("Este projeto não diz se uma casa, rua ou rota seria atingida.", { x: 0.8, y: 1.5, w: 8.4, h: 1.0, fontFace: HF, fontSize: 24, bold: true, color: C.navy, margin: 0, isTextBox: true, valign: "middle" });
s.addText("O relevo tem 30 m de resolução: é grosso demais para decidir sobre um endereço.", { x: 0.8, y: 2.55, w: 8.4, h: 0.8, fontFace: BF, fontSize: 16, color: C.ink, margin: 0, isTextBox: true, valign: "top" });
bullets(s, ["Procure a Defesa Civil do município.", "Consulte o PAE oficial e conheça a sua rota de fuga e os sinais de alerta."], 0.5, 3.9, 9, 1.2, 17);
s.addNotes("Mensagem central para o morador. Nunca afirmar 'sua casa está segura' ou 'em risco'.");

// 12 -----------------------------------------------------------
s = base("Como sabemos? O método", { tag: "D" });
const cards = [["0,47 m", "erro ao posicionar o mapa de Jurumirim (36 pontos)"], ["2 escalas", "tabelas de Piraju lidas por OCR, sem divergência"], ["94,6 %", "da mancha de referência coberta pela estimativa"]];
cards.forEach((c, i) => stat(s, 0.5 + i * 3.1, 1.4, 2.9, c[0], c[1]));
para(s, "Limites honestos: a leitura por OCR ainda não foi revisada por um engenheiro; a estimativa mede cobertura, não excesso.", 0.5, 3.5, 9, 1, 16);
s.addNotes("Perfil engenheiro. Georreferência e vetorização têm erro de poucos metros. Cite o relatório de validação.");

// 13 -----------------------------------------------------------
s = base("A força da água", { tag: "D" });
stat(s, 0.5, 1.4, 4.2, "5,9×", "pressão dinâmica da ruptura de Piraju vs. cheia natural (mediana)", C.orange);
stat(s, 5.3, 1.4, 4.2, "85 × 29 kPa", "ruptura vs. cheia natural no ponto mais forte");
para(s, "Pressão dinâmica = ½ · densidade · velocidade². São valores máximos no canal do rio (modelo do PAE), não no terreno junto às casas.", 0.5, 3.3, 9, 1, 16);
s.addNotes("Correção importante: a razão mediana é 5,9 vezes, não 3 vezes. Valores no canal, não no terreno.");

// 14 -----------------------------------------------------------
s = base("O que ninguém sabe", { tag: "O" });
const unk = [["Cascata", "Os PAEs estudam cada barragem isoladamente. Nenhum estudo cobre a ruptura em cadeia."], ["Duração", "Quanto tempo a água ficaria? Os documentos não trazem a descida do nível."], ["Mapa de Piraju", "A mancha oficial de ruptura não está nos PDFs. Pedir à empresa."]];
unk.forEach((u, i) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5 + i * 3.1, y: 1.4, w: 2.9, h: 2.9, fill: { color: C.ice }, line: { color: C.ice }, rectRadius: 0.12 });
  s.addText(u[0], { x: 0.65 + i * 3.1, y: 1.55, w: 2.6, h: 0.5, fontFace: HF, fontSize: 20, bold: true, color: C.orange, margin: 0, isTextBox: true });
  s.addText(u[1], { x: 0.65 + i * 3.1, y: 2.15, w: 2.6, h: 2.0, fontFace: BF, fontSize: 15, color: C.ink, margin: 0, valign: "top", isTextBox: true });
});
para(s, "Essas lacunas são os próximos passos, não falhas escondidas.", 0.5, 4.5, 9, 0.5, 15);
s.addNotes("Cascata permanece 'não modelada'. O encadeamento no dashboard é só uma hipótese de relógios.");

// 15 -----------------------------------------------------------
s = base("Confiabilidade e limites", { tag: "D" });
bullets(s, ["Mais de 100 testes automáticos; tudo é reprodutível com um comando.", "As falhas que encontramos estão no relatório de validação (VALIDATION_REPORT.md).", "As fontes se contradizem em alguns números, por exemplo a vazão do vertedouro (2.621 × 2.594 m³/s); mostramos as duas.", "Seções de Piraju no mapa são ilustração; OCR sem revisão de engenheiro.", "Nada aqui é probabilidade de ruptura nem classificação de segurança."], 0.5, 1.35, 9, 3.7, 17);
s.addNotes("Cite as falhas encontradas. Transparência é parte da confiança.");

// 16 -----------------------------------------------------------
s = base("Sobre o autor");
s.addImage({ path: AUTOR, x: 0.5, y: 1.3, w: 2.4, h: 3.0, altText: "Foto de Renan Cunha de Oliveira" });
s.addText("Renan Cunha de Oliveira", { x: 3.3, y: 1.3, w: 6.2, h: 0.5, fontFace: HF, fontSize: 24, bold: true, color: C.navy, margin: 0, isTextBox: true });
s.addText("Engenheiro de IA e Machine Learning · fundador da Nexus Sight", { x: 3.3, y: 1.8, w: 6.2, h: 0.4, fontFace: BF, fontSize: 14, color: C.teal, margin: 0, isTextBox: true });
bullets(s, ["Visão computacional, agentes de IA e LLMs.", "AgTech: clima, satélite, terreno, rebanho e daninhas.", "RetailTech: câmeras que viram indicadores.", "Este projeto: estudo pessoal e independente."], 3.3, 2.35, 6.2, 2.4, 16);
s.addText("github.com/RenanCOliveira93", { x: 0.5, y: 4.5, w: 4, h: 0.3, fontFace: BF, fontSize: 12, color: C.mute, margin: 0, isTextBox: true });
s.addNotes("Mais detalhes na página 'Sobre o autor' do dashboard.");

// 17 -----------------------------------------------------------
s = base("Fontes e próximos passos", { dark: true });
bullets(s, ["PAE UHE Jurumirim (CTG) · PAE UHE Piraju rev. 5, out/2025 e PSB (CBA) · PAE UHE Paranapanema (Enel)", "IBGE (municípios e áreas urbanizadas 2019) · Copernicus GLO-30 · OpenStreetMap", "Próximo: pedir à CBA e à CTG o mapa de ruptura de Piraju e os hidrogramas", "Código, dados e documentação: github.com/RenanCOliveira93/Jurumirim-Flood_Explorer"], 0.5, 1.35, 9, 3.4, 16, C.white);
s.slideNumber = undefined;
s.addNotes("Referências completas em docs/DOCUMENTACAO.md. Confirmar com a CBA se o PSB (sigilo: interno) pode ser citado em público.");
// cores do texto em slide escuro
s.background = { color: C.navy };

pres.writeFile({ fileName: path.join(__dirname, "Jurumirim_Flood_Explorer.pptx") }).then((f) => console.log("ok", f));
