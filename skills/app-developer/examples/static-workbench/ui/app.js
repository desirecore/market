import { connectBridge } from './bridge.js'
const element = id => document.getElementById(id)
let bridge, connection, etag, notes = [], selected, rememberedNoteId, pendingSave, pendingWork, pendingViewState, viewRevision = 'none'
const status = message => { element('status').textContent = message }
function render() {
  element('notes').replaceChildren()
  for (const note of notes) {
    const row = document.createElement('li'), text = document.createElement('div'), button = document.createElement('button')
    text.textContent = note.text; button.textContent = selected?.id === note.id ? '已选中' : '选择此笔记'
    button.addEventListener('click', () => { selected = note; render() }); row.append(text,button); element('notes').append(row)
  }
}
async function read() {
  const result = await bridge.call('readData',{key:'notes'})
  const value = result.exists ? JSON.parse(result.content) : {schemaVersion:1,notes:[]}
  if (value.schemaVersion !== 1 || !Array.isArray(value.notes)) throw new Error('notes_format_unsupported')
  notes = value.notes; etag = result.etag; selected = notes.find(note => note.id === (selected?.id ?? rememberedNoteId)); render()
  status('已读取当前实例的数据。')
}
async function save() {
  if (!pendingSave) {
    const text = element('note').value.trim()
    if (!text) return status('先输入笔记。')
    pendingSave = {key:'notes',mutationId:crypto.randomUUID(),content:JSON.stringify({schemaVersion:1,notes:[...notes,{id:crypto.randomUUID(),revision:'1',text}]}),
      ...(etag ? {expectedETag:etag} : {expectedAbsent:true})}
  }
  try {
    const receipt = await bridge.call('saveData',pendingSave)
    if (receipt.status !== 'saved') throw new Error('save_result_unknown')
    pendingSave = undefined; element('recover').disabled = true; element('note').value = ''; await read(); status('保存回执已核验。')
  } catch (error) { element('recover').disabled = false; status(`保存尚未确认：${error.message}。保留原ID和正文，先查询原保存；未确认前不要添加另一条笔记。`) }
}
element('save').addEventListener('click',save)
element('refresh').addEventListener('click',() => pendingSave ? status('还有结果不明的原保存，请先查询。') : read().catch(error => status(error.message)))
element('recover').addEventListener('click',async () => {
  if (!pendingSave) return
  try {
    const result = await bridge.call('lookupDataMutation',{key:'notes',mutationId:pendingSave.mutationId})
    if (result.status === 'saved') { pendingSave = undefined; element('recover').disabled = true; element('note').value = ''; await read() }
    else status(result.status === 'absent' ? '原保存明确未发生。可以用“保存笔记”重试同ID和原正文，冲突时读取并人工合并。' : '原保存仍不明确，请保留当前页面和原ID。')
  } catch (error) { status(error.message) }
})
element('request').addEventListener('click',async () => {
  const agentId = element('agent').value.trim()
  if (!agentId || !selected) return element('work-status').textContent = '先选择笔记和实际Agent。'
  if (pendingWork) return element('work-status').textContent = '已有待查询请求，请沿原ID恢复。'
  pendingWork = {clientRequestId:crypto.randomUUID(),userMessageId:crypto.randomUUID(),agentId,
    prompt:`请讨论这条笔记并给出可执行建议：${selected.text}`,scopeDescription:'读取notes来源文件核验所选笔记，只讨论该记录，不修改其他记录。',
    selection:{schemaVersion:1,selectionRevision:crypto.randomUUID(),summary:`笔记ID:${selected.id}，记录版本:${selected.revision}，内容:${selected.text}；正式实例对象引用授予读取notes来源文件。`,objects:connection.application && etag ?
      [{schemaVersion:1,...connection.application,namespace:'data-files',objectId:'notes',revision:etag}] : []}}
  element('work').disabled = false
  try {
    const proposal = await bridge.call('prepareWork',pendingWork)
    element('work-status').textContent = `提案已准备，等待平台控件接纳。提案引用：${proposal.proposalRef}`
  } catch (error) { element('work-status').textContent = `提案/请求结果尚未确认：${error.message}；保留原请求ID查询。` }
})
element('work').addEventListener('click',async () => {
  if (!pendingWork) return
  try { element('work-status').textContent = JSON.stringify(await bridge.call('lookupRequest',{agentId:pendingWork.agentId,clientRequestId:pendingWork.clientRequestId}),null,2) }
  catch (error) { element('work-status').textContent = error.message }
})
element('progress').addEventListener('click',async () => {
  if (!pendingWork) return
  try {
    const snapshot = await bridge.call('readWork',{agentId:pendingWork.agentId,clientRequestId:pendingWork.clientRequestId})
    element('work-status').textContent = `准入：${snapshot.admission}；执行：${snapshot.execution}。执行完成后仍需核读实际成果。`
    element('cancel').disabled = !connection.capabilities?.includes('controlWork') || !snapshot.availableActions?.includes('abort')
    element('results').replaceChildren()
    for (const [index, resource] of (snapshot.resources ?? []).entries()) {
      const row = document.createElement('li'), button = document.createElement('button')
      button.textContent = `${resource.role === 'evidence' ? '查看证据' : '打开成果'} ${index + 1}`
      button.disabled = !connection.capabilities?.includes('openResource')
      button.addEventListener('click',async () => {
        try {
          const result = await bridge.call('openResource',{locator:resource.locator})
          element('work-status').textContent = result.state === 'navigation-requested' ? '已请求平台定位该成果，文件正文继续由原授权入口核验。' : result.opened === true ? '平台已打开获授权对象。' : '定位结果尚未确认。'
        } catch (error) { element('work-status').textContent = `成果未打开：${error.message}` }
      })
      row.append(button); element('results').append(row)
    }
  } catch (error) { element('work-status').textContent = `进度暂不可读：${error.message}` }
})
element('cancel').addEventListener('click',async () => {
  if (!pendingWork) return
  try {
    const receipt = await bridge.call('controlWork',{agentId:pendingWork.agentId,clientRequestId:pendingWork.clientRequestId,action:'abort'})
    element('work-status').textContent = `原工作停止结果：${receipt.status}。requested 仅表示停止意图已接纳，结果未知时沿原请求查询。`
  } catch (error) { element('work-status').textContent = `停止未确认：${error.message}` }
})
element('remember').addEventListener('click',async () => {
  if (!pendingViewState) pendingViewState = {schemaVersion:1,key:'selection',state:JSON.stringify({selectedNoteId:selected?.id ?? null}),
    persistence:'device',expectedRevision:viewRevision,mutationId:crypto.randomUUID()}
  try {
    const receipt = await bridge.call('saveViewState',pendingViewState)
    if (receipt.persistence !== 'device' || typeof receipt.revision !== 'string') throw new Error('view_save_result_unknown')
    viewRevision = receipt.revision; pendingViewState = undefined
    element('view-status').textContent = '已在这台设备记住所选位置。笔记正文仍由实例数据单独保存。'
  } catch (error) { element('view-status').textContent = `位置保存未确认：${error.message}。再次点击重试原ID、正文与修订，不覆盖其他更新。` }
})
try {
  bridge = await connectBridge(); connection = await bridge.call('connect')
  const remembered = connection.viewStates?.find(value => value.key === 'selection' && value.persistence === 'device')
  if (remembered) {
    viewRevision = remembered.revision
    try { const state = JSON.parse(remembered.state); if (typeof state.selectedNoteId === 'string') rememberedNoteId = state.selectedNoteId } catch { element('view-status').textContent = '此前位置格式不可读，已保留原偏好。' }
  }
  bridge.onEvent(event => { if (event?.type === 'work-accepted' && event.clientRequestId === pendingWork?.clientRequestId)
    element('work-status').textContent = `平台接纳回执：${JSON.stringify(event.result)}。通过原请求继续查询，接纳不等于业务完成。` })
  await read(); element('save').disabled = !connection.capabilities?.includes('saveData'); element('refresh').disabled = false
  element('request').disabled = !connection.capabilities?.includes('requestWork')
  element('progress').disabled = !connection.capabilities?.includes('readWork')
  element('remember').disabled = !connection.capabilities?.includes('saveViewState') || connection.deviceViewState?.state !== 'available'
  if (element('remember').disabled) element('view-status').textContent = `设备位置记忆不可用：${connection.deviceViewState?.reason ?? '未授权'}。业务笔记仍可按实际数据能力保存。`
} catch (error) { status(`当前持久数据或协作能力不可用：${error.message}。未保存任何业务数据。`) }
