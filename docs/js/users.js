const USERS_URL = "./users.json";

async function loadUsers() {
  try {
    const response = await fetch(USERS_URL);
    const users = await response.json();
    renderUsers(users);
  } catch (err) {
    console.error("Ошибка загрузки users.json:", err);
  }
}

function renderUsers(users) {
  const container = document.getElementById("users");
  container.innerHTML = "";

  users.forEach(user => {
    const div = document.createElement("div");
    div.classList.add("user");
    div.style.display = "flex";
    div.style.alignItems = "center";
    div.style.justifyContent = "flex-start";
    div.style.position = "relative";
    div.style.marginBottom = "10px";
    div.style.padding = "10px 15px";
    div.style.borderRadius = "10px";
    div.style.background = "rgba(255,255,255,0.05)";
    div.style.transition = "background 0.3s";

    // сохраняем id и username в data-атрибуты
    div.dataset.id = user.id || "";
    div.dataset.username = user.username || "";

    // статичная аватарка 👤
    const avatar = document.createElement("div");
    avatar.style.width = "50px";
    avatar.style.height = "50px";
    avatar.style.borderRadius = "50%";
    avatar.style.flexShrink = "0";
    avatar.style.backgroundColor = "rgba(150,150,150,0.5)";
    avatar.style.marginRight = "10px";
    avatar.style.display = "flex";
    avatar.style.alignItems = "center";
    avatar.style.justifyContent = "center";
    avatar.style.fontSize = "24px";
    avatar.style.color = "white";
    avatar.textContent = "👤";

    // имя пользователя
    const nameSpan = document.createElement("span");
    nameSpan.style.color = "#eee";
    nameSpan.style.fontSize = "16px";
    nameSpan.style.fontWeight = "500";
    if (user.first_name && user.last_name) {
      nameSpan.textContent = `${user.first_name} ${user.last_name}`;
    } else if (user.first_name) {
      nameSpan.textContent = user.first_name;
    } else {
      nameSpan.textContent = "Без имени";
    }

    // username или ID справа
    const rightInfo = document.createElement("span");
    rightInfo.style.position = "absolute";
    rightInfo.style.right = "15px";
    rightInfo.style.color = "#aabaff";
    rightInfo.style.fontSize = "14px";
    rightInfo.style.opacity = "0";
    rightInfo.style.transition = "opacity 0.3s";
    if (user.username) {
      rightInfo.textContent = `@${user.username}`;
    } else {
      rightInfo.textContent = `ID:${user.id}`;
    }

    // эффекты при наведении
    div.addEventListener("mouseenter", () => {
      div.style.background = "rgba(255,255,255,0.1)";
      rightInfo.style.opacity = "1";
    });
    div.addEventListener("mouseleave", () => {
      div.style.background = "rgba(255,255,255,0.05)";
      rightInfo.style.opacity = "0";
    });

    // собираем div
    div.appendChild(avatar);
    div.appendChild(nameSpan);
    div.appendChild(rightInfo);
    container.appendChild(div);
  });
}

// фильтр поиска по id, username, имени
document.getElementById("searchInput").addEventListener("input", e => {
  const value = e.target.value.trim().toLowerCase();
  document.querySelectorAll(".user").forEach(div => {
    const id = (div.dataset.id || "").toLowerCase();
    const username = (div.dataset.username || "").toLowerCase();
    const text = (div.querySelector("span").textContent || "").toLowerCase();
    div.style.display = id.includes(value) || username.includes(value) || text.includes(value) ? "flex" : "none";
  });
});

loadUsers();
