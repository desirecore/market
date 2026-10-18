/** 只读应用服务；业务数据在平台实例data key中，绝不写固定release目录。 */
import http from 'node:http'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const port = Number(process.env.PORT)
if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('PORT_required')
const files = new Map([
  ['/', ['../ui/index.html','text/html; charset=utf-8']],
  ['/app.js',['../ui/app.js','text/javascript; charset=utf-8']],
  ['/bridge.js',['../ui/bridge.js','text/javascript; charset=utf-8']],
])
const server = http.createServer(async (request,response) => {
  const url = new URL(request.url ?? '/',`http://127.0.0.1:${port}`)
  response.setHeader('X-Content-Type-Options','nosniff')
  response.setHeader('Referrer-Policy','origin')
  if (request.method !== 'GET') { response.writeHead(405); return response.end() }
  if (url.pathname === '/.desirecore-app-identity') {
    response.setHeader('Content-Type','application/json')
    response.setHeader('Cache-Control','no-store')
    const identity = {proof:process.env.DESIRECORE_APP_RUNTIME_PROOF,releaseDigest:process.env.DESIRECORE_APP_RELEASE_DIGEST,
      scopeId:process.env.DESIRECORE_APP_SCOPE_ID,runtimeGeneration:process.env.DESIRECORE_APP_RUNTIME_GENERATION}
    if (Object.values(identity).some(value => typeof value !== 'string' || !value)) { response.writeHead(503); return response.end(JSON.stringify({error:'managed_runtime_identity_unavailable'})) }
    return response.end(JSON.stringify(identity))
  }
  if (url.pathname === '/api/summary') {
    const count = Number(url.searchParams.get('count'))
    if (!Number.isInteger(count) || count < 0 || count > 10000) { response.writeHead(400); return response.end() }
    response.setHeader('Content-Type','application/json')
    return response.end(JSON.stringify({count,summary:`当前工作台有 ${count} 条笔记。`,dataAccess:'none'}))
  }
  const entry = files.get(url.pathname)
  if (!entry) { response.writeHead(404); return response.end() }
  response.setHeader('Content-Type',entry[1])
  response.setHeader('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'")
  try { response.end(readFileSync(fileURLToPath(new URL(entry[0],import.meta.url)))) }
  catch { response.writeHead(503); response.end('material_unavailable') }
})
server.listen(port,'127.0.0.1',() => console.log(`Application service listening on loopback port ${port}`))
for (const signal of ['SIGINT','SIGTERM']) process.on(signal,() => server.close(() => process.exit(0)))
