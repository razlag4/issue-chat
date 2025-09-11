const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;


const EVENTS_FILE = path.join(__dirname, 'iventbot', 'ivents.json');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'docs')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'docs', 'ownbok.html'));
});

function loadEvents() {
    try {
        if (!fs.existsSync(EVENTS_FILE)) fs.writeFileSync(EVENTS_FILE, '[]', 'utf-8');
        const data = fs.readFileSync(EVENTS_FILE, 'utf-8');
        return JSON.parse(data);
    } catch {
        return [];
    }
}

function saveEvents(events) {
    try {
        fs.writeFileSync(EVENTS_FILE, JSON.stringify(events, null, 2), 'utf-8');
    } catch {}
}

app.get('/events', (req, res) => {
    res.json(loadEvents());
});

app.post('/delete-event', (req, res) => {
    const { name } = req.body;
    if (!name) return res.status(400).json({ error: 'Не указан name' });
    const events = loadEvents();
    const newEvents = events.filter(ev => ev.name !== name);
    if (newEvents.length === events.length) return res.status(404).json({ error: 'Событие не найдено' });
    saveEvents(newEvents);
    res.json({ success: true });
});

app.listen(PORT, () => console.log(`✅ Server running on port ${PORT}`));

