import sys, re, subprocess, json
out={}
for f in sys.argv[1:]:
    t=subprocess.run(['pdftotext','-layout',f,'-'],capture_output=True,text=True).stdout.splitlines()
    name=next((l.strip() for l in t if l.strip().startswith('Kommunalprofil')),f)
    name=re.sub(r'\s{2,}.*','',name).replace('Kommunalprofil ','')
    # find the block "Bevölkerungsstand*) und -bewegung 2018 – 2024"
    i=next(k for k,l in enumerate(t) if 'und -bewegung 2018' in l)
    blk=t[i:i+45]
    def grab(label, which):
        for k,l in enumerate(blk):
            if l.strip().startswith(label):
                # the line with label has 'a' values; next lines 'b'
                for m in range(k,k+3):
                    s=blk[m]
                    mm=re.search(r'\s'+which+r'\s+(.*)$',s)
                    if mm:
                        vals=re.findall(r'[–+-]?\s?\d[\d ]*?(?=\s{2,}|$)',mm.group(1)+'  ')
                        vals=[int(v.replace('–','-').replace(' ','').replace('+','')) for v in re.findall(r'[–+]?\s?\d{1,3}(?: \d{3})*',mm.group(1))]
                        return vals
        return None
    d={}
    for lab,key in [('Bevölkerung am','pop'),('Lebendgeborene','geb'),('Gestorbene','gest'),('Zugezogene','zu'),('Fortgezogene','fort'),('Überschuss der Zu','wsaldo')]:
        d[key+'_a']=grab(lab,'a'); d[key+'_b']=grab(lab,'b')
    out[name]=d
json.dump(out,open(sys.argv[0].replace('parse_kp.py','kp.json'),'w'),ensure_ascii=False,indent=0)
for n,d in out.items(): print(n, 'pop',d['pop_a'],'\n  wsaldo_a',d['wsaldo_a'],'\n  wsaldo_b',d['wsaldo_b'])
