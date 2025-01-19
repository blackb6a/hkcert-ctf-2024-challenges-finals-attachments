function initInventory () {
  const inventoryDom = document.getElementById('inventory')

  inventoryDom.innerHTML = ''
  for (let i = 0; i < 16; i++) {
    inventoryDom.innerHTML += `
      <div class="rpgui-icon empty-slot item-slot my-1">
        <img class="paintball rpgui-cursor-point" src="/rpgui/img/icons/potion-blue.png" onclick="selectPaintball(${i})">
        <span class="stats-base rpgui-cursor-point" onclick="selectPaintball(${i})">
          <span>RAD</span>
          <span>MP</span>
          <span class="radius-value"></span>
          <span class="mana-value"></span>
        </span>
      </div>
    `
  }
}

function flash (error) {
  const errorMessageDom = document.getElementById('error-message')
  const errorMessageContentDom = errorMessageDom.getElementsByTagName('span')[0]

  if (FLASH_CLOSE) clearTimeout(FLASH_CLOSE)

  errorMessageDom.classList.remove('hidden')
  errorMessageContentDom.innerText = error
  FLASH_CLOSE = setTimeout(() => errorMessageDom.classList.add('hidden'), 3000)
}

function setInventorySlot (idx, paintball) {
  const inventoryDom = document.getElementById('inventory')
  const slotDom = inventoryDom.getElementsByTagName('div')[idx]
  const radiusDom = slotDom.getElementsByClassName('radius-value')[0]
  const manaDom = slotDom.getElementsByClassName('mana-value')[0]

  slotDom.classList.remove('hidden')
  slotDom.setAttribute('data-token', paintball.token)
  radiusDom.innerText = paintball.radius
  manaDom.innerText = paintball.mana
}

function clearInventorySlot (idx) {
  const inventoryDom = document.getElementById('inventory')
  const slotDom = inventoryDom.getElementsByTagName('div')[idx]

  slotDom.classList.add('hidden')
}

function selectPaintball (idx) {
  const inventoryDom = document.getElementById('inventory')

  for (let i = 0; i < 16; i++) {
    const slotDom = inventoryDom.getElementsByTagName('div')[i]
    slotDom.classList.remove('active')
  }

  if (typeof idx === 'number') {
    const slotDom = inventoryDom.getElementsByTagName('div')[idx]
    slotDom.classList.add('active')

    TOKEN = slotDom.getAttribute('data-token')
  } else {
    TOKEN = null
  }
}

async function fetchPaintballs () {
  const res = await fetch('/api/paintballs/')
  const { paintballs, error } = await res.json()

  if (!!error) {
    console.error(error)
    return
  }

  for (let i = 0; i < 16; i++) {
    const paintball = paintballs[i]
    if (!paintball) {
      clearInventorySlot(i)
    } else {
      setInventorySlot(i, paintball)
    }
  }
}

async function fetchMessages () {
  const res = await fetch('/api/messages/')
  const { messages, error } = await res.json()

  if (!!error) {
    console.error(error)
    return
  }

  document.getElementById('messages').innerHTML = DOMPurify.sanitize(
    messages.map(message => `<span>${message}</span>`).join('<br>')
  )
}

async function throwPaintball (event) {
  event.preventDefault()

  const x = event.offsetX
  const y = event.offsetY
  const token = TOKEN
  if (!token) {
    flash('pick a paintball')
    return
  }

  const res = await fetch('/api/paintballs/', {
    method: 'POST',
    headers: {
      'content-type': 'application/json'
    },
    body: JSON.stringify({ x, y, token })
  })
  const {mana, error} = await res.json()

  if (error === 'paintball not found') {
    selectPaintball()
    flash(error)
    return
  } else if (!!error) {
    flash(error)
    return
  }
  
  MANA_VALUE = mana
  MANA_OBSERVED_AT = new Date()

  selectPaintball() // unselects the current paintball
  fetchPaintballs()
  fetchMessages()
  reloadMap()
}

// ======

window.onload = async () => {
  const manaDom = document.getElementById('user-mana')
  RPGUI.set_value(manaDom, 0)

  await fetchMe()

  initInventory()
  reloadMap()
  fetchPaintballs()
  fetchMessages()
  fetchScoreboard()

  setInterval(() => {
    fetchScoreboard()
  }, 3*1000)

  setInterval(() => {
    reloadMap()
    fetchPaintballs()
    fetchMessages()
  }, 1000)

  setInterval(() => {
    const mana = Math.min(100, MANA_VALUE + (new Date() - MANA_OBSERVED_AT) / 1000)
    const manaDom = document.getElementById('user-mana')
    RPGUI.set_value(manaDom, mana / 100)
    manaDom.getElementsByTagName('span')[0].innerText = Math.floor(mana)
  }, 100)
}
