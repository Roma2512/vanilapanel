function ansiToHtml(text) {
    // Базовые ANSI цвета
    const colors = {
        '0': 'color: inherit', // reset
        '30': 'color: black',
        '31': 'color: red',
        '32': 'color: green',
        '33': 'color: yellow',
        '34': 'color: blue',
        '35': 'color: magenta',
        '36': 'color: cyan',
        '37': 'color: white',
        '90': 'color: gray',
        '91': 'color: lightred',
        '92': 'color: lightgreen',
        '93': 'color: lightyellow',
        '94': 'color: lightblue',
        '95': 'color: lightmagenta',
        '96': 'color: lightcyan',
        '97': 'color: white'
    };

    // Регулярное выражение для поиска ANSI escape-последовательностей
    const ansiRegex = /\x1b\[([0-9;]*)m/g;
    
    let html = '';
    let lastIndex = 0;
    let match;
    let currentStyle = '';

    while ((match = ansiRegex.exec(text)) !== null) {
        // Добавляем текст перед последовательностью
        html += `<span style="${currentStyle}">${text.substring(lastIndex, match.index)}</span>`;
        
        // Обрабатываем ANSI код
        const codes = match[1].split(';');
        currentStyle = codes.map(code => colors[code] || '').join(';');
        
        lastIndex = ansiRegex.lastIndex;
    }
    
    // Добавляем оставшийся текст
    html += `<span style="${currentStyle}">${text.substring(lastIndex)}</span>`;
    
    return html;
}
