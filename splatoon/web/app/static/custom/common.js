var USERNAME = ''
var TOKEN = ''
var MANA_VALUE = 100
var MANA_OBSERVED_AT = new Date()
var FLASH_CLOSE = undefined

async function fetchMe () {
  const res = await fetch('/api/me/')
  const { user, error } = await res.json()
  
  if (!!error) {
    if (window.location.pathname === '/') {
      window.location = '/login/'
    } else {
      document.getElementById('login-button').classList.remove('hidden')
      document.getElementById('play-button').classList.add('hidden')
    }
    return
  }

  USERNAME = user.name

  if (window.location.pathname === '/') {
    const userNameDom = document.getElementById('user-name')

    userNameDom.style.color = user.color
    userNameDom.innerText = user.name

    MANA_VALUE = user.mana
    MANA_OBSERVED_AT = new Date()
  }
}

function buildScoreboardRow (row, isCurrentUser) {
  const colorSubDom = document.createElement('span')
  const nameSubDom = document.createElement('span')
  const scoreSubDom = document.createElement('span')

  colorSubDom.innerHTML = `<span style='color: ${row.color}; margin-right: 4px;'>@</span>`
  nameSubDom.innerText = row.name
  scoreSubDom.innerText = row.score

  const nameDom = document.createElement('td')
  const scoreDom = document.createElement('td')

  scoreDom.style = 'text-align: right;'

  nameDom.appendChild(colorSubDom)
  nameDom.appendChild(nameSubDom)
  scoreDom.appendChild(scoreSubDom)
  
  const rowDom = document.createElement('tr')

  rowDom.appendChild(nameDom)
  rowDom.appendChild(scoreDom)

  console.log(row, isCurrentUser)
  if (isCurrentUser) rowDom.classList.add('active')

  return rowDom
}

async function fetchScoreboard () {
  const res = await fetch('/api/scoreboard/', {
    method: 'GET',
    headers: {
      'content-type': 'application/json'
    }
  })
  const scoreboard = await res.json()

  const scoreboardDataDom = document.getElementById('scoreboard-data')

  scoreboardDataDom.innerHTML = ''
  scoreboard.forEach(row => scoreboardDataDom.appendChild(buildScoreboardRow(row, row.name === USERNAME)))
}

function reloadMap () {
  const img = document.getElementById('game-map')
  if (!img) return
  img.src = `/api/map/?${Math.random()}`
}
