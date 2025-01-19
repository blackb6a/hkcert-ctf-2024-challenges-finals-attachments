async function doLogin (event) {
  event.preventDefault()

  const token = document.getElementById('token').value

  const res = await fetch('/api/login/', {
    method: 'POST',
    headers: {
      'content-type': 'application/json'
    },
    body: JSON.stringify({ token }),
  })
  const { error } = await res.json()
  if (!!error) {
    alert(error)
    return
  }

  window.location = '/'
}

// ======

window.onload = () => {
  fetchMe()
}
