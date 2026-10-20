const { spawnSync } = require('node:child_process')
const fs = require('node:fs')
const path = require('node:path')

// repo.txt holds the absolute path of the repository to sync.
// commit-message.txt is optional; without it the commit message is "update <time>".
const configDir = process.env.HERDR_PLUGIN_CONFIG_DIR ?? path.join(__dirname, 'config')

function readConfig(name) {
  const file = path.join(configDir, name)
  if (!fs.existsSync(file)) return null
  return fs.readFileSync(file, 'utf8').trim()
}

function git(repo, args) {
  const result = spawnSync('git', ['-C', repo, ...args], { encoding: 'utf8' })
  if (result.status !== 0) {
    throw new Error(`git ${args.join(' ')} 실패\n${result.stderr.trim()}`)
  }
  return result.stdout.trim()
}

function update(repo) {
  const before = git(repo, ['rev-parse', 'HEAD'])
  git(repo, ['pull', '--ff-only'])
  const after = git(repo, ['rev-parse', 'HEAD'])
  if (before === after) {
    console.log('update: 이미 최신')
    return
  }
  const count = git(repo, ['rev-list', '--count', `${before}..${after}`])
  console.log(`update: ${count}개 커밋 받음`)
}

function commit(repo) {
  const changed = git(repo, ['status', '--porcelain'])
  if (changed === '') {
    console.log('commit: 커밋할 변경 없음')
    return
  }
  const message = readConfig('commit-message.txt') || `update ${new Date().toLocaleString('sv-SE')}`
  git(repo, ['add', '-A'])
  git(repo, ['commit', '-m', message])
  console.log(`commit: ${changed.split('\n').length}개 파일 커밋 (${message})`)
}

function push(repo) {
  const ahead = git(repo, ['rev-list', '--count', '@{u}..HEAD'])
  if (ahead === '0') {
    console.log('push: 푸시할 커밋 없음')
    return
  }
  git(repo, ['push'])
  console.log(`push: ${ahead}개 커밋 푸시`)
}

function main() {
  const action = process.argv[2]
  const repo = readConfig('repo.txt')
  if (!repo) {
    throw new Error(`${path.join(configDir, 'repo.txt')} 에 저장소 경로를 적어주세요`)
  }

  switch (action) {
    case 'update':
      return update(repo)
    case 'commit':
      return commit(repo)
    case 'push':
      return push(repo)
    case 'all':
      update(repo)
      commit(repo)
      return push(repo)
    default:
      throw new Error(`알 수 없는 action: ${action}`)
  }
}

try {
  main()
} catch (error) {
  console.error(error.message)
  process.exit(1)
}
