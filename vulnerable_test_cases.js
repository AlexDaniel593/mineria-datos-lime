function xss_vulnerability() {
    // Case 3: XSS Reflejado (Vulnerable)
    // El modelo de ML lo detectó, pero SonarQube lo marcará como una vulnerabilidad de seguridad crítica (Sink: document.write)
    document.write('Hello ' + window.location.search);
}

function safe_dom_manipulation(name) {
    // Case 8: Safe DOM (Seguro)
    // Uso de textContent en lugar de innerHTML o document.write
    document.getElementById('msg').textContent = 'Hello ' + name;
}
