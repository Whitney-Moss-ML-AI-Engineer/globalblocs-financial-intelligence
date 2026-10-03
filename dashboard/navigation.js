/* GlobalBLOCS application shell and workspace navigation */
(function(){
  const init=()=>{
    const nav=document.querySelector(".nav");
    const legacyHeader=document.querySelector("body > header");
    if(!nav || document.querySelector(".app-shell-nav")) return;

    nav.classList.add("workspace-nav");
    nav.id="workspaceNav";
    nav.setAttribute("aria-label","GlobalBLOCS workspaces");

    const shell=document.createElement("div");
    shell.className="app-shell-nav";
    shell.innerHTML=
      '<div class="topbar">'+
        '<div class="brand-area">'+
          '<button class="menu-toggle" id="workspaceMenuToggle" aria-controls="workspaceNav" aria-expanded="false" aria-label="Open workspace menu"><span class="hamburger">☰</span><span>Menu</span></button>'+
          '<button class="brand-home" data-page="overview" aria-label="GlobalBLOCS Home">'+
            '<span class="brand-mark">GB</span><span class="brand-copy"><strong>GlobalBLOCS</strong><small>Financial Intelligence</small></span>'+
          '</button>'+
        '</div>'+
        '<nav class="topbar-links" aria-label="Primary navigation">'+
          '<button data-page="overview">Home</button>'+
          '<button data-page="intelligence">Intelligence</button>'+
          '<button data-page="visualization">Analytics</button>'+
          '<button data-page="data">Data Explorer</button>'+
        '</nav>'+
        '<div class="topbar-actions">'+
          '<button id="globalSearchButton" title="Open Data Explorer">⌕ <span>Search</span></button>'+
          '<button id="topExportButton" title="Export current dashboard view">⇩ <span>Export</span></button>'+
          '<button id="topResetButton" title="Reset dashboard filters">↺ <span>Reset</span></button>'+
        '</div>'+
      '</div>'+
      '<div class="workspace-strip"><div class="workspace-title"><span>Workspace</span><strong id="activeWorkspaceLabel">Overview</strong></div><div class="workspace-hint">Global economic • financial • risk • statistical • ML/DL intelligence</div></div>'+
      '<div class="nav-backdrop" id="navBackdrop" hidden></div>';

    document.body.insertBefore(shell, document.querySelector("main"));
    shell.appendChild(nav);
    if(legacyHeader) legacyHeader.setAttribute("hidden","hidden");

    const menuToggle=document.getElementById("workspaceMenuToggle");
    const backdrop=document.getElementById("navBackdrop");
    const label=document.getElementById("activeWorkspaceLabel");

    const setOpen=(open)=>{
      nav.classList.toggle("open",open);
      menuToggle.setAttribute("aria-expanded",String(open));
      backdrop.hidden=!open;
      document.body.classList.toggle("menu-open",open);
    };

    const titleFor=(page)=>{
      const button=nav.querySelector('button[data-page="'+page+'"]');
      return button ? button.textContent.trim() : "Workspace";
    };

    menuToggle.addEventListener("click",()=>setOpen(!nav.classList.contains("open")));
    backdrop.addEventListener("click",()=>setOpen(false));
    nav.querySelectorAll("button[data-page]").forEach(button=>{
      button.addEventListener("click",()=>{
        label.textContent=titleFor(button.dataset.page);
        setOpen(false);
      });
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
      setTimeout(()=>document.getElementById("search")?.focus(),50);
    });

    document.getElementById("topExportButton").addEventListener("click",()=>{
      document.getElementById("export")?.click();
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