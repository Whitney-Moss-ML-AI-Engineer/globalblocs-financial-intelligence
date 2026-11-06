/* SEC EDGAR annual company-facts panel for the Energy workspace. */
(function(){
 const API=window.GLOBALBLOCS_API_BASE||(location.protocol==="http:"||location.protocol==="https:"?location.origin:"http://127.0.0.1:8000");
 const $=id=>document.getElementById(id);
 const esc=v=>String(v??"—").replace(/[&<>"]/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[m]));
 const labels={revenue:"Revenue",operating_income:"Operating income",net_income:"Net income",assets:"Total assets",cash_from_operations:"Cash from operations",capital_expenditures:"Capital expenditures (reported cash outflow)",long_term_debt:"Long-term debt (reported concepts)",equity:"Stockholders' equity"};
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
   $("energySecStatus").textContent="SEC EDGAR facts retrieved • "+rows.length+" annual observations • source periods and filing references retained.";
  }catch(e){$("energySecStatus").textContent=e.message;}
 }
 $("energyLoadSec")?.addEventListener("click",load);
})();
