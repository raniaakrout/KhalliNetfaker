/**
 * Token management utilities
 */

const TOKEN_KEY = 'token';

export const TokenUtils = {

  setToken: (token: string) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(TOKEN_KEY, token);
    }
  },

  /**
   * Get token from localStorage.
   */
  getToken: (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(TOKEN_KEY);
    }
    return null;
  },

  /**
   * Remove token from localStorage and clear the httpOnly cookie via the backend.
   */
  removeToken: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
    }
  },

  /**
   * Check if user is authenticated (based on localStorage token presence).
   */
  isAuthenticated: (): boolean => {
    return !!TokenUtils.getToken();
  },
};
