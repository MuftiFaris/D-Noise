'use strict';
// Plotting only: all pixel statistics and quality metrics come from manual Python loops.
const seriesNames=['Citra asli','Citra noisy',...labels];
const chartSelection={profile:'all',histogram:'all'};

function getFilteredSeries(series,filterVal){
  if(!filterVal||filterVal==='all')return series;
  const match=series.filter(s=>String(s.key)===String(filterVal));
  return match.length?match:series;
}

function analysisSeries(){
  const s=state.session;
  return [
    {key:0,label:seriesNames[0],image:s.original,analysis:s.analysis.original,metrics:s.baseline.original},
    {key:1,label:seriesNames[1],image:s.noisy,analysis:s.analysis.noisy,metrics:s.baseline.noisy},
    ...state.results.flatMap((r,i)=>r?[{key:i+2,label:labels[i],...r}]:[])
  ];
}

function seriesStyle(key){return `var(--series-${key})`;}
function dash(key){return ['','2 4','9 4','5 3 1 3','12 3 2 3'][key];}
function legend(series){
  return `<ul class="chart-legend">${series.map(s=>`<li data-key="${s.key}" tabindex="0"><svg width="28" height="12" aria-hidden="true"><path d="M0 6H28" stroke="${seriesStyle(s.key)}" stroke-width="2.5" stroke-dasharray="${dash(s.key)}"/></svg><span>${esc(s.label)}</span></li>`).join('')}</ul>`;
}

function getElements(parent,selector){
  if(parent&&typeof parent.querySelectorAll==='function'){
    return Array.from(parent.querySelectorAll(selector));
  }
  return [];
}

function lineChart(series,kind,id){
  const profile=kind==='profile', count=profile?series[0].analysis.profile.length:256;
  let maximum=profile?255:1;
  if(!profile)for(const s of series)for(const v of s.analysis.histogram)if(v>maximum)maximum=v;
  const left=62,top=22,width=600,height=210;
  const px=x=>left+x/Math.max(1,count-1)*width, py=y=>top+height-y/maximum*height;
  const title=profile?'Profil intensitas pada satu baris':'Histogram seluruh citra';
  let svg=`<svg class="analysis-chart" viewBox="0 0 690 286" role="img" aria-labelledby="${id}-title ${id}-desc"><title id="${id}-title">${title}</title><desc id="${id}-desc">${profile?'Intensitas 0 sampai 255 pada koordinat x yang sama.':'Jumlah piksel untuk setiap intensitas 0 sampai 255.'} ${esc(series.map(s=>s.label).join(', '))}.</desc>`;
  for(let i=0;i<5;i++){
    const v=maximum*i/4,y=py(v),x=(count-1)*i/4;
    svg+=`<path class="chart-grid" d="M${left} ${y}H${left+width}"/><text class="chart-tick" x="${left-9}" y="${y+4}" text-anchor="end">${num(v,0)}</text><text class="chart-tick" x="${px(x)}" y="${top+height+22}" text-anchor="middle">${num(x,0)}</text>`;
  }
  for(const s of series){
    const values=s.analysis[kind];
    const points=values.map((v,x)=>`${x?'L':'M'}${px(x).toFixed(2)} ${py(v).toFixed(2)}`).join(' ');
    svg+=`<g class="chart-series" data-key="${s.key}">`+
      `<path class="chart-hit-area" d="${points}" fill="none" stroke="transparent" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>`+
      `<path class="chart-curve chart-curve-${s.key}" data-key="${s.key}" d="${points}" fill="none" stroke="${seriesStyle(s.key)}" stroke-width="2" stroke-dasharray="${dash(s.key)}"/>`+
      `<title>${esc(s.label)}</title></g>`;
  }
  return svg+`<text class="chart-tick" x="${left}" y="13">${profile?'Intensitas':'Jumlah piksel'}</text><text class="chart-tick" x="362" y="278" text-anchor="middle">${profile?'Koordinat x (piksel)':'Intensitas grayscale'}</text></svg>`;
}

