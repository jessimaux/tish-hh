export function getCookie(name: string): string | undefined {
    const pairs: string[] = document.cookie.split('; ')
    const cookie: string | undefined = pairs.find(p => p.startsWith(name + '='))
    return cookie?.substring(name.length + 1)
}