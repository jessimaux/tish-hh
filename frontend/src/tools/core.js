export function getCookie(name) {
  const pairs = document.cookie.split('; ')
  const cookie = pairs.find((p) => p.startsWith(name + '='))
  return cookie?.substring(name.length + 1)
}

export function setCookie(name, value, exp) {
  var expires = ''
  if (exp) {
    var date = new Date()
    date.setTime(date.getTime() + exp)
    expires = '; expires=' + date.toUTCString()
  }
  document.cookie = name + '=' + (value || '') + expires + '; path=/'
}

export function eraseCookie(name) {
  document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;'
}
