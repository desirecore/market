/** 教学SDK适配：桌面有限preload；Web严格parent来源/nonce握手，没有管理token或任意invoke。 */
const methods = new Set(['connect','capabilities','publishSelection','prepareWork','lookupRequest','readWork','controlWork','openResource','readData','saveData','lookupDataMutation','saveViewState'])
export async function connectBridge() {
  if (window.desirecoreApp?.call) return window.desirecoreApp
  if (window.parent === window) throw new Error('app_bridge_host_unavailable')
  let origin
  try { origin = new URL(document.referrer).origin } catch { throw new Error('app_bridge_host_origin_required') }
  if (origin === 'null' || origin === location.origin) throw new Error('app_bridge_independent_origin_required')
  return new Promise((resolve, reject) => {
    let nonce
    const timer = setTimeout(() => { window.removeEventListener('message', receive); reject(new Error('app_bridge_host_unavailable')) }, 15000)
    function receive(event) {
      if (event.source !== window.parent || event.origin !== origin || !event.data || typeof event.data !== 'object') return
      if (event.data.protocol === 'desirecore-app-hello-v1' && typeof event.data.nonce === 'string' && !nonce) {
        nonce = event.data.nonce
        window.parent.postMessage({ protocol:'desirecore-app-ready-v1',nonce },origin)
      } else if (nonce && event.data.protocol === 'desirecore-app-port-v1' && event.data.nonce === nonce && event.ports.length === 1) {
        window.removeEventListener('message',receive); clearTimeout(timer); resolve(portClient(event.ports[0]))
      }
    }
    window.addEventListener('message',receive)
  })
}
function portClient(port) {
  const pending = new Map(), listeners = new Set()
  port.onmessage = event => {
    const message = event.data
    if (message?.protocol !== 'desirecore-app-bridge-v1') return
    const request = pending.get(message.requestId)
    if (request) { pending.delete(message.requestId); clearTimeout(request.timer); message.error ? request.reject(new Error(message.error)) : request.resolve(message.result) }
    else if (message.event !== undefined) for (const listener of listeners) listener(message.event)
  }
  port.start()
  return {
    call(method,payload) {
      if (!methods.has(method)) return Promise.reject(new Error('app_bridge_method_rejected'))
      const requestId = crypto.randomUUID()
      return new Promise((resolve,reject) => {
        const timer = setTimeout(() => { pending.delete(requestId); reject(new Error('app_bridge_result_unknown')) },30000)
        pending.set(requestId,{resolve,reject,timer}); port.postMessage({ protocol:'desirecore-app-bridge-v1',requestId,method,payload })
      })
    },
    onEvent(callback) { listeners.add(callback); return () => listeners.delete(callback) },
    close() { for (const request of pending.values()) { clearTimeout(request.timer); request.reject(new Error('app_bridge_closed')) }; pending.clear(); listeners.clear(); port.close() },
  }
}
