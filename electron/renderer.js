const API_BASE = window.tasktideConfig?.apiBase || "http://127.0.0.1:8765";

const els = {
  statTotal: document.getElementById("statTotal"),
  statCompleted: document.getElementById("statCompleted"),
  statProgress: document.getElementById("statProgress"),
  statTodo: document.getElementById("statTodo"),
  tasksList: document.getElementById("tasksList"),
  tasksListFull: document.getElementById("tasksListFull"),
  notesList: document.getElementById("notesList"),
  notesTaskFilter: document.getElementById("notesTaskFilter"),
  notesTaskPickerBtn: document.getElementById("notesTaskPickerBtn"),
  notesTaskPickerMenu: document.getElementById("notesTaskPickerMenu"),
  notesSearchInput: document.getElementById("notesSearchInput"),
  notesTaskQuickSearchInput: document.getElementById("notesTaskQuickSearchInput"),
  profileAvatar: document.getElementById("profileAvatar"),
  profileName: document.getElementById("profileName"),
  profileAuthBtn: document.getElementById("profileAuthBtn"),
  authModal: document.getElementById("authModal"),
  authModalTitle: document.getElementById("authModalTitle"),
  authTabLoginBtn: document.getElementById("authTabLoginBtn"),
  authTabRegisterBtn: document.getElementById("authTabRegisterBtn"),
  authNameRow: document.getElementById("authNameRow"),
  authNameInput: document.getElementById("authNameInput"),
  authEmailInput: document.getElementById("authEmailInput"),
  authPasswordInput: document.getElementById("authPasswordInput"),
  authErrorText: document.getElementById("authErrorText"),
  authSubmitBtn: document.getElementById("authSubmitBtn"),
  authLogoutBtn: document.getElementById("authLogoutBtn"),
  authCancelBtn: document.getElementById("authCancelBtn"),
  noteReplyInfo: document.getElementById("noteReplyInfo"),
  noteReplyText: document.getElementById("noteReplyText"),
  noteReplyCancelBtn: document.getElementById("noteReplyCancelBtn"),
  nameInput: document.getElementById("nameInput"),
  priorityInput: document.getElementById("priorityInput"),
  categoryInput: document.getElementById("categoryInput"),
  deadlineModeInput: document.getElementById("deadlineModeInput"),
  minutesInput: document.getElementById("minutesInput"),
  deadlineAtBtn: document.getElementById("deadlineAtBtn"),
  deadlineAtInput: document.getElementById("deadlineAtInput"),
  deadlineModal: document.getElementById("deadlineModal"),
  deadlineModalBackdrop: document.getElementById("deadlineModalBackdrop"),
  deadlineMonthLabel: document.getElementById("deadlineMonthLabel"),
  deadlinePrevMonthBtn: document.getElementById("deadlinePrevMonthBtn"),
  deadlineNextMonthBtn: document.getElementById("deadlineNextMonthBtn"),
  deadlineCalendarGrid: document.getElementById("deadlineCalendarGrid"),
  deadlineHourSelect: document.getElementById("deadlineHourSelect"),
  deadlineMinuteSelect: document.getElementById("deadlineMinuteSelect"),
  deadlineTodayBtn: document.getElementById("deadlineTodayBtn"),
  deadlineCancelBtn: document.getElementById("deadlineCancelBtn"),
  deadlineApplyBtn: document.getElementById("deadlineApplyBtn"),
  descriptionInput: document.getElementById("descriptionInput"),
  createBtn: document.getElementById("createBtn"),
  createNoteBtn: document.getElementById("createNoteBtn"),
  noteTitleInput: document.getElementById("noteTitleInput"),
  noteContentInput: document.getElementById("noteContentInput"),
  resetFocusSessionsBtn: document.getElementById("resetFocusSessionsBtn"),
  focusStatsText: document.getElementById("focusStatsText"),
  focusSessionsList: document.getElementById("focusSessionsList"),
  timerLabel: document.getElementById("timerLabel"),
  timerState: document.getElementById("timerState"),
  focusTaskSelect: document.getElementById("focusTaskSelect"),
  focusTaskInfo: document.getElementById("focusTaskInfo"),
  themeToggleBtn: document.getElementById("themeToggleBtn"),
  themeLightBtn: document.getElementById("themeLightBtn"),
  themeDarkBtn: document.getElementById("themeDarkBtn"),
  timerStartBtn: document.getElementById("timerStartBtn"),
  timerPauseBtn: document.getElementById("timerPauseBtn"),
  timerResetBtn: document.getElementById("timerResetBtn"),
  timerFinishBtn: document.getElementById("timerFinishBtn"),
  searchInput: document.getElementById("searchInput"),
  taskPriorityFilter: document.getElementById("taskPriorityFilter"),
  taskCategoryFilter: document.getElementById("taskCategoryFilter"),
  statusFilterBtn: document.getElementById("statusFilterBtn"),
  statusFilterMenu: document.getElementById("statusFilterMenu"),
  statusFilterOptions: document.querySelectorAll(".status-filter-option"),
  viewTitle: document.getElementById("viewTitle"),
  graphsUpdatedAt: document.getElementById("graphsUpdatedAt"),
  graphStatusDonut: document.getElementById("graphStatusDonut"),
  graphStatusTotal: document.getElementById("graphStatusTotal"),
  graphDoneCount: document.getElementById("graphDoneCount"),
  graphProgressCount: document.getElementById("graphProgressCount"),
  graphTodoCount: document.getElementById("graphTodoCount"),
  graphOverdueCount: document.getElementById("graphOverdueCount"),
  graphPriorityBars: document.getElementById("graphPriorityBars"),
  graphCategoryBars: document.getElementById("graphCategoryBars"),
  graphWeeklyBars: document.getElementById("graphWeeklyBars"),
  graphsExtraList: document.getElementById("graphsExtraList"),
  reportText: document.getElementById("reportText"),
  reportActionBtn: document.getElementById("reportActionBtn"),
  pillTotal: document.getElementById("pillTotal"),
  pillDone: document.getElementById("pillDone"),
  pillOverdue: document.getElementById("pillOverdue"),
  completionRate: document.getElementById("completionRate"),
  completionSub: document.getElementById("completionSub"),
  roiValue: document.getElementById("roiValue"),
  roiSub: document.getElementById("roiSub"),
  productivityChart: document.getElementById("productivityChart"),
  productivityBadge: document.getElementById("productivityBadge"),
  summaryCard: document.getElementById("summaryCard"),
  reportCard: document.getElementById("reportCard"),
  completionCard: document.getElementById("completionCard"),
  focusCard: document.getElementById("focusCard"),
  productivityCard: document.getElementById("productivityCard"),
  notifyEnabledInput: document.getElementById("notifyEnabledInput"),
  notifySoundInput: document.getElementById("notifySoundInput"),
  notifyMonthInput: document.getElementById("notifyMonthInput"),
  notifyWeekInput: document.getElementById("notifyWeekInput"),
  notifyDayInput: document.getElementById("notifyDayInput"),
  notify6hInput: document.getElementById("notify6hInput"),
  notify1hInput: document.getElementById("notify1hInput"),
  notify30mInput: document.getElementById("notify30mInput"),
  notify5mInput: document.getElementById("notify5mInput"),
  notifySettingsStatus: document.getElementById("notifySettingsStatus"),
  filterPills: document.querySelectorAll(".filter-pill"),
  viewButtons: document.querySelectorAll("[data-view-btn]"),
  views: document.querySelectorAll(".view")
};

const POMODORO_CONFIG = {
  workSeconds: 25 * 60,
  shortBreakSeconds: 5 * 60,
  longBreakSeconds: 20 * 60,
  sessionsBeforeLongBreak: 4
};

const focusState = {
  durationSeconds: POMODORO_CONFIG.workSeconds,
  remainingSeconds: POMODORO_CONFIG.workSeconds,
  running: false,
  timerId: null,
  phase: "work",
  completedWorkSessions: 0
};

const appState = {
  overview: null,
  tasks: [],
  focusSessions: [],
  taskFilter: "all",
  statusFilter: "all",
  searchQuery: "",
  priorityFilter: "all",
  categoryFilter: "all",
  draftTaskQuery: "",
  selectedTaskId: null,
  shouldScrollToSelectedTask: false,
  newTaskId: null,
  pulseStatsOnNextTasksLoad: false,
  noteReplyParentId: null,
  notesTaskSearchQuery: "",
  notesSearchQuery: "",
  notes: [],
  expandedNoteIds: new Set(),
  activeNoteId: null,
  currentView: "dashboard",
  notificationSettings: null,
  authMode: "login",
  authToken: null,
  currentUser: null
};

const deadlinePickerState = {
  selectedDate: null,
  viewYear: 0,
  viewMonth: 0,
  returnFocusEl: null
};

let deadlineTickerId = null;
let graphsRefreshId = null;
let notificationTickerId = null;
let tasksLiveRefreshId = null;
let tasksLiveRefreshInFlight = false;
let graphsEntryAnimationPlayed = false;
let shouldPlayGraphsEntryAnimation = false;
let sentDeadlineNotifications = {};
const TASKS_LIVE_REFRESH_MS = 8000;
const animatedCountFrames = new WeakMap();

const PRIORITY_ICONS = {
  "Важно - Срочно": "🔥",
  "Важно - Не срочно": "⭐",
  "Не важно - Срочно": "⚡",
  "Не важно - Не срочно": "📝"
};

const CATEGORY_ICONS = {
  "Работа": "💼",
  "Учёба": "📚",
  "Личное": "👤"
};

const DEADLINE_NOTIFICATION_INTERVALS = [
  { key: "month", label: "за месяц", ms: 30 * 24 * 60 * 60 * 1000 },
  { key: "week", label: "за неделю", ms: 7 * 24 * 60 * 60 * 1000 },
  { key: "day", label: "за день", ms: 24 * 60 * 60 * 1000 },
  { key: "h6", label: "за 6 часов", ms: 6 * 60 * 60 * 1000 },
  { key: "h1", label: "за 1 час", ms: 60 * 60 * 1000 },
  { key: "m30", label: "за 30 минут", ms: 30 * 60 * 1000 },
  { key: "m5", label: "за 5 минут", ms: 5 * 60 * 1000 }
];

const DEFAULT_NOTIFICATION_SETTINGS = {
  enabled: false,
  sound: true,
  points: {
    month: false,
    week: false,
    day: true,
    h6: true,
    h1: true,
    m30: true,
    m5: true
  }
};

const VIEW_TITLES = {
  dashboard: "Статистика",
  tasks: "Список задач",
  notes: "Заметки",
  focus: "Таймер выполнения задач",
  graphs: "Графики",
  settings: "Настройки",
  guide: "Инструкция"
};

function normalizeLabel(value) {
  return String(value || "")
    .replace(/^[\s🔥⭐⚡📝💼📚👤🏠]+/u, "")
    .trim();
}

function formatPriorityWithIcon(priority) {
  const clean = normalizeLabel(priority);
  const icon = PRIORITY_ICONS[clean];
  return icon ? `${icon} ${clean}` : clean;
}

function formatCategoryWithIcon(category) {
  const clean = normalizeLabel(category);
  const icon = CATEGORY_ICONS[clean];
  return icon ? `${icon} ${clean}` : clean;
}

function initMarqueeSelect(select) {
  if (!select) return;
  if (select.classList.contains("status-select")) return;
  if (select.classList.contains("notes-task-select-hidden")) return;
  if (select.parentElement && select.parentElement.classList.contains("select-marquee-wrap")) return;

  const wrapper = document.createElement("div");
  wrapper.className = "select-marquee-wrap";
  select.parentNode.insertBefore(wrapper, select);
  wrapper.append(select);

  const overlay = document.createElement("div");
  overlay.className = "select-marquee-overlay";
  const track = document.createElement("span");
  track.className = "select-marquee-track";
  overlay.append(track);
  wrapper.append(overlay);

  select.classList.add("select-marquee-native");

  const update = () => {
    const selectedOption = select.options[select.selectedIndex];
    const text = selectedOption ? selectedOption.textContent.trim() : "";
    track.textContent = text;

    wrapper.classList.remove("marquee-overflow");
    wrapper.style.removeProperty("--marquee-shift");
    wrapper.style.removeProperty("--marquee-duration");

    const visibleWidth = overlay.clientWidth;
    if (!visibleWidth) return;

    const overflow = track.scrollWidth - visibleWidth;
    if (overflow <= 2) return;

    const shiftPx = Math.ceil(overflow + 24);
    const durationSec = Math.max(4, Math.min(18, shiftPx / 20));
    wrapper.classList.add("marquee-overflow");
    wrapper.style.setProperty("--marquee-shift", `-${shiftPx}px`);
    wrapper.style.setProperty("--marquee-duration", `${durationSec}s`);
  };

  const scheduleUpdate = () => window.requestAnimationFrame(update);
  select.addEventListener("change", scheduleUpdate);
  window.addEventListener("resize", scheduleUpdate);

  if ("ResizeObserver" in window) {
    const resizeObserver = new ResizeObserver(scheduleUpdate);
    resizeObserver.observe(wrapper);
  }

  const mutationObserver = new MutationObserver(scheduleUpdate);
  mutationObserver.observe(select, {
    childList: true,
    subtree: true,
    characterData: true
  });

  scheduleUpdate();
}

function initMarqueeSelects() {
  document
    .querySelectorAll("select:not(.status-select):not(.notes-task-select-hidden)")
    .forEach((select) => initMarqueeSelect(select));
}

function initMarqueePlaceholderInput(input) {
  if (!input) return;
  if (input.parentElement && input.parentElement.classList.contains("input-marquee-wrap")) return;

  const placeholderText = String(input.getAttribute("placeholder") || "").trim();
  if (!placeholderText) return;

  const wrapper = document.createElement("div");
  wrapper.className = "input-marquee-wrap";
  input.parentNode.insertBefore(wrapper, input);
  wrapper.append(input);

  const overlay = document.createElement("div");
  overlay.className = "input-marquee-overlay";
  const track = document.createElement("span");
  track.className = "input-marquee-track";
  track.textContent = placeholderText;
  overlay.append(track);
  wrapper.append(overlay);

  input.classList.add("input-marquee-native");
  input.setAttribute("placeholder", "");

  const update = () => {
    const shouldShow = !input.value && document.activeElement !== input;
    wrapper.classList.toggle("input-marquee-visible", shouldShow);
    wrapper.classList.remove("marquee-overflow");
    wrapper.style.removeProperty("--marquee-shift");
    wrapper.style.removeProperty("--marquee-duration");
    if (!shouldShow) return;

    const visibleWidth = overlay.clientWidth;
    if (!visibleWidth) return;
    const overflow = track.scrollWidth - visibleWidth;
    if (overflow <= 2) return;

    const shiftPx = Math.ceil(overflow + 24);
    const durationSec = Math.max(4, Math.min(18, shiftPx / 20));
    wrapper.classList.add("marquee-overflow");
    wrapper.style.setProperty("--marquee-shift", `-${shiftPx}px`);
    wrapper.style.setProperty("--marquee-duration", `${durationSec}s`);
  };

  const scheduleUpdate = () => window.requestAnimationFrame(update);
  input.addEventListener("input", scheduleUpdate);
  input.addEventListener("focus", scheduleUpdate);
  input.addEventListener("blur", scheduleUpdate);
  window.addEventListener("resize", scheduleUpdate);

  if ("ResizeObserver" in window) {
    const resizeObserver = new ResizeObserver(scheduleUpdate);
    resizeObserver.observe(wrapper);
  }

  scheduleUpdate();
}

