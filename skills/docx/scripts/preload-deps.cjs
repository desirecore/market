// preload-deps.cjs —— 跨平台 Node 预加载（无需 bash），让 docx 生成复用客户端预装依赖
//
// 客户端启动时会把 docx-js 预装到 <DESIRECORE_ROOT>/runtime-deps/node_modules/。
// 本文件通过 `node -r` 预加载，把该目录注入模块解析路径，使生成脚本里的
// require('docx') 无需联网 `npm install` 即可命中预装库。纯 Node 实现，在
// Windows / macOS / Linux 上用同一条命令运行，不依赖 bash / Git Bash：
//
//   node -r "<skill-dir>/scripts/preload-deps.cjs" generate.js
//
// 若预装目录不存在（老客户端 / 离线种子缺失），则不做任何事，由生成脚本自身
// 回退（require 失败 → 提示 npm install -g docx）。env 仅作用于本进程。
'use strict'
const path = require('path')
const fs = require('fs')
const Module = require('module')

// scripts → docx → skills → <ROOT>；预装 Node 依赖在 <ROOT>/runtime-deps/node_modules
const depsDir = path.resolve(__dirname, '..', '..', '..', 'runtime-deps', 'node_modules')
if (fs.existsSync(depsDir)) {
  // path.delimiter 跨平台自动取 ';'(Windows) / ':'(POSIX)
  process.env.NODE_PATH = depsDir + (process.env.NODE_PATH ? path.delimiter + process.env.NODE_PATH : '')
  Module._initPaths() // 让随后运行的 generate.js 的 require('docx') 命中预装库
}
