/* GlobalBLOCS metric-agnostic SVG visualization renderer. */
(function(){
  function el(id){return document.getElementById(id)}
  function esc(v){return String(v??"").replace(/[&<>"]/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[m]))}
  function points(values,w=760,h=300,p=36){
    const nums=values.map(Number).filter(Number.isFinite); if(!nums.length)return [];
    const min=Math.min(...nums),max=Math.max(...nums),range=max-min||1;
    return nums.map((v,i)=>({x:p+i*(w-2*p)/Math.max(1,nums.length-1),y:h-p-(v-min)*(h-2*p)/range,v}));
  }
  function render(targetId,type,values,labels){
    const t=el(targetId); if(!t)return;
    values=(values||[]).map(Number).filter(Number.isFinite);
    if(values.length<1){t.innerHTML="<p class='note'>No numeric observations available.</p>";return}
    const w=760,h=300,p=36,pts=points(values,w,h,p);
    if(["line","area","drawdown"].includes(type)){
      const path=pts.map((q,i)=>(i?"L":"M")+q.x.toFixed(1)+" "+q.y.toFixed(1)).join(" ");
      const area=type==="area"||type==="drawdown"?path+" L "+pts[pts.length-1].x+" "+(h-p)+" L "+pts[0].x+" "+(h-p)+" Z":"";
      t.innerHTML="<svg viewBox='0 0 "+w+" "+h+"' class='metric-chart'><line x1='"+p+"' y1='"+(h-p)+"' x2='"+(w-p)+"' y2='"+(h-p)+"' class='axis'/><path d='"+area+"' class='area'/><path d='"+path+"' class='series'/></svg>";
    } else if(type==="bar"){
      const bw=Math.max(2,(w-2*p)/values.length-3), max=Math.max(...values.map(Math.abs))||1;
      t.innerHTML="<svg viewBox='0 0 "+w+" "+h+"' class='metric-chart'>"+values.map((v,i)=>{const bh=Math.abs(v)/max*(h-2*p),x=p+i*(w-2*p)/values.length,y=v>=0?h-p-bh:h-p;return "<rect x='"+x+"' y='"+y+"' width='"+bw+"' height='"+bh+"' class='bar'/>"}).join("")+"</svg>";
    } else if(type==="histogram"){
      const bins=10,min=Math.min(...values),max=Math.max(...values),range=max-min||1,count=Array(bins).fill(0);values.forEach(v=>count[Math.min(bins-1,Math.floor((v-min)/range*bins))]++);
      const mx=Math.max(...count)||1,bw=(w-2*p)/bins;
      t.innerHTML="<svg viewBox='0 0 "+w+" "+h+"' class='metric-chart'>"+count.map((n,i)=>{const bh=n/mx*(h-2*p);return "<rect x='"+(p+i*bw)+"' y='"+(h-p-bh)+"' width='"+(bw-2)+"' height='"+bh+"' class='bar'/>"}).join("")+"</svg>";
    } else if(type==="scatter"){
      t.innerHTML="<svg viewBox='0 0 "+w+" "+h+"' class='metric-chart'>"+pts.map(q=>"<circle cx='"+q.x+"' cy='"+q.y+"' r='4' class='point'/>").join("")+"</svg>";
    } else {
      t.innerHTML="<div class='viz-special'><b>"+esc(type)+"</b><p>Renderer contract registered. Provide compatible dataset fields to render this visualization.</p></div>";
    }
  }
  window.GlobalBLOCSViz={render};
})();