function applyTheme(theme) {
  const light = theme === "light";
  document.body.classList.toggle("light-theme", light);
  els.themeLightBtn.classList.toggle("active", light);
  els.themeDarkBtn.classList.toggle("active", !light);
  localStorage.setItem("tasktide-theme", light ? "light" : "dark");
}

function authTokenStorageKey() {
  return "tasktide-auth-token";
}

function setAuthToken(token) {
  appState.authToken = token || null;
  if (appState.authToken) {
    localStorage.setItem(authTokenStorageKey(), appState.authToken);
  } else {
    localStorage.removeItem(authTokenStorageKey());
  }
}

function getUserDisplayName(user) {
  if (!user) return "Гость";
  return String(user.username || user.email || "Пользователь").trim() || "Пользователь";
}

function getUserInitials(user) {
  const source = getUserDisplayName(user);
  const parts = source.split(/\s+/).filter(Boolean);
  if (!parts.length) return "U";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0] || ""}${parts[1][0] || ""}`.toUpperCase();
}

function renderProfile() {
  if (els.profileName) {
    els.profileName.textContent = getUserDisplayName(appState.currentUser);
  }
  if (els.profileAvatar) {
    els.profileAvatar.textContent = getUserInitials(appState.currentUser);
  }
  if (els.profileAuthBtn) {
    els.profileAuthBtn.textContent = appState.currentUser ? "Аккаунт" : "Войти";
  }
}

function showAuthError(message) {
  if (!els.authErrorText) return;
  const text = String(message || "").trim();
  if (!text) {
    els.authErrorText.classList.add("hidden");
    els.authErrorText.textContent = "";
    return;
  }
  els.authErrorText.classList.remove("hidden");
  els.authErrorText.textContent = text;
}

function setAuthMode(mode) {
  appState.authMode = mode === "register" ? "register" : "login";
  const register = appState.authMode === "register";
  if (els.authTabLoginBtn) els.authTabLoginBtn.classList.toggle("active", !register);
  if (els.authTabRegisterBtn) els.authTabRegisterBtn.classList.toggle("active", register);
  if (els.authNameRow) els.authNameRow.classList.toggle("hidden", !register);
  if (els.authModalTitle) els.authModalTitle.textContent = register ? "Регистрация" : "Вход в аккаунт";
  if (els.authSubmitBtn) els.authSubmitBtn.textContent = register ? "Создать аккаунт" : "Войти";
  showAuthError("");
}

function showAuthModal(force = false) {
  if (!els.authModal) return;
  if (!force && appState.currentUser) return;
  els.authModal.classList.remove("hidden");
  setAuthMode(appState.authMode || "login");
  if (els.authLogoutBtn) {
    els.authLogoutBtn.classList.toggle("hidden", !appState.currentUser);
  }
  if (els.authCancelBtn) {
    els.authCancelBtn.classList.toggle("hidden", !appState.currentUser);
  }
}

function hideAuthModal() {
  if (!els.authModal) return;
  els.authModal.classList.add("hidden");
  showAuthError("");
}

function applyAuthSuccess(payload) {
  if (!payload || !payload.token || !payload.user) return;
  setAuthToken(payload.token);
  appState.currentUser = payload.user;
  renderProfile();
  hideAuthModal();
}

async function fetchCurrentUser() {
  const data = await api("/auth/me");
  appState.currentUser = data.user || null;
  renderProfile();
}

function notificationStorageKey() {
  return "tasktide-deadline-notification-settings";
}

function notificationSentStorageKey() {
  return "tasktide-deadline-notification-sent";
}

function cloneDefaultNotificationSettings() {
  return {
    enabled: DEFAULT_NOTIFICATION_SETTINGS.enabled,
    sound: DEFAULT_NOTIFICATION_SETTINGS.sound,
    points: { ...DEFAULT_NOTIFICATION_SETTINGS.points }
  };
}

function normalizeNotificationSettings(raw) {
  const fallback = cloneDefaultNotificationSettings();
  if (!raw || typeof raw !== "object") return fallback;
  const points = raw.points && typeof raw.points === "object" ? raw.points : {};
  return {
    enabled: Boolean(raw.enabled),
    sound: raw.sound === undefined ? DEFAULT_NOTIFICATION_SETTINGS.sound : Boolean(raw.sound),
    points: {
      month: Boolean(points.month),
      week: Boolean(points.week),
      day: Boolean(points.day),
      h6: Boolean(points.h6),
      h1: Boolean(points.h1),
      m30: Boolean(points.m30),
      m5: Boolean(points.m5)
    }
  };
}

function loadNotificationSettings() {
  try {
    const raw = localStorage.getItem(notificationStorageKey());
    if (!raw) return cloneDefaultNotificationSettings();
    return normalizeNotificationSettings(JSON.parse(raw));
  } catch {
    return cloneDefaultNotificationSettings();
  }
}

function saveNotificationSettings() {
  if (!appState.notificationSettings) return;
  localStorage.setItem(notificationStorageKey(), JSON.stringify(appState.notificationSettings));
}

function loadSentDeadlineNotifications() {
  try {
    const raw = localStorage.getItem(notificationSentStorageKey());
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function saveSentDeadlineNotifications() {
  localStorage.setItem(notificationSentStorageKey(), JSON.stringify(sentDeadlineNotifications));
}

function renderNotificationSettings() {
  const settings = appState.notificationSettings || cloneDefaultNotificationSettings();
  const enabled = settings.enabled;

  if (els.notifyEnabledInput) els.notifyEnabledInput.checked = enabled;
  if (els.notifySoundInput) els.notifySoundInput.checked = !!settings.sound;
  if (els.notifyMonthInput) els.notifyMonthInput.checked = !!settings.points.month;
  if (els.notifyWeekInput) els.notifyWeekInput.checked = !!settings.points.week;
  if (els.notifyDayInput) els.notifyDayInput.checked = !!settings.points.day;
  if (els.notify6hInput) els.notify6hInput.checked = !!settings.points.h6;
  if (els.notify1hInput) els.notify1hInput.checked = !!settings.points.h1;
  if (els.notify30mInput) els.notify30mInput.checked = !!settings.points.m30;
  if (els.notify5mInput) els.notify5mInput.checked = !!settings.points.m5;

  const pointInputs = [
    els.notifyMonthInput,
    els.notifyWeekInput,
    els.notifyDayInput,
    els.notify6hInput,
    els.notify1hInput,
    els.notify30mInput,
    els.notify5mInput
  ];
  pointInputs.forEach((input) => {
    if (!input) return;
    input.disabled = !enabled;
  });
  if (els.notifySoundInput) {
    els.notifySoundInput.disabled = !enabled;
  }

  if (!els.notifySettingsStatus) return;
  if (!enabled) {
    els.notifySettingsStatus.textContent = "Уведомления выключены.";
    return;
  }
  const activeLabels = DEADLINE_NOTIFICATION_INTERVALS
    .filter((interval) => settings.points[interval.key])
    .map((interval) => interval.label);
  const soundLabel = settings.sound ? "звук: вкл." : "звук: выкл.";
  els.notifySettingsStatus.textContent = activeLabels.length
    ? `Активные точки: ${activeLabels.join(", ")}. ${soundLabel} Проверка каждую минуту.`
    : `Уведомления включены, но интервалы не выбраны (${soundLabel}).`;
}

function playNotificationSound() {
  const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextCtor) return;
  try {
    const ctx = new AudioContextCtor();
    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(920, now);
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(0.16, now + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.22);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.23);
    osc.onended = () => {
      ctx.close().catch(() => {});
    };
  } catch {
    // no-op
  }
}

function ensureInAppToastRoot() {
  let root = document.getElementById("inAppToastRoot");
  if (root) return root;
  root = document.createElement("div");
  root.id = "inAppToastRoot";
  root.className = "in-app-toast-root";
  document.body.append(root);
  return root;
}

function showInAppToast(title, body) {
  const root = ensureInAppToastRoot();
  const toast = document.createElement("div");
  toast.className = "in-app-toast";
  toast.innerHTML = `
    <div class="in-app-toast-head">
      <div class="in-app-toast-title">${escapeHtml(title)}</div>
      <button class="in-app-toast-close" type="button" aria-label="Закрыть уведомление">✕</button>
    </div>
    <div class="in-app-toast-body">${escapeHtml(body)}</div>
  `;
  root.append(toast);

  const closeBtn = toast.querySelector(".in-app-toast-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      toast.classList.add("hide");
      setTimeout(() => {
        toast.remove();
      }, 220);
    });
  }
}

async function ensureNotificationPermission() {
  if (window.tasktideNative && typeof window.tasktideNative.showSystemNotification === "function") {
    return true;
  }
  if (!("Notification" in window)) return false;
  if (Notification.permission === "granted") return true;
  if (Notification.permission === "denied") return false;
  try {
    const result = await Notification.requestPermission();
    return result === "granted";
  } catch {
    return false;
  }
}

function toNotificationPointKey(inputId) {
  if (inputId === "notifyMonthInput") return "month";
  if (inputId === "notifyWeekInput") return "week";
  if (inputId === "notifyDayInput") return "day";
  if (inputId === "notify6hInput") return "h6";
  if (inputId === "notify1hInput") return "h1";
  if (inputId === "notify30mInput") return "m30";
  if (inputId === "notify5mInput") return "m5";
  return null;
}

function buildDeadlineNotificationKey(taskId, deadlineMs, intervalKey) {
  return `${taskId}|${deadlineMs}|${intervalKey}`;
}

function cleanupSentNotificationKeys() {
  const aliveTaskDeadlines = new Map();
  (appState.tasks || []).forEach((task) => {
    const parsed = parseLocalDeadline(task.deadline);
    if (!parsed) return;
    aliveTaskDeadlines.set(String(task.id), String(parsed.getTime()));
  });
  let changed = false;
  Object.keys(sentDeadlineNotifications).forEach((key) => {
    const [taskId, deadlineMs] = key.split("|");
    const aliveDeadline = aliveTaskDeadlines.get(String(taskId || ""));
    if (!aliveDeadline || String(deadlineMs || "") !== aliveDeadline) {
      delete sentDeadlineNotifications[key];
      changed = true;
    }
  });
  if (changed) {
    saveSentDeadlineNotifications();
  }
}

function showDeadlineNotification(task, intervalLabel) {
  const nowMs = Date.now();
  const deadline = parseLocalDeadline(task.deadline);
  const remainingMs = deadline ? Math.max(0, deadline.getTime() - nowMs) : 0;
  const totalMinutes = Math.floor(remainingMs / 60000);
  const days = Math.floor(totalMinutes / (24 * 60));
  const hours = Math.floor((totalMinutes % (24 * 60)) / 60);
  const minutes = totalMinutes % 60;
  const remainingText = `${days}д ${hours}ч ${minutes}м`;
  const title = "TaskTide: напоминание о дедлайне";
  const body = `${task.name}: уведомление ${intervalLabel}. Осталось: ${remainingText}. Дедлайн: ${task.deadline || "не указан"}.`;
  const settings = appState.notificationSettings || cloneDefaultNotificationSettings();
  showInAppToast(title, body);
  if (window.tasktideNative && typeof window.tasktideNative.showSystemNotification === "function") {
    window.tasktideNative.showSystemNotification({ title, body, silent: false }).catch(() => {});
  } else {
    try {
      new Notification(title, { body, silent: false });
    } catch {
      // no-op
    }
  }
  if (settings.enabled && settings.sound) {
    playNotificationSound();
  }
}

async function runDeadlineNotificationCheck() {
  const settings = appState.notificationSettings;
  if (!settings || !settings.enabled) return;
  const activeIntervals = DEADLINE_NOTIFICATION_INTERVALS.filter((interval) => settings.points[interval.key]);
  if (!activeIntervals.length) return;

  const hasPermission = await ensureNotificationPermission();
  if (!hasPermission) return;

  cleanupSentNotificationKeys();
  const nowMs = Date.now();
  const toleranceMs = 60 * 1000;
  let changed = false;

  (appState.tasks || []).forEach((task) => {
    if (task.status === "выполнена") return;
    const deadline = parseLocalDeadline(task.deadline);
    if (!deadline) return;
    const deadlineMs = deadline.getTime();
    const remainingMs = deadlineMs - nowMs;
    if (remainingMs < -toleranceMs) return;

    activeIntervals.forEach((interval) => {
      const inWindow = Math.abs(remainingMs - interval.ms) <= toleranceMs;
      if (!inWindow) return;

      const notificationKey = buildDeadlineNotificationKey(task.id, deadlineMs, interval.key);
      if (sentDeadlineNotifications[notificationKey]) return;
      showDeadlineNotification(task, interval.label);
      sentDeadlineNotifications[notificationKey] = true;
      changed = true;
    });
  });

  if (changed) {
    saveSentDeadlineNotifications();
  }
}

function startNotificationTicker() {
  if (notificationTickerId) return;
  notificationTickerId = setInterval(() => {
    runDeadlineNotificationCheck().catch(() => {});
  }, 60 * 1000);
}

async function api(path, options = {}) {
  const authHeaders = {};
  if (appState.authToken) {
    authHeaders.Authorization = `Bearer ${appState.authToken}`;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
      ...(options.headers || {})
    },
    ...options
  });
  if (!res.ok) {
    const text = await res.text();
    let message = text || `API error ${res.status}`;
    try {
      const parsed = JSON.parse(text);
      if (parsed && parsed.error) message = parsed.error;
    } catch {
      // keep raw text
    }
    const error = new Error(message);
    error.status = res.status;
    throw error;
  }
  if (res.status === 204) return null;
  return res.json();
}

function switchView(name) {
  appState.currentView = name;
  els.viewButtons.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.viewBtn === name);
  });
  els.views.forEach((view) => {
    view.classList.toggle("active", view.id === `view-${name}`);
  });
  if (els.viewTitle) {
    els.viewTitle.textContent = VIEW_TITLES[name] || "Статистика";
    pulseElement(els.viewTitle);
  }
  if (name === "graphs") {
    if (!graphsEntryAnimationPlayed) {
      shouldPlayGraphsEntryAnimation = true;
    }
    renderGraphsFromState();
  }
}

function pulseElement(el) {
  if (!el) return;
  el.classList.remove("stat-refresh");
  // Force reflow so repeated updates retrigger the short animation.
  void el.offsetWidth;
  el.classList.add("stat-refresh");
  window.setTimeout(() => {
    el.classList.remove("stat-refresh");
  }, 220);
}

function pulseTaskStatNumbers() {
  [
    els.statTotal,
    els.statCompleted,
    els.statProgress,
    els.statTodo,
    els.pillTotal,
    els.pillDone,
    els.pillOverdue,
    els.completionRate,
    els.graphStatusTotal,
    els.graphDoneCount,
    els.graphProgressCount,
    els.graphTodoCount,
    els.graphOverdueCount
  ].forEach((el) => pulseElement(el));
}

function waitMs(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function prefersReducedMotion() {
  return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function readFirstIntFromText(value) {
  const match = String(value || "").match(/-?\d+/);
  return match ? Number(match[0]) : 0;
}

function animateCountText(el, toValue, options = {}) {
  if (!el) return;
  const { prefix = "", suffix = "", duration = 760, formatter } = options;
  const nextValue = Number(toValue || 0);
  if (!Number.isFinite(nextValue)) {
    el.textContent = `${prefix}${toValue}${suffix}`;
    return;
  }
  const fromValue = readFirstIntFromText(el.textContent);
  const render = typeof formatter === "function"
    ? (value) => formatter(value)
    : (value) => `${prefix}${value}${suffix}`;

  if (prefersReducedMotion() || fromValue === nextValue) {
    el.textContent = render(nextValue);
    return;
  }

  const runningFrame = animatedCountFrames.get(el);
  if (runningFrame) {
    window.cancelAnimationFrame(runningFrame);
  }

  const start = performance.now();
  const delta = nextValue - fromValue;
  const step = (now) => {
    const progress = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(fromValue + delta * eased);
    el.textContent = render(current);
    if (progress < 1) {
      const rafId = window.requestAnimationFrame(step);
      animatedCountFrames.set(el, rafId);
    } else {
      animatedCountFrames.delete(el);
      el.textContent = render(nextValue);
    }
  };
  const rafId = window.requestAnimationFrame(step);
  animatedCountFrames.set(el, rafId);
}

function donutGradientByPercents(donePct, progressPct, todoPct) {
  const safeDone = Math.max(0, Math.min(100, Number(donePct) || 0));
  const safeProgress = Math.max(0, Math.min(100 - safeDone, Number(progressPct) || 0));
  const safeTodo = Math.max(0, Math.min(100 - safeDone - safeProgress, Number(todoPct) || 0));
  const doneEnd = safeDone;
  const progressEnd = doneEnd + safeProgress;
  const todoEnd = progressEnd + safeTodo;
  return `conic-gradient(
    #6fd18c 0 ${doneEnd}%,
    #79b8ff ${doneEnd}% ${progressEnd}%,
    #b1b8c9 ${progressEnd}% ${todoEnd}%,
    #ff8a8a ${todoEnd}% 100%
  )`;
}

function animateGraphBarsOnce() {
  const fills = document.querySelectorAll(
    "#view-graphs .graphs-bar-fill, #view-graphs .graphs-week-fill.focus, #view-graphs .graphs-week-fill.done"
  );
  fills.forEach((fill) => {
    const targetWidth = fill.style.width || "0%";
    fill.style.width = "0%";
    fill.classList.add("graphs-fill-animating");
    window.requestAnimationFrame(() => {
      fill.style.width = targetWidth;
    });
    window.setTimeout(() => {
      fill.classList.remove("graphs-fill-animating");
    }, 820);
  });
}

function animateGraphsEntry(donePct, progressPct, todoPct) {
  if (!els.graphStatusDonut || prefersReducedMotion()) return;
  const duration = 720;
  const start = performance.now();
  const tick = (now) => {
    const progress = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - progress, 3);
    els.graphStatusDonut.style.background = donutGradientByPercents(
      donePct * eased,
      progressPct * eased,
      todoPct * eased
    );
    if (progress < 1) {
      window.requestAnimationFrame(tick);
    }
  };
  window.requestAnimationFrame(tick);
}

function parseLocalDeadline(deadlineLabel) {
  if (!deadlineLabel || typeof deadlineLabel !== "string") return null;
  const match = deadlineLabel.match(/^(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2})$/);
  if (!match) return null;
  const [, dd, mm, yyyy, hh, mi] = match;
  return new Date(Number(yyyy), Number(mm) - 1, Number(dd), Number(hh), Number(mi), 0, 0);
}

function formatDeadlineHumanDate(dt) {
  return new Intl.DateTimeFormat("ru-RU", { day: "2-digit", month: "long" }).format(dt);
}

function buildDeadlineCountdown(deadlineLabel) {
  const dt = parseLocalDeadline(deadlineLabel);
  if (!dt) return `Ваш дедлайн: ${deadlineLabel || "не указан"}`;

  const now = new Date();
  const diffMs = Math.max(0, dt.getTime() - now.getTime());
  const totalMinutes = Math.floor(diffMs / 60000);
  const days = Math.floor(totalMinutes / (24 * 60));
  const hours = Math.floor((totalMinutes % (24 * 60)) / 60);
  const minutes = totalMinutes % 60;
  const humanDate = formatDeadlineHumanDate(dt);

  return `Вам осталось: ${String(days).padStart(3, "0")} дней, ${String(hours).padStart(2, "0")} часов, ${String(minutes).padStart(2, "0")} мин. Ваш дедлайн ${humanDate}`;
}

function selectedFocusTaskId() {
  const value = els.focusTaskSelect.value;
  if (!value) return null;
  const parsed = Number(value);
  return Number.isNaN(parsed) ? null : parsed;
}

function updateFocusTaskInfo() {
  const taskId = selectedFocusTaskId();
  if (!taskId) {
    els.focusTaskInfo.textContent = "Задача не выбрана";
    return;
  }
  const task = appState.tasks.find((t) => Number(t.id) === taskId);
  if (!task) {
    els.focusTaskInfo.textContent = "Задача не найдена";
    return;
  }
  els.focusTaskInfo.textContent = `${task.name} · ${task.category} · ${task.status}`;
}

function isTaskOverdue(task) {
  if (!task || task.status === "выполнена") return false;
  const dt = parseLocalDeadline(task.deadline);
  if (!dt) return false;
  return dt < new Date();
}

function compareTasksByDeadlinePriority(a, b) {
  const now = new Date();
  const aDeadline = parseLocalDeadline(a.deadline);
  const bDeadline = parseLocalDeadline(b.deadline);

  // Задачи без дедлайна отправляем вниз.
  if (!aDeadline && !bDeadline) return Number(b.id || 0) - Number(a.id || 0);
  if (!aDeadline) return 1;
  if (!bDeadline) return -1;

  const aOverdue = aDeadline < now;
  const bOverdue = bDeadline < now;

  // Непросроченные выше просроченных.
  if (aOverdue !== bOverdue) return aOverdue ? 1 : -1;

  // Для непросроченных: ближайший дедлайн выше.
  if (!aOverdue) {
    const diff = aDeadline - bDeadline;
    if (diff !== 0) return diff;
  } else {
    // Для просроченных: тот, у кого дедлайн истек позже, выше.
    const diff = bDeadline - aDeadline;
    if (diff !== 0) return diff;
  }

  // Детеминированный тай-брейк для одинаковых дедлайнов.
  return Number(b.id || 0) - Number(a.id || 0);
}

function taskMatchesCurrentFilters(task) {
  if (Number(task.id) === Number(appState.selectedTaskId)) return true;
  const q = appState.searchQuery.trim().toLowerCase();
  const taskPriority = normalizeLabel(task.priority);
  const taskCategory = normalizeLabel(task.category);
  let statusOk = true;
  if (appState.taskFilter === "overdue") {
    statusOk = isTaskOverdue(task);
  }
  if (appState.statusFilter !== "all") {
    statusOk = statusOk && task.status === appState.statusFilter;
  }
  const priorityOk =
    appState.priorityFilter === "all" || taskPriority === appState.priorityFilter;
  const categoryOk =
    appState.categoryFilter === "all" || taskCategory === appState.categoryFilter;

  if (!statusOk || !priorityOk || !categoryOk) return false;
  if (!q) return true;
  const blob = `${task.name} ${taskPriority} ${taskCategory} ${task.description || ""}`.toLowerCase();
  return blob.includes(q);
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function highlightMatch(text, query) {
  const safeText = escapeHtml(text);
  if (!query) return safeText;
  const lowerText = String(text).toLowerCase();
  const lowerQuery = query.toLowerCase();
  const idx = lowerText.indexOf(lowerQuery);
  if (idx < 0) return safeText;
  const before = escapeHtml(String(text).slice(0, idx));
  const match = escapeHtml(String(text).slice(idx, idx + query.length));
  const after = escapeHtml(String(text).slice(idx + query.length));
  return `${before}<mark>${match}</mark>${after}`;
}

function setTaskFilter(filter) {
  appState.taskFilter = filter;
  els.filterPills.forEach((pill) => {
    pill.classList.toggle("active-day", pill.dataset.filter === filter);
  });
  loadTasks().catch(() => {});
}

function closeStatusMenu() {
  if (els.statusFilterMenu) {
    els.statusFilterMenu.classList.remove("open");
  }
}

function toggleStatusMenu() {
  if (!els.statusFilterMenu) return;
  els.statusFilterMenu.classList.toggle("open");
}

function setStatusFilter(status) {
  appState.statusFilter = status || "all";
  if (els.statusFilterOptions) {
    els.statusFilterOptions.forEach((option) => {
      option.classList.toggle("selected", option.dataset.statusFilter === appState.statusFilter);
    });
  }
  if (els.statusFilterBtn) {
    els.statusFilterBtn.classList.toggle("active-day", appState.statusFilter !== "all");
  }
  loadTasks().catch(() => {});
}

function setTaskSearchQuery(query, source = null) {
  appState.searchQuery = query || "";
  if (source !== "top" && els.searchInput) {
    els.searchInput.value = appState.searchQuery;
  }
  loadTasks().catch(() => {});
}

function setTaskDimensionsFilters({ priority, category }) {
  appState.priorityFilter = priority ?? appState.priorityFilter;
  appState.categoryFilter = category ?? appState.categoryFilter;
  if (els.taskPriorityFilter) {
    els.taskPriorityFilter.value = appState.priorityFilter;
  }
  if (els.taskCategoryFilter) {
    els.taskCategoryFilter.value = appState.categoryFilter;
  }
  loadTasks().catch(() => {});
}

function renderProductivityChart({ completed, inProgress, notStarted, overdue }) {
  if (!els.productivityChart) return;
  const values = [
    { key: "done", label: "Выполнено", value: Number(completed || 0), cls: "done" },
    { key: "progress", label: "В процессе", value: Number(inProgress || 0), cls: "progress" },
    { key: "todo", label: "Не начато", value: Number(notStarted || 0), cls: "todo" },
    { key: "overdue", label: "Просрочено", value: Number(overdue || 0), cls: "overdue" }
  ];

  const maxValue = Math.max(1, ...values.map((item) => item.value));
  els.productivityChart.innerHTML = values
    .map((item) => {
      const width = Math.round((item.value / maxValue) * 100);
      return `
        <div class="chart-row">
          <div class="chart-label">${item.label}</div>
          <div class="chart-track"><div class="chart-fill ${item.cls}" style="width:${width}%"></div></div>
          <div class="chart-value">${item.value}</div>
        </div>
      `;
    })
    .join("");
}

function renderCountBars(targetEl, countMap, colorClass) {
  if (!targetEl) return;
  const entries = Object.entries(countMap || {}).filter(([, value]) => Number(value) > 0);
  if (!entries.length) {
    targetEl.innerHTML = `<div class="task-meta">Пока нет данных</div>`;
    return;
  }
  const maxValue = Math.max(1, ...entries.map(([, value]) => Number(value)));
  targetEl.innerHTML = entries
    .sort((a, b) => Number(b[1]) - Number(a[1]))
    .map(([label, value]) => {
      const width = Math.max(6, Math.round((Number(value) / maxValue) * 100));
      return `
        <div class="graphs-bar-row">
          <div class="graphs-bar-label">${escapeHtml(label)}</div>
          <div class="graphs-bar-track"><div class="graphs-bar-fill ${colorClass}" style="width:${width}%"></div></div>
          <div class="graphs-bar-value">${value}</div>
        </div>
      `;
    })
    .join("");
}

function renderWeeklyGraph(tasks, sessions) {
  if (!els.graphWeeklyBars) return;
  const today = new Date();
  const days = [];
  for (let i = 6; i >= 0; i -= 1) {
    const day = new Date(today.getFullYear(), today.getMonth(), today.getDate() - i);
    days.push(day);
  }

  const makeDayKey = (date) =>
    `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
  const dayKeys = days.map(makeDayKey);
  const focusByDay = Object.fromEntries(dayKeys.map((k) => [k, 0]));
  const doneByDay = Object.fromEntries(dayKeys.map((k) => [k, 0]));

  (sessions || []).forEach((session) => {
    const dt = new Date(session.created_at);
    if (Number.isNaN(dt.getTime())) return;
    const key = makeDayKey(dt);
    if (!(key in focusByDay)) return;
    focusByDay[key] += Number(session.duration_minutes || 0);
  });

  (tasks || []).forEach((task) => {
    if (task.status !== "выполнена") return;
    const dt = new Date(task.updated_at || task.created_at || "");
    if (Number.isNaN(dt.getTime())) return;
    const key = makeDayKey(dt);
    if (!(key in doneByDay)) return;
    doneByDay[key] += 1;
  });

  const maxFocus = Math.max(1, ...Object.values(focusByDay));
  const maxDone = Math.max(1, ...Object.values(doneByDay));
  const formatDay = (date) =>
    new Intl.DateTimeFormat("ru-RU", { weekday: "short", day: "2-digit" }).format(date).replace(".", "");

  els.graphWeeklyBars.innerHTML = days
    .map((day) => {
      const key = makeDayKey(day);
      const focusWidth = Math.max(4, Math.round((focusByDay[key] / maxFocus) * 100));
      const doneWidth = Math.max(4, Math.round((doneByDay[key] / maxDone) * 100));
      return `
        <div class="graphs-week-row">
          <div class="graphs-week-label">${escapeHtml(formatDay(day))}</div>
          <div class="graphs-week-tracks">
            <div class="graphs-week-track"><div class="graphs-week-fill focus" style="width:${focusWidth}%"></div></div>
            <div class="graphs-week-track"><div class="graphs-week-fill done" style="width:${doneWidth}%"></div></div>
          </div>
          <div class="graphs-week-value">${focusByDay[key]}м / ${doneByDay[key]}</div>
        </div>
      `;
    })
    .join("");
}

function toDayKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function daysBack(count) {
  const base = new Date();
  return Array.from({ length: count }, (_, idx) => {
    const delta = count - idx - 1;
    return new Date(base.getFullYear(), base.getMonth(), base.getDate() - delta);
  });
}

function buildLineSvg(seriesList) {
  const width = 560;
  const height = 180;
  const padding = 18;
  const pointCount = Math.max(1, ...seriesList.map((s) => s.values.length));
  const allValues = seriesList.flatMap((s) => s.values);
  const maxValue = Math.max(1, ...allValues);

  const xFor = (index) =>
    pointCount <= 1 ? width / 2 : padding + (index * (width - padding * 2)) / (pointCount - 1);
  const yFor = (value) => height - padding - (Number(value || 0) / maxValue) * (height - padding * 2);

  const pathFor = (values) =>
    values
      .map((value, index) => `${index === 0 ? "M" : "L"} ${xFor(index).toFixed(2)} ${yFor(value).toFixed(2)}`)
      .join(" ");

  const gridLines = [0.25, 0.5, 0.75].map((k) => {
    const y = padding + (height - padding * 2) * k;
    return `<line class="graphs-grid-line" x1="${padding}" y1="${y.toFixed(2)}" x2="${(width - padding).toFixed(2)}" y2="${y.toFixed(2)}"></line>`;
  });

  const paths = seriesList
    .map(
      (series) =>
        `<path class="graphs-series" style="stroke:${series.color}" d="${pathFor(series.values)}"></path>`
    )
    .join("");

  const legends = seriesList
    .map(
      (series) =>
        `<span><span class="graphs-carousel-dot" style="color:${series.color}">●</span>${escapeHtml(series.label)}</span>`
    )
    .join("");

  return `
    <svg class="graphs-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
      ${gridLines.join("")}
      ${paths}
    </svg>
    <div class="graphs-carousel-legend">${legends}</div>
  `;
}

