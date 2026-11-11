export interface User { id: number; email: string; first_name?: string; last_name?: string; phone?: string; bio?: string; roles?: string[]; status?: string; }
export interface TokenOut { access_token: string; user: User; }
export interface Page<T> { items: T[]; total: number; page: number; size: number; }
export interface Msg { detail: string; }
export interface Ref { id: number; name: string; region_id?: number; }
export interface Img { id: number; url?: string; path?: string; }
export interface PropertyCard { id: number; title: string; price: number; city_name?: string; images?: Img[]; is_favorite?: boolean; status?: string; coliving?: boolean; rooms?: number | null;surface_m2?: number | null;category_name?: string | null;}
export interface PropertyDetail extends PropertyCard { description?: string; rooms?: number; surface_m2?: number | null; available_from?: string | null; coliving_allowed?: boolean; max_roommates?: number; owner_id?: number; address?: string; conditions?: string;category_name?: string | null; }
export interface PropertyPayload { title: string; description: string; price: number; rooms: number; surface_m2: number | null; city_id: number; category_id: number; address: string; coliving_allowed: boolean; max_roommates: number; conditions: string; available_from: string | null; }
export interface PropertyFilters { q?: string; city_id?: number | string; category_id?: number | string; min_price?: number | string; max_price?: number | string; min_rooms?: number | string; coliving?: boolean | ''; sort?: string; }
export interface RentalRequest { id: number; status: string; message?: string; property?: PropertyCard; group_id?: number | null; }
export interface Slot { id: number; starts_at: string; ends_at: string; }
export interface Visit { id: number; status: string; property_id?: number; slots?: Slot[]; }
export interface Conversation { id: number; title?: string; unread_count?: number; }
export interface ChatMessage { id: number; sender_id: number; body: string | null; attachment?: { id: number; original_name: string } | null; }
export interface AppNotification { id: number; title: string; body?: string; is_read: boolean; }
export interface NotificationList { items: AppNotification[]; unread_count: number; }
export type Schedule = 'EARLY' | 'NIGHT' | 'FLEXIBLE';
export interface RoommateProfile {id?: number; user_id: number; city_id?: number | null;budget_min?: number | string | null; budget_max?: number | string | null;smoker: boolean; has_pets: boolean; schedule: Schedule;cleanliness: number; sociability: number;about?: string | null; is_active: boolean;looking_for?: 'ROOM' | 'HOUSE';}
export interface RoommateMatch { profile: RoommateProfile; display_name: string; score: number; }
export interface RoommateRequest { id: number; status: string; message?: string | null; sender_id?: number; receiver_id?: number; created_at?: string; }
export interface Group { id: number; name: string; max_members: number; members?: { user_id: number }[]; }
export interface Invitation { id: number; group_id: number; status: string; }
export interface Review { id: number; rating: number; comment?: string; }
export interface ReviewList { items: Review[]; average: number | null; count: number; }
export interface AdminUser { id: number; email: string; status: string; roles: string[]; }
export interface SavedSearch { id: number; name: string; filters: PropertyFilters; alert_active: boolean; }
