-- Run in Supabase SQL Editor or with `supabase db push` after linking a project.
-- Email/password auth is enabled by default for hosted Supabase projects. Leave
-- it enabled in Authentication > Providers; this schema does not require login.

create table if not exists public.energy_readings (
  id uuid primary key default gen_random_uuid(),
  timestamp timestamptz not null,
  location_lat double precision not null check (location_lat between -90 and 90),
  location_lng double precision not null check (location_lng between -180 and 180),
  irradiance_ghi double precision not null check (irradiance_ghi >= 0),
  irradiance_dni double precision not null check (irradiance_dni >= 0),
  tilt_angle double precision not null check (tilt_angle between 0 and 90),
  azimuth_angle double precision not null check (azimuth_angle between 0 and 360),
  energy_output_kwh double precision check (energy_output_kwh >= 0),
  mode text not null check (mode in ('fixed', 'tracked')),
  created_at timestamptz not null default now()
);

create table if not exists public.tracker_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  started_at timestamptz not null,
  ended_at timestamptz not null,
  location_lat double precision not null check (location_lat between -90 and 90),
  location_lng double precision not null check (location_lng between -180 and 180),
  total_energy_fixed_kwh double precision not null check (total_energy_fixed_kwh >= 0),
  total_energy_tracked_kwh double precision not null check (total_energy_tracked_kwh >= 0),
  efficiency_gain_pct double precision not null,
  check (ended_at >= started_at)
);

create table if not exists public.kardashev_progress (
  id uuid primary key default gen_random_uuid(),
  -- Nullable so a direct raw-energy demo score can be recorded without a session.
  session_id uuid references public.tracker_sessions(id) on delete cascade,
  scale_value double precision not null,
  computed_at timestamptz not null default now()
);

-- Data access is only through the FastAPI backend using a service-role key for
-- now. Policies can be added with authenticated user ownership in a later phase.
alter table public.energy_readings enable row level security;
alter table public.tracker_sessions enable row level security;
alter table public.kardashev_progress enable row level security;

create index if not exists energy_readings_location_timestamp_idx
  on public.energy_readings (location_lat, location_lng, timestamp);
create index if not exists kardashev_progress_session_idx
  on public.kardashev_progress (session_id, computed_at desc);
