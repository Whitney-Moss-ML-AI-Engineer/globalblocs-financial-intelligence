/* SEC EDGAR annual company-facts panel for the Energy workspace. */
(function(){
 const API=window.GLOBALBLOCS_API_BASE||(location.protocol==="http:"||location.protocol==="https:"?location.origin:"http://127.0.0.1:8000");
 const $=id=>document.getElementById(id);
 const esc=v=>String(v??"—").replace(/[&<>"]/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[m]));
 const labels={revenue:"Revenue",operating_income:"Operating income",net_income:"Net income",assets:"Total assets",cash_from_operations:"Cash from operations",capital_expenditures:"Capital expenditures (reported cash outflow)",long_term_debt:"Long-term debt (reported concepts)",equity:"Stockholders' equity",cash_and_equivalents:"Cash and cash equivalents"};
 const fmt=v=>typeof v==="number"?new Intl.NumberFormat("en-US",{maximumFractionDigits:0}).format(v):v;
 async function load(){
  const ticker=$("energySecTicker").value.trim().toUpperCase();
  if(!ticker){$("energySecStatus").textContent="Enter a company ticker.";return;}
  $("energySecStatus").textContent="Requesting annual SEC company facts…";
  $("energySecFinancials").innerHTML="";
  try{
   const response=await fetch(API+"/api/v1/energy/sec/company/"+encodeURIComponent(ticker)+"/facts");
   const d=await response.json();if(!response.ok)throw Error(d.detail||response.statusText);
   $("energySecCompany").textContent=d.company_name+" • ticker "+d.ticker+" • CIK "+d.cik+" • retrieved "+d.retrieved_at;
   const financials=d.financials||{};
   const rows=[];
   Object.entries(labels).forEach(([key,label])=>(financials[key]||[]).forEach(x=>rows.push({metric:label,...x})));
   if(!rows.length){$("energySecFinancials").innerHTML="<p class='note'>No matching annual XBRL facts were found for this issuer using the current standard-tag mapping.</p>";}
   else{
    const cols=[["metric","Financial metric"],["fiscal_year","Fiscal year"],["period_end","Period end"],["value","Reported value"],["unit","Unit"],["form","Filing"],["filed","Filed date"],["concept","XBRL concept"]];
    $("energySecFinancials").innerHTML="<div class='tablewrap'><table><thead><tr>"+cols.map(c=>"<th>"+c[1]+"</th>").join("")+"</tr></thead><tbody>"+rows.sort((a,b)=>String(b.period_end).localeCompare(String(a.period_end))).map(row=>"<tr>"+cols.map(c=>"<td>"+esc(c[0]==="value"?fmt(row[c[0]]):row[c[0]])+"</td>").join("")+"</tr>").join("")+"</tbody></table></div>";
   }
   $("energySecSources").innerHTML="Sources: <a href='"+esc(d.source_url)+"' target='_blank' rel='noopener'>SEC Company Facts JSON</a> · <a href='"+esc(d.filing_source_url)+"' target='_blank' rel='noopener'>SEC filings</a><p class='note'>"+(d.limitations||[]).map(esc).join("<br>")+"</p>";
   try{
    const ar=await fetch(API+"/api/v1/energy/analytics/company/"+encodeURIComponent(ticker));
    const ad=await ar.json();if(!ar.ok)throw Error(ad.detail||ar.statusText);
    const labels={revenue_growth:"Revenue growth",operating_margin:"Operating margin",net_margin:"Net margin",free_cash_flow:"Free cash flow",free_cash_flow_margin:"FCF margin",cash_conversion:"Cash conversion",return_on_assets:"Return on assets",return_on_equity:"Return on equity",long_term_debt_to_assets:"Long-term debt / assets",long_term_debt_to_equity:"Long-term debt / equity",net_debt:"Net debt",capital_expenditure_intensity:"Capex / revenue"};
    const percentages=new Set(["revenue_growth","operating_margin","net_margin","free_cash_flow_margin","cash_conversion","return_on_assets","return_on_equity","long_term_debt_to_assets","long_term_debt_to_equity","capital_expenditure_intensity"]);
    const dollars=new Set(["free_cash_flow","net_debt"]);
    const rowsOut=[];
    (ad.periods||[]).forEach(p=>Object.keys(labels).forEach(key=>{
      const value=p[key];let display="—",unit=percentages.has(key)?"%":dollars.has(key)?"USD":"ratio";
      if(value!==null&&value!==undefined)display=percentages.has(key)?(value*100).toFixed(2)+"%":dollars.has(key)?fmt(value):Number(value).toFixed(3);
      rowsOut.push({metric:labels[key],period:p.period_end,value:display,unit});
    }));
    $("energySecAnalytics").innerHTML=rowsOut.length?"<div class='tablewrap'><table><thead><tr><th>Metric</th><th>Period end</th><th>Value</th><th>Unit</th></tr></thead><tbody>"+rowsOut.map(x=>"<tr><td>"+esc(x.metric)+"</td><td>"+esc(x.period)+"</td><td>"+esc(x.value)+"</td><td>"+esc(x.unit)+"</td></tr>").join("")+"</tbody></table></div><p class='note'>"+esc(ad.methodology.free_cash_flow)+" "+esc(ad.methodology.return_on_assets)+" "+esc(ad.methodology.limitations)+"</p>":"<p class='note'>No derived ratios available; required SEC facts may be missing.</p>";
   }catch(e){$("energySecAnalytics").textContent="Derived analytics unavailable: "+e.message;}
   $("energySecStatus").textContent="SEC EDGAR facts retrieved • "+rows.length+" annual observations • derived metrics loaded where source facts permit.";
  }catch(e){$("energySecStatus").textContent=e.message;}
 }
 $("energyLoadSec")?.addEventListener("click",load);
})();
