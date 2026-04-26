with open('admin/index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# Locate and replace the RecipesView function
start_marker = "function RecipesView({data, setData, toast, ghItems, onSave, onDelete, ghMedia, setGhMedia}){"
end_marker = "\nfunction RecipeEditor("

si = src.find(start_marker)
ei = src.find(end_marker, si)

if si == -1 or ei == -1:
    print(f"ERROR: markers not found si={si} ei={ei}")
    exit(1)

new_recipes_view = r"""function RecipesView({data, toast, ghRecList, setGhRecList, ghCats, ghMedia, setGhMedia}){
  const [editing, setEditing]   = useState(null);
  const [statusF, setStatusF]   = useState("all");
  const [catF, setCatF]         = useState("all");
  const [search, setSearch]     = useState("");

  const items = (ghRecList && ghRecList.items.length > 0) ? ghRecList.items : data.recipes;

  const saveRecipeList = async (newItems) => {
    toast('Saving to GitHub…');
    try {
      const result = await ghWrite('content/recipes-list.json', newItems, ghRecList.sha, 'Update recipes list via CMS');
      setGhRecList({sha: result.content.sha, items: newItems});
      toast('Saved ✓ — deploying now');
    } catch(e) { toast('Save failed: ' + e.message); }
  };

  const handleSave = async (recipe, newData) => {
    const isNew = recipe._listIdx === undefined;
    let newItems;
    if (isNew) {
      const nextId = items.length > 0 ? Math.max(...items.map(r=>r.id||0)) + 1 : 1;
      newItems = [...items, {...newData, id: nextId}];
    } else {
      newItems = items.map((r, i) => i === recipe._listIdx ? {...r, ...newData} : r);
    }
    await saveRecipeList(newItems);
    if (isNew) setEditing(null);
  };

  const handleDelete = async (recipe) => {
    if (recipe._listIdx === undefined) return;
    const newItems = items.filter((_, i) => i !== recipe._listIdx);
    await saveRecipeList(newItems);
    setEditing(null);
  };

  if (editing != null) {
    return <RecipeEditor recipe={editing} back={()=>setEditing(null)} toast={toast}
      onSave={handleSave} onDelete={handleDelete} ghMedia={ghMedia} setGhMedia={setGhMedia} ghCats={ghCats}/>;
  }

  const filtered = items.filter(r => {
    if (statusF !== "all" && r.status !== statusF) return false;
    if (catF !== "all" && r.cat !== catF) return false;
    if (search && !((r.title||r.name||"").toLowerCase().includes(search.toLowerCase()))) return false;
    return true;
  });

  const catLabel = (id) => { const c = (ghCats||[]).find(x=>x.id===id); return c ? c.label : id; };

  return (
    <>
      <div className="ph-head">
        <div>
          <div className="ek">Recipes &middot; {items.length} total{ghRecList&&ghRecList.items.length>0?' · from GitHub':' · preview data'}</div>
          <h1>Recipes</h1>
          <p>Your recipe library. Drafts don't appear on the live site.</p>
        </div>
        <div className="actions">
          <button className="btn btn-accent" onClick={()=>setEditing({title:'',slug:'',cat:'quick',time:'',servings:'2',difficulty:'Easy',blurb:'',status:'draft',tags:'',ingredients:[],steps:[],heroImage:'',nutrition:{}})}><Icon name="plus" size={14}/> New recipe</button>
        </div>
      </div>
      <div className="fbar">
        <div className="search"><Icon name="search" size={14}/><input placeholder="Search recipes…" value={search} onChange={e=>setSearch(e.target.value)}/></div>
        <div className="seg">
          {[["all","All"],["live","Live"],["draft","Draft"],["sched","Scheduled"]].map(([k,l])=>(
            <button key={k} className={statusF===k?"on":""} onClick={()=>setStatusF(k)}>{l}</button>
          ))}
        </div>
        <div className="right">
          <select value={catF} onChange={e=>setCatF(e.target.value)} style={{background:"#fff",border:"1px solid var(--line)",borderRadius:10,height:38,padding:"0 12px",fontSize:13}}>
            <option value="all">All categories</option>
            {(ghCats||[]).map(c=><option key={c.id} value={c.id}>{c.label}</option>)}
          </select>
        </div>
      </div>
      <table className="tbl">
        <thead><tr><th style={{width:"40%"}}>Recipe</th><th>Category</th><th>Time</th><th>Rating</th><th>Status</th><th></th></tr></thead>
        <tbody>
          {filtered.map((r,i) => {
            const idx = items.indexOf(r);
            return (
              <tr key={r.slug||r.id||i} onClick={()=>setEditing({...r, _listIdx:idx})} style={{cursor:"pointer"}}>
                <td><div className="row-thumb">{(r.heroImage||r.image)?<img src={r.heroImage||r.image} style={{width:44,height:44,borderRadius:8,objectFit:"cover",flexShrink:0}}/>:<div className={"ph "+(r.kind||"")}><span className="lbl">{r.cat}</span></div>}<div><div className="title">{r.title||r.name}</div><div className="sub">{r.slug||'--'}</div></div></div></td>
                <td><span className="chip" style={{background:"var(--surface-2)",color:"#6b6658"}}>{catLabel(r.cat)||r.cat||'--'}</span></td>
                <td className="num">{r.time||'--'}</td>
                <td className="num">{r.stars>0?<span style={{display:"inline-flex",alignItems:"center",gap:4}}><Icon name="star" size={11}/> {r.stars}</span>:'--'}</td>
                <td><span className={"chip "+(r.status||'draft')}>{r.status==="live"?"Live":r.status==="sched"?"Scheduled":"Draft"}</span></td>
                <td className="act"><button className="icon-btn" onClick={e=>{e.stopPropagation();setEditing({...r,_listIdx:idx});}}><Icon name="edit" size={14}/></button></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </>
  );
}"""

src = src[:si] + new_recipes_view + src[ei:]
print(f"RecipesView replaced OK (was {ei-si} chars, now {len(new_recipes_view)} chars)")

with open('admin/index.html', 'w', encoding='utf-8') as f:
    f.write(src)
