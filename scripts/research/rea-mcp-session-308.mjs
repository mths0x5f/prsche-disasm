// One real REA MCP stdio connection, with every JSON-RPC frame recorded.
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, appendFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { performance } from 'node:perf_hooks';

const root = resolve(import.meta.dirname, '../..');
const packageDir = join(root, 'local/tools/rea-pilot-302/.pilot/package');
const node = join(root, 'local/tools/rea-pilot-302/.pilot/node/node-v26.12.0-win-x64/node.exe');
const target = resolve(process.argv[2]);
const out = resolve(process.argv[3]);
const requireFromPackage = createRequire(pathToFileURL(join(packageDir, 'package.json')));
const { Client } = requireFromPackage('@modelcontextprotocol/client');
const { StdioClientTransport } = requireFromPackage('@modelcontextprotocol/client/stdio');
const sha = p => createHash('sha256').update(readFileSync(p)).digest('hex');
const write = (name, value) => writeFileSync(join(out, name), JSON.stringify(value, null, 2) + '\n');
const event = value => appendFileSync(join(out, 'events.jsonl'), JSON.stringify({at: new Date().toISOString(), ...value}) + '\n');
const targetHashBefore = sha(target);
const server = join(packageDir, 'scripts/rea.mjs');
const childEnv = {...process.env};
const transport = new StdioClientTransport({
  command: node, args: [server, 'mcp'], cwd: packageDir,
  env: childEnv, stderr: 'pipe', maxBufferSize: 16 * 1024 * 1024,
});
const originalSend = transport.send.bind(transport);
transport.send = async message => {
  event({direction: 'client-to-server', message});
  return originalSend(message);
};
let receiver;
Object.defineProperty(transport, 'onmessage', {
  get: () => receiver,
  set: handler => { receiver = message => {
    event({direction: 'server-to-client', message});
    handler(message);
  }; }, configurable: true,
});
const client = new Client({name: 'porsche-rea-mcp-pilot-308', version: '1.0.0'});
let stderrBytes = 0;
transport.stderr?.on('data', chunk => {
  stderrBytes += chunk.length;
  appendFileSync(join(out, 'server-stderr.log'), chunk);
});
const timings = {};
const call = async (name, args, label) => {
  const begin = performance.now();
  const reply = await client.callTool({name, arguments: args},
    {timeout: 600000, signal: AbortSignal.timeout(650000)});
  timings[label] = Math.round((performance.now() - begin) * 1000) / 1000;
  write(label + '.json', reply);
  event({kind: 'tool-complete', label, name, milliseconds: timings[label], isError: reply.isError ?? false});
  return reply;
};
let connected = false;
let serverPid = null;
let binaryOpen = false;
let failure = null;
try {
  const begin = performance.now();
  await client.connect(transport);
  connected = true;
  serverPid = transport.pid;
  timings.initialize = Math.round((performance.now() - begin) * 1000) / 1000;
  event({kind: 'initialized', server_pid: transport.pid, milliseconds: timings.initialize});
  const tools = await client.listTools(undefined, {timeout: 120000});
  write('tools-list.json', tools);
  event({kind: 'tools-listed', names: tools.tools.map(t => t.name)});
  const select = name => {
    const found = tools.tools.find(t => t.name === name);
    if (!found) throw new Error(`Discovered tools/list omits ${name}`);
    return found;
  };
  const open = select('open_binary');
  const session = select('binary_session');
  const analyze = select('analyze_function');
  const close = select('close_binary');
  write('selected-tool-schemas.json', {open, session, analyze, close});
  const expected = 'ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39';
  if (targetHashBefore !== expected) throw new Error('Target SHA mismatch before open');
  const opened = await call(open.name, {path: target, provider_id: 'ghidra'}, 'open');
  if (opened.isError) throw new Error('open_binary returned isError');
  binaryOpen = true;
  await call(session.name, {}, 'session-before');
  const first = await call(analyze.name, {procedure: '0x00476170'}, 'function-cold');
  if (first.isError) throw new Error('First analyze_function returned isError');
  await call(session.name, {}, 'session-middle');
  const second = await call(analyze.name, {procedure: '0x00476170'}, 'function-warm');
  if (second.isError) throw new Error('Second analyze_function returned isError');
  await call(session.name, {}, 'session-after');
  const closed = await call(close.name, {}, 'close');
  if (closed.isError) throw new Error('close_binary returned isError');
  binaryOpen = false;
} catch (error) {
  failure = String(error?.stack ?? error);
  event({kind: 'failure', message: failure});
} finally {
  if (connected && binaryOpen) {
    try { await call('close_binary', {}, 'close-after-failure'); }
    catch (error) { event({kind: 'close-binary-failure', message: String(error)}); }
  }
  try { await client.close(); } catch (error) {
    failure ??= String(error?.stack ?? error);
    event({kind: 'close-failure', message: String(error)});
  }
  write('status.json', {
    connected, server_pid: serverPid, target_sha256_before: targetHashBefore,
    target_sha256_after: sha(target), stderr_bytes: stderrBytes, timings,
    failure,
  });
}
if (failure) { console.error(failure); process.exitCode = 1; }
else console.log(JSON.stringify({status: 'completed', server_pid: serverPid, timings}));