function buildPieHtml(mapObj, palette) {
  const entries = Object.entries(mapObj || {}).filter(([, v]) => Number(v) > 0);
  if (!entries.length) {
    return `<div class="task-meta">Пока нет данных</div>`;
  }
  const total = entries.reduce((sum, [, v]) => sum + Number(v), 0);
  let start = 0;
  const segments = entries.map(([label, value], idx) => {
    const percent = (Number(value) / total) * 100;
    const color = palette[idx % palette.length];
    const segment = `${color} ${start.toFixed(2)}% ${(start + percent).toFixed(2)}%`;
    start += percent;
    return { label, value, color, segment };
  });
  const gradient = `conic-gradient(${segments.map((s) => s.segment).join(", ")})`;
  const legend = segments
    .map(
      (s) =>
        `<span><span class="graphs-carousel-dot" style="color:${s.color}">●</span>${escapeHtml(s.label)}: ${s.value}</span>`
    )
    .join("");
  return `
    <div class="graphs-carousel-pie" style="background:${gradient}"></div>
    <div class="graphs-carousel-legend">${legend}</div>
  `;
}

function buildPriorityPieDetailedHtml(tasks) {
  const priorityOrder = [
    "Важно - Срочно",
    "Важно - Не срочно",
    "Не важно - Срочно",
    "Не важно - Не срочно"
  ];
  const palette = ["#2ec6df", "#6a2de2", "#a33bd8", "#f34a98", "#ece168", "#4fd0ff"];
  const counts = (tasks || []).reduce((acc, task) => {
    const key = normalizeLabel(task.priority) || "Без приоритета";
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});

  const ordered = [
    ...priorityOrder.filter((key) => counts[key] > 0).map((key) => [key, counts[key]]),
    ...Object.entries(counts).filter(([key]) => !priorityOrder.includes(key) && counts[key] > 0)
  ];

  if (!ordered.length) {
    return `<div class="task-meta">Пока нет данных</div>`;
  }

  const total = ordered.reduce((sum, [, value]) => sum + Number(value), 0);
  let start = 0;
  const segments = ordered.map(([label, value], idx) => {
    const percent = (Number(value) / total) * 100;
    const color = palette[idx % palette.length];
    const segment = `${color} ${start.toFixed(2)}% ${(start + percent).toFixed(2)}%`;
    start += percent;
    return { label, value, color, segment };
  });

  const gradient = `conic-gradient(${segments.map((s) => s.segment).join(", ")})`;
  const legend = segments
    .map(
      (s) =>
        `<div class="graphs-pie-legend-item"><span class="dot" style="color:${s.color}">●</span>${escapeHtml(s.label)}: ${s.value}</div>`
    )
    .join("");

  return `
    <div class="graphs-carousel-pie" style="background:${gradient}"></div>
    <div class="graphs-pie-legend-grid">${legend}</div>
  `;
}

function buildGraphSlides(tasks, sessions) {
  const recentSessions = (sessions || []).slice(0, 12).reverse();
  const workSessionValues = recentSessions.map((s) => (s.session_type === "pomodoro" ? Number(s.duration_minutes || 0) : 0));
  const breakSessionValues = recentSessions.map((s) =>
    s.session_type === "short_break" || s.session_type === "long_break" ? Number(s.duration_minutes || 0) : 0
  );

  const dayList = daysBack(14);
  const dayKeys = dayList.map((d) => toDayKey(d));
  const createdByDay = Object.fromEntries(dayKeys.map((k) => [k, 0]));
  const completedByDay = Object.fromEntries(dayKeys.map((k) => [k, 0]));
  const focusByDay = Object.fromEntries(dayKeys.map((k) => [k, 0]));
  const overdueByDay = Object.fromEntries(dayKeys.map((k) => [k, 0]));

  (tasks || []).forEach((task) => {
    const created = new Date(task.created_at || "");
    if (!Number.isNaN(created.getTime())) {
      const key = toDayKey(created);
      if (key in createdByDay) createdByDay[key] += 1;
    }
    if (task.status === "выполнена") {
      const completed = new Date(task.updated_at || "");
      if (!Number.isNaN(completed.getTime())) {
        const key = toDayKey(completed);
        if (key in completedByDay) completedByDay[key] += 1;
      }
    }
    if (isTaskOverdue(task)) {
      const deadline = parseLocalDeadline(task.deadline);
      if (deadline) {
        const key = toDayKey(deadline);
        if (key in overdueByDay) overdueByDay[key] += 1;
      }
    }
  });

  (sessions || []).forEach((session) => {
    const dt = new Date(session.created_at || "");
    if (Number.isNaN(dt.getTime())) return;
    const key = toDayKey(dt);
    if (!(key in focusByDay)) return;
    focusByDay[key] += Number(session.duration_minutes || 0);
  });

  const priorityCounts = (tasks || []).reduce((acc, task) => {
    const key = String(task.priority || "Без приоритета");
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});

  return [
    {
      title: "Фокус: работа и перерывы",
      sub: "Последние 12 сессий (минуты)",
      html: buildLineSvg([
        { label: "Работа", color: "#ece168", values: workSessionValues.length ? workSessionValues : [0] },
        { label: "Перерывы", color: "#ff4d94", values: breakSessionValues.length ? breakSessionValues : [0] }
      ])
    },
    {
      title: "Создано vs выполнено",
      sub: "Последние 14 дней",
      html: buildLineSvg([
        { label: "Создано", color: "#79b8ff", values: dayKeys.map((k) => createdByDay[k]) },
        { label: "Выполнено", color: "#ece168", values: dayKeys.map((k) => completedByDay[k]) }
      ])
    },
    {
      title: "Фокус vs просрочки",
      sub: "Последние 14 дней",
      html: buildLineSvg([
        { label: "Фокус (мин)", color: "#6fd18c", values: dayKeys.map((k) => focusByDay[k]) },
        { label: "Просрочки", color: "#ff4d94", values: dayKeys.map((k) => overdueByDay[k]) }
      ])
    },
    {
      title: "Структура по приоритетам",
      sub: "Доля задач по важности",
      html: buildPieHtml(priorityCounts, ["#28c3df", "#6a2de2", "#a738d8", "#ff4d94", "#ece168"])
    }
  ];
}

function renderExtraGraphsFromState() {
  if (!els.graphsExtraList) return;
  const slides = buildGraphSlides(appState.tasks || [], appState.focusSessions || []);
  if (!slides.length) return;
  els.graphsExtraList.innerHTML = slides
    .map(
      (slide) => `
        <section class="graphs-extra-item">
          <div class="graphs-carousel-title-wrap">
            <h3>${escapeHtml(slide.title)}</h3>
            <div class="graphs-carousel-sub">${escapeHtml(slide.sub)}</div>
          </div>
          <div class="graphs-carousel-stage">${slide.html}</div>
        </section>
      `
    )
    .join("");
}

