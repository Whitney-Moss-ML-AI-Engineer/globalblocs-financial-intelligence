const API_BASE=window.GLOBALBLOCS_API_BASE||"http://127.0.0.1:8000";
const demo={kpis:{real_gdp_growth:{value:2.8,unit:"%"},inflation:{value:3.1,unit:"%"},unemployment:{value:4.2,unit:"%"},policy_rate:{value:4.25,unit:"%"},trade_balance:{value:-215,unit:"USD billions"}},observations:[{country:"United States",bloc:"North America",variable:"Real GDP Growth",period:"2025",value:2.8,unit:"%"},{country:"United States",bloc:"North America",variable:"Inflation Rate",period:"2025",value:3.1,unit:"%"},{country:"Germany",bloc:"European Union",variable:"Real GDP Growth",period:"2025",value:1.1,unit:"%"},{country:"Japan",bloc:"Asia-Pacific",variable:"Real GDP Growth",period:"2025",value:1.0,unit:"%"},{country:"Brazil",bloc:"Emerging Markets",variable:"Inflation Rate",period:"2025",value:4.8,unit:"%"},{country:"India",bloc:"Emerging Markets",variable:"Real GDP Growth",period:"2025",value:6.4,unit:"%"}]};
let state={overview:demo,observations:demo.observations,dataMode:"demo",api:null};
const venues=[["NYSE","United States","Equities"],["Nasdaq","United States","Equities"],["London Stock Exchange","United Kingdom","Equities"],["Deutsche Börse","Germany","Equities"],["Japan Exchange Group","Japan","Equities/Derivatives"],["Shanghai Stock Exchange","China","Equities"],["Hong Kong Exchanges and Clearing","Hong Kong","Equities/Derivatives"],["National Stock Exchange of India","India","Equities/Derivatives"],["B3","Brazil","Equities/Derivatives"],["Johannesburg Stock Exchange","South Africa","Equities/Derivatives"],["ASX","Australia","Equities/Derivatives"],["Singapore Exchange","Singapore","Equities/Derivatives"]];
const $=id=>document.getElementById(id);
async function get(path){const r=await fetch(API_BASE+path);if(!r.ok)throw Error(r.statusText);return r.json()}
function esc(v){return String(v??"").replace(/[&<>"]/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[m]))}
async function load(){try{state.overview=await get("/api/v1/overview");state.dataMode=state.overview.data_mode||"api";state.observations=await get("/api/v1/observations");setStatus("API connected • "+state.dataMode,"good")}catch(e){state.dataMode="demo";setStatus("Offline demo mode • connect FastAPI for repository data","warn")}render();loadContracts()}
function setStatus(text,kind){if($("status")){$("status").textContent=text;$("status").className="status "+kind}}
function render(){const k=state.overview.kpis||demo.kpis;[["gdp","real_gdp_growth"],["infl","inflation"],["unemp","unemployment"],["rate","policy_rate"],["trade","trade_balance"]].forEach(([id,key])=>{if($(id)){const x=k[key];$(id).textContent=x.unit==="USD billions"?"$"+x.value+"B":x.value+"%"}});const q=($("search")?.value||"").toLowerCase();if($("marketRows"))$("marketRows").innerHTML=venues.map(v=>"<tr><td>"+esc(v[0])+"</td><td>"+esc(v[1])+"</td><td>"+esc(v[2])+"</td></tr>").join("");if($("datarows"))$("datarows").innerHTML=state.observations.filter(r=>(r.country+" "+r.bloc+" "+r.variable+" "+r.period).toLowerCase().includes(q)).map(r=>"<tr><td>"+esc(r.country)+"</td><td>"+esc(r.bloc)+"</td><td>"+esc(r.variable)+"</td><td>"+esc(r.period)+"</td><td>"+esc(r.value)+esc(r.unit)+"</td></tr>").join("")}
function showTable(title,rows){if(!Array.isArray(rows)||!rows.length)return "<p class='note'>No results.</p>";const keys=Object.keys(rows[0]);return "<h3>"+esc(title)+"</h3><div class='tablewrap'><table><thead><tr>"+keys.map(k=>"<th>"+esc(k)+"</th>").join("")+"</tr></thead><tbody>"+rows.map(r=>"<tr>"+keys.map(k=>"<td>"+esc(typeof r[k]==="object"?JSON.stringify(r[k]):r[k])+"</td>").join("")+"</tr>").join("")+"</tbody></table></div>"}
function renderApiResult(data){state.api=data;const out=$("apiOutput");if(!out)return;const tab=document.querySelector(".tab.active")?.dataset.tab||"api-quality";let html="";if(tab==="api-quality")html="<h3>Data Quality / Provenance</h3><p>Rows: "+esc(data.row_count)+" • Columns: "+esc(data.column_count)+"</p>"+showTable("Data Dictionary",data.data_dictionary)+showTable("EDA Summary",Object.entries(data.eda||{}).map(([k,v])=>({metric:k,value:v})))+"<p class='note'>"+esc(JSON.stringify(data.provenance))+"</p>";else if(tab==="api-eda")html=showTable("Numeric Analytical Summary",data.analytical_summary)+showTable("Data Dictionary",data.data_dictionary);else if(tab==="api-transform")html=showTable("Transformation Audit",data.transformation_audit)+showTable("Silver Preview",data.silver_preview);else if(tab==="api-features")html=showTable("Feature Audit",data.feature_audit)+showTable("Feature Table",data.feature_table)+showTable("Feature Matrix",data.feature_matrix);else if(tab==="api-metrics")html=showTable("GlobalBLOCS Investment Metrics",data.investment_metrics||[]);else if(tab==="api-trend")html=showTable("Trend Intelligence",data.trend_summary);else if(tab==="api-viz")html="<div class='grid'><div class='card'><h3>Visualization Framework</h3><p>Use the API result to plot value history, returns, volatility, drawdown, volume/liquidity and comparative benchmarks. Product-specific views support duration/DV01, spreads, tranche sensitivity and derivatives payoff analysis.</p></div><div class='card'><h3>Intelligence Chain</h3><p>RAW → DATA QUALITY → ETL → SILVER → FEATURES → METRICS → TREND → MACRO / INDUSTRY / MARKET CONTEXT.</p></div></div>";else if(tab==="api-export")html="<button class='button primary' id='downloadApi'>Download Analysis JSON</button>";out.innerHTML=html;if($("downloadApi"))$("downloadApi").onclick=()=>downloadJson("globalblocs-api-analysis.json",data)}
async function loadContracts(){try{const d=await get("/api/v1/finance/api-contracts");if($("apiContract"))$("apiContract").innerHTML=d.contracts.map(x=>"<option value='"+esc(x.id)+"'>"+esc(x.provider)+"</option>").join("");if($("providerRows"))$("providerRows").innerHTML=d.contracts.map(x=>"<tr><td>"+esc(x.provider)+"</td><td>"+esc(x.canonical_domains.join(", "))+"</td><td>"+esc(x.auth)+"</td></tr>").join("")}catch(e){}}
async function runApi(){const endpoint=$("apiEndpoint").value.trim();if(!endpoint){alert("Enter an API endpoint.");return}let params={};try{params=JSON.parse($("apiParams").value||"{}")}catch(e){alert("Query Parameters JSON is invalid.");return}const op=$("featureOperation").value;const featureName=$("featureName").value.trim();const source=$("featureSource").value.trim();const features=source&&featureName?[{feature_name:featureName,source_column:source,operation:op,window:Number($("featureWindow").value||20),periods:Number($("featureWindow").value||1)}]:[];const body={provider:$("apiProvider").value,endpoint,method:$("apiMethod").value,auth_method:$("apiAuth").value,credential_name:$("apiCredentialName").value,credential_value:$("apiCredentialValue").value,params,feature_rules:features,transform_rules:[]};const button=$("runApi");button.disabled=true;button.textContent="Running ETL / EDA…";try{const r=await fetch(API_BASE+"/api/v1/finance/ingest-and-analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});const d=await r.json();if(!r.ok)throw Error(d.detail||"API request failed");renderApiResult(d.analysis);setStatus("Credentialed API analyzed • credentials not persisted","good")}catch(e){$("apiOutput").innerHTML="<p class='status warn'>"+esc(e.message)+"</p>"}finally{button.disabled=false;button.textContent="Test Connection + Ingest + ETL/EDA";}}
function downloadJson(name,obj){const blob=new Blob([JSON.stringify(obj,null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;a.click();URL.revokeObjectURL(a.href)}
document.querySelectorAll(".nav button").forEach(b=>b.onclick=()=>{document.querySelectorAll(".nav button").forEach(x=>x.classList.remove("active"));b.classList.add("active");document.querySelectorAll("main section").forEach(s=>s.hidden=s.id!==b.dataset.page);if(b.dataset.page==="api-intelligence"&&!state.api)loadContracts();if(b.dataset.page==="production")loadProductionCapabilities();if(b.dataset.page==="intelligence")loadIntelligenceWorkspace();if(b.dataset.page==="visualization")loadMetricVisualizationWorkspace()});
document.querySelectorAll(".tab").forEach(b=>b.onclick=()=>{document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));b.classList.add("active");if(state.api)renderApiResult(state.api)});
$("search")?.addEventListener("input",render);
$("runApi")?.addEventListener("click",runApi);$("runRisk")?.addEventListener("click",runRiskAnalytics);
$("loadContracts")?.addEventListener("click",loadContracts);
$("apiContract")?.addEventListener("change",async e=>{try{const d=await get("/api/v1/finance/api-contracts/"+e.target.value);$("apiProvider").value=d.provider}catch(err){}});
$("reset")?.addEventListener("click",()=>{$("search").value="";document.querySelectorAll("select").forEach(s=>s.selectedIndex=0);render()});
$("export")?.addEventListener("click",()=>downloadJson("globalblocs-dashboard-view.json",{data_mode:state.dataMode,observations:state.observations,api_analysis:state.api}));
load();loadRegistries();

async function loadRegistries(){try{const [m,cx,kb]=await Promise.all([get("/api/v1/finance/metrics"),get("/api/v1/finance/economic-concepts"),get("/api/v1/production/metrics/knowledge-base")]);if($("metricRows"))$("metricRows").innerHTML=(kb.metrics||[]).map(x=>"<tr><td>"+esc(x.id)+"</td><td>"+esc(x.name)+"</td><td>"+esc(x.category)+"</td></tr>").join("");const concepts=[...(cx.macro||[]),...(cx.micro||[])];if($("conceptSelect")){$("conceptSelect").innerHTML=concepts.map(x=>"<option value='"+esc(x.name)+"'>"+esc(x.name)+"</option>").join("");$("conceptSelect").addEventListener("change",loadConcept);loadConcept({target:$("conceptSelect")})}}catch(e){}}
async function loadConcept(e){const name=e.target.value;try{const d=await get("/api/v1/finance/concept-securities/"+encodeURIComponent(name));$("conceptSecurity").innerHTML=(d.securities||[]).map(x=>"<option>"+esc(x)+"</option>").join("")||"<option>No mapped securities</option>";$("conceptOutput").innerHTML="<p><b>Categories:</b> "+esc((d.categories||[]).join(", "))+"</p>"+showTable("Mapped U.S. Security Universe",(d.securities||[]).map(x=>({security:x}))) }catch(err){$("conceptOutput").innerHTML="<p class='status warn'>"+esc(err.message)+"</p>"}}


async function loadMetricVisualizationWorkspace(){
  try{
    const d=await get("/api/v1/production/metrics/knowledge-base");
    const metrics=d.metrics||[];
    const opts=metrics.map(m=>"<option value='"+esc(m.id)+"'>"+esc(m.id+" — "+m.name)+"</option>").join("");
    ["vizMetric","metricA","metricB"].forEach(id=>{if($(id))$(id).innerHTML=opts});
    await updateMetricVisualization();
    $("vizMetric")?.addEventListener("change",updateMetricVisualization);
    $("vizCategory")?.addEventListener("change",loadMetricVisualizationWorkspace);
    $("vizType")?.addEventListener("change",updateVisualizationExplanation);
    $("metricA")?.addEventListener("change",updateMetricComparison);
    $("metricB")?.addEventListener("change",updateMetricComparison);
    $("vizCompare")?.addEventListener("change",updateMetricComparison);
    $("vizMode")?.addEventListener("change",updateMetricComparison);
  }catch(e){if($("vizProfile"))$("vizProfile").innerHTML="<p class='status warn'>"+esc(e.message)+"</p>";}
}
async function updateMetricVisualization(){
  const id=$("vizMetric")?.value||1;
  try{
    const m=await get("/api/v1/production/metrics/knowledge-base/"+id);
    if($("vizProfile"))$("vizProfile").innerHTML="<p><b>"+esc(m.name)+"</b> • "+esc(m.category)+"</p><p>"+esc(m.definition)+"</p><p><b>Formula:</b> "+esc(m.formula)+"</p><p><b>Data:</b> "+esc(m.data_sources.join(", "))+"</p>";
    const p=await get("/api/v1/production/metrics/knowledge-base/"+id+"/visualization");
    const types=p.available||[];
    $("vizType").innerHTML=types.map(x=>"<option value='"+esc(x)+"'>"+esc(x)+(p.recommended.some(r=>r.type===x)?" ★ Recommended":"")+"</option>").join("");
    $("vizType").value=p.default||types[0];
    if($("vizWhy"))$("vizWhy").innerHTML=(p.recommended||[]).map(x=>"<p><b>"+esc(x.type)+"</b> — "+esc(x.reason)+"</p>").join("");
    updateVisualizationExplanation();
  }catch(e){$("vizProfile").innerHTML="<p class='status warn'>"+esc(e.message)+"</p>";}
}
function updateVisualizationExplanation(){
  const type=$("vizType")?.value||"line";
  const reasons={line:"Best for time-series trend inspection.",bar:"Best for discrete period or peer comparison.",area:"Emphasizes cumulative magnitude.",histogram:"Shows distribution shape.",box:"Shows median, spread and outliers.",violin:"Shows distribution shape and density.",scatter:"Shows relationships between two numeric variables.",heatmap:"Shows matrix-style relationships such as correlations.",waterfall:"Shows sequential contributions to a total.",candlestick:"Shows OHLC market movement.",drawdown:"Shows peak-to-trough losses.",forecast_interval:"Shows forecasts with uncertainty intervals.",actual_predicted:"Compares observed and model-predicted values.",roc:"Shows classifier discrimination across thresholds.",precision_recall:"Shows precision/recall tradeoffs.",confusion_matrix:"Shows actual versus predicted classes.",pca_projection:"Shows observations in principal-component space.",feature_importance:"Ranks model features by importance.",shap:"Shows feature contribution and direction."};
  if($("vizCanvas"))$("vizCanvas").innerHTML="<h4>"+esc(type)+"</h4><p>"+esc(reasons[type]||"Compatible visualization selected.")+"</p><p class='note'>Chart rendering is data-driven; this workspace does not restrict the user to the recommendation.</p>"; fetch(API_BASE+"/api/v1/production/evaluations/"+encodeURIComponent(type)).then(r=>r.json()).then(d=>{if($("vizEvaluation"))$("vizEvaluation").innerHTML=(d.evaluation_metrics||[]).map(x=>"<span class='badge'>"+esc(x)+"</span>").join(" ")||"Descriptive statistics";}).catch(()=>{});
}
function updateMetricComparison(){
  const a=$("metricA")?.selectedOptions[0]?.textContent||"Metric A";
  const b=$("metricB")?.selectedOptions[0]?.textContent||"Metric B";
  const mode=$("vizMode")?.value||"Single Chart";
  if($("vizCompareOutput"))$("vizCompareOutput").innerHTML="<p><b>"+esc(mode)+"</b>: "+esc(a)+" ↔ "+esc(b)+"</p><p class='note'>Metric-to-metric, peer, benchmark, and SEC-vs-yfinance comparison modes use the same visualization engine when the underlying data is compatible.</p>";
}
\nasync function loadIntelligenceWorkspace(){
  try{
    const [domains,blocs,recession,providers,metrics]=await Promise.all([
      get("/api/v1/production/intelligence/domains"),
      get("/api/v1/production/intelligence/blocs"),
      get("/api/v1/production/intelligence/recession-indicators"),
      get("/api/v1/production/intelligence/research-providers"),
      get("/api/v1/production/intelligence/metrics")
    ]);
    if($("intelligenceDomains")) $("intelligenceDomains").innerHTML=showTable("Domains",(domains.domains||[]).map(x=>({domain:x.name,focus:x.focus,metrics:(x.metrics||[]).join(", ")})));
    if($("intelligenceBlocs")) $("intelligenceBlocs").innerHTML=showTable("Economic BLOCs",Object.entries(blocs.blocs||{}).map(([name,members])=>({name,members:(members||[]).join(", ")})))+showTable("Regions",Object.entries(blocs.regions||{}).map(([name,members])=>({name,members:members?(members||[]).join(", "):"Global"})));
    if($("recessionIndicators")) $("recessionIndicators").innerHTML=showTable("Indicators",Object.entries(recession.indicators||{}).map(([name,code])=>({indicator:name,source_code:code})));
    if($("intelligenceProviders")) $("intelligenceProviders").innerHTML=showTable("Providers",(providers.providers||[]).map(x=>({provider:x.name,category:x.category,access:x.access,priority:x.priority})));
    if($("intelligenceMetrics")) $("intelligenceMetrics").innerHTML=showTable("50 Investment Metrics",(metrics.metrics||[]).map(x=>({id:x.ID,metric:x.Metric,category:x.Category,definition:x.Definition})));
    setStatus("Financial intelligence workspace connected","good");
  }catch(e){setStatus("Financial intelligence workspace unavailable","warn");}
}
async function runRiskAnalytics(){
  try{
    const prices=($("riskPrices").value||"").split(",").map(Number).filter(Number.isFinite);
    const r=await fetch(API_BASE+"/api/v1/production/intelligence/risk",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prices})});
    const d=await r.json(); if(!r.ok) throw Error(d.detail||"Risk analysis failed");
    $("riskOutput").innerHTML=showTable("Risk Summary",Object.entries(d.risk_summary||{}).map(([metric,value])=>({metric,value})));
  }catch(e){$("riskOutput").innerHTML="<p class='status warn'>"+esc(e.message)+"</p>";}
}
async function loadProductionCapabilities(){
  try{
    const [scripts,sources,models]=await Promise.all([
      get("/api/v1/production/scripts"),
      get("/api/v1/production/sources"),
      get("/api/v1/production/models")
    ]);
    if($("productionScripts")) $("productionScripts").innerHTML=showTable("Production Python Modules",(scripts.scripts||[]).map(x=>({area:x.area,module:x.path,status:x.status})));
    if($("productionSources")) $("productionSources").innerHTML=showTable("Registered Data Sources",(sources.sources||[]).map(x=>({provider:x.provider,domain:x.domain,auth:x.auth,format:x.format})));
    if($("productionModels")) $("productionModels").innerHTML=showTable("Model Families",Object.entries(models.models||{}).map(([family,items])=>({family,models:items.join(", ")})));
    if($("productionStatus")) setStatus("Production script registry connected","good");
  }catch(e){if($("productionStatus")) $("productionStatus").innerHTML="<p class='status warn'>"+esc(e.message)+"</p>";}
}
