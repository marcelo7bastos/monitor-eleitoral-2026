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
test('margem de cenário: faixas 25/50/75, valor do piso da faixa e limites exatos',()=>{
 const {margemCenario,DELTA_CENARIO}=require('../site/dashboard.js');
 assert.equal(DELTA_CENARIO,10);
 assert.equal(margemCenario(null),null);assert.equal(margemCenario('x'),null);assert.equal(margemCenario(undefined),null);
 for(const c of [0,1,24.99])assert.equal(margemCenario(c).estado,'inicial');
 assert.equal(margemCenario(24.99).margem,undefined);
 for(const [c,estado,m] of [[25,'ampla',7.5],[49.99,'ampla',7.5],[50,'moderada',5],[74.99,'moderada',5],[75,'estreita',2.5],[99.99,'estreita',2.5]]){
  const r=margemCenario(c);assert.equal(r.estado,estado,String(c));assert.equal(r.margem,m,String(c));}
 assert.equal(margemCenario(100).estado,'completa');assert.equal(margemCenario(100).margem,undefined);
 assert.equal(margemCenario('62.5').estado,'moderada');
 assert.equal(margemCenario(80,true).estado,'sem');
});
test('selo de margem não aparece sem estimativa e nunca derruba o placar',()=>{
 const {seloMargem,placar}=require('../site/dashboard.js');
 assert.equal(seloMargem(undefined,undefined),'');
 assert.equal(seloMargem({cobertura:60},{lula:null}),'');
 assert.equal(seloMargem({cobertura:null},{lula:'50'}),'');
 assert.equal(seloMargem(null,{lula:'50'}),'');
 const h=seloMargem({cobertura:60},{lula:'50',flavio:'50'});
 assert.match(h,/± 5,0 p\.p\./);assert.match(h,/data-method="margem"/);assert.match(h,/moderada/);
 assert.match(seloMargem({cobertura:10},{lula:'50'}),/Apuração inicial · sem margem/);
 assert.match(seloMargem({cobertura:100},{lula:'50'}),/Apuração completa/);
 assert.match(seloMargem({cobertura:90},{lula:'50',parcial:true,ufs_com_dados:20,ufs_total:28}),/Sem margem/);
});
test('placar renderiza com e sem dados e inclui o selo de margem quando há estimativa',()=>{
 const {placar}=require('../site/dashboard.js');
 assert.doesNotThrow(()=>placar(undefined));
 assert.doesNotThrow(()=>placar({cobertura:null,estimativa:null}));
 assert.doesNotMatch(placar(undefined),/margem-btn/);
 const v={lula:'48.3',flavio:'51.7',votos_lula:1,votos_flavio:2,cobertura:62,estimativa:{lula:'48.9',flavio:'51.1',votos_lula:1,votos_flavio:2}};
 assert.match(placar(v),/margem-btn moderada/);
});
test('apuração por região soma as UFs, não arredonda para 100% antes da hora e avisa dado ausente',()=>{
 const {coberturaGrupo,seloRegiao}=require('../site/dashboard.js');
 const v={AC:{totalizadas:100,secoes:1000},AP:{totalizadas:'50',secoes:'500'},AM:{totalizadas:0,secoes:1500}};
 const r=coberturaGrupo(['AC','AP','AM'],v);
 assert.equal(r.st,150);assert.equal(r.ts,3000);assert.equal(r.p,5);assert.equal(r.rotulo,'5%');assert.equal(r.incompleto,false);
 assert.equal(coberturaGrupo(['AC'],{AC:{totalizadas:1,secoes:1000}}).rotulo,'<1%');
 assert.equal(coberturaGrupo(['AC'],{AC:{totalizadas:0,secoes:1000}}).rotulo,'0%');
 assert.equal(coberturaGrupo(['AC'],{AC:{totalizadas:999,secoes:1000}}).rotulo,'99%');
 assert.equal(coberturaGrupo(['AC'],{AC:{totalizadas:1000,secoes:1000}}).rotulo,'100%');
 const falta=coberturaGrupo(['AC','SE'],{AC:{totalizadas:500,secoes:1000}});
 assert.equal(falta.rotulo,'50%');assert.equal(falta.incompleto,true);
 assert.equal(coberturaGrupo(['SE'],{}).p,null);assert.equal(coberturaGrupo(['SE'],undefined).rotulo,'—');
 assert.match(seloRegiao('Norte',['AC'],{AC:{totalizadas:20,secoes:100}}),/<b>20%<\/b>/);
 assert.match(seloRegiao('Norte',['AC'],{AC:{totalizadas:20,secoes:100}}),/--p:20\.00/);
 assert.match(seloRegiao('Norte',['SE'],{}),/reg-cob vazio/);
});
