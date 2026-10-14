/**
 * Модуль налаштувань Telegram-бота та Банки Monobank в адмін-панелі
 * для 3D Shop Степанського академічного ліцею
 */

const STORAGE_KEY_TG_TOKEN = "sal_tg_bot_token";
const STORAGE_KEY_TG_CHAT_ID = "sal_tg_chat_id";
const STORAGE_KEY_TG_USERNAME = "sal_tg_username";
const STORAGE_KEY_MONO_JAR = "sal_mono_jar_link";
const STORAGE_KEY_MONO_TITLE = "sal_mono_jar_title";

// 1. НАЛАШТУВАННЯ TELEGRAM-БОТА
function saveTelegramSettings() {
  const token = document.getElementById("tg-bot-token").value.trim();
  const chatId = document.getElementById("tg-chat-id").value.trim();
  const username = document.getElementById("tg-bot-username").value.trim().replace('@', '');

  localStorage.setItem(STORAGE_KEY_TG_TOKEN, token);
  localStorage.setItem(STORAGE_KEY_TG_CHAT_ID, chatId);
  localStorage.setItem(STORAGE_KEY_TG_USERNAME, username || "stepan_lyceum_3d_bot");

  updateTelegramUIStatus();
  showToast("Налаштування Telegram-бота збережено!");
}

function updateTelegramUIStatus() {
  const token = localStorage.getItem(STORAGE_KEY_TG_TOKEN) || "";
  const chatId = localStorage.getItem(STORAGE_KEY_TG_CHAT_ID) || "";
  const username = localStorage.getItem(STORAGE_KEY_TG_USERNAME) || "stepan_lyceum_3d_bot";

  const pill = document.getElementById("tg-status-pill");
  if (pill) {
    if (token && chatId) {
      pill.className = "text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 border border-emerald-300";
      pill.innerText = "Підключено";
    } else {
      pill.className = "text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 border border-amber-300";
      pill.innerText = "Потрібен токен";
    }
  }

  const tokenInput = document.getElementById("tg-bot-token");
  const chatInput = document.getElementById("tg-chat-id");
  const userInput = document.getElementById("tg-bot-username");
  if (tokenInput && !tokenInput.value) tokenInput.value = token;
  if (chatInput && !chatInput.value) chatInput.value = chatId;
  if (userInput && !userInput.value) userInput.value = username;

  const headerTgLink = document.getElementById("header-tg-link");
  if (headerTgLink) {
    headerTgLink.href = `https://t.me/${username}`;
  }
}

async function testTelegramConnection() {
  const token = (document.getElementById("tg-bot-token") && document.getElementById("tg-bot-token").value.trim()) || localStorage.getItem(STORAGE_KEY_TG_TOKEN);
  const chatId = (document.getElementById("tg-chat-id") && document.getElementById("tg-chat-id").value.trim()) || localStorage.getItem(STORAGE_KEY_TG_CHAT_ID);

  if (!token || !chatId) {
    showToast("Вкажіть токен бота та Chat ID!");
    return;
  }

  showToast("Відправка тестового сповіщення...");
  try {
    const text = `🔔 <b>Тестове сповіщення:</b>\\nTelegram-бот STEM-майстерні Степанського ліцею налаштовано успішно!\\n🕒 Час: ${new Date().toLocaleString('uk-UA')}`;
    const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: text,
        parse_mode: 'HTML'
      })
    });
    const data = await res.json();
    if (data.ok) {
      showToast("✅ Тест успішний! Сповіщення надіслано.");
    } else {
      showToast(`❌ Помилка: ${data.description || 'Не вдалося надіслати'}`);
    }
  } catch (err) {
    showToast("Помилка зв'язку з Telegram API");
  }
}

// 2. НАЛАШТУВАННЯ MONOBANK БАНКИ
function saveMonobankSettings() {
  let link = document.getElementById("mono-jar-link").value.trim();
  const title = document.getElementById("mono-jar-title").value.trim();
  if (link && !link.startsWith("http")) {
    if (link.startsWith("send.monobank.ua")) link = "https://" + link;
    else link = "https://send.monobank.ua/jar/" + link;
  }
  const finalLink = link || "https://send.monobank.ua/jar/89mXHukogN";
  const finalTitle = title || "Банка STEM-хабу на пластик та ЗСУ 🇺🇦";

  localStorage.setItem(STORAGE_KEY_MONO_JAR, finalLink);
  localStorage.setItem(STORAGE_KEY_MONO_TITLE, finalTitle);
  updateMonobankUIStatus();
  showToast("Банку Monobank збережено!");
}

function updateMonobankUIStatus() {
  const link = localStorage.getItem(STORAGE_KEY_MONO_JAR) || "https://send.monobank.ua/jar/89mXHukogN";
  const title = localStorage.getItem(STORAGE_KEY_MONO_TITLE) || "Банка STEM-хабу на пластик та ЗСУ 🇺🇦";

  const pill = document.getElementById("mono-status-pill");
  if (pill) {
    if (link) {
      pill.className = "text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 border border-emerald-300";
      pill.innerText = "Банку підключено";
    } else {
      pill.className = "text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 border border-amber-300";
      pill.innerText = "Вкажіть вашу банку";
    }
  }

  const linkInput = document.getElementById("mono-jar-link");
  const titleInput = document.getElementById("mono-jar-title");
  if (linkInput && !linkInput.value) linkInput.value = link;
  if (titleInput && !titleInput.value) titleInput.value = title;
}

function testOpenMonobankJar() {
  const link = (document.getElementById("mono-jar-link") && document.getElementById("mono-jar-link").value.trim()) || localStorage.getItem(STORAGE_KEY_MONO_JAR) || "https://send.monobank.ua/jar/89mXHukogN";
  window.open(link, "_blank");
}
