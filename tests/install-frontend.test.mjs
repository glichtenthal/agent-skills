// Offline installer control-flow tests: downloads and checksum tools are mocks.
// A separate release check must install the actual public ZIP with real hashing.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {test} from 'node:test';
import {execFileSync,spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const script=path.join(repo,'install.sh');
const name='production-frontend-engineer';
const pin='production-frontend-engineer-v1.3.2';
const url=`https://github.com/glichtenthal/agent-skills/releases/download/${pin}/${name}-1.3.2.zip`;
const checksum='80c22c5034fde5d952159ebbd66f52950ab25bd4e62180c8818f0d44e0d9dd7c';
const tool=n=>execFileSync('/bin/bash',['-c',`command -v ${n}`],{encoding:'utf8'}).trim();
function fixture({mode='valid',version='1.3.2',status='stable',skillName=name,hashTool='shasum',wrongRoot=false}={}){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'frontend-installer-test-'));
 const bin=path.join(root,'bin'),dest=path.join(root,'skills'),tmp=path.join(root,'temp');
 for(const d of [bin,tmp])fs.mkdirSync(d);
 const payload=path.join(root,'payload',wrongRoot?'other-skill':name);
 const files={'SKILL.md':`---\nname: ${skillName}\ndescription: Synthetic installer fixture only.\n---\n`,LICENSE:'Synthetic fixture',
  'agents/openai.yaml':'interface:\n  display_name: Synthetic fixture\n',
  'metadata/release.json':JSON.stringify({name:skillName,version,status}),
  'references/release-readiness.md':'Synthetic reference','references/runtime-ui-reliability.md':'Synthetic reference'};
 for(const [n,s]of Object.entries(files)){const p=path.join(payload,n);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,s);}
 const archive=path.join(root,'fixture.zip');execFileSync('zip',['-q','-r',archive,path.basename(payload)],{cwd:path.dirname(payload)});
 const mock=(n,body)=>{const p=path.join(bin,n);fs.writeFileSync(p,`#!${process.execPath}\n${body}\n`);fs.chmodSync(p,0o755);};
 mock('curl',`const fs=require('node:fs'),a=process.argv.slice(2);fs.appendFileSync(process.env.FRONTEND_TEST_LOG,JSON.stringify(a)+'\\n');if(process.env.FRONTEND_TEST_MODE==='download-failure')process.exit(22);if(!a.includes(${JSON.stringify(url)}))process.exit(91);const i=a.indexOf('-o');if(i<0)process.exit(92);fs.copyFileSync(process.env.FRONTEND_TEST_ARCHIVE,a[i+1]);`);
 if(hashTool)mock(hashTool,`process.stdout.write((process.env.FRONTEND_TEST_MODE==='hash-mismatch'?'0'.repeat(64):${JSON.stringify(checksum)})+'  fixture\\n');`);
 for(const n of ['mkdir','mktemp','unzip','mv','rm','awk','grep'])fs.symlinkSync(tool(n),path.join(bin,n));
 if(mode==='replacement-failure'){
  fs.unlinkSync(path.join(bin,'mv'));mock('mv',`const a=process.argv.slice(2);if(a[0].includes('.${name}.install.')&&a[1]===process.env.FRONTEND_TEST_TARGET)process.exit(73);const r=require('node:child_process').spawnSync(${JSON.stringify(tool('mv'))},a,{stdio:'inherit'});process.exit(r.status??1);`);
 }
 const log=path.join(root,'curl.jsonl'),target=path.join(dest,name);
 const run=(args=[])=>spawnSync('/bin/bash',[script,'--dest',dest,...args],{encoding:'utf8',env:{...process.env,PATH:bin,TMPDIR:tmp,FRONTEND_TEST_MODE:mode,FRONTEND_TEST_ARCHIVE:archive,FRONTEND_TEST_LOG:log,FRONTEND_TEST_TARGET:target}});
 const seed=()=>{fs.mkdirSync(target,{recursive:true});fs.writeFileSync(path.join(target,'keep.txt'),'prior user copy');};
 const kept=()=>assert.equal(fs.readFileSync(path.join(target,'keep.txt'),'utf8'),'prior user copy');
 const calls=()=>fs.existsSync(log)?fs.readFileSync(log,'utf8').trim().split('\n').filter(Boolean).map(JSON.parse):[];
 return{root,dest,target,tmp,run,seed,kept,calls};
}
test('default selection and all existing release pins stay unchanged',()=>{
 const f=fixture(),r=f.run(['--dry-run']);assert.equal(r.status,0,r.stderr);
 assert.deepEqual(r.stdout.split('\n').filter(l=>l.startsWith('Install ')),[
  `Install briefing-room v1.2.1 at ${f.dest}/briefing-room`,
  `Install ground-truth v1.2 at ${f.dest}/ground-truth`,
  `Install the-quorum v1.4.1 at ${f.dest}/the-quorum`,
  `Install test-drive v1.6.1 at ${f.dest}/test-drive`]);
 assert.equal(fs.existsSync(f.dest),false);assert.equal(f.calls().length,0);
 const steward=f.run(['--skill','ai-project-steward','--dry-run']);assert.equal(steward.status,0,steward.stderr);assert.match(steward.stdout,/ai-project-steward v2\.1\.3/);
});
test('Frontend is explicit, deduplicated and pinned; dry-run writes no destination or download',()=>{
 const f=fixture(),r=f.run(['--skill',name,'--skill',name,'--dry-run']);assert.equal(r.status,0,r.stderr);assert.equal(r.stdout.split('\n').filter(l=>l.startsWith('Install ')).length,1);assert.ok(r.stdout.includes(pin));assert.equal(fs.existsSync(f.dest),false);assert.equal(f.calls().length,0);
});
test('mocked valid install uses the exact standalone release URL and one root folder',()=>{
 const f=fixture(),r=f.run(['--skill',name]);assert.equal(r.status,0,r.stderr);assert.equal(f.calls().length,1);assert.ok(f.calls()[0].includes(url));assert.equal(JSON.parse(fs.readFileSync(path.join(f.target,'metadata/release.json'))).version,'1.3.2');assert.deepEqual(fs.readdirSync(f.dest),[name]);assert.equal(fs.existsSync(path.join(f.target,name)),false);
});
test('existing copies are skipped without update, without downloading',()=>{
 const f=fixture();f.seed();const r=f.run(['--skill',name]);assert.equal(r.status,0,r.stderr);assert.match(r.stdout,/Skipping/);f.kept();assert.equal(f.calls().length,0);
});
test('mocked successful update replaces only the selected target and leaves sibling skills',()=>{
 const f=fixture();f.seed();const sibling=path.join(f.dest,'do-not-touch');fs.mkdirSync(sibling);fs.writeFileSync(path.join(sibling,'keep.txt'),'sibling');const r=f.run(['--skill',name,'--update']);assert.equal(r.status,0,r.stderr);assert.equal(fs.existsSync(path.join(f.target,'keep.txt')),false);assert.equal(fs.readFileSync(path.join(sibling,'keep.txt'),'utf8'),'sibling');assert.equal(fs.readdirSync(f.tmp).length,0);
});
test('bad checksum fails before replacement and preserves the existing copy',()=>{
 const f=fixture({mode:'hash-mismatch'});f.seed();const r=f.run(['--skill',name,'--update']);assert.notEqual(r.status,0);assert.match(r.stderr,/SHA-256 mismatch/);f.kept();assert.deepEqual(fs.readdirSync(f.dest),[name]);
});
test('download failure preserves the existing copy',()=>{
 const f=fixture({mode:'download-failure'});f.seed();const r=f.run(['--skill',name,'--update']);assert.equal(r.status,22);f.kept();assert.equal(fs.readdirSync(f.tmp).length,0);
});
test('sha256sum fallback works; absence of both hash tools fails closed',()=>{
 const f=fixture({hashTool:'sha256sum'}),r=f.run(['--skill',name]);assert.equal(r.status,0,r.stderr);const missing=fixture({hashTool:null});missing.seed();const fail=missing.run(['--skill',name,'--update']);assert.notEqual(fail.status,0);assert.match(fail.stderr,/requires shasum or sha256sum/);missing.kept();
});
test('wrong version, status, skill name or archive root cannot replace an install',()=>{
 for(const opts of[{version:'1.3.1'},{status:'candidate'},{skillName:'other-skill'},{wrongRoot:true}]){const f=fixture(opts);f.seed();const r=f.run(['--skill',name,'--update']);assert.notEqual(r.status,0,JSON.stringify(opts));f.kept();}
});
test('replacement failure restores the previous target',()=>{
 const f=fixture({mode:'replacement-failure'});f.seed();const r=f.run(['--skill',name,'--update']);assert.notEqual(r.status,0);assert.match(r.stderr,/previous copy was restored/);f.kept();assert.deepEqual(fs.readdirSync(f.dest),[name]);
});
test('symbolic-link target is rejected without touching its destination',()=>{
 const f=fixture(),elsewhere=path.join(f.root,'elsewhere');fs.mkdirSync(f.dest);fs.mkdirSync(elsewhere);fs.writeFileSync(path.join(elsewhere,'keep.txt'),'untouched');fs.symlinkSync(elsewhere,f.target);const r=f.run(['--skill',name,'--update']);assert.notEqual(r.status,0);assert.match(r.stderr,/symbolic link/);assert.ok(fs.lstatSync(f.target).isSymbolicLink());assert.equal(fs.readFileSync(path.join(elsewhere,'keep.txt'),'utf8'),'untouched');assert.equal(f.calls().length,0);
});
test('Design and Backend do not become installer options',()=>{
 const f=fixture();for(const n of['product-design-director','production-backend-engineer']){const r=f.run(['--skill',n,'--dry-run']);assert.notEqual(r.status,0);assert.match(r.stderr,/Unknown skill/);}assert.equal(fs.existsSync(f.dest),false);
});