function metricChart(series,metric){
  const spec={mse:['MSE','Lebih kecil lebih baik'],psnr:['PSNR (dB)','Lebih besar lebih baik'],ssim:['SSIM','Lebih dekat ke 1 lebih baik']}[metric];
  let high=metric==='ssim'?1:Math.max(1,...series.map(s=>s.metrics[metric]===null?0:s.metrics[metric]));
  const low=metric==='ssim'?-1:0,position=v=>(v-low)/(high-low)*100,zero=position(0);
  return `<p class="metric-direction">${spec[0]} · ${spec[1]} · sumbu ${num(low,metric==='ssim'?1:0)}–${num(high,metric==='ssim'?1:2)}</p><div class="metric-bars">${series.map(s=>{
    const v=s.metrics[metric],end=v===null?zero:position(v);
    return `<div class="metric-row"><span>${esc(s.label)}</span><div class="metric-track"><span class="metric-zero" style="left:${zero}%"></span>${v===null?'':`<span class="metric-fill" style="left:${Math.min(zero,end)}%;width:${Math.abs(end-zero)}%;background:${seriesStyle(s.key)}"></span>`}</div><strong>${num(v,metric==='ssim'?5:3)}</strong></div>`;
  }).join('')}</div><p class="support">${metric==='psnr'?'∞ berarti MSE = 0; tidak digambar sebagai batang dengan panjang terbatas.':metric==='ssim'?'Skala −1 hingga 1. Garis tegak menandai nol.':'Acuan identik memiliki MSE = 0; batangnya memang tidak memiliki panjang.'}</p>`;
}

function chartOptions(series,currentVal){
  return `<option value="all" ${currentVal==='all'?'selected':''}>Semua grafik</option>`+
    series.map(s=>`<option value="${s.key}" ${String(s.key)===String(currentVal)?'selected':''}>${esc(s.label)}</option>`).join('');
}

function analysisMarkup(series,id){
  const profileFiltered=getFilteredSeries(series,chartSelection.profile);
  const histFiltered=getFilteredSeries(series,chartSelection.histogram);

  return `<div class="analysis-section"><h3>Analisis citra</h3>${legend(series)}`+
    `<div class="chart-header-row"><div><h4>Profil intensitas · y = ${series[0].analysis.profile_row}</h4>`+
    `<p class="support">Satu baris horizontal yang sama pada semua citra. Garis yang mendekati acuan menunjukkan intensitas lokal yang lebih mirip; ini bukan skor seluruh citra.</p></div>`+
    `<label class="chart-control">Filter grafik <select data-filter="profile" aria-label="Pilih grafik profil intensitas">${chartOptions(series,chartSelection.profile)}</select></label></div>`+
    `<div id="${id}-profile-chart">${lineChart(profileFiltered,'profile',id+'-profile')}</div>`+
    `<div class="chart-header-row"><div><h4>Distribusi intensitas</h4>`+
    `<p class="support">Histogram dihitung dari seluruh piksel. Sumbu x adalah intensitas, bukan posisi piksel. Histogram serupa belum menjamin struktur citra serupa.</p></div>`+
    `<label class="chart-control">Filter grafik <select data-filter="histogram" aria-label="Pilih grafik distribusi intensitas">${chartOptions(series,chartSelection.histogram)}</select></label></div>`+
    `<div id="${id}-histogram-chart">${lineChart(histFiltered,'histogram',id+'-histogram')}</div>`+
    `<h4>Kualitas terhadap citra asli</h4><label class="chart-control">Metrik <select data-metric="${id}"><option value="mse">MSE</option><option value="psnr">PSNR (dB)</option><option value="ssim">SSIM</option></select></label><div id="${id}-metrics">${metricChart(series,'mse')}</div></div>`;
}