function renderGraphsFromState() {
  if (!els.graphStatusDonut) return;
  const tasks = appState.tasks || [];
  const focusSessions = appState.focusSessions || [];
  const done = tasks.filter((t) => t.status === "выполнена").length;
  const inProgress = tasks.filter((t) => t.status === "в процессе").length;
  const notStarted = tasks.filter((t) => t.status === "не начата").length;
  const overdue = tasks.filter((t) => isTaskOverdue(t)).length;
  const total = tasks.length;
  const shouldAnimateEntry = shouldPlayGraphsEntryAnimation && !graphsEntryAnimationPlayed;

  if (els.graphStatusTotal) animateCountText(els.graphStatusTotal, total, { duration: 760 });
  if (els.graphDoneCount) animateCountText(els.graphDoneCount, done, { duration: 760 });
  if (els.graphProgressCount) animateCountText(els.graphProgressCount, inProgress, { duration: 760 });
  if (els.graphTodoCount) animateCountText(els.graphTodoCount, notStarted, { duration: 760 });
  if (els.graphOverdueCount) animateCountText(els.graphOverdueCount, overdue, { duration: 760 });
  pulseElement(els.graphStatusTotal);
  pulseElement(els.graphDoneCount);
  pulseElement(els.graphProgressCount);
  pulseElement(els.graphTodoCount);
  pulseElement(els.graphOverdueCount);

  if (!total) {
    els.graphStatusDonut.style.background = "conic-gradient(#414a61 0 100%)";
  } else {
    const donePct = (done / total) * 100;
    const progressPct = (inProgress / total) * 100;
    const todoPct = (notStarted / total) * 100;
    if (shouldAnimateEntry) {
      animateGraphsEntry(donePct, progressPct, todoPct);
    } else {
      els.graphStatusDonut.style.background = donutGradientByPercents(donePct, progressPct, todoPct);
    }
  }

  const priorityCounts = tasks.reduce((acc, task) => {
    const key = String(task.priority || "Без приоритета");
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  const categoryCounts = tasks.reduce((acc, task) => {
    const key = String(task.category || "Без места");
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});

  renderCountBars(els.graphPriorityBars, priorityCounts, "priority");
  renderCountBars(els.graphCategoryBars, categoryCounts, "category");
  renderWeeklyGraph(tasks, focusSessions);
  renderExtraGraphsFromState();
  if (shouldAnimateEntry) {
    animateGraphBarsOnce();
    graphsEntryAnimationPlayed = true;
    shouldPlayGraphsEntryAnimation = false;
  }

  if (els.graphsUpdatedAt) {
    els.graphsUpdatedAt.textContent = `Обновление: ${new Date().toLocaleString("ru-RU")}`;
    pulseElement(els.graphsUpdatedAt);
  }
}

function buildReportCardMarkup({ nextDeadlineTask, completed, inProgress, notStarted, overdue, focusMinutes }) {
  const metricsMarkup = `
    <div class="report-stats-grid">
      <div class="report-stat">
        <span>Выполнено</span>
        <strong>${completed}</strong>
      </div>
      <div class="report-stat">
        <span>В процессе</span>
        <strong>${inProgress}</strong>
      </div>
      <div class="report-stat">
        <span>Не начато</span>
        <strong>${notStarted}</strong>
      </div>
      <div class="report-stat">
        <span>Просрочено</span>
        <strong>${overdue}</strong>
      </div>
    </div>
  `;

  if (!nextDeadlineTask) {
    return `
      <div class="report-empty">Активных дедлайнов нет</div>
      ${metricsMarkup}
    `;
  }

  const deadlineDt = parseLocalDeadline(nextDeadlineTask.deadline);
  const now = new Date();
  let etaText = "срок не определён";
  if (deadlineDt) {
    const totalMinutes = Math.max(0, Math.floor((deadlineDt.getTime() - now.getTime()) / 60000));
    const days = Math.floor(totalMinutes / (24 * 60));
    const hours = Math.floor((totalMinutes % (24 * 60)) / 60);
    const minutes = totalMinutes % 60;
    etaText = `через ${days}д ${hours}ч ${minutes}м`;
  }

  return `
    <div class="report-hero">
      <div class="report-eyebrow">Ближайший дедлайн</div>
      <div class="report-title">${escapeHtml(nextDeadlineTask.name || "Без названия")}</div>
      <div class="report-meta">${escapeHtml(nextDeadlineTask.deadline || "не указан")} · ${etaText}</div>
    </div>
    ${metricsMarkup}
  `;
}

function updateDashboardCardsFromState() {
  const overview = appState.overview || {};
  const stats = overview.stats || {};
  const focus = overview.focus || {};
  const tasks = appState.tasks || [];

  const total = Number(stats.total || 0);
  const completed = Number(stats.completed || 0);
  const activeTasks = tasks.filter((t) => t.status !== "выполнена");
  const overdue = activeTasks.filter((t) => isTaskOverdue(t)).length;

  const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;
  animateCountText(els.pillTotal, total, { prefix: "Всего ", duration: 760 });
  animateCountText(els.pillDone, completed, { prefix: "Выполнено ", duration: 760 });
  animateCountText(els.pillOverdue, overdue, { prefix: "Просрочено ", duration: 760 });
  animateCountText(els.completionRate, completionRate, { suffix: "%", duration: 760 });
  els.completionSub.textContent = `${completed} из ${total} задач выполнено`;
  pulseElement(els.pillTotal);
  pulseElement(els.pillDone);
  pulseElement(els.pillOverdue);
  pulseElement(els.completionRate);
  pulseElement(els.completionSub);

  const focusMinutes = Number(focus.total_focus_minutes || 0);
  const focusCycles = Number(focus.completed_cycles || 0);
  animateCountText(els.roiValue, focusMinutes, { suffix: "м", duration: 760 });
  els.roiSub.textContent = `${focusCycles} циклов сегодня`;
  pulseElement(els.roiValue);
  pulseElement(els.roiSub);

  const focusScore = Math.min(100, Math.round((focusMinutes / 180) * 35));
  const completionScore = Math.round(completionRate * 0.65);
  const overduePenalty = Math.min(25, overdue * 2);
  const productivityScore = Math.max(0, Math.min(100, completionScore + focusScore - overduePenalty));
  animateCountText(els.productivityBadge, productivityScore, {
    duration: 760,
    formatter: (value) => `Оценка продуктивности: ${value}/100`
  });
  pulseElement(els.productivityBadge);
  const inProgress = Number(stats.in_progress || 0);
  const notStarted = Number(stats.not_started || 0);
  renderProductivityChart({
    completed,
    inProgress,
    notStarted,
    overdue
  });

  const now = new Date();
  const nextDeadlineTask = activeTasks
    .map((t) => ({ ...t, parsedDeadline: parseLocalDeadline(t.deadline) }))
    .filter((t) => t.parsedDeadline && t.parsedDeadline >= now)
    .sort((a, b) => a.parsedDeadline - b.parsedDeadline)[0];

  els.reportText.innerHTML = buildReportCardMarkup({
    nextDeadlineTask,
    completed,
    inProgress,
    notStarted,
    overdue,
    focusMinutes
  });
  pulseElement(els.reportText);
  renderGraphsFromState();
}

function formatTimer(seconds) {
  const mm = Math.floor(seconds / 60)
    .toString()
    .padStart(2, "0");
  const ss = (seconds % 60).toString().padStart(2, "0");
  return `${mm}:${ss}`;
}

function phaseLabel() {
  if (focusState.phase === "short_break") return "Короткий перерыв";
  if (focusState.phase === "long_break") return "Длинный перерыв";
  return "Работа";
}

function phaseDurationSeconds(phase) {
  if (phase === "short_break") return POMODORO_CONFIG.shortBreakSeconds;
  if (phase === "long_break") return POMODORO_CONFIG.longBreakSeconds;
  return POMODORO_CONFIG.workSeconds;
}

function setPhase(phase) {
  focusState.phase = phase;
  focusState.durationSeconds = phaseDurationSeconds(phase);
  focusState.remainingSeconds = focusState.durationSeconds;
}

function advancePomodoroPhase() {
  if (focusState.phase === "work") {
    focusState.completedWorkSessions += 1;
    const shouldUseLongBreak =
      focusState.completedWorkSessions % POMODORO_CONFIG.sessionsBeforeLongBreak === 0;
    setPhase(shouldUseLongBreak ? "long_break" : "short_break");
    return;
  }
  setPhase("work");
}

function renderTimer() {
  els.timerLabel.textContent = formatTimer(focusState.remainingSeconds);
  const state = phaseLabel();
  els.timerState.textContent = focusState.running ? `${state} (идёт)` : state;
}

function stopTimer() {
  if (focusState.timerId) {
    clearInterval(focusState.timerId);
    focusState.timerId = null;
  }
  focusState.running = false;
  renderTimer();
}

function startTimer() {
  if (focusState.running) return;
  focusState.running = true;
  renderTimer();
  focusState.timerId = setInterval(() => {
    focusState.remainingSeconds -= 1;
    if (focusState.remainingSeconds <= 0) {
      stopTimer();
      advancePomodoroPhase();
    }
    renderTimer();
  }, 1000);
}

function resetTimer() {
  stopTimer();
  focusState.completedWorkSessions = 0;
  setPhase("work");
  renderTimer();
}

function taskItemNode(task, onChanged, options = {}) {
  const { highlightQuery = "", matched = false, selected = false, isNew = false } = options;
  const item = document.createElement("div");
  item.className = "task-item";
  item.dataset.taskId = String(task.id);
  if (matched) {
    item.classList.add("task-item--match");
  }
  if (selected) {
    item.classList.add("task-item--selected");
  }
  if (isNew) {
    item.classList.add("task-item--new");
  }
  item.addEventListener("click", (event) => {
    const interactiveTarget = event.target.closest(
      ".status-select-wrap, .task-actions, button, select, input, textarea, label, a"
    );
    if (interactiveTarget) return;
    if (appState.selectedTaskId == null) return;
    if (Number(task.id) === Number(appState.selectedTaskId)) return;
    appState.selectedTaskId = null;
    appState.shouldScrollToSelectedTask = false;
    renderTaskViews();
  });

  const left = document.createElement("div");
  const priorityLabel = formatPriorityWithIcon(task.priority);
  const categoryLabel = formatCategoryWithIcon(task.category);
  const deadlineCountdown = buildDeadlineCountdown(task.deadline);
  const descriptionText = String(task.description || "").trim();
  left.innerHTML = `
    <div class="task-title">${highlightMatch(task.name, highlightQuery)}</div>
    <div class="task-meta">${priorityLabel} · ${categoryLabel} · ${task.deadline}</div>
    <div class="task-deadline">${deadlineCountdown}</div>
    ${descriptionText ? `<div class="task-description">${escapeHtml(descriptionText)}</div>` : ""}
  `;

  const statusSelect = document.createElement("select");
  statusSelect.className = "status-select";
  ["не начата", "в процессе", "выполнена"].forEach((status) => {
    const option = document.createElement("option");
    option.value = status;
    option.textContent = status;
    option.selected = status === task.status;
    statusSelect.append(option);
  });
  statusSelect.addEventListener("change", async () => {
    if (statusSelect.disabled) return;
    const nextStatus = statusSelect.value;
    item.classList.add("task-item--status-updating");
    statusSelect.disabled = true;
    try {
      await api(`/api/tasks/${task.id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status: nextStatus })
      });
      appState.pulseStatsOnNextTasksLoad = true;
      await waitMs(170);
      await onChanged();
    } finally {
      statusSelect.disabled = false;
      item.classList.remove("task-item--status-updating");
    }
  });
  const statusSelectWrap = document.createElement("div");
  statusSelectWrap.className = "status-select-wrap";
  statusSelectWrap.append(statusSelect);

  const actions = document.createElement("div");
  actions.className = "task-actions";
  const deleteBtn = document.createElement("button");
  deleteBtn.className = "mini-btn";
  deleteBtn.textContent = "Удалить";
  deleteBtn.addEventListener("click", async () => {
    if (item.classList.contains("task-item--removing")) return;
    const itemHeight = item.offsetHeight;
    item.style.maxHeight = `${itemHeight}px`;
    item.style.overflow = "hidden";
    item.classList.add("task-item--removing");
    statusSelect.disabled = true;
    deleteBtn.disabled = true;
    try {
      await waitMs(200);
      await api(`/api/tasks/${task.id}`, { method: "DELETE" });
      await onChanged();
    } catch (error) {
      item.classList.remove("task-item--removing");
      item.style.maxHeight = "";
      item.style.overflow = "";
      statusSelect.disabled = false;
      deleteBtn.disabled = false;
      window.alert(`Не удалось удалить задачу: ${error?.message || "неизвестная ошибка"}`);
    }
  });
  actions.append(deleteBtn);

  item.append(left, statusSelectWrap, actions);
  return item;
}

function formatDashboardDeadline(deadlineLabel) {
  const dt = parseLocalDeadline(deadlineLabel);
  if (!dt) return String(deadlineLabel || "—");
  const pad = (value) => String(value).padStart(2, "0");
  return `${pad(dt.getDate())}.${pad(dt.getMonth() + 1)} ${pad(dt.getHours())}:${pad(dt.getMinutes())}`;
}

function dashboardTaskItemNode(task) {
  const item = document.createElement("button");
  item.type = "button";
  item.className = "dashboard-task-item";
  item.addEventListener("click", () => {
    appState.selectedTaskId = Number(task.id);
    appState.shouldScrollToSelectedTask = true;
    switchView("tasks");
    renderTaskViews();
  });

  const title = document.createElement("div");
  title.className = "dashboard-task-title";
  title.textContent = String(task.name || "Без названия");

  const deadline = document.createElement("div");
  deadline.className = "dashboard-task-deadline";
  deadline.textContent = formatDashboardDeadline(task.deadline);

  const meta = document.createElement("div");
  meta.className = "dashboard-task-meta";

  const priorityBadge = document.createElement("span");
  priorityBadge.className = "dashboard-task-badge priority";
  priorityBadge.textContent = normalizeLabel(task.priority) || "Без приоритета";

  const categoryBadge = document.createElement("span");
  categoryBadge.className = "dashboard-task-badge category";
  categoryBadge.textContent = normalizeLabel(task.category) || "Без места";

  const overdue = isTaskOverdue(task);
  meta.append(priorityBadge, categoryBadge);
  if (overdue) {
    const overdueBadge = document.createElement("span");
    overdueBadge.className = "dashboard-task-badge overdue";
    overdueBadge.textContent = "Просрочено";
    meta.append(overdueBadge);
    deadline.classList.add("is-overdue");
  }

  item.append(title, deadline, meta);
  return item;
}

function setReplyParent(note) {
  appState.noteReplyParentId = note ? Number(note.id) : null;
  if (appState.noteReplyParentId) {
    els.noteReplyText.textContent = `Подзаметка к: ${note.title}`;
    els.noteReplyInfo.classList.remove("hidden");
  } else {
    els.noteReplyText.textContent = "Добавляется подзаметка";
    els.noteReplyInfo.classList.add("hidden");
  }
}

function noteItemNode(note, onChanged, depth = 0, options = {}) {
  const { hasChildren = false, isExpanded = false, isActive = false, isDescendantOfActive = false, onToggle } = options;
  const item = document.createElement("div");
  item.className = "note-item";
  item.classList.add(`depth-${Math.min(depth, 3)}`);
  if (isActive) {
    item.classList.add("note-item--active");
  }
  if (isDescendantOfActive) {
    item.classList.add("note-item--outlined");
  }

  const left = document.createElement("div");
  const taskLabel = note.task_name ? `Задача: ${note.task_name}` : "Задача: Без привязки";
  left.innerHTML = `
    <div class="note-title">${hasChildren ? (isExpanded ? "▾ " : "▸ ") : ""}${note.title}</div>
    <div class="note-content">${note.content || "Без описания"}</div>
    <div class="note-task-link">${taskLabel}</div>
  `;

  const actions = document.createElement("div");
  actions.className = "task-actions";

  const subNoteBtn = document.createElement("button");
  subNoteBtn.className = "mini-btn";
  subNoteBtn.textContent = "Подзаметка";
  subNoteBtn.addEventListener("click", () => {
    setReplyParent(note);
    els.noteTitleInput.focus();
  });

  const pinBtn = document.createElement("button");
  pinBtn.className = "mini-btn";
  pinBtn.textContent = note.is_pinned ? "Открепить" : "Закрепить";
  pinBtn.addEventListener("click", async () => {
    await api(`/api/notes/${note.id}/pin`, {
      method: "PATCH",
      body: JSON.stringify({ is_pinned: !note.is_pinned })
    });
    await onChanged();
  });

  const deleteBtn = document.createElement("button");
  deleteBtn.className = "mini-btn";
  deleteBtn.textContent = "Удалить";
  deleteBtn.addEventListener("click", async () => {
    await api(`/api/notes/${note.id}`, { method: "DELETE" });
    if (appState.noteReplyParentId === Number(note.id)) {
      setReplyParent(null);
    }
    await onChanged();
  });

  actions.append(subNoteBtn, pinBtn, deleteBtn);
  item.append(left, actions);

  item.addEventListener("click", (event) => {
    if (event.target.closest("button,select,input,a")) {
      return;
    }
    if (onToggle) {
      onToggle(note);
    }
  });

  return item;
}

function filterNotesByQuery(items, query) {
  const q = String(query || "").trim().toLowerCase();
  if (!q) return items;
  return items.filter((note) => {
    const blob = `${note.title || ""} ${note.content || ""} ${note.task_name || ""}`.toLowerCase();
    return blob.includes(q);
  });
}

function renderNotesFromState() {
  const filtered = filterNotesByQuery(appState.notes, appState.notesSearchQuery);
  renderNotesTree(filtered);
}

function getFilteredTasksForNotesPicker() {
  const q = appState.notesTaskSearchQuery.trim().toLowerCase();
  if (!q) return appState.tasks;
  return appState.tasks.filter((task) => String(task.name || "").toLowerCase().includes(q));
}

function renderNotesTaskPickerOptions() {
  if (!els.notesTaskPickerMenu || !els.notesTaskFilter) return;
  const currentValue = String(els.notesTaskFilter.value || "");
  const items = getFilteredTasksForNotesPicker();
  if (!items.length) {
    els.notesTaskPickerMenu.innerHTML =
      '<div class="notes-task-option" aria-disabled="true">Ничего не найдено</div>';
    return;
  }
  const options = [{ id: "", label: "Все задачи" }, ...items.map((t) => ({ id: String(t.id), label: t.name }))];
  els.notesTaskPickerMenu.innerHTML = options
    .map((option) => {
      const selected = option.id === currentValue ? " selected" : "";
      return `<button type="button" class="notes-task-option${selected}" data-task-id="${option.id}">${escapeHtml(option.label)}</button>`;
    })
    .join("");
}

function syncNotesTaskPickerLabel() {
  if (!els.notesTaskPickerBtn || !els.notesTaskFilter) return;
  const currentValue = String(els.notesTaskFilter.value || "");
  if (!currentValue) {
    els.notesTaskPickerBtn.textContent = "Все задачи";
    return;
  }
  const task = appState.tasks.find((t) => String(t.id) === currentValue);
  els.notesTaskPickerBtn.textContent = task ? task.name : "Все задачи";
}

function closeNotesTaskPickerMenu() {
  if (els.notesTaskPickerMenu) {
    els.notesTaskPickerMenu.classList.remove("open");
  }
}

function toggleNotesTaskPickerMenu() {
  if (els.notesTaskPickerMenu) {
    els.notesTaskPickerMenu.classList.toggle("open");
  }
}

function renderNotesTree(items) {
  const byParent = new Map();
  const noteIds = new Set(items.map((n) => Number(n.id)));
  items.forEach((note) => {
    const parentId = note.parent_note_id == null ? null : Number(note.parent_note_id);
    const isRoot = parentId == null || Number.isNaN(parentId) || parentId === 0 || !noteIds.has(parentId);
    const key = isRoot ? "root" : String(parentId);
    if (!byParent.has(key)) byParent.set(key, []);
    byParent.get(key).push(note);
  });

  const sortNotes = (arr) =>
    [...arr].sort((a, b) => {
      if (a.is_pinned !== b.is_pinned) return a.is_pinned ? -1 : 1;
      return String(b.updated_at || "").localeCompare(String(a.updated_at || ""));
    });

  const activeId = appState.activeNoteId;
  const activeDescendants = new Set();

  const hasChildrenMap = new Map();
  items.forEach((note) => {
    hasChildrenMap.set(Number(note.id), !!(byParent.get(String(note.id)) || []).length);
  });

  const markDescendants = (id) => {
    const children = byParent.get(String(id)) || [];
    children.forEach((child) => {
      const childId = Number(child.id);
      activeDescendants.add(childId);
      markDescendants(childId);
    });
  };
  if (activeId != null) {
    markDescendants(Number(activeId));
  }

  const container = document.createDocumentFragment();
  const addLevel = (parentKey, depth, ancestorExpanded) => {
    const notes = sortNotes(byParent.get(parentKey) || []);
    notes.forEach((note) => {
      const idNum = Number(note.id);
      const hasChildren = hasChildrenMap.get(idNum);
      const isExpanded = appState.expandedNoteIds.has(idNum);
      const isActive = activeId != null && idNum === Number(activeId);
      const isDescendantOfActive =
        activeId != null && !isActive && activeDescendants.has(idNum);

      container.append(
        noteItemNode(note, async () => {
          await loadNotes();
        }, depth, {
          hasChildren,
          isExpanded,
          isActive,
          isDescendantOfActive,
          onToggle: (clickedNote) => {
            const clickedId = Number(clickedNote.id);
            appState.activeNoteId = clickedId;
            if (hasChildrenMap.get(clickedId)) {
              if (appState.expandedNoteIds.has(clickedId)) {
                appState.expandedNoteIds.delete(clickedId);
              } else {
                appState.expandedNoteIds.add(clickedId);
              }
            }
            renderNotesFromState();
          }
        })
      );
      const shouldShowChildren = ancestorExpanded && isExpanded;
      if (shouldShowChildren) {
        addLevel(String(note.id), depth + 1, true);
      }
    });
  };

  addLevel("root", 0, true);
  els.notesList.innerHTML = "";
  if (!container.childNodes.length) {
    els.notesList.innerHTML = `<div class="task-item"><div class="task-title">Пусто</div></div>`;
    return;
  }
  els.notesList.append(container);
}

function renderList(targetEl, items, createNode) {
  targetEl.innerHTML = "";
  if (!items.length) {
    targetEl.innerHTML = `<div class="task-item"><div class="task-title">Пусто</div></div>`;
    return;
  }
  items.forEach((item) => targetEl.append(createNode(item)));
}

function sessionTypeLabel(type) {
  if (type === "short_break") return "короткий перерыв";
  if (type === "long_break") return "длинный перерыв";
  return type || "сессия";
}

async function loadOverview() {
  const overview = await api("/api/overview");
  appState.overview = overview;
  const stats = overview.stats || {};
  animateCountText(els.statTotal, Number(stats.total ?? 0), { duration: 760 });
  animateCountText(els.statCompleted, Number(stats.completed ?? 0), { duration: 760 });
  animateCountText(els.statProgress, Number(stats.in_progress ?? 0), { duration: 760 });
  animateCountText(els.statTodo, Number(stats.not_started ?? 0), { duration: 760 });
  updateDashboardCardsFromState();
}

async function loadTasks() {
  const data = await api("/api/tasks");
  const items = data.items || [];
  appState.tasks = items;
  renderTaskViews();

  const current = els.notesTaskFilter.value;
  els.notesTaskFilter.innerHTML = `<option value="">Все задачи</option>`;
  const currentFocusTask = els.focusTaskSelect.value;
  els.focusTaskSelect.innerHTML = `<option value="">Без привязки к задаче</option>`;
  items.forEach((task) => {
    const option = document.createElement("option");
    option.value = String(task.id);
    option.textContent = task.name;
    els.notesTaskFilter.append(option);
  });
  items.forEach((task) => {

    const focusOption = document.createElement("option");
    focusOption.value = String(task.id);
    focusOption.textContent = `${task.name} (${task.status})`;
    els.focusTaskSelect.append(focusOption);
  });
  if (current) {
    els.notesTaskFilter.value = current;
  }
  renderNotesTaskPickerOptions();
  syncNotesTaskPickerLabel();
  if (currentFocusTask) {
    els.focusTaskSelect.value = currentFocusTask;
  }
  updateFocusTaskInfo();
  updateDashboardCardsFromState();
  if (appState.pulseStatsOnNextTasksLoad) {
    pulseTaskStatNumbers();
    appState.pulseStatsOnNextTasksLoad = false;
  }
  runDeadlineNotificationCheck().catch(() => {});
}

function renderTaskViews() {
  const filtered = appState.tasks.filter(taskMatchesCurrentFilters);
  const draftQuery = appState.draftTaskQuery.trim().toLowerCase();

  let ordered = [...filtered].sort(compareTasksByDeadlinePriority);
  if (draftQuery) {
    const matched = [];
    const rest = [];
    filtered.forEach((task) => {
      if (task.name.toLowerCase().includes(draftQuery)) {
        matched.push(task);
      } else {
        rest.push(task);
      }
    });
    ordered = [...matched, ...rest];
  }

  const now = new Date();
  const startMs = now.getTime() - 24 * 60 * 60 * 1000;
  const endMs = now.getTime() + 7 * 24 * 60 * 60 * 1000;
  const recentInWindow = [...appState.tasks]
    .filter((task) => {
      const deadline = parseLocalDeadline(task.deadline);
      if (!deadline) return false;
      const deadlineMs = deadline.getTime();
      return deadlineMs >= startMs && deadlineMs <= endMs;
    })
    .sort((a, b) => {
      const aDeadline = parseLocalDeadline(a.deadline)?.getTime() ?? Number.MAX_SAFE_INTEGER;
      const bDeadline = parseLocalDeadline(b.deadline)?.getTime() ?? Number.MAX_SAFE_INTEGER;
      if (aDeadline !== bDeadline) return aDeadline - bDeadline;
      return Number(a.id || 0) - Number(b.id || 0);
    });
  const fallbackRecent = [...appState.tasks]
    .sort((a, b) => {
      const aCreated = new Date(a.created_at || "").getTime();
      const bCreated = new Date(b.created_at || "").getTime();
      if (!Number.isNaN(aCreated) && !Number.isNaN(bCreated) && aCreated !== bCreated) {
        return bCreated - aCreated;
      }
      return Number(b.id || 0) - Number(a.id || 0);
    })
    .slice(0, 3);
  const recent = recentInWindow.length >= 3 ? recentInWindow : fallbackRecent;

  renderList(els.tasksList, recent, (task) => dashboardTaskItemNode(task));

  renderList(els.tasksListFull, ordered, (task) =>
    taskItemNode(task, async () => {
      await loadAll();
    }, {
      highlightQuery: draftQuery,
      matched: !!draftQuery && task.name.toLowerCase().includes(draftQuery),
      selected: Number(task.id) === Number(appState.selectedTaskId),
      isNew: Number(task.id) === Number(appState.newTaskId)
    })
  );
  if (appState.newTaskId != null) {
    const createdNode = els.tasksListFull.querySelector(`.task-item[data-task-id="${appState.newTaskId}"]`);
    if (createdNode) {
      window.setTimeout(() => {
        createdNode.classList.remove("task-item--new");
      }, 220);
      appState.newTaskId = null;
    }
  }
  if (appState.shouldScrollToSelectedTask && appState.selectedTaskId != null) {
    const selectedNode = els.tasksListFull.querySelector(`.task-item[data-task-id="${appState.selectedTaskId}"]`);
    if (selectedNode) {
      selectedNode.scrollIntoView({ block: "center", behavior: "smooth" });
    }
    appState.shouldScrollToSelectedTask = false;
  }
}

function refreshDeadlineViewsRealtime() {
  const activeEl = document.activeElement;
  if (activeEl && activeEl.classList && activeEl.classList.contains("status-select")) {
    return;
  }
  if (!appState.tasks.length) return;
  renderTaskViews();
}

function startDeadlineTicker() {
  if (deadlineTickerId) return;
  deadlineTickerId = setInterval(() => {
    refreshDeadlineViewsRealtime();
  }, 60 * 1000);
}

async function loadNotes() {
  const taskId = els.notesTaskFilter.value;
  const path = taskId ? `/api/notes?task_id=${encodeURIComponent(taskId)}` : "/api/notes";
  const data = await api(path);
  appState.notes = data.items || [];
  renderNotesFromState();
}

async function loadFocus() {
  const [stats, sessions] = await Promise.all([api("/api/focus/stats"), api("/api/focus/sessions?limit=10000")]);
  const focusSessions = sessions.items || [];
  appState.focusSessions = focusSessions;
  els.focusStatsText.textContent = `Сегодня: ${stats.total_focus_minutes} мин, ${stats.completed_cycles} циклов`;
  renderList(els.focusSessionsList, focusSessions.slice(0, 12), (session) => {
    const item = document.createElement("div");
    item.className = "note-item";
    item.innerHTML = `
      <div>
        <div class="note-title">${sessionTypeLabel(session.session_type)} · ${session.duration_minutes} мин</div>
        <div class="note-content">${session.task_name || "Без задачи"} · ${session.created_at}</div>
      </div>
      <div></div>
    `;
    return item;
  });
  renderGraphsFromState();
}

async function loadAll() {
  try {
    await Promise.all([loadOverview(), loadTasks(), loadNotes(), loadFocus()]);
    renderGraphsFromState();
  } catch (error) {
    if (error && error.status === 401) {
      setAuthToken(null);
      appState.currentUser = null;
      renderProfile();
      showAuthModal(true);
    }
    throw error;
  }
}

function startGraphsAutoRefresh() {
  if (graphsRefreshId) return;
  graphsRefreshId = setInterval(async () => {
    try {
      await loadAll();
    } catch {
      // ignore transient errors, next cycle will retry
    }
  }, 5 * 60 * 1000);
}

function shouldSkipTasksLiveRefresh() {
  if (appState.currentView !== "tasks") return true;
  if (!appState.authToken) return true;
  if (els.deadlineModal && !els.deadlineModal.classList.contains("hidden")) return true;
  const activeEl = document.activeElement;
  if (!activeEl || !activeEl.classList) return false;
  if (activeEl.classList.contains("status-select")) return true;
  if (activeEl.closest && activeEl.closest(".status-select-wrap")) return true;
  return false;
}

function startTasksLiveRefresh() {
  if (tasksLiveRefreshId) return;
  tasksLiveRefreshId = setInterval(async () => {
    if (tasksLiveRefreshInFlight) return;
    if (shouldSkipTasksLiveRefresh()) return;
    tasksLiveRefreshInFlight = true;
    try {
      await loadTasks();
    } catch {
      // ignore transient errors, next cycle will retry
    } finally {
      tasksLiveRefreshInFlight = false;
    }
  }, TASKS_LIVE_REFRESH_MS);
}

async function refreshAndResetSessions() {
  await api("/api/focus/sessions", { method: "DELETE" });
  await loadAll();
}

function parseDurationString(value) {
  const match = String(value || "").trim().match(/^(\d{3}):(\d{2}):(\d{2})$/);
  if (!match) {
    return null;
  }
  const days = Number(match[1]);
  const hours = Number(match[2]);
  const minutes = Number(match[3]);
  if ([days, hours, minutes].some((v) => Number.isNaN(v) || v < 0)) {
    return null;
  }
  const totalMinutes = minutes + hours * 60 + days * 24 * 60;
  if (totalMinutes <= 0) {
    return null;
  }
  return { minutes, hours, days, totalMinutes };
}

function normalizeDurationFieldValue(raw) {
  const digits = String(raw || "")
    .replace(/\D/g, "")
    .slice(0, 7);

  if (digits.length <= 3) return digits;
  if (digits.length <= 5) return `${digits.slice(0, 3)}:${digits.slice(3)}`;
  return `${digits.slice(0, 3)}:${digits.slice(3, 5)}:${digits.slice(5, 7)}`;
}

function toDatetimeLocalValue(date) {
  const pad = (value) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function defaultAbsoluteDeadlineValue() {
  const nextHour = new Date(Date.now() + 60 * 60 * 1000);
  nextHour.setSeconds(0, 0);
  return toDatetimeLocalValue(nextHour);
}

function parseAbsoluteDeadlineInput(value) {
  const raw = String(value || "").trim();
  if (!raw) return null;
  const normalized = raw.length === 16 ? `${raw}:00` : raw;
  const date = new Date(normalized);
  if (Number.isNaN(date.getTime())) {
    return null;
  }
  return { normalized, date };
}

function formatAbsoluteDeadlineForButton(date) {
  const pad = (value) => String(value).padStart(2, "0");
  return `📅 ${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function updateAbsoluteDeadlineButtonLabel() {
  if (!els.deadlineAtBtn) return;
  const absolute = parseAbsoluteDeadlineInput(els.deadlineAtInput?.value);
  if (!absolute) {
    els.deadlineAtBtn.textContent = "📅 Выбрать дату";
    return;
  }
  els.deadlineAtBtn.textContent = formatAbsoluteDeadlineForButton(absolute.date);
}

function ensureDeadlineTimeOptions() {
  if (els.deadlineHourSelect && !els.deadlineHourSelect.options.length) {
    for (let hour = 0; hour < 24; hour += 1) {
      const option = document.createElement("option");
      option.value = String(hour);
      option.textContent = String(hour).padStart(2, "0");
      els.deadlineHourSelect.append(option);
    }
  }
  if (els.deadlineMinuteSelect && !els.deadlineMinuteSelect.options.length) {
    for (let minute = 0; minute < 60; minute += 1) {
      const option = document.createElement("option");
      option.value = String(minute);
      option.textContent = String(minute).padStart(2, "0");
      els.deadlineMinuteSelect.append(option);
    }
  }
}

function formatDeadlineMonthLabel(year, month) {
  const date = new Date(year, month, 1);
  const formatted = new Intl.DateTimeFormat("ru-RU", { month: "long", year: "numeric" }).format(date);
  return formatted.slice(0, 1).toUpperCase() + formatted.slice(1);
}

function isSameDay(left, right) {
  if (!left || !right) return false;
  return (
    left.getFullYear() === right.getFullYear() &&
    left.getMonth() === right.getMonth() &&
    left.getDate() === right.getDate()
  );
}

function renderDeadlineCalendar() {
  if (!els.deadlineCalendarGrid) return;
  const year = deadlinePickerState.viewYear;
  const month = deadlinePickerState.viewMonth;
  const firstDay = new Date(year, month, 1);
  const mondayOffset = (firstDay.getDay() + 6) % 7;
  const gridStart = new Date(year, month, 1 - mondayOffset);
  const today = new Date();

  els.deadlineCalendarGrid.innerHTML = "";
  for (let index = 0; index < 42; index += 1) {
    const dayDate = new Date(
      gridStart.getFullYear(),
      gridStart.getMonth(),
      gridStart.getDate() + index,
      0,
      0,
      0,
      0
    );
    const button = document.createElement("button");
    button.type = "button";
    button.className = "deadline-day-btn";
    if (dayDate.getMonth() !== month) {
      button.classList.add("other-month");
    }
    if (isSameDay(dayDate, today)) {
      button.classList.add("today");
    }
    if (isSameDay(dayDate, deadlinePickerState.selectedDate)) {
      button.classList.add("selected");
    }
    button.dataset.year = String(dayDate.getFullYear());
    button.dataset.month = String(dayDate.getMonth());
    button.dataset.day = String(dayDate.getDate());
    button.textContent = String(dayDate.getDate());
    els.deadlineCalendarGrid.append(button);
  }
}

function renderDeadlineModal() {
  if (!deadlinePickerState.selectedDate) return;
  if (els.deadlineMonthLabel) {
    els.deadlineMonthLabel.textContent = formatDeadlineMonthLabel(
      deadlinePickerState.viewYear,
      deadlinePickerState.viewMonth
    );
  }
  if (els.deadlineHourSelect) {
    els.deadlineHourSelect.value = String(deadlinePickerState.selectedDate.getHours());
  }
  if (els.deadlineMinuteSelect) {
    els.deadlineMinuteSelect.value = String(deadlinePickerState.selectedDate.getMinutes());
  }
  renderDeadlineCalendar();
}

function closeDeadlineModal() {
  if (!els.deadlineModal) return;
  els.deadlineModal.classList.add("hidden");
  if (deadlinePickerState.returnFocusEl && typeof deadlinePickerState.returnFocusEl.focus === "function") {
    deadlinePickerState.returnFocusEl.focus();
  }
  deadlinePickerState.returnFocusEl = null;
}

function setDeadlinePickerTimeFromSelects() {
  if (!deadlinePickerState.selectedDate) return;
  const nextHour = Number(els.deadlineHourSelect?.value ?? deadlinePickerState.selectedDate.getHours());
  const nextMinute = Number(els.deadlineMinuteSelect?.value ?? deadlinePickerState.selectedDate.getMinutes());
  deadlinePickerState.selectedDate.setHours(nextHour, nextMinute, 0, 0);
}

function shiftDeadlineMonth(offset) {
  const next = new Date(deadlinePickerState.viewYear, deadlinePickerState.viewMonth + offset, 1);
  deadlinePickerState.viewYear = next.getFullYear();
  deadlinePickerState.viewMonth = next.getMonth();
  renderDeadlineModal();
}

function selectDeadlineDay(year, month, day) {
  if (!deadlinePickerState.selectedDate) return;
  const nextDate = new Date(
    year,
    month,
    day,
    deadlinePickerState.selectedDate.getHours(),
    deadlinePickerState.selectedDate.getMinutes(),
    0,
    0
  );
  deadlinePickerState.selectedDate = nextDate;
  deadlinePickerState.viewYear = nextDate.getFullYear();
  deadlinePickerState.viewMonth = nextDate.getMonth();
  renderDeadlineModal();
}

function openAbsoluteDeadlinePicker() {
  if (!els.deadlineModal || !els.deadlineAtInput) return;
  ensureDeadlineTimeOptions();

  const parsed = parseAbsoluteDeadlineInput(els.deadlineAtInput.value);
  const selected = parsed?.date || new Date(defaultAbsoluteDeadlineValue());
  selected.setSeconds(0, 0);

  deadlinePickerState.selectedDate = selected;
  deadlinePickerState.viewYear = selected.getFullYear();
  deadlinePickerState.viewMonth = selected.getMonth();
  deadlinePickerState.returnFocusEl = document.activeElement;

  renderDeadlineModal();
  els.deadlineModal.classList.remove("hidden");
}

function setDeadlineInputMode(mode) {
  const isAbsolute = mode === "absolute";
  const durationContainer =
    (els.minutesInput && els.minutesInput.closest(".input-marquee-wrap")) || els.minutesInput;
  const absoluteContainer =
    (els.deadlineAtBtn && els.deadlineAtBtn.closest(".deadline-picker-wrap")) || els.deadlineAtBtn;
  if (els.minutesInput) {
    // minutesInput может быть обёрнут в .input-marquee-wrap, скрываем весь контейнер.
    durationContainer.style.display = isAbsolute ? "none" : "";
  }
  if (absoluteContainer) {
    absoluteContainer.style.display = isAbsolute ? "" : "none";
  }
  if (els.deadlineAtInput && isAbsolute && !els.deadlineAtInput.value) {
    els.deadlineAtInput.value = defaultAbsoluteDeadlineValue();
  }
  updateAbsoluteDeadlineButtonLabel();
}

async function createTask() {
  const name = els.nameInput.value.trim();
  if (!name) return;
  const deadlineMode = els.deadlineModeInput?.value === "absolute" ? "absolute" : "duration";
  const payload = {
    name,
    priority: els.priorityInput.value,
    category: els.categoryInput.value,
    description: els.descriptionInput.value.trim(),
    deadline_mode: deadlineMode
  };

  if (deadlineMode === "absolute") {
    const absolute = parseAbsoluteDeadlineInput(els.deadlineAtInput?.value);
    if (!absolute) {
      window.alert("Выберите корректные дату и время дедлайна.");
      return;
    }
    if (absolute.date.getTime() <= Date.now()) {
      window.alert("Дата дедлайна должна быть позже текущего времени.");
      return;
    }
    payload.deadline_at = absolute.normalized;
  } else {
    const duration = parseDurationString(els.minutesInput.value);
    if (!duration) {
      window.alert("Введите дедлайн строго в формате 000:00:00 (дни:часы:минуты)");
      return;
    }
    payload.duration = `${String(duration.days).padStart(3, "0")}:${String(duration.hours).padStart(2, "0")}:${String(duration.minutes).padStart(2, "0")}`;
    payload.minutes = duration.totalMinutes;
  }

  const createdTask = await api("/api/tasks", {
    method: "POST",
    body: JSON.stringify(payload)
  });
  const createdTaskId = Number(
    createdTask?.id ?? createdTask?.item?.id ?? createdTask?.task?.id ?? Number.NaN
  );
  if (Number.isFinite(createdTaskId)) {
    appState.newTaskId = createdTaskId;
  }
  els.nameInput.value = "";
  els.descriptionInput.value = "";
  if (deadlineMode === "absolute" && els.deadlineAtInput) {
    els.deadlineAtInput.value = defaultAbsoluteDeadlineValue();
    updateAbsoluteDeadlineButtonLabel();
  }
  await loadAll();
}

async function createNote() {
  const title = els.noteTitleInput.value.trim();
  if (!title) return;
  const parentId = appState.noteReplyParentId;
  let taskId = els.notesTaskFilter.value ? Number(els.notesTaskFilter.value) : null;
  if (!taskId && parentId) {
    const parentNote = appState.notes.find((n) => Number(n.id) === Number(parentId));
    if (parentNote && parentNote.task_id) {
      taskId = Number(parentNote.task_id);
    }
  }
  await api("/api/notes", {
    method: "POST",
    body: JSON.stringify({
      title,
      content: els.noteContentInput.value.trim(),
      task_id: taskId,
      parent_note_id: parentId
    })
  });
  els.noteTitleInput.value = "";
  els.noteContentInput.value = "";
  setReplyParent(null);
  await loadNotes();
}

async function finishFocusSession() {
  stopTimer();

  const taskId = selectedFocusTaskId();
  let sessionType = null;
  let durationMinutes = 0;

  if (focusState.phase === "work") {
    sessionType = "pomodoro";
    // Кнопка "Завершить сессию" трактуется как завершение полного рабочего Pomodoro.
    durationMinutes = Math.round(POMODORO_CONFIG.workSeconds / 60);
  } else if (focusState.phase === "short_break") {
    sessionType = "short_break";
    durationMinutes = Math.round(POMODORO_CONFIG.shortBreakSeconds / 60);
  } else if (focusState.phase === "long_break") {
    sessionType = "long_break";
    durationMinutes = Math.round(POMODORO_CONFIG.longBreakSeconds / 60);
  }

  if (sessionType) {
    await api("/api/focus/session", {
      method: "POST",
      body: JSON.stringify({
        task_id: taskId,
        session_type: sessionType,
        duration_minutes: durationMinutes
      })
    });
    await loadFocus();
    await loadOverview();
  }

  advancePomodoroPhase();
  renderTimer();
}

function downloadReport() {
  const overview = appState.overview || {};
  const tasks = appState.tasks || [];
  const focusSessions = appState.focusSessions || [];
  const now = new Date();
  const nowLabel = now.toLocaleString("ru-RU");
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const startOfYear = new Date(now.getFullYear(), 0, 1);

  const parseDate = (value) => {
    if (!value) return null;
    const text = String(value).trim();
    const normalized = text.includes("T") ? text : text.replace(" ", "T");
    const dt = new Date(normalized);
    return Number.isNaN(dt.getTime()) ? null : dt;
  };

  const inRange = (date, start) => !!date && date >= start && date <= now;
  const formatMinutes = (minutes) => `${Math.max(0, Math.round(minutes || 0))} мин`;
  const minutesToHuman = (minutes) => {
    const safe = Math.max(0, Math.round(minutes || 0));
    const hours = Math.floor(safe / 60);
    const mins = safe % 60;
    if (!hours) return `${mins} мин`;
    return `${hours} ч ${mins} мин`;
  };

  const countBy = (items, getter) => {
    const map = new Map();
    items.forEach((item) => {
      const keyRaw = getter(item);
      const key = String(keyRaw || "Не указано").trim() || "Не указано";
      map.set(key, (map.get(key) || 0) + 1);
    });
    return map;
  };

  const mapToText = (map) => {
    if (!map.size) return "нет данных";
    return [...map.entries()]
      .sort((a, b) => b[1] - a[1] || String(a[0]).localeCompare(String(b[0]), "ru"))
      .map(([key, value]) => `${key}: ${value}`)
      .join(", ");
  };

  const topKey = (map) => {
    if (!map.size) return "нет данных";
    return [...map.entries()].sort((a, b) => b[1] - a[1])[0][0];
  };

  const taskCreatedAt = (task) => parseDate(task.created_at);
  const taskUpdatedAt = (task) => parseDate(task.updated_at);
  const taskPriority = (task) => normalizeLabel(task.priority) || "Не указано";
  const taskPlace = (task) => normalizeLabel(task.category) || "Не указано";
  const taskOverdue = (task) => task.status !== "выполнена" && isTaskOverdue(task);

  const tasksForPeriod = (start) => {
    if (!start) return tasks;
    return tasks.filter((task) => inRange(taskCreatedAt(task), start));
  };

  const summarizePeriod = (periodTasks) => {
    const completed = periodTasks.filter((t) => t.status === "выполнена").length;
    const overdue = periodTasks.filter(taskOverdue).length;
    const notStarted = periodTasks.filter((t) => t.status === "не начата").length;
    return {
      completed,
      overdue,
      notStarted,
      byCategory: mapToText(countBy(periodTasks, taskPriority)),
      byPlace: mapToText(countBy(periodTasks, taskPlace)),
      total: periodTasks.length
    };
  };

  const monthSummary = summarizePeriod(tasksForPeriod(startOfMonth));
  const yearSummary = summarizePeriod(tasksForPeriod(startOfYear));
  const allSummary = summarizePeriod(tasksForPeriod(null));

  const sumFocusMinutes = (start) =>
    focusSessions
      .filter((session) => inRange(parseDate(session.created_at), start))
      .reduce((sum, session) => sum + Number(session.duration_minutes || 0), 0);

  const focusDayMinutes = sumFocusMinutes(startOfDay);
  const focusMonthMinutes = sumFocusMinutes(startOfMonth);
  const focusYearMinutes = sumFocusMinutes(startOfYear);

  const completionPercent = (start) => {
    const scoped = tasksForPeriod(start);
    if (!scoped.length) return 0;
    const done = scoped.filter((t) => t.status === "выполнена").length;
    return Math.round((done / scoped.length) * 100);
  };

  const completionDay = completionPercent(startOfDay);
  const completionMonth = completionPercent(startOfMonth);
  const completionYear = completionPercent(startOfYear);

  const allByCategory = countBy(tasks, taskPriority);
  const allByPlace = countBy(tasks, taskPlace);
  const popularCategory = topKey(allByCategory);
  const popularPlace = topKey(allByPlace);

  const completedWithDuration = tasks
    .filter((task) => task.status === "выполнена")
    .map((task) => {
      const created = taskCreatedAt(task);
      const updated = taskUpdatedAt(task);
      if (!created || !updated || updated < created) return null;
      const minutes = Math.round((updated - created) / (1000 * 60));
      return { name: task.name, minutes };
    })
    .filter(Boolean);

  let fastestTaskText = "нет данных";
  let slowestTaskText = "нет данных";
  if (completedWithDuration.length) {
    completedWithDuration.sort((a, b) => a.minutes - b.minutes);
    const fastest = completedWithDuration[0];
    const slowest = completedWithDuration[completedWithDuration.length - 1];
    fastestTaskText = `${fastest.name} (${minutesToHuman(fastest.minutes)})`;
    slowestTaskText = `${slowest.name} (${minutesToHuman(slowest.minutes)})`;
  }

  const overdueAll = allSummary.overdue;
  const productivityScore = Math.max(
    0,
    Math.min(100, Math.round(completionMonth * 0.6 + Math.min(100, focusMonthMinutes / 3) * 0.4 - overdueAll * 2))
  );
  let productivityText = `Индекс продуктивности: ${productivityScore}/100. `;
  if (productivityScore >= 75) {
    productivityText += "Высокая стабильность выполнения задач.";
  } else if (productivityScore >= 45) {
    productivityText += "Средняя стабильность, есть точки для роста.";
  } else {
    productivityText += "Низкая стабильность, стоит пересобрать планирование.";
  }

  const recommendations = [];
  if (overdueAll > 0) recommendations.push(`Снизить просрочки: сейчас ${overdueAll}, ставить более реалистичные дедлайны и дробить задачи.`);
  if (completionMonth < 60) recommendations.push(`Поднять процент выполнения за месяц (${completionMonth}%): ограничить объём задач в день и фиксировать 3 приоритета.`);
  if (focusDayMinutes < 30) recommendations.push("Добавить минимум 1 фокус-сессию в день (25-30 минут).");
  if (popularCategory !== "нет данных") recommendations.push(`Основной тип задач: ${popularCategory}. Выделить для него отдельные временные блоки.`);
  if (!recommendations.length) recommendations.push("Динамика стабильная. Сохраняйте текущий темп и пересматривайте цели еженедельно.");

  const report = [
    "Отчёт TaskTide",
    `Дата: ${nowLabel}`,
    "",
    "Отчёт:",
    "",
    `1) Всего задач: ${tasks.length}`,
    "",
    `2) За месяц: выполнено ${monthSummary.completed}, просрочено ${monthSummary.overdue}, не начато ${monthSummary.notStarted}; по категории: ${monthSummary.byCategory}; по месту: ${monthSummary.byPlace}`,
    "",
    `3) За год: выполнено ${yearSummary.completed}, просрочено ${yearSummary.overdue}, не начато ${yearSummary.notStarted}; по категории: ${yearSummary.byCategory}; по месту: ${yearSummary.byPlace}`,
    "",
    `4) За всё время: выполнено ${allSummary.completed}, просрочено ${allSummary.overdue}, не начато ${allSummary.notStarted}; по категории: ${allSummary.byCategory}; по месту: ${allSummary.byPlace}`,
    "",
    `5) Сколько провёл времени в приложении: за день ${formatMinutes(focusDayMinutes)}, за месяц ${formatMinutes(focusMonthMinutes)}, за год ${formatMinutes(focusYearMinutes)}`,
    "",
    `6) Анализ продуктивности: ${productivityText}`,
    "",
    `7) Процент выполнения: за день ${completionDay}%, за месяц ${completionMonth}%, за год ${completionYear}%`,
    "",
    `8) Популярная категория: ${popularCategory}`,
    "",
    `9) Популярное место: ${popularPlace}`,
    "",
    `10) Самое долго/быстро выполнил задачу: долго — ${slowestTaskText}; быстро — ${fastestTaskText}`,
    "",
    `11) Рекомендации по улучшению: ${recommendations.join(" ")}`
  ].join("\n");

  const blob = new Blob([report], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `tasktide-report-${new Date().toISOString().slice(0, 10)}.txt`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function submitAuth() {
  const login = String(els.authEmailInput?.value || "").trim();
  const password = String(els.authPasswordInput?.value || "");
  const username = String(els.authNameInput?.value || "").trim();
  if (!login || !password) {
    showAuthError("Введите login и пароль.");
    return;
  }
  if (appState.authMode === "register" && username.length < 2) {
    showAuthError("Имя должно быть не короче 2 символов.");
    return;
  }
  try {
    showAuthError("");
    const endpoint = appState.authMode === "register" ? "/auth/register" : "/auth/login";
    const payload =
      appState.authMode === "register"
        ? { username, login, password }
        : { login, password };
    const data = await api(endpoint, {
      method: "POST",
      headers: { Authorization: "" },
      body: JSON.stringify(payload)
    });
    applyAuthSuccess(data);
    await loadAll();
  } catch (error) {
    const rawMessage = String(error?.message || "Ошибка авторизации");
    if (rawMessage.toLowerCase().includes("failed to fetch")) {
      showAuthError(`Нет подключения к серверу (${API_BASE}). Запусти server/api_server.py и проверь TASKTIDE_API_BASE.`);
    } else {
      showAuthError(rawMessage);
    }
  }
}

function logoutAuth() {
  setAuthToken(null);
  appState.currentUser = null;
  appState.tasks = [];
  appState.notes = [];
  appState.focusSessions = [];
  appState.overview = null;
  renderProfile();
  renderTaskViews();
  renderNotesFromState();
  renderGraphsFromState();
  showAuthModal(true);
}

els.viewButtons.forEach((btn) => {
  btn.addEventListener("click", () => switchView(btn.dataset.viewBtn));
});
if (els.profileAuthBtn) {
  els.profileAuthBtn.addEventListener("click", () => {
    showAuthModal(true);
  });
}
if (els.authTabLoginBtn) {
  els.authTabLoginBtn.addEventListener("click", () => setAuthMode("login"));
}
if (els.authTabRegisterBtn) {
  els.authTabRegisterBtn.addEventListener("click", () => setAuthMode("register"));
}
if (els.authSubmitBtn) {
  els.authSubmitBtn.addEventListener("click", () => {
    submitAuth().catch(() => {});
  });
}
if (els.authPasswordInput) {
  els.authPasswordInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      submitAuth().catch(() => {});
    }
  });
}
if (els.authCancelBtn) {
  els.authCancelBtn.addEventListener("click", () => {
    if (!appState.currentUser) return;
    hideAuthModal();
  });
}
if (els.authLogoutBtn) {
  els.authLogoutBtn.addEventListener("click", () => {
    logoutAuth();
  });
}
els.createBtn.addEventListener("click", createTask);
els.createNoteBtn.addEventListener("click", createNote);
els.resetFocusSessionsBtn.addEventListener("click", () => {
  refreshAndResetSessions().catch(() => {});
});
els.notesTaskFilter.addEventListener("change", async () => {
  setReplyParent(null);
  await loadNotes();
});
if (els.notesSearchInput) {
  els.notesSearchInput.addEventListener("input", (event) => {
    appState.notesSearchQuery = event.target.value || "";
    renderNotesFromState();
  });
}
if (els.notesTaskQuickSearchInput) {
  els.notesTaskQuickSearchInput.addEventListener("input", (event) => {
    appState.notesTaskSearchQuery = event.target.value || "";
    renderNotesTaskPickerOptions();
    if (els.notesTaskPickerMenu) {
      els.notesTaskPickerMenu.classList.add("open");
    }
  });
}
if (els.notesTaskPickerBtn) {
  els.notesTaskPickerBtn.addEventListener("click", (event) => {
    event.stopPropagation();
    toggleNotesTaskPickerMenu();
  });
}
if (els.notesTaskPickerMenu) {
  els.notesTaskPickerMenu.addEventListener("click", async (event) => {
    const option = event.target.closest(".notes-task-option");
    if (!option || !els.notesTaskFilter) return;
    els.notesTaskFilter.value = option.dataset.taskId || "";
    renderNotesTaskPickerOptions();
    syncNotesTaskPickerLabel();
    closeNotesTaskPickerMenu();
    setReplyParent(null);
    await loadNotes();
  });
}
els.noteReplyCancelBtn.addEventListener("click", () => setReplyParent(null));
els.nameInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") createTask();
});
els.nameInput.addEventListener("input", (event) => {
  appState.draftTaskQuery = event.target.value || "";
  renderTaskViews();
});
els.noteTitleInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") createNote();
});
els.timerStartBtn.addEventListener("click", startTimer);
els.timerPauseBtn.addEventListener("click", stopTimer);
els.timerResetBtn.addEventListener("click", resetTimer);
els.timerFinishBtn.addEventListener("click", finishFocusSession);
els.focusTaskSelect.addEventListener("change", updateFocusTaskInfo);
els.reportActionBtn.addEventListener("click", downloadReport);
els.themeToggleBtn.addEventListener("click", () => {
  const next = document.body.classList.contains("light-theme") ? "dark" : "light";
  applyTheme(next);
});
els.themeLightBtn.addEventListener("click", () => applyTheme("light"));
els.themeDarkBtn.addEventListener("click", () => applyTheme("dark"));
els.searchInput.addEventListener("input", (event) => {
  setTaskSearchQuery(event.target.value || "", "top");
});
if (els.deadlineModeInput) {
  els.deadlineModeInput.addEventListener("change", (event) => {
    setDeadlineInputMode(event.target.value || "duration");
  });
}
if (els.minutesInput) {
  els.minutesInput.addEventListener("input", (event) => {
    const normalized = normalizeDurationFieldValue(event.target.value);
    if (event.target.value !== normalized) {
      event.target.value = normalized;
    }
  });
}
if (els.deadlineAtInput) {
  els.deadlineAtInput.addEventListener("change", () => {
    updateAbsoluteDeadlineButtonLabel();
  });
  els.deadlineAtInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      createTask().catch(() => {});
    }
  });
}
if (els.deadlineAtBtn) {
  els.deadlineAtBtn.addEventListener("click", () => {
    openAbsoluteDeadlinePicker();
  });
  els.deadlineAtBtn.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openAbsoluteDeadlinePicker();
    }
  });
}
if (els.deadlinePrevMonthBtn) {
  els.deadlinePrevMonthBtn.addEventListener("click", () => shiftDeadlineMonth(-1));
}
if (els.deadlineNextMonthBtn) {
  els.deadlineNextMonthBtn.addEventListener("click", () => shiftDeadlineMonth(1));
}
if (els.deadlineCalendarGrid) {
  els.deadlineCalendarGrid.addEventListener("click", (event) => {
    const button = event.target.closest(".deadline-day-btn");
    if (!button) return;
    const year = Number(button.dataset.year);
    const month = Number(button.dataset.month);
    const day = Number(button.dataset.day);
    if ([year, month, day].some((value) => Number.isNaN(value))) return;
    selectDeadlineDay(year, month, day);
  });
}
if (els.deadlineHourSelect) {
  els.deadlineHourSelect.addEventListener("change", () => {
    setDeadlinePickerTimeFromSelects();
  });
}
if (els.deadlineMinuteSelect) {
  els.deadlineMinuteSelect.addEventListener("change", () => {
    setDeadlinePickerTimeFromSelects();
  });
}
if (els.deadlineTodayBtn) {
  els.deadlineTodayBtn.addEventListener("click", () => {
    const now = new Date();
    now.setSeconds(0, 0);
    deadlinePickerState.selectedDate = now;
    deadlinePickerState.viewYear = now.getFullYear();
    deadlinePickerState.viewMonth = now.getMonth();
    renderDeadlineModal();
  });
}
if (els.deadlineCancelBtn) {
  els.deadlineCancelBtn.addEventListener("click", () => {
    closeDeadlineModal();
  });
}
if (els.deadlineApplyBtn) {
  els.deadlineApplyBtn.addEventListener("click", () => {
    setDeadlinePickerTimeFromSelects();
    if (!deadlinePickerState.selectedDate || !els.deadlineAtInput) {
      closeDeadlineModal();
      return;
    }
    els.deadlineAtInput.value = toDatetimeLocalValue(deadlinePickerState.selectedDate);
    updateAbsoluteDeadlineButtonLabel();
    closeDeadlineModal();
  });
}
if (els.deadlineModalBackdrop) {
  els.deadlineModalBackdrop.addEventListener("click", () => {
    closeDeadlineModal();
  });
}
if (els.taskPriorityFilter) {
  els.taskPriorityFilter.addEventListener("change", (event) => {
    setTaskDimensionsFilters({ priority: event.target.value });
  });
}
if (els.taskCategoryFilter) {
  els.taskCategoryFilter.addEventListener("change", (event) => {
    setTaskDimensionsFilters({ category: event.target.value });
  });
}
if (els.statusFilterBtn) {
  els.statusFilterBtn.addEventListener("click", (event) => {
    event.stopPropagation();
    toggleStatusMenu();
  });
}
if (els.statusFilterOptions) {
  els.statusFilterOptions.forEach((option) => {
    option.addEventListener("click", () => {
      setStatusFilter(option.dataset.statusFilter || "all");
      closeStatusMenu();
    });
  });
}
document.addEventListener("click", (event) => {
  if (!els.statusFilterMenu || !els.statusFilterBtn) return;
  if (els.statusFilterMenu.contains(event.target) || els.statusFilterBtn.contains(event.target)) return;
  closeStatusMenu();
});
document.addEventListener("click", (event) => {
  if (!els.notesTaskPickerMenu || !els.notesTaskPickerBtn) return;
  if (els.notesTaskPickerMenu.contains(event.target) || els.notesTaskPickerBtn.contains(event.target)) return;
  closeNotesTaskPickerMenu();
});
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (!els.deadlineModal || els.deadlineModal.classList.contains("hidden")) return;
  event.preventDefault();
  closeDeadlineModal();
});
if (els.notifyEnabledInput) {
  els.notifyEnabledInput.addEventListener("change", async (event) => {
    const enabled = !!event.target.checked;
    if (enabled) {
      const hasPermission = await ensureNotificationPermission();
      appState.notificationSettings.enabled = hasPermission;
      if (!hasPermission) {
        window.alert("Браузерные уведомления отключены системой. Разрешите уведомления для приложения.");
      }
    } else {
      appState.notificationSettings.enabled = false;
    }
    saveNotificationSettings();
    renderNotificationSettings();
    runDeadlineNotificationCheck().catch(() => {});
  });
}
if (els.notifySoundInput) {
  els.notifySoundInput.addEventListener("change", (event) => {
    appState.notificationSettings.sound = !!event.target.checked;
    saveNotificationSettings();
    renderNotificationSettings();
  });
}
[
  els.notifyMonthInput,
  els.notifyWeekInput,
  els.notifyDayInput,
  els.notify6hInput,
  els.notify1hInput,
  els.notify30mInput,
  els.notify5mInput
].forEach((input) => {
  if (!input) return;
  input.addEventListener("change", (event) => {
    const pointKey = toNotificationPointKey(event.target.id);
    if (!pointKey) return;
    appState.notificationSettings.points[pointKey] = !!event.target.checked;
    saveNotificationSettings();
    renderNotificationSettings();
  });
});
els.summaryCard.addEventListener("click", () => switchView("tasks"));
els.reportCard.addEventListener("dblclick", () => switchView("tasks"));
els.completionCard.addEventListener("click", () => switchView("tasks"));
els.focusCard.addEventListener("click", () => switchView("focus"));
els.productivityCard.addEventListener("click", () => switchView("notes"));
els.filterPills.forEach((pill) => {
  pill.addEventListener("click", () => {
    const filter = pill.dataset.filter || "all";
    setTaskFilter(filter);
    switchView("tasks");
  });
});

