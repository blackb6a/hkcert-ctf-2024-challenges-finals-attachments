window.onload = async () => {
  await fetchMe()

  fetchScoreboard()
  reloadMap()

  setInterval(() => {
    fetchScoreboard()
    reloadMap()
  }, 3*1000)
}
