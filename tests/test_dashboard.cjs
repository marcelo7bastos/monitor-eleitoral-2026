const test=require('node:test');
const assert=require('node:assert/strict');
const {numero,pontos,periodo,status,parcial}=require('../site/dashboard.js');
test('ausência não se torna zero eleitoral',()=>{assert.equal(numero(null),null);assert.equal(numero('0'),0);});
test('histórico não inventa pontos, filtra intervalo e ausência de apuração',()=>{
 const h=[{coleta_utc:'2026-10-25T19:00:00Z',vistas:{AC:{lula:40,flavio:60}}},{coleta_utc:'2026-10-25T21:00:00Z',vistas:{AC:{lula:null,flavio:null}}}];
 assert.equal(pontos(h,'AC','oficial','2026-10-25T20:00:00Z').length,0);
 h.push({coleta_utc:'2026-10-25T21:10:00Z',vistas:{AC:{lula:'40.1',flavio:'59.9'}}});
 assert.equal(pontos(h,'AC','oficial','2026-10-25T20:00:00Z').length,1);
});
test('eixo estende depois de meia-noite sem apagar o começo',()=>{
 const [a,b]=periodo('2026-10-25T17:00:00-03:00','2026-10-26T00:00:00-03:00',Date.parse('2026-10-26T00:20:00-03:00'),[]);
 assert.equal(a,Date.parse('2026-10-25T17:00:00-03:00'));assert.equal(b,Date.parse('2026-10-26T00:20:00-03:00'));
});
test('falha, indisponibilidade e atraso aparecem no painel',()=>{
 const agora=Date.parse('2026-10-25T22:00:00Z');
 assert.match(status({apurado:true},{status:'erro'},'2026-10-25T21:59:00Z',agora).texto,/Falha na coleta/);
 assert.match(status({apurado:true},{status:'sucesso'},'2026-10-25T21:00:00Z',agora).texto,/Coleta desatualizada/);
 assert.match(status({apurado:false},{status:'sucesso'},'2026-10-25T21:59:00Z',agora).texto,/Sem apuração/);
 assert.match(status(null,{},null,agora).texto,/Indisponível/);
});
test('estimativa parcial do Brasil sempre informa N de 28',()=>{
 assert.equal(parcial({parcial:true,ufs_com_dados:5,ufs_total:28}),'parcial · 5 de 28 UFs');
 assert.equal(parcial({parcial:false,ufs_com_dados:28,ufs_total:28}),'');
 assert.equal(parcial(null),'');
});
test('placar mostra diferença estimativa − oficial com sinal e sem inventar valor',()=>{
 const {delta,pp}=require('../site/dashboard.js');
 assert.equal(pp(delta('67.05','65.36')),'+1,69 p.p.');
 assert.equal(pp(delta('32.95','34.64')),'−1,69 p.p.');
 assert.equal(delta(null,'65.36'),null);
 assert.equal(pp(null),'');
});
test('escala padrão 30–70% amplia em passos de 10 sem esconder pontos',()=>{
 const {escala}=require('../site/dashboard.js');
 assert.deepEqual(escala(['65.36','34.64']),{lo:30,hi:70,ampliada:false});
 assert.deepEqual(escala(['72.1','27.9']),{lo:20,hi:80,ampliada:true});
 assert.deepEqual(escala(['100','0']),{lo:0,hi:100,ampliada:true});
 assert.deepEqual(escala([]),{lo:30,hi:70,ampliada:false});
});
