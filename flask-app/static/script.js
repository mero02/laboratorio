function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('Comando copiado al portapapeles: ' + text);
    }, function(err) {
        console.error('Error al copiar: ', err);
        // Fallback para navegadores antiguos
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Comando copiado al portapapeles: ' + text);
    });
}

function testEndpoint(endpoint) {
    const responseDiv = document.getElementById('response');
    responseDiv.innerHTML = '<p>Probando ' + endpoint + '...</p>';

    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            responseDiv.innerHTML = '<h3>Respuesta de ' + endpoint + ':</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
        })
        .catch(error => {
            responseDiv.innerHTML = '<p>Error al probar ' + endpoint + ': ' + error.message + '</p>';
        });
}