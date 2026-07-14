from pathlib import Path
from services.curriculum_adapters.regular import RegularAdapter
a=RegularAdapter()
d={'curso':'1° básico','asignatura':'Matemática','unidades':[{'nombre':'U1'}],'oa':['OA1']}
assert a.can_handle(Path('x.json'),d)
r=a.adapt(Path('x.json'),d)
assert r[0]['curso']=='1° básico'
print('RegularAdapter OK')
