/* GlobalBLOCS application navigation */
(function(){
  const init=()=>{
    const nav=document.querySelector(".nav");
    if(!nav || document.querySelector(".app-shell-nav")) return;

    nav.classList.add("workspace-nav");
    nav.id="workspaceNav";
    nav.setAttribute("aria-label","GlobalBLOCS workspaces");

    const shell=document.createElement("div");
    shell.className="app-shell-nav";
    shell.innerHTML=
      '<div class="topbar">'+
        '<div class="topbar-brand"><button class="menu-toggle" id="workspaceMenuToggle" aria-controls="workspaceNav" aria-expanded="false" aria-label="Open workspace menu"><span>☰</span><span class="menu-label">Menu</span></button>'+
        '<button class="topbar-home" data-page="overview" aria-label="Go to Home"><span class="home-icon">⌂</span><span>Home</span></button></div>'+
        '<nav class="topbar-links" aria-label="Primary navigation">'+
          '<button data-page="overview">Overview</button>'+
          '<button data-page="intelligence">Financial Intelligence</button>'+
          '<button data-page="visualization">Metric Visualization</button>'+
          '<button data-page="data">Data Explorer</button>'+
        '</nav>'+
        '<div class="topbar-actions"><button id="globalSearchButton" title="Focus Data Explorer search">⌕ Search</button><button id="topResetButton" title="Reset dashboard filters">↺ Reset</button></div>'+
      '</div>'+
      '<div class="nav-backdrop" id="navBackdrop" hidden></div>';

    document.body.insertBefore(shell, document.querySelector("main"));
    shell.appendChild(nav);

    const menuToggle=document.getElementById("workspaceMenuToggle");
    const backdrop=document.getElementById("navBackdrop");
    const setOpen=(open)=>{
      nav.classList.toggle("open",open);
      menuToggle.setAttribute("aria-expanded",String(open));
      backdrop.hidden=!open;
      document.body.classList.toggle("menu-open",open);
    };
    menuToggle.addEventListener("click",()=>setOpen(!nav.classList.contains("open")));
    backdrop.addEventListener("click",()=>setOpen(false));

    nav.querySelectorAll("button[data-page]").forEach(button=>{
      button.addEventListener("click",()=>setOpen(false));
    });

    document.querySelectorAll(".topbar [data-page]").forEach(button=>{
      button.addEventListener("click",()=>{
        const target=nav.querySelector('button[data-page="'+button.dataset.page+'"]');
        if(target) target.click();
      });
    });

    document.getElementById("globalSearchButton").addEventListener("click",()=>{
      const target=nav.querySelector('button[data-page="data"]');
      if(target) target.click();
      setTimeout(()=>document.getElementById("search")?.focus(),0);
    });
    document.getElementById("topResetButton").addEventListener("click",()=>{
      document.getElementById("reset")?.click();
    });

    document.addEventListener("keydown",(event)=>{
      if(event.key==="Escape") setOpen(false);
    });
  };
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",init);
  else init();
})();