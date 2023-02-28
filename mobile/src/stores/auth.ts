import { defineStore } from 'pinia';
import authApi from '@/api/auth';


interface AuthState {
    currentUser: object | null;
    refreshTokenTimeout: number;
    isLoading: boolean;
    errors: object | null;
}

export const useAuthStore = defineStore({
    id: 'auth',
    state: (): AuthState => ({
        currentUser: null,
        refreshTokenTimeout: 0,
        isLoading: false,
        errors: null,
    }),
    actions: {
        async getCurrentUser() {
            this.isLoading = true
            await authApi.getCurrentUser()
                .then((response) => {
                    this.isLoading = false
                    this.currentUser = response.data
                })
                .catch((result) => {
                    this.isLoading = false
                    this.currentUser = null
                })
        },

        async login(user: object) {
            this.errors = null
            await authApi.login(user)
                .then((response) => {
                    localStorage.setItem('accessToken', response.data.access_token)
                })
                .catch((result) => {
                    this.errors = result.response.data
                    throw result.response.data
                })
            this.startRefreshTokenTimer();
        },

        logout() {
            this.stopRefreshTokenTimer();
        },

        async refreshToken() {
            this.startRefreshTokenTimer();
        },

        startRefreshTokenTimer() {
            // set a timeout to refresh the token a minute before it expires
            const expires = new Date(14 * 1000);
            const timeout = expires.getTime() - Date.now() - (60 * 1000);
            this.refreshTokenTimeout = setTimeout(this.refreshToken, timeout);
        },
        
        stopRefreshTokenTimer() {
            clearTimeout(this.refreshTokenTimeout);
        }
    }
});