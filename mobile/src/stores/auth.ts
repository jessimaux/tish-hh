import { defineStore } from 'pinia';
import authApi from '@/api/auth';
import {getCookie} from '@/tools/core'


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
        // at in coockie, rt localstorage

        async getCurrentUser() {
            this.errors = null
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
            this.isLoading = true
            await authApi.login(user)
                .then(async (response) => {
                    localStorage.setItem('accessToken', response.data.access_token)
                    document.cookie = `refreshToken=${response.data.refresh_token}`
                    this.isLoading = false
                })
                .catch((result) => {
                    this.errors = result.response.data
                    this.isLoading = false
                    throw result.response.data
                })
            this.startRefreshTokenTimer();
        },

        logout() {
            this.currentUser = null
            localStorage.removeItem('accessToken')
            document.cookie = 'refreshToken='
            this.stopRefreshTokenTimer();
        },

        async refreshToken() {
            this.errors = null
            this.isLoading = true
            const refreshToken  = getCookie('refreshToken')
            await authApi.refresh(refreshToken)
            .then(async (response) => {
                localStorage.setItem('accessToken', response.data.access_token)
                document.cookie = `refreshToken=${response.data.refresh_token}`
                this.isLoading = false
            })
            .catch((result) => {
                this.errors = result.response.data
                this.isLoading = false
                throw result.response.data
            })
            this.startRefreshTokenTimer();
        },

        startRefreshTokenTimer() {
            // set a timeout to refresh the token a minute before it expires
            this.refreshTokenTimeout = setTimeout(this.refreshToken, process.env.VUE_APP_JWT_ACCESS_TOKEN_EXPIRE_MINUTES);
        },
        
        stopRefreshTokenTimer() {
            clearTimeout(this.refreshTokenTimeout);
        }
    }
});