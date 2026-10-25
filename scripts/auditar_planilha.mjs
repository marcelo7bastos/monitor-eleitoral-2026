// Recalcula casos em memória; não salva nem altera o XLSX original.
import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const folder='evidencias/auditoria';
const inv=JSON.parse(await fs.readFile(`${folder}/inventario_formulas.json`,'utf8'));
const casos=JSON.parse(await fs.readFile(`${folder}/casos_equivalencia.json`,'utf8'));
const workbook=await SpreadsheetFile.importXlsx(await FileBlob.load('referencias/estimativa voto 2T.xlsx'));
const sheet=workbook.worksheets.getItem(inv.sheet);
// O importador não expande todas as fórmulas compartilhadas deste XLSX.
// Restaurar em memória as 118 fórmulas originais, lidas por openpyxl com expansão.
for(const [cell,formula] of Object.entries(inv.formulas)) sheet.getRange(cell).formulas=[[formula]];
const linhas=[];
for(const caso of casos){
 sheet.getRange('D2:H29').values=caso.entradas.map(row=>row.map(Number));
 workbook.recalculate();
 for(const [cell,python] of Object.entries(caso.python)){
  const engine=sheet.getRange(cell).values[0][0];
  const p=Number(python);
  const tolerance=(/^[IMN]/.test(cell)?1e-12:1e-6)+Math.abs(p)*1e-12;
  const delta=typeof engine==='number'?Math.abs(engine-p):null;
  const ok=delta!==null && delta<=tolerance;
  linhas.push({caso:caso.nome,celula:cell,python,planilha:engine,delta,tolerancia:tolerance,aprovado:ok});
 }
}
// Teste do denominador zero: Excel gera erro; Python sinaliza indisponível.
sheet.getRange('D2:H29').values=Array.from({length:28},()=>[0,0,0,0,100]);
workbook.recalculate();
const zero=sheet.getRange('I2:L2').values[0];
const resultado={motor:'@oai/artifact-tool 2.8.58+ (não Excel nativo)',formula_sha256:inv.sha256,
 formulas_restauradas:Object.keys(inv.formulas).length,comparacoes:linhas.length,
 falhas:linhas.filter(x=>!x.aprovado).length,denominador_zero:zero,linhas};
await fs.writeFile(`${folder}/equivalencia.json`,JSON.stringify(resultado,null,2));
const esc=v=>'"'+String(v??'').replaceAll('"','""')+'"';
await fs.writeFile(`${folder}/equivalencia.csv`,'\ufeff'+['caso;celula;python;planilha;delta;tolerancia;aprovado',...linhas.map(x=>Object.values(x).map(esc).join(';'))].join('\n'));
console.log(JSON.stringify({...resultado,linhas:undefined}));
if(resultado.falhas || !String(zero[0]).includes('DIV/0')) process.exitCode=1;
