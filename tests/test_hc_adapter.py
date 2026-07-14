from pathlib import Path
from services.curriculum_adapters.hc import HCAdapter

a=HCAdapter()
d={
 'modalidad':'Humanístico-Científica',
 'curso':'3° medio HC',
 'asignatura':'Diseño y arquitectura',
 'unidades':[{'nombre':'Unidad 1'}],
 'oa':['OA1']
}
assert a.can_handle(Path('electivos_profundizacion_hc/diseno.json'),d)
r=a.adapt(Path('x.json'),d)
assert len(r)==1
assert r[0]['modalidad']=='hc'
assert r[0]['curso']=='3° medio HC'
assert len(r[0]['unidades'])==1
print("HCAdapter OK")
