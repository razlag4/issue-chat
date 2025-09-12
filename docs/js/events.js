async function fetchEvents() {
  try {
    const response = await fetch(`https://issue-chat.onrender.com/events?v=${Date.now()}`);
    if (!response.ok) throw new Error();
    return await response.json();
  } catch {
    return [];
  }
}

function removeEventFromServer(name) {
  fetch('/delete-event', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  }).catch(console.error);
}

function updateTimers(eventElements) {
  const now = new Date();
  eventElements.forEach(({ container, timer, endTime, button, wingLeft, wingRight, name }) => {
    const diff = endTime - now;
    if (diff <= 0) {
      container.remove();
      removeEventFromServer(name);
    } else {
      const days = Math.floor(diff / 86400000);
      const hours = Math.floor((diff % 86400000) / 3600000);
      const minutes = Math.floor((diff % 3600000) / 60000);
      const seconds = Math.floor((diff % 60000) / 1000);
      let text = '';
      if (days > 0) text += `${days}д `;
      if (hours > 0 || days > 0) text += `${hours}ч `;
      if (minutes > 0 || hours > 0 || days > 0) text += `${minutes}м `;
      text += `${seconds}с`;
      timer.textContent = `До окончания: ${text}`;
    }
  });
}

function createEventButton(event) {
  const container = document.createElement('div');
  container.classList.add('event-block');

  const button = document.createElement('a');
  button.href = event.link || '#';
  button.target = '_blank';
  button.textContent = event.name;
  button.classList.add('event-btn');

  const wingLeft = document.createElement('span');
  wingLeft.classList.add('wing-left');
  const wingRight = document.createElement('span');
  wingRight.classList.add('wing-right');
  button.appendChild(wingLeft);
  button.appendChild(wingRight);

  const timer = document.createElement('div');
  timer.classList.add('event-timer');

  container.appendChild(button);
  container.appendChild(timer);

  return { container, timer, button, wingLeft, wingRight, endTime: new Date(event.end_time), name: event.name };
}

async function renderEvents() {
  const container = document.getElementById('events-container');
  container.innerHTML = '';
  const events = await fetchEvents();
  if (!events.length) {
    const p = document.createElement('p');
    p.textContent = 'Ивентов нет';
    container.appendChild(p);
    return [];
  }
  const eventElements = events.map(ev => {
    const elem = createEventButton(ev);
    container.appendChild(elem.container);
    return elem;
  });
  return eventElements;
}

let currentEventElements = [];

async function updateEventsLoop() {
  currentEventElements = await renderEvents();
  setInterval(() => updateTimers(currentEventElements), 1000);
  setInterval(async () => {
    currentEventElements = await renderEvents();
  }, 30000);
}

document.addEventListener('DOMContentLoaded', updateEventsLoop);
