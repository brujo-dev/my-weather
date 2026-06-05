# myWeather — Design System

## Indice
1. [Filosofia](#filosofia)
2. [Token CSS (variabili)](#token-css)
3. [Tipografia](#tipografia)
4. [Colori e sfondi](#colori-e-sfondi)
5. [Primitive: Glass](#primitive-glass)
6. [Layout](#layout)
7. [Componenti](#componenti)
   - [Navbar](#navbar)
   - [Bottoni](#bottoni)
   - [Form](#form)
   - [Cards](#cards)
   - [Alert e Flash messages](#alert-e-flash-messages)
   - [Footer](#footer)
8. [Pattern per pagina](#pattern-per-pagina)
   - [Pagine centrate (auth / search / history)](#pagine-centrate)
   - [Dashboard](#dashboard)
   - [Profile](#profile)
9. [Animazioni](#animazioni)
10. [Cursore meteo-aware](#cursore-meteo-aware)
11. [Responsive](#responsive)

---

## Filosofia

Il design system è basato su **glassmorphism** su sfondo scuro fisso (`#0b1020`). Ogni elemento visibile usa la primitiva `.glass` — sfondo semi-trasparente con `backdrop-filter: blur`. L'estetica è dark, raffinata, con testo bianco e accenti viola/blu/verde.

Principi guida:
- **Glass over everything** — nessun elemento solido opaco, tutto è traslucido
- **Colori tramite CSS variables** — mai hardcodare colori fuori dalle var
- **Hover = lift** — tutti i componenti interattivi si alzano di 4px su hover (`translateY(-4px)`)
- **Transizioni brevi** — 0.2s–0.25s ease per micro-interazioni
- **Font ereditato** — tutti i bottoni e input usano `font-family: inherit`

---

## Token CSS

Definiti in `:root`, da usare sempre al posto dei valori hardcodati.

```css
:root {
    --font-family: 'Google Sans', 'DM Sans', 'Helvetica Neue', Arial, sans-serif;

    /* Testo */
    --color-text:       #ffffff;                    /* testo principale */
    --color-text-muted: rgba(255, 255, 255, 0.78);  /* testo secondario */
    --color-text-dim:   rgba(255, 255, 255, 0.6);   /* testo terziario, label, date */

    /* Glass */
    --glass-bg:         rgba(255, 255, 255, 0.12);  /* background card */
    --glass-bg-strong:  rgba(255, 255, 255, 0.18);  /* background card su hover */
    --glass-border:     rgba(255, 255, 255, 0.25);  /* bordo card */
    --glass-shadow:     0 8px 32px rgba(0, 0, 0, 0.25);

    /* Border radius */
    --radius-lg: 24px;  /* card grandi */
    --radius-md: 16px;  /* input, bottoni, card piccole */
}
```

---

## Tipografia

**Font stack:** `'Google Sans'` → `'DM Sans'` → `'Helvetica Neue'` → `Arial`

| Uso | Size | Weight | Note |
|---|---|---|---|
| Titolo hero temperatura | `clamp(4.5rem, 12vw, 7rem)` | 500 | `letter-spacing: -2px` |
| Titolo hero città | `clamp(2rem, 4vw, 3rem)` | 700 | |
| Titolo pagina (auth/search) | `2rem` | 700 | `letter-spacing: 0.3px` |
| Section title (forecast) | `1.25rem` | 500 | `color: --color-text-muted` |
| Body / descrizione | `1rem` | 400 | |
| Stat value | `1.75rem` | 700 | `letter-spacing: -0.5px` |
| Temperature card | `2rem`–`2.5rem` | 500–700 | |
| Label uppercase | `0.78rem`–`0.85rem` | 500 | `text-transform: uppercase; letter-spacing: 0.4–0.5px` |
| Data / testo dim | `0.8rem` | 400 | `color: --color-text-dim` |

---

## Colori e Sfondi

### Base
```css
background: #0b1020;  /* blu-notte, sempre fisso */
```

### Sfondo pagine centrate (auth / search / history / profile)
Applicato tramite `::before` pseudo-elemento fisso (`position: fixed; inset: 0; z-index: -1`):
```css
background:
    radial-gradient(circle at 25% 15%, rgba(110, 130, 230, 0.45), transparent 55%),  /* viola-blu top-left */
    radial-gradient(circle at 80% 85%, rgba(220, 100, 180, 0.35), transparent 55%),  /* rosa bottom-right */
    linear-gradient(160deg, #0b1020 0%, #1a1340 100%);
```

### Sfondo Dashboard (city background)
`.city-bg` — immagine fotografica della città, `position: fixed`, `filter: saturate(110%)`
`.city-bg-overlay` — overlay con gradienti radiali per leggibilità:
```css
background:
    radial-gradient(circle at 20% 0%, rgba(80, 100, 200, 0.35), transparent 60%),
    radial-gradient(circle at 80% 100%, rgba(200, 80, 160, 0.25), transparent 55%),
    linear-gradient(180deg, rgba(10, 15, 35, 0.45) 0%, rgba(10, 15, 35, 0.75) 100%);
```

### Palette accenti (usata nei bottoni)
| Colore | Uso | Valore |
|---|---|---|
| Viola/blu | `btn-primary` (CTA principale) | `rgba(140,170,255,0.7)` → `rgba(200,120,220,0.7)` |
| Rosso | `btn-danger` (rimuovi) | `rgba(255,90,110,0.7)` → `rgba(220,60,90,0.7)` |
| Verde | `btn-save-city` (salva) | `rgba(100,200,160,0.7)` → `rgba(60,160,120,0.7)` |
| Rosso logout | `btn-logout` | `rgba(255,110,130,0.7)` → `rgba(220,80,120,0.7)` |
| Utente navbar | `navbar-user` | `rgba(140,170,255,0.45)` → `rgba(200,120,220,0.45)` |

---

## Primitive: Glass

La classe `.glass` è il mattone fondamentale di tutto il sistema. Si applica a qualsiasi contenitore visibile.

```css
.glass {
    background: var(--glass-bg);                        /* rgba bianco 12% */
    border: 1px solid var(--glass-border);              /* rgba bianco 25% */
    border-radius: var(--radius-lg);                    /* 24px */
    backdrop-filter: blur(22px) saturate(180%);
    -webkit-backdrop-filter: blur(22px) saturate(180%);
    box-shadow: var(--glass-shadow);
}
```

**Hover state** (su card interattive):
```css
transform: translateY(-4px);
background: var(--glass-bg-strong);  /* rgba bianco 18% */
```

---

## Layout

### Struttura globale
```
body (flex column, min-height: 100vh)
  ├── nav.navbar (sticky top)
  ├── main (flex: 1, z-index: 1)
  │     ├── .flash-list (messaggi flash)
  │     └── {% block content %}
  └── footer
```

### Layout centrato (pagine auth/search/history/profile)
```css
.auth-wrapper / .search-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 160px);
    padding: 48px 24px;
}
```
Il contenuto interno ha `max-width: 420px` (auth) o `max-width: 500px` (search/profile).

### Layout dashboard
```css
.dashboard-wrapper {
    max-width: 1100px;
    margin: 0 auto;
    padding: 48px 24px 64px;
    display: flex;
    flex-direction: column;
    gap: 32px;
}
```

---

## Componenti

### Navbar

```html
<nav class="navbar">
    <div class="navbar-brand">myWeather</div>
    <ul class="navbar-links">
        <li><a href="..." class="active">Link</a></li>
        <li><a href="..." class="navbar-user">👤 Username</a></li>
    </ul>
</nav>
```

- Sticky, `z-index: 50`, `backdrop-filter: blur(18px)`
- Link normali: pill `border-radius: 999px`, hover aggiunge `var(--glass-bg)`
- Link attivo `.active`: aggiunge `var(--glass-bg-strong)` + bordo glass
- Link utente `.navbar-user`: gradiente viola/rosa, sempre con bordo

---

### Bottoni

Tutti i bottoni condividono:
- `font-family: inherit`
- `border-radius: var(--radius-md)` (16px)
- `transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease`
- Hover: `translateY(-1px)` + `filter: brightness(1.08)` + box-shadow colorato
- Active: `translateY(0)`

#### `.btn-primary` — azione principale (cerca, accedi, registrati)
```css
background: linear-gradient(135deg, rgba(140,170,255,0.7), rgba(200,120,220,0.7));
padding: 14px 20px;
font-size: 1rem; font-weight: 600;
```

#### `.btn-danger` — rimozione (rimuovi città)
```css
background: linear-gradient(135deg, rgba(255,90,110,0.7), rgba(220,60,90,0.7));
border-color: rgba(255,130,150,0.4);
width: 100%;  /* full-width nella card */
```

#### `.btn-save-city` — salvataggio città
```css
background: linear-gradient(135deg, rgba(100,200,160,0.7), rgba(60,160,120,0.7));
border-color: rgba(120,220,170,0.4);
padding: 12px 28px;
```

#### `.btn-logout` — logout (estende `.btn-primary`)
```css
background: linear-gradient(135deg, rgba(255,110,130,0.7), rgba(220,80,120,0.7));
display: block; width: 100%; text-align: center;
```

---

### Form

Struttura standard per tutti i form:

```html
<form class="auth-form">  <!-- oppure search-form -->
    <div class="form-field">
        <label>...</label>
        <input type="text" ...>
        <span class="form-error">Messaggio errore</span>  <!-- se presente -->
    </div>
    <button class="btn-primary">Invia</button>
</form>
```

#### Input
```css
/* .form-field input  oppure  .form-input */
background: rgba(255, 255, 255, 0.08);
border: 1px solid var(--glass-border);
border-radius: var(--radius-md);
padding: 12px 16px;
color: var(--color-text);

/* :hover */
background: rgba(255, 255, 255, 0.12);

/* :focus */
background: rgba(255, 255, 255, 0.15);
border-color: rgba(180, 200, 255, 0.6);
box-shadow: 0 0 0 3px rgba(140, 170, 255, 0.18);  /* focus ring blu */
```

#### Label
```css
font-size: 0.85rem; font-weight: 500;
color: var(--color-text-muted);
letter-spacing: 0.4px;
```

#### Errore di validazione
```css
.form-error {
    display: block;
    font-size: 0.8rem;
    color: rgba(255, 130, 150, 0.95);  /* rosso chiaro */
}
```

---

### Cards

#### Card generica `.glass`
Base riutilizzabile, padding variabile per contesto.

#### `.auth-card` — login / register / profile
```css
max-width: 420px; padding: 40px 36px;
```

#### `.forecast-card` — previsioni orarie
```css
padding: 24px 20px; text-align: center;
/* contiene: .forecast-time (dim), .forecast-temp (2rem), .forecast-description (muted) */
```

#### `.city-card` — città salvate con meteo live
```css
padding: 24px 20px;
display: flex; flex-direction: column; gap: 6px;
/* contiene: .city-card-header (.city-card-name + .city-card-country) */
/*           .city-card-temp (2.5rem bold), .city-card-description, .city-card-humidity */
/*           .delete-city-form con .btn-danger */
```

#### `.search-card` / `.results-card` / `.no-results-card` — pagina search
```css
.search-card    { padding: 40px 36px; }
.results-card   { padding: 32px 36px; animation: slideUp 0.4s ease; }
.no-results-card { padding: 40px 36px; text-align: center; animation: slideUp 0.4s ease; }
```

#### `.profile-stat-card` — statistiche profilo
```css
padding: 24px 16px; text-align: center;
/* .profile-stat-value (1.75rem bold), .profile-stat-label (uppercase dim) */
```

---

### Alert e Flash messages

```html
<div class="flash-list">
    <div class="alert alert-success">Messaggio</div>
    <div class="alert alert-error">Errore</div>
    <div class="alert alert-warning">Attenzione</div>
    <div class="alert alert-info">Info</div>
</div>
```

```css
.alert { padding: 12px 16px; border-radius: var(--radius-md); text-align: center; }

.alert-success { background: rgba(120,220,160,0.18); border-color: rgba(150,230,180,0.45); }
.alert-error   { background: rgba(255,90,110,0.18);  border-color: rgba(255,130,150,0.45); }
.alert-warning { background: rgba(255,190,80,0.18);  border-color: rgba(255,210,120,0.45); }
.alert-info    { background: rgba(100,160,255,0.18); border-color: rgba(140,190,255,0.45); }
```

Nota: `.alert-rain` (dashboard) usa `rgba(80,140,255,0.18)` — variante blu per pioggia prevista.

---

### Footer

```css
footer {
    padding: 24px; text-align: center;
    color: var(--color-text-dim); font-size: 0.85rem;
    background: rgba(10, 15, 35, 0.6);
    backdrop-filter: blur(12px);
    border-top: 1px solid var(--glass-border);
}
```

---

## Pattern per pagina

### Pagine centrate

Usate da: **login**, **register**, **search**, **history**, **profile**.

```html
<div class="auth-wrapper">           <!-- oppure search-wrapper -->
    <div class="search-layout">      <!-- oppure profile-layout -->
        <section class="glass search-card">
            <h1 class="search-title">Titolo</h1>
            <!-- contenuto -->
        </section>
        <!-- eventuale seconda card (risultati, stats) -->
    </div>
</div>
```

Lo sfondo radiale viola/rosa viene applicato dal `::before` del wrapper — **non serve aggiungere nulla allo `<body>`**.

---

### Dashboard

```html
<div class="city-bg" style="background-image: url(...)"></div>
<div class="city-bg-overlay"></div>
<div class="weather-intro" data-type="{{ weather_type }}"><!-- particelle --></div>

<div class="dashboard-wrapper">
    <h2 class="dashboard-welcome">Ciao, {{ user.username }}!</h2>
    <section class="hero glass">...</section>
    <div class="alert glass alert-rain">...</div>  <!-- condizionale -->
    <section class="forecast">
        <div class="forecast-row">
            <div class="forecast-card glass">...</div>
        </div>
    </section>
    <section class="saved-cities">
        <div class="cities-grid">
            <div class="city-card glass">...</div>
        </div>
    </section>
</div>
```

Il `data-weather` sul `<body>` (impostato in `base.html`) controlla il **cursore emoji** e le **animazioni particelle**.

---

### Profile

```html
<div class="auth-wrapper">
    <div class="profile-layout">         <!-- max-width: 500px, flex column -->
        <section class="auth-card glass">
            <!-- info utente + logout -->
        </section>
        <section class="profile-stats">
            <div class="profile-stats-grid">  <!-- 3 colonne -->
                <div class="profile-stat-card glass">
                    <p class="profile-stat-value">42</p>
                    <p class="profile-stat-label">Label</p>
                </div>
            </div>
        </section>
    </div>
</div>
```

---

## Animazioni

### `slideUp` — comparsa card risultati
```css
@keyframes slideUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
/* Usato da: .results-card, .no-results-card */
```

### Weather intro (particelle)
La `.weather-intro` è un overlay `position: fixed` che scompare dopo 2.5s (fade 1s) e viene rimosso dal DOM dopo 3.5s via JavaScript.

| Tipo meteo | Comportamento particelle | Animazione |
|---|---|---|
| `rain`, `storm` | Gocce cadono dall'alto | `fall` |
| `snow` | Fiocchi con oscillazione laterale | `fall-sway` |
| `cloudy`, `fog` | Nuvole driftano orizzontalmente | `drift` |
| `clear`, `clear_night` | Soli/lune pulsano e svaniscono | `pulse` |
| `storm` | Flash lampo (overlay `::before`) | `flicker` |

Le particelle usano CSS custom properties inline: `--x`, `--y`, `--dur`, `--delay`.

---

## Cursore meteo-aware

`body[data-weather="X"]` imposta un cursore SVG emoji corrispondente:

| `data-weather` | Cursore |
|---|---|
| `rain` | ☔ |
| `storm` | ⛈️ |
| `snow` | ❄️ |
| `cloudy` / `cloudy_night` | ☁️ |
| `fog` | 🌫️ |
| `clear` | ☀️ |
| `clear_night` | 🌙 |

Il valore viene impostato in `base.html`: `<body data-weather="{{ weather_type | default('clear') }}">`.

---

## Responsive

Breakpoint unico a `640px`:

```css
@media (max-width: 640px) {
    .navbar           { flex-direction: column; gap: 8px; padding: 12px 16px; }
    .dashboard-wrapper { padding: 24px 16px 40px; }
    .hero             { padding: 32px 20px; }
    .auth-card        { padding: 32px 24px; }
    .search-card,
    .results-card,
    .no-results-card  { padding: 32px 24px; }
    .search-title     { font-size: 1.5rem; }
    .result-city-name { font-size: 1.3rem; }
    .result-grid      { grid-template-columns: 1fr; }  /* da 2 a 1 colonna */
}
```

Le grid (`forecast-row`, `cities-grid`) usano `auto-fit`/`auto-fill` con `minmax()` e si adattano automaticamente senza breakpoint aggiuntivi.
