/**
 * gptc extension — shared constants & defaults.
 */

export const DEFAULT_SETTINGS = {
  // Base URL of the gptc server (default: public instance; run your own with
  // `python -m gptc --port 1337` and point this at http://localhost:1337).
  serverUrl: "https://gptc.space",
  // Optional API key (GPTC_API_KEY). Empty = no auth.
  apiKey: "",
  // Default model id (from /v1/models). Empty = server default.
  model: "",
  // Default provider name. Empty = server default / auto.
  provider: "",
  // Streaming responses.
  stream: true,
  // System prompt prepended to every conversation.
  systemPrompt: "You are a helpful assistant running inside a browser extension. Be concise and use markdown.",
  // Temperature (null = provider default).
  temperature: null,
  // Max tokens (null = provider default).
  maxTokens: null,
  // Include the text of the active tab as context when asked from the side panel.
  includePageContext: false,
  // Max characters of page context to send.
  pageContextLimit: 6000,
  // Image generation defaults.
  imageModel: "",
  imageCount: 1,
  // UI
  fontSize: "medium",
  sendOnEnter: true,
  // Quick actions shown in the popup.
  quickActions: [
    { id: "summarize", label: "Summarize page", prompt: "Summarize the following page content in a few bullet points:\n\n" },
    { id: "explain", label: "Explain selection", prompt: "Explain this in simple terms:\n\n" },
    { id: "translate", label: "Translate to English", prompt: "Translate the following text to English. Only output the translation:\n\n" },
    { id: "reply", label: "Draft a reply", prompt: "Draft a short, friendly reply to this message:\n\n" },
  ],
};

export const STORAGE_KEYS = {
  settings: "settings",
  conversations: "conversations",
  activeConversation: "activeConversationId",
  // OAuth session (chrome.storage.local)
  user: "gptcUser",
  token: "gptcToken",
  expires: "gptcExpires",
  workspaceSecret: "gptcWorkspaceSecret",
};

export const MESSAGE_TYPES = {
  // popup/sidepanel -> background
  CHAT: "gptc:chat",
  CHAT_ABORT: "gptc:chat:abort",
  IMAGE: "gptc:image",
  MODELS: "gptc:models",
  PROVIDERS: "gptc:providers",
  HEALTH: "gptc:health",
  GET_PAGE: "gptc:get-page",
  GET_SELECTION: "gptc:get-selection",
  OPEN_SIDE_PANEL: "gptc:open-side-panel",
  // account & cloud sync
  OAUTH_START: "gptc:oauth:start",
  OAUTH_LOGOUT: "gptc:oauth:logout",
  OAUTH_STATUS: "gptc:oauth:status",
  SYNC_PUSH: "gptc:sync:push",
  SYNC_PULL: "gptc:sync:pull",
  SYNC_NOW: "gptc:sync:now",
  // background -> UI (stream chunks)
  STREAM_CHUNK: "gptc:stream:chunk",
  STREAM_DONE: "gptc:stream:done",
  STREAM_ERROR: "gptc:stream:error",
};

/** Parse a server base URL, trimming trailing slashes. */
export function normalizeBaseUrl(url) {
  let u = (url || "").trim();
  if (!u) return DEFAULT_SETTINGS.serverUrl;
  if (!/^https?:\/\//i.test(u)) u = "http://" + u;
  return u.replace(/\/+$/, "");
}
