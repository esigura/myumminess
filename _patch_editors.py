with open('admin/index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# ── 1. RecipeEditor: fix signature, state, category field, fullData ──────────

# signature
src = src.replace(
    "function RecipeEditor({recipe, back, toast, onSave, onDelete, ghMedia, setGhMedia}){",
    "function RecipeEditor({recipe, back, toast, onSave, onDelete, ghMedia, setGhMedia, ghCats}){"
)

# initial state: change `category` to `cat`
src = src.replace(
    "    category:   recipe.cat  || recipe.category  || 'Drinks',",
    "    cat:        recipe.cat  || recipe.category  || 'quick',"
)

# category select: use ghCats dynamically
src = src.replace(
    """              <div className="fld"><label>Category</label>
                <select value={local.category} onChange={e=>setLocal({...local,category:e.target.value})}>
                  {['Drinks','Breakfast','Lunch','Dinner','Snacks','Guides'].map(c=><option key={c}>{c}</option>)}
                </select>
              </div>""",
    """              <div className="fld"><label>Category</label>
                <select value={local.cat} onChange={e=>setLocal({...local,cat:e.target.value})}>
                  {(ghCats&&ghCats.length>0?ghCats:[{id:'quick',label:'Quick Meals'},{id:'weight',label:'Weight Management'},{id:'gut',label:'Gut Health'},{id:'breakfast',label:'Breakfast'},{id:'snacks',label:'Snacks'}]).map(c=><option key={c.id} value={c.id}>{c.label}</option>)}
                </select>
              </div>"""
)

# fullData: change `category` to `cat`
src = src.replace(
    "      title: local.title, slug, category: local.category,",
    "      title: local.title, slug, cat: local.cat, kind: recipe.kind||'',"
)

print("RecipeEditor patches applied")

# ── 2. PageFieldEditor: handle array fields (categories, featured) ──────────
# Find the field rendering block and add array-type handling

old_field_type = """  const fieldType = (key) => {
    const k = key.toLowerCase();
    if(k.endsWith('image')||k.startsWith('image')) return 'image';
    if(k.includes('body')||k.endsWith('sub')||k==='subtitle'||k.includes('blurb')||k==='promisebar'||(k.includes('desc')&&!k.includes('url'))) return 'textarea';
    if(k.includes('href')||k.endsWith('url')||k==='url') return 'url';
    return 'text';
  };"""

new_field_type = """  const fieldType = (key, val) => {
    if(Array.isArray(val)) return 'array';
    const k = key.toLowerCase();
    if(k.endsWith('image')||k.startsWith('image')) return 'image';
    if(k.includes('body')||k.endsWith('sub')||k==='subtitle'||k.includes('blurb')||k==='promisebar'||(k.includes('desc')&&!k.includes('url'))) return 'textarea';
    if(k.includes('href')||k.endsWith('url')||k==='url') return 'url';
    return 'text';
  };"""

if old_field_type in src:
    src = src.replace(old_field_type, new_field_type)
    print("fieldType patched OK")
else:
    print("ERROR: fieldType not found")

# Update the grouped logic to also pass value to fieldType
src = src.replace(
    "Object.entries(local).forEach(([k,v])=>{ const g=getGroup(k); if(!grouped[g]) grouped[g]=[]; grouped[g].push([k,v]); });",
    "Object.entries(local).forEach(([k,v])=>{ if(typeof v==='object'&&!Array.isArray(v)&&v!==null) return; const g=getGroup(k); if(!grouped[g]) grouped[g]=[]; grouped[g].push([k,v]); });"
)

# Update PageFieldEditor signature to accept ghRecList
src = src.replace(
    "function PageFieldEditor({pageId, data, back, toast, ghPage, onSave, ghMedia, setGhMedia}){",
    "function PageFieldEditor({pageId, data, back, toast, ghPage, onSave, ghMedia, setGhMedia, ghRecList}){"
)

# Update the field type call in rendering to pass value
src = src.replace(
    "              const type = fieldType(key);",
    "              const type = fieldType(key, value);"
)

# Add array rendering before the existing field-type render block
old_render_block = """                <div className={'fld '+(full?'full':'')} key={key}>
                  <label>{fmtLabel(key)}</label>"""

new_render_block = """                {type==='array' && key==='categories' && (
                  <div className="fld full" key={key}>
                    <label>Category tabs <span className="hint" style={{fontWeight:400}}>— shown as filter tabs on the Recipes page</span></label>
                    {(value||[]).map((cat,ci)=>(
                      <div key={ci} style={{display:'flex',gap:8,alignItems:'center',marginBottom:6}}>
                        <input value={cat.label||''} onChange={e=>{const a=[...value];a[ci]={...a[ci],label:e.target.value};set(key,a);}} placeholder="Label e.g. Quick Meals" style={{flex:2,background:'var(--input)',border:'1px solid transparent',borderRadius:8,padding:'8px 10px',fontSize:13}}/>
                        <input value={cat.id||''} onChange={e=>{const a=[...value];a[ci]={...a[ci],id:e.target.value};set(key,a);}} placeholder="ID e.g. quick" style={{flex:1,background:'var(--input)',border:'1px solid transparent',borderRadius:8,padding:'8px 10px',fontSize:13,fontFamily:'var(--mono)'}}/>
                        <button onClick={()=>set(key,value.filter((_,x)=>x!==ci))} style={{background:'none',border:0,cursor:'pointer',color:'var(--muted)',fontSize:18,lineHeight:1}}>×</button>
                      </div>
                    ))}
                    <button className="btn btn-ghost btn-sm" style={{marginTop:4}} onClick={()=>set(key,[...(value||[]),{id:'',label:''}])}><Icon name="plus" size={12}/> Add category</button>
                    <span className="hint" style={{display:'block',marginTop:6}}>Label = display name · ID = short key used in recipe files (e.g. "quick", "gut")</span>
                  </div>
                )}
                {type==='array' && key==='featured' && (
                  <div className="fld full" key={key}>
                    <label>This week's top picks <span className="hint" style={{fontWeight:400}}>— shown in the hero section</span></label>
                    {[0,1,2].map(pi=>{
                      const recipes = ghRecList&&ghRecList.items.length>0?ghRecList.items:[];
                      return (
                        <div key={pi} style={{marginBottom:6}}>
                          <select value={(value||[])[pi]||''} onChange={e=>{const a=[...(value||[])];a[pi]=e.target.value;set(key,a.filter(Boolean));}} style={{width:'100%',background:'var(--input)',border:'1px solid transparent',borderRadius:8,padding:'8px 10px',fontSize:13}}>
                            <option value="">— Pick {pi===0?'1st':pi===1?'2nd':'3rd'} featured recipe —</option>
                            {recipes.filter(r=>r.status!=='draft').map(r=><option key={r.slug||r.id} value={r.slug}>{r.title||r.name}</option>)}
                          </select>
                        </div>
                      );
                    })}
                    <span className="hint" style={{display:'block',marginTop:4}}>Only published (live) recipes appear here</span>
                  </div>
                )}
                {type!=='array' && (
                <div className={'fld '+(full?'full':'')} key={key}>
                  <label>{fmtLabel(key)}</label>"""

if old_render_block in src:
    src = src.replace(old_render_block, new_render_block)
    print("Array field rendering inserted OK")
else:
    print("ERROR: render block not found")

# Close the extra conditional wrapper — find the closing of field block
# The field block ends with: </div>\n              );\n            })}
old_field_close = """                </div>
              );
            })}"""
new_field_close = """                </div>
                )}
              );
            })}"""

src = src.replace(old_field_close, new_field_close, 1)  # only replace first occurrence
print("Field close wrapper updated")

with open('admin/index.html', 'w', encoding='utf-8') as f:
    f.write(src)
print("All editor patches done")
