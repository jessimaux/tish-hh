export interface ProfileLink {
  id: number
  name: string
  link: string
}

export interface UserBase {
  username: string
  name: string
  bio: string
  image: string
  country: string
  region: string
  city: string
  links: ProfileLink[]
  events_count: number
  followers_count: number
  following_count: number
}

