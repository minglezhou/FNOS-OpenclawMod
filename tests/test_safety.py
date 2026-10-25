"""Offline boundary tests. Do not contact a NAS or provider."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import os
import subprocess
import types
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/(name+'.py'))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

fetch=load('fetch_release');backup=load('cold_backup');inspect=load('inspect');health=load('health')

class Boundaries(unittest.TestCase):
    def test_exact_versions(self):
        self.assertEqual(fetch.exact_version('2026.10.5'),'2026.10.5')
        for v in ['latest','^2026.10.5','../x','1.2.3;id','']:
            with self.assertRaises(ValueError):fetch.exact_version(v)
    def test_registry_origin(self):
        fetch.check_url('https://registry.npmjs.org/openclaw/1.2.3')
        for u in ['http://registry.npmjs.org/x','https://evil.test/x','https://a@registry.npmjs.org/x','https://registry.npmjs.org:8443/x']:
            with self.assertRaises(ValueError):fetch.check_url(u)
    def test_sri_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a';p.write_bytes(b'archive')
            sri='sha512-'+base64.b64encode(hashlib.sha512(b'archive').digest()).decode()
            self.assertTrue(fetch.sri_matches(p,sri));p.write_bytes(b'changed')
            self.assertFalse(fetch.sri_matches(p,sri))
    def test_no_weak_sri_fallback(self):
        with self.assertRaises(ValueError):fetch.sri_matches('/not-read','sha1-abcd')
    def test_source_overlap(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'source/child').mkdir(parents=True)
            with self.assertRaises(ValueError):backup.validate_paths([p/'source',p/'source/child'],p/'out',p/'verify')
    def test_output_inside_source(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'source').mkdir()
            with self.assertRaises(ValueError):backup.validate_paths([p/'source'],p/'source/out',p/'verify')
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'source').mkdir();(p/'out').mkdir()
            with self.assertRaises(ValueError):backup.validate_paths([p/'source'],p/'out',p/'verify')
    def test_safe_distinct_paths(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'source').mkdir()
            s,o,v=backup.validate_paths([p/'source'],p/'out',p/'verify')
            self.assertEqual(o,p/'out')
    def test_symlink_destination_resolved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'source').mkdir();(p/'link').symlink_to(p/'source',target_is_directory=True)
            with self.assertRaises(ValueError):backup.validate_paths([p/'source'],p/'link/out',p/'verify')
    def test_inventory_does_not_emit_secrets(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'package.json';p.write_text(json.dumps({'name':'x','apiKey':'DO_NOT_EMIT','dependencies':{'openclaw':'1.2.3'}}))
            result=json.dumps(inspect.package_summary(p))
            self.assertNotIn('DO_NOT_EMIT',result);self.assertNotIn('apiKey',result)
    def test_health_error_redacted(self):
        with patch.object(health.urllib.request,'build_opener',side_effect=ValueError('sensitive body')):
            r=health.probe(11434)
        self.assertFalse(r['bridge_alive']);self.assertNotIn('sensitive',json.dumps(r))
    def test_health_json_whitespace_independent(self):
        class Response:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,n):return b'{"status":"ok"}'
        with patch.object(health.urllib.request,'build_opener') as build:
            build.return_value.open.return_value=Response()
            self.assertTrue(health.probe(11434)['bridge_alive'])

class UpgradeContract(unittest.TestCase):
    def setup_project(self, directory):
        p=Path(directory)
        for n in ('home','state','project','logs','bin'):(p/n).mkdir()
        (p/'project/package.json').write_text(json.dumps({'dependencies':{'openclaw':'1.2.2'}}))
        (p/'project/bun.lock').write_text('fixture')
        (p/'receipt.json').write_text(json.dumps({'verification_matches':True,'sources':[str(p)]}))
        # Mock identity only inside this offline test. Production script keeps its real check.
        (p/'bin/id').write_text('#!/bin/sh\ncase "$1" in -u) echo 12345;; -un) echo fixture-app;; esac\n')
        (p/'bin/bun').write_text('#!/bin/sh\ntouch "$MARKER"\nexit 19\n')
        (p/'bin/node').write_text('#!/bin/sh\nexit 0\n')
        for x in (p/'bin').iterdir():x.chmod(0o700)
        env=dict(os.environ,PATH=str(p/'bin')+':'+os.environ['PATH'],APP_USER='fixture-app',
                 APP_HOME=str(p/'home'),STATE_DIR=str(p/'state'),INSTALL_DIR=str(p/'project'),
                 NODE_BIN=str(p/'bin/node'),BUN_BIN=str(p/'bin/bun'),TARGET_VERSION='1.2.3',
                 CHECKPOINT_RECEIPT=str(p/'receipt.json'),LOG_PARENT=str(p/'logs'),MARKER=str(p/'executed'))
        return p,env
    def run_script(self,mode,env):
        return subprocess.run(['bash',str(ROOT/'scripts/upgrade-core.sh'),mode],env=env,capture_output=True,text=True)
    def test_plan_never_installs(self):
        with tempfile.TemporaryDirectory() as d:
            p,e=self.setup_project(d);r=self.run_script('--plan',e)
            self.assertEqual(r.returncode,0,r.stderr);self.assertFalse((p/'executed').exists())
            self.assertEqual(list((p/'logs').iterdir()),[])
    def test_apply_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as d:
            p,e=self.setup_project(d);e.pop('MAINTENANCE_CONFIRMED',None)
            self.assertNotEqual(self.run_script('--apply',e).returncode,0)
            self.assertFalse((p/'executed').exists())
    def test_checkpoint_inventory_must_cover_state(self):
        with tempfile.TemporaryDirectory() as d:
            p,e=self.setup_project(d)
            (p/'receipt.json').write_text(json.dumps({'verification_matches':True,'sources':[str(p/'project')]}))
            self.assertNotEqual(self.run_script('--plan',e).returncode,0)
    def test_unverified_checkpoint_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p,e=self.setup_project(d)
            (p/'receipt.json').write_text(json.dumps({'verification_matches':False,'sources':[str(p)]}))
            self.assertNotEqual(self.run_script('--plan',e).returncode,0)

class ColdCaptureIntegration(unittest.TestCase):
    def execute(self,p):
        argv=['cold_backup.py','--source',str(p/'source'),'--out',str(p/'backup'),
              '--verify-dir',str(p/'verify'),'--user','fixture','--port','65534',
              '--ack-all-writers-stopped']
        with patch('sys.argv',argv),patch.object(backup.os,'geteuid',return_value=0), \
             patch.object(backup.pwd,'getpwnam',return_value=types.SimpleNamespace(pw_uid=1234567)), \
             patch.object(backup,'require_quiet'),patch.object(backup.time,'sleep'),patch('builtins.print'):
            backup.main()
    def test_real_tar_rsync_roundtrip(self):
        # Root gate/quiescence are mocked; real GNU tar/rsync touch only this fixture.
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);s=p/'source';s.mkdir();f=s/'file';f.write_bytes(b'cold-data');f.chmod(0o600)
            os.link(f,s/'hardlink');(s/'symlink').symlink_to('file')
            self.execute(p)
            r=json.loads((p/'backup/receipt.json').read_text())
            self.assertTrue(r['verification_matches'])
            restored=p/'verify'/str(s).lstrip('/')
            self.assertEqual((restored/'file').read_bytes(),b'cold-data')
            self.assertEqual((restored/'file').stat().st_mode & 0o777,0o600)
            self.assertEqual((restored/'file').stat().st_ino,(restored/'hardlink').stat().st_ino)
            self.assertEqual(os.readlink(restored/'symlink'),'file')
    def test_failed_extract_retains_archive(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'source').mkdir();(p/'source/file').write_bytes(b'fixture')
            real=backup.run_logged
            def injected(argv,out,label):
                if label=='extract':raise RuntimeError('injected extraction failure')
                return real(argv,out,label)
            with patch.object(backup,'run_logged',side_effect=injected),self.assertRaises(RuntimeError):
                self.execute(p)
            self.assertTrue((p/'backup/cold.tar').exists())
            self.assertTrue((p/'verify').is_dir())
            self.assertFalse((p/'backup/receipt.json').exists())

if __name__=='__main__':unittest.main()
