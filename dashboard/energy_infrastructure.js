/* PHMSA public source directory and FERC catalog discovery. */
(function(){
 const API=window.GLOBALBLOCS_API_BASE||(location.protocol==="http:"||location.protocol==="https:"?location.origin:"http://127.0.0.1:8000");
 const $=id=>document.getElementById(id);
 const req=async path=>{const r=await fetch(API+path);const d=await r.json();if(!r.ok)throw Error(d.detail||r.statusText);return d;};
 const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
 function renderSources(rows){
  $("energyInfrastructureSources").innerHTML=rows.map(x=>"<div class='infra-source'><div><strong>"+esc(x.name)+"</strong><span class='infra-agency'>"+esc(x.agency)+" · "+esc(x.access)+"</span></div><p>"+esc(x.coverage)+"</p><small>"+esc(x.limitations)+"</small><a href='"+esc(x.url)+"' target='_blank' rel='noopener noreferrer'>Open official source</a></div>").join("");
 }
 async function loadSources(){
  const el=$("energyInfrastructureSources");el.textContent="Loading PHMSA source directory…";
  try{const d=await req("/api/v1/energy/infrastructure/sources");renderSources(d.phmsa_sources);const notice=document.createElement("p");notice.className="note";notice.textContent=d.security_notice;el.appendChild(notice);}
  catch(e){el.textContent=e.message;}
 }
 function findAssetIds(data){
  const found=[];
  const visit=(node,depth=0)=>{
   if(depth>5||node==null)return;
   if(Array.isArray(node)){node.slice(0,100).forEach(x=>visit(x,depth+1));return;}
   if(typeof node!=="object")return;
   const id=node.id??node.dataset_id??node.datasetId;
   const label=node.name??node.title??node.asset_name??node.dataset_name;
   if(id!==undefined&&label!==undefined)found.push({id:String(id),label:String(label)});
   Object.values(node).forEach(v=>visit(v,depth+1));
  };
  visit(data);return [...new Map(found.map(x=>[x.id,x])).values()];
 }
 async function loadFerc(){
  $("energyFercStatus").textContent="Requesting FERC data-assets catalog…";
  $("energyFercAssets").textContent="";$("energyFercDetails").textContent="";
  try{
   const d=await req("/api/v1/energy/infrastructure/ferc/assets");
   const items=findAssetIds(d.catalog);
   const pre=document.createElement("pre");pre.className="infra-json";pre.textContent=JSON.stringify(d.catalog,null,2);
   const wrapper=document.createElement("details");const summary=document.createElement("summary");summary.textContent="Inspect raw FERC data-assets metadata";wrapper.append(summary,pre);
   $("energyFercAssets").appendChild(wrapper);
   if(items.length){
    const box=document.createElement("div");box.className="infra-dataset-picker";
    const label=document.createElement("label");label.textContent="Dataset ID";
    const select=document.createElement("select");select.id="energyFercDatasetId";
    items.forEach(item=>{const opt=document.createElement("option");opt.value=item.id;opt.textContent=item.label+" (ID "+item.id+")";select.appendChild(opt);});
    const button=document.createElement("button");button.className="button";button.textContent="Load dataset details";button.addEventListener("click",loadDetails);
    box.append(label,select,button);$("energyFercAssets").prepend(box);
   }else{
    const note=document.createElement("p");note.className="note";note.textContent="The FERC response is available above. No generic dataset ID/name pairs were detected in this response shape; use the provider catalog to identify the dataset ID."; $("energyFercAssets").prepend(note);
   }
   $("energyFercStatus").textContent="FERC catalog retrieved • "+items.length+" dataset identifiers detected • "+d.retrieved_at;
  }catch(e){$("energyFercStatus").textContent=e.message;}
 }
 async function loadDetails(){
  const id=$("energyFercDatasetId")?.value;if(!id)return;
  $("energyFercDetails").textContent="Loading FERC dataset details…";
  try{const d=await req("/api/v1/energy/infrastructure/ferc/datasets/"+encodeURIComponent(id)+"/details");const pre=document.createElement("pre");pre.className="infra-json";pre.textContent=JSON.stringify(d.details,null,2);$("energyFercDetails").replaceChildren(pre);}
  catch(e){$("energyFercDetails").textContent=e.message;}
 }
 $("energyLoadInfrastructure")?.addEventListener("click",loadSources);
 $("energyLoadFerc")?.addEventListener("click",loadFerc);
 loadSources();
})();