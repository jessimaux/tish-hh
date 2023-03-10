import { defineStore } from 'pinia';
import authApi from '@/api/users';

interface UserState {
    data: User | null;
    isLoading: boolean;
    errors: object | null;
}

interface User {
    username: string
    name: string
    bio: string
    image: string
    events_count: number
    followers_count: number
    following_count: number
}

export const useUsersStore = defineStore({
    id: 'users',
    state: (): UserState => ({
        data: null,
        isLoading: true,
        errors: null,
    }),
    actions: {
        async getUser(username: string) {
            this.errors = null
            this.isLoading = true
            await authApi.getUser(username)
            .then((response) => {
                this.isLoading = false
                this.data = response.data
            })
            .catch((result) => {
                this.isLoading = false
                this.errors = result.response
                throw result.response.data
            })
        }
    }
});