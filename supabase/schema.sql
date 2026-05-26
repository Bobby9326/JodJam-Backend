-- USERS
create table users (
    id uuid primary key references auth.users(id) on delete cascade,
    username text unique not null,
    avatar_url text,
    bio text,
    created_at timestamptz default now()
);

-- ENTRIES
create table entries (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users(id) on delete cascade,
    date date not null,
    image_url text not null,
    note text not null,
    mood text check (
        mood in (
            'happy',
            'sad',
            'tired',
            'stressed',
            'excited',
            'angry',
            'bored',
            'lonely'
        )
    ),
    rating int check (
        rating between 1 and 5
    ),
    created_at timestamptz default now(),
    unique(user_id, date)
);

