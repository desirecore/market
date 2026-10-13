import { connectBridge } from './bridge.js'
const element = id => document.getElementById(id)
let bridge, connection, etag, notes = [], selected, pendingSave, pendingWork
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
  notes = value.notes; etag = result.etag; selected = notes.find(note => note.id === selected?.id); render()
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
  try { element('work-status').textContent = JSON.stringify(await bridge.call('lookupRequest',{clientRequestId:pendingWork.clientRequestId}),null,2) }
  catch (error) { element('work-status').textContent = error.message }
})
try {
  bridge = await connectBridge(); connection = await bridge.call('connect')
  bridge.onEvent(event => { if (event?.type === 'work-accepted' && event.clientRequestId === pendingWork?.clientRequestId)
    element('work-status').textContent = `平台接纳回执：${JSON.stringify(event.result)}。通过原请求继续查询，接纳不等于业务完成。` })
  await read(); element('save').disabled = !connection.capabilities?.includes('saveData'); element('refresh').disabled = false
  element('request').disabled = !connection.capabilities?.includes('requestWork')
} catch (error) { status(`当前持久数据或协作能力不可用：${error.message}。未保存任何业务数据。`) }
