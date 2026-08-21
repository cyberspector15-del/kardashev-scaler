import { createClient, type SupabaseClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

/** Optional client for future auth. The demo remains usable when unconfigured. */
export const supabase: SupabaseClient | null = url && anonKey ? createClient(url, anonKey) : null