function wireChart(containerId){
  const container=document.getElementById(containerId);
  if(!container)return;
  container.onmouseover=e=>{
    const seriesG=e.target.closest?e.target.closest('.chart-series'):null;
    if(!seriesG)return;
    const key=seriesG.getAttribute('data-key');
    const legendLis=getElements(document,'.chart-legend li');
    for(const li of legendLis){
      li.classList.toggle('legend-active',li.getAttribute('data-key')===key);
    }
  };
  container.onmouseout=e=>{
    const seriesG=e.target.closest?e.target.closest('.chart-series'):null;
    if(!seriesG)return;
    const legendLis=getElements(document,'.chart-legend li');
    for(const li of legendLis)li.classList.remove('legend-active');
  };
}

function wireLegend(target){
  const legendEl=target.querySelector('.chart-legend');
  if(!legendEl)return;
  legendEl.onmouseover=e=>{
    const li=e.target.closest?e.target.closest('li[data-key]'):null;
    if(!li)return;
    const key=li.getAttribute('data-key');
    highlightSeries(target,key);
  };
  legendEl.onmouseout=e=>{
    const li=e.target.closest?e.target.closest('li[data-key]'):null;
    if(!li)return;
    highlightSeries(target,null);
  };
}

function highlightSeries(target,key){
  const charts=getElements(target,'.analysis-chart');
  const seriesItems=getElements(target,'.chart-series');
  const legendItems=getElements(target,'.chart-legend li');
  if(key===null){
    for(const c of charts)c.classList.remove('has-active-series');
    for(const s of seriesItems)s.classList.remove('is-active');
    for(const l of legendItems)l.classList.remove('legend-active');
  }else{
    for(const c of charts)c.classList.add('has-active-series');
    for(const s of seriesItems)s.classList.toggle('is-active',s.getAttribute('data-key')===String(key));
    for(const l of legendItems)l.classList.toggle('legend-active',l.getAttribute('data-key')===String(key));
  }
}

function mountAnalysis(target,series,id){
  target.innerHTML=analysisMarkup(series,id);
  const profileSelect=target.querySelector('[data-filter="profile"]');
  if(profileSelect){
    profileSelect.onchange=e=>{
      chartSelection.profile=e.target.value;
      const filtered=getFilteredSeries(series,chartSelection.profile);
      const container=document.getElementById(id+'-profile-chart');
      if(container){
        container.innerHTML=lineChart(filtered,'profile',id+'-profile');
        wireChart(id+'-profile-chart');
      }
    };
  }
  const histSelect=target.querySelector('[data-filter="histogram"]');
  if(histSelect){
    histSelect.onchange=e=>{
      chartSelection.histogram=e.target.value;
      const filtered=getFilteredSeries(series,chartSelection.histogram);
      const container=document.getElementById(id+'-histogram-chart');
      if(container){
        container.innerHTML=lineChart(filtered,'histogram',id+'-histogram');
        wireChart(id+'-histogram-chart');
      }
    };
  }
  const metricSelect=target.querySelector('[data-metric]');
  if(metricSelect){
    metricSelect.onchange=e=>{
      const container=document.getElementById(id+'-metrics');
      if(container)container.innerHTML=metricChart(series,e.target.value);
    };
  }
  wireChart(id+'-profile-chart');
  wireChart(id+'-histogram-chart');
  wireLegend(target);
}

function renderCombinedAnalysis(){
  const selected=$('#analysis-method').value;
  const series=analysisSeries().filter(s=>s.key<2||selected==='all'||s.key===Number(selected)+2);
  if(chartSelection.profile!=='all'&&!series.some(s=>String(s.key)===chartSelection.profile)){
    chartSelection.profile='all';
  }
  if(chartSelection.histogram!=='all'&&!series.some(s=>String(s.key)===chartSelection.histogram)){
    chartSelection.histogram='all';
  }
  mountAnalysis($('#summary-analysis'),series,'summary');
}

function downloadChartCsv(){
  const series=analysisSeries(),rows=[['image','noise_percent','seed','series','data','row_y','x_or_intensity','value']];
  for(const s of series)for(const kind of ['profile','histogram'])for(let x=0;x<s.analysis[kind].length;x++)rows.push([state.session.image,state.session.noise,state.session.seed,s.label,kind,kind==='profile'?s.analysis.profile_row:'',x,s.analysis[kind][x]]);
  saveCsv(rows,'grafik');
}
