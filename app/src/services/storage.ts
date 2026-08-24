import type { StoredScreening } from "./types";

const SESSION_KEY = "ocuscreen:demo-session";
const HISTORY_KEY = "ocuscreen:history";
const CURRENT_KEY = "ocuscreen:current";

export const storage = {
  signedIn: () => typeof window !== "undefined" && localStorage.getItem(SESSION_KEY) === "active",
  signIn: () => localStorage.setItem(SESSION_KEY, "active"),
  signOut: () => { localStorage.removeItem(SESSION_KEY); localStorage.removeItem(CURRENT_KEY); },
  current: (): StoredScreening | null => {
    try { return JSON.parse(sessionStorage.getItem(CURRENT_KEY) || "null"); } catch { return null; }
  },
  setCurrent: (value: StoredScreening): boolean => {
    try {
      sessionStorage.setItem(CURRENT_KEY, JSON.stringify(value));
      return true;
    } catch {
      sessionStorage.removeItem(CURRENT_KEY);
      try {
        sessionStorage.setItem(CURRENT_KEY, JSON.stringify(value));
        return true;
      } catch {
        return false;
      }
    }
  },
  history: (): StoredScreening[] => {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]"); } catch { return []; }
  },
  add: (value: StoredScreening): boolean => {
    const entries = [value, ...storage.history().filter(item => item.id !== value.id)].slice(0, 20);
    // Full retinal images can exceed browser storage limits. Preserve the newest
    // screenings and progressively evict the oldest until the write succeeds.
    while (entries.length > 0) {
      try {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(entries));
        return true;
      } catch {
        entries.pop();
      }
    }
    return false;
  },
};
