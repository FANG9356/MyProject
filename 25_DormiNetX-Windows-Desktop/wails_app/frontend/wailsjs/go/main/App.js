
export function GetLocalIP() {
  return window['go']['main']['App']['GetLocalIP']();
}

export function GetLocalSubnet() {
  return window['go']['main']['App']['GetLocalSubnet']();
}

export function Greet(arg1) {
  return window['go']['main']['App']['Greet'](arg1);
}

export function PrintHtml(arg1) {
  return window['go']['main']['App']['PrintHtml'](arg1);
}

export function StartLocalServer() {
  return window['go']['main']['App']['StartLocalServer']();
}