renderTimer();
setReplyParent(null);
initMarqueeSelects();
initMarqueePlaceholderInput(els.minutesInput);
setDeadlineInputMode(els.deadlineModeInput?.value || "duration");
setAuthToken(localStorage.getItem(authTokenStorageKey()) || null);
renderProfile();
appState.notificationSettings = loadNotificationSettings();
sentDeadlineNotifications = loadSentDeadlineNotifications();
renderNotificationSettings();
applyTheme(localStorage.getItem("tasktide-theme") === "light" ? "light" : "dark");
switchView("dashboard");
setTaskFilter(appState.taskFilter);
setTaskDimensionsFilters({
  priority: appState.priorityFilter,
  category: appState.categoryFilter
});
setStatusFilter(appState.statusFilter);
startDeadlineTicker();
startGraphsAutoRefresh();
startTasksLiveRefresh();
startNotificationTicker();
runDeadlineNotificationCheck().catch(() => {});
(async () => {
  try {
    if (appState.authToken) {
      await fetchCurrentUser();
      await loadAll();
    } else {
      showAuthModal(true);
    }
  } catch (error) {
    const msg = `Ошибка API: ${error.message}`;
    els.tasksList.innerHTML = `<div class="task-item"><div class="task-title">${msg}</div></div>`;
    els.tasksListFull.innerHTML = `<div class="task-item"><div class="task-title">${msg}</div></div>`;
    els.notesList.innerHTML = `<div class="task-item"><div class="task-title">${msg}</div></div>`;
    if (error.status === 401 || !appState.currentUser) {
      showAuthModal(true);
    }
  }
})();
