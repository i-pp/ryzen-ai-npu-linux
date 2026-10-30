#!/usr/bin/env python3
"""Bounded read-only inspection; all generated output stays in this repository.
Private raw output may identify this host. Never add .private-evidence to Git.
No vendor runtime imports, device opening, package installation or compilation.
"""
import datetime, glob, hashlib, json, os, pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
WORK = ROOT.parent
OUT = ROOT / '.private-evidence' / datetime.datetime.now(datetime.timezone.utc).strftime('capture-%Y%m%dT%H%M%SZ')
OUT.mkdir(parents=True, exist_ok=False, mode=0o700)
SDK = WORK / 'ryzen-ai-1.8.0'
MLIR = WORK / 'mlir-aie'
records = []

def command(key, argv):
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=25, env={**os.environ, 'GIT_OPTIONAL_LOCKS':'0', 'PYTHONDONTWRITEBYTECODE':'1', 'LC_ALL':'C'})
        obj = {'argv':argv,'returncode':r.returncode,'stdout':r.stdout[:300000],'stderr':r.stderr[:20000]}
    except (OSError, subprocess.TimeoutExpired) as e:
        obj = {'argv':argv,'error':str(e)}
    (OUT / (key+'.json')).write_text(json.dumps(obj,indent=2))
    return obj

def file(path, category, copy_text=False):
    p = pathlib.Path(path)
    rec = {'path':str(p),'category':category}
    try:
        st = p.stat()
        rec.update(size_bytes=st.st_size, mtime_utc=datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat(), mode=oct(st.st_mode & 0o777), symlink_target=os.readlink(p) if p.is_symlink() else None)
        if p.is_file() and st.st_size <= 64*1024*1024:
            data = p.read_bytes()
            rec['sha256'] = hashlib.sha256(data).hexdigest()
            if copy_text and len(data)<1000000:
                name = 'source-%04d.txt' % len(records)
                (OUT/name).write_bytes(data)
                rec['private_copy'] = name
        elif p.is_file(): rec['hash_status']='DEFERRED_SIZE_OVER_64_MIB'
        rec['status']='READ_METADATA'
    except OSError as e:
        rec.update(status='UNAVAILABLE',error=str(e))
    records.append(rec)

commands = {
 'os':['cat','/etc/os-release'], 'kernel':['uname','-r'],
 'cpu':['lscpu'], 'pci-npu':['lspci','-nnk','-d','1022:17f0'],
 'process-limits':['cat','/proc/self/limits'],
 'account':['id'], 'account-database':['getent','group','render','video'],
 'device-nodes':['ls','-ld','/dev/accel','/dev/accel/accel0','/dev/dri'],
 'device-acl':['getfacl','-p','/dev/accel/accel0'],
 'driver':['modinfo','amdxdna'],
 'packages':['dpkg-query','-W','-f=${Package}\t${Version}\t${Status}\n','*xrt*','*xdna*','linux-image*','linux-firmware*','python3.12*','python3.14*','libstdc++6'],
 'mlir-revision':['git','-C',str(MLIR),'log','-1','--format=%H%n%aI%n%cI%n%s'],
 'mlir-worktree':['git','-C',str(MLIR),'status','--short'],
 'mlir-submodules':['git','-C',str(MLIR),'submodule','status'],
 'mlir-diff':['git','-C',str(MLIR),'diff','--','utils/env_install.sh','test/test_kernel_workflows.py'],
 'mlir-origin':['git','-C',str(MLIR),'config','--get','remote.origin.url'],
 'systemd-user':['systemctl','--user','show','--property=DefaultLimitMEMLOCK'],
 'systemd-user-unit':['systemctl','show',f'user@{os.getuid()}.service','--property=LimitMEMLOCK','--property=LimitMEMLOCKSoft','--property=FragmentPath','--property=DropInPaths'],
 'kernel-npu-log':['journalctl','-k','--no-pager','-g','amdxdna|memlock|accel','-n','250','-o','short-iso'],
 'quicktest-elf':['readelf','-d',str(SDK/'cpp-test/quicktest')],
 'vaiml-elf':['readelf','-d',str(SDK/'cpp-test/sdk/onnxruntime/lib/libvaiml2.so')],
}
for key, args in commands.items(): command(key,args)
for tool in ['python3','python3.12','python3.14','gcc','g++','clang','cmake','ninja','ld']:
    command('version-'+tool,[tool,'--version'])
for name, root in [('iron',MLIR/'ironenv'),('sdk',SDK/'ryzenenv314')]:
    file(root/'pyvenv.cfg','python',True)
    command('python-'+name,[str(root/'bin/python'),'-I','-S','-B','--version'])
    packages=[]
    for p in root.glob('lib/python*/site-packages/*.dist-info/METADATA'):
        try:
            t=p.read_text(errors='replace')
            packages.append({'name':re.search(r'^Name: (.+)$',t,re.M).group(1),'version':re.search(r'^Version: (.+)$',t,re.M).group(1),'metadata':str(p)})
        except (OSError,AttributeError): pass
    (OUT/('packages-'+name+'.json')).write_text(json.dumps(packages,indent=2))
    for pattern in ['lib/python*/site-packages/*aie*.dist-info/direct_url.json','lib/python*/site-packages/*aie*.dist-info/METADATA','bin/activate','lib/python*/site-packages/mlir_aie*/METADATA']:
        for p in root.glob(pattern): file(p,'python-provenance',True)
