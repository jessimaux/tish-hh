export function getCookie(name: string): string | undefined {
    const pairs: string[] = document.cookie.split('; ')
    const cookie: string | undefined = pairs.find(p => p.startsWith(name + '='))
    return cookie?.substring(name.length + 1)
}

export function setCookie(name: string, value: string, exp: number) {
    var expires = "";
    if (exp) {
        var date = new Date();
        date.setTime(date.getTime() + (exp));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

export function eraseCookie(name: string) {   
    document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}