for p in ['/etc/security/limits.conf','/etc/pam.d/login','/etc/pam.d/sshd','/etc/pam.d/sudo','/etc/pam.d/su','/etc/pam.d/gdm-password','/etc/pam.d/common-session','/etc/pam.d/common-session-noninteractive','/etc/systemd/user.conf','/etc/systemd/system.conf','/sys/devices/virtual/dmi/id/sys_vendor','/sys/devices/virtual/dmi/id/product_name','/sys/devices/virtual/dmi/id/product_version','/sys/module/amdxdna/version','/usr/bin/python3.12','/usr/bin/python3.14']:
    file(p,'host-config',not str(p).startswith('/usr/bin'))
for pattern in ['/etc/security/limits.d/*','/etc/systemd/user.conf.d/*','/etc/systemd/system/user@.service.d/*','/etc/systemd/system/user@1000.service.d/*','/etc/udev/rules.d/*xdna*','/usr/lib/udev/rules.d/*xdna*','/lib/firmware/amdnpu/*/*','/usr/lib/x86_64-linux-gnu/libxrt_coreutil*','/usr/share/doc/xrt*/copyright']:
    for p in glob.glob(pattern): file(p,'host-config', any(s in p for s in ['/etc/','rules.d','copyright']))
for p in SDK.iterdir():
    if p.is_file(): file(p,'sdk-distribution',p.suffix in ['.sh','.patch','.txt'])
for pattern in ['cpp-test/*.cpp','cpp-test/run-npu.sh','cpp-test/quicktest','cpp-test/samples/quicktest/*','xrt-packages/**/*','xrt-2.25.37/opt/xilinx/xrt/version.json','xrt-2.25.37/opt/xilinx/xrt/lib/libxrt_coreutil.so*','cpp-test/sdk/onnxruntime/lib/libonnxruntime.so*','cpp-test/peano/*']:
    for p in SDK.glob(pattern):
        if p.is_file(): file(p,'sdk-runtime',p.suffix in ['.cpp','.sh','.md','.json','.py'])
for pattern in ['.gitmodules','utils/env_install.sh','utils/env_setup.sh','programming_examples/getting_started/00_memcpy/*','programming_examples/getting_started/00_memcpy/build/*','programming_examples/getting_started/00_memcpy/logs/*']:
    for p in MLIR.glob(pattern):
        if p.is_file(): file(p,'mlir-iron',p.suffix in ['.sh','.md','.py','.lit','.txt','.log'] or p.name=='.gitmodules')
# Historic logs: bounded relevant apt/dpkg lines only, never shell history or all environment values.
for pattern in ['/var/log/apt/history.log*','/var/log/dpkg.log*']:
    import gzip
    for p in glob.glob(pattern):
        try:
            opener = gzip.open if p.endswith('.gz') else open
            with opener(p,'rt',errors='replace') as f:
                lines=[line.rstrip() for line in f if re.search(r'(?i)xrt|xdna|linux-image-7|python3\.12|python3\.14',line)]
            (OUT/('history-'+pathlib.Path(p).name+'.txt')).write_text('\n'.join(lines))
        except OSError: pass
for p in [pathlib.Path.home()/'Downloads/RAI_1.8_Linux_NPU_XRT.zip', pathlib.Path.home()/'Downloads/ryzen_ai-1.8.0.tgz', pathlib.Path.home()/'.local/share/xrt/2.21.75/amdxdna/bins/xrt_smi_strx.a']:
    file(p,'distribution-provenance')
# Do not copy /tmp content wholesale; metadata for narrowly named candidate diagnostic logs.
for pattern in ['/tmp/*xrt*','/tmp/*npu*','/tmp/*quicktest*','/tmp/*iron*','/tmp/*memcpy*']:
    for p in glob.glob(pattern):
        if pathlib.Path(p).is_file(): file(p,'candidate-historical-log',True)
(OUT/'inventory.json').write_text(json.dumps(records,indent=2))
(OUT/'scope.json').write_text(json.dumps({'captured_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'workspace':str(WORK),'no_device_execution':True,'no_rebuild':True,'clean_room_tested':False,'hash_size_limit_bytes':64*1024*1024,'history_scope':'relevant apt/dpkg lines; shell history not captured'},indent=2))
unavailable_probes = sum(1 for p in OUT.glob('*.json') if p.name not in ['inventory.json','scope.json'] and isinstance((o := json.loads(p.read_text())), dict) and ('error' in o or o.get('returncode',0) != 0))
print(json.dumps({'status':'READ_ONLY_CAPTURE_COMPLETE_WITH_UNAVAILABLE_PROBES' if unavailable_probes else 'READ_ONLY_CAPTURE_COMPLETE', 'unavailable_probe_count':unavailable_probes,'directory':str(OUT),'inventory_count':len(records),'device_execution':False,'clean_room_tested':False}